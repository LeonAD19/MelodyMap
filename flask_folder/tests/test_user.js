// pull in test dependencies
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { URLSearchParams } = require("node:url");

// load user.js as a a script
const userScript = fs.readFileSync(
  path.join(__dirname, "..", "static", "js", "user.js"),
  "utf8"
);

// helper function to create mock DOM elements
function createElement() {
  return { style: {}, textContent: "", src: "" };
}

// function to run the user.js script in a controlled context
// with elelments and fetch mocked
function runUserScript({ authorized = true, payload }) {
  const elements = {
    "user-card": createElement(),
    "user-art": createElement(),
    "user-title": createElement(),
    "user-artists": createElement(),
    "user-progress-fill": createElement(),
    "user-current": createElement(),
    "user-duration": createElement(),
  };

  // mock document and event handling
  const document = {
    getElementById: (id) => elements[id],
    addEventListener: (event, callback) => {
      if (event === "DOMContentLoaded") {
        // store the callback to trigger later
        // context._onReady will be called to simulate DOM ready
        context._onReady = callback;
      }
    },
  };

  // to track intervals set by the script 
  // mockNow will simulate the current time
  const intervals = [];
  let mockNow = 0;

  // create the context for the script
  const context = {
    console,
    URLSearchParams,
    window: { SPOTIFY_AUTH: authorized },
    document,
    fetch: () =>
      Promise.resolve({
        json: () => Promise.resolve(payload()),
      }),
    setInterval: (fn) => {
      intervals.push(fn);
      return intervals.length;
    },
    // no operation clearInterval
    clearInterval: () => {},
    Date: class extends Date {
        // ...args are passed to the original Date constructor 
        // it collects them but we override now()
      constructor(...args) {
        super(...args);
      }
      static now() {
        return mockNow;
      }
    },
    setImmediate,
  };

  context.global = context;
  context.globalThis = context;

  // run the user script in the created context
  vm.runInNewContext(userScript, context, { filename: "user.js" });

  // return handles to elements and intervals for assertions
  return {
    elements,
    intervals,
    setNow: (v) => {
      mockNow = v;
    },
    async triggerDomReady() {
      context._onReady();
      // allow async tasks (fetch/json) to resolve
      await new Promise((r) => setImmediate(r));
      await new Promise((r) => setImmediate(r));
    },
  };
}

test("hides the card when the user is not authorized", async () => {
  const harness = runUserScript({
    authorized: false, 
    payload: () => ({}),
  });

  await harness.triggerDomReady();

  assert.equal(harness.elements["user-card"].style.display, "none");
  assert.equal(harness.intervals.length, 0, "no intervals should start");
});

test("hides the card when backend reports unauthorized", async () => {
  const harness = runUserScript({
    authorized: true,
    payload: () => ({ authorized: false }),
  });

  await harness.triggerDomReady();

  assert.equal(harness.elements["user-card"].style.display, "none");
});

test("renders now-playing data and advances progress on tick", async () => {
  const harness = runUserScript({
    authorized: true,
    payload: () => ({
      authorized: true,
      playing: {
        name: "Test Song",
        artists: "Test Artist",
        art: "/img/test.png",
        progress_ms: 50000,
        duration_ms: 100000,
        is_playing: true,
      },
    }),
  });

  harness.setNow(0);
  await harness.triggerDomReady();

  const card = harness.elements["user-card"];
  assert.equal(card.style.display, "block");
  assert.equal(harness.elements["user-title"].textContent, "Test Song");
  assert.equal(harness.elements["user-artists"].textContent, "Test Artist");
  assert.equal(harness.elements["user-art"].src, "/img/test.png");
  assert.equal(harness.elements["user-progress-fill"].style.width, "50%");

  // Simulate 5 seconds of playback and tick
  harness.setNow(5000);
  const tick = harness.intervals[1]; // second interval is tick
  tick();

  const widthAfterTick = parseFloat(
    harness.elements["user-progress-fill"].style.width
  );
  assert.ok(widthAfterTick > 50, "progress should advance");
});
