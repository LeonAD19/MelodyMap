// side-panel.test.js
// Run with: node --test flask_folder/tests/side-panel.test.js
// Requires Node.js 18+

const { test, describe, beforeEach } = require('node:test');
const assert = require('node:assert');
const { JSDOM } = require('jsdom');

// Import the actual SidePanel class from the source file
// This ensures tests always test the real production code
const { SidePanel } = require('../static/js/side-panel.js');

// Set up DOM environment
let dom, document, window;

function resetDOM() {
  dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
  document = dom.window.document;
  window = dom.window;
  global.document = document;
  global.window = window;
}

describe('SidePanel', () => {
  let sidePanel;

  beforeEach(() => {
    resetDOM();
    sidePanel = new SidePanel();
  });

  describe('constructor', () => {
    test('creates panel elements in DOM', () => {
      assert.ok(document.getElementById('side-panel'));
      assert.ok(document.getElementById('side-panel-overlay'));
      assert.ok(document.getElementById('side-panel-iframe'));
    });

    test('initializes isOpen to false', () => {
      assert.strictEqual(sidePanel.isOpen, false);
    });

    test('creates close button with correct aria-label', () => {
      const closeBtn = document.getElementById('side-panel-close');
      assert.ok(closeBtn);
      assert.strictEqual(closeBtn.getAttribute('aria-label'), 'Close panel');
    });
  });

  describe('open()', () => {
    test('sets iframe src and opens panel completely', () => {
      const url = 'https://open.spotify.com/embed/track/test123';

      sidePanel.open(url);

      assert.strictEqual(sidePanel.iframe.src, url);
      assert.ok(sidePanel.panel.classList.contains('open'));
      assert.ok(sidePanel.overlay.classList.contains('show'));
      assert.strictEqual(sidePanel.isOpen, true);
    });

    test('does nothing when url is null', () => {
      sidePanel.open(null);

      assert.strictEqual(sidePanel.isOpen, false);
      assert.strictEqual(sidePanel.panel.classList.contains('open'), false);
      assert.strictEqual(sidePanel.overlay.classList.contains('show'), false);
    });

    test('does nothing when url is empty string', () => {
      sidePanel.open('');

      assert.strictEqual(sidePanel.isOpen, false);
      assert.strictEqual(sidePanel.panel.classList.contains('open'), false);
    });
  });

  describe('close()', () => {
    test('closes panel and removes all classes and state', () => {
      sidePanel.open('https://example.com');

      sidePanel.close();

      assert.strictEqual(sidePanel.panel.classList.contains('open'), false);
      assert.strictEqual(sidePanel.overlay.classList.contains('show'), false);
      assert.strictEqual(sidePanel.isOpen, false);
    });

    test('can be called safely when panel is already closed', () => {
      assert.strictEqual(sidePanel.isOpen, false);

      sidePanel.close();

      assert.strictEqual(sidePanel.isOpen, false);
    });
  });

  describe('event listeners', () => {
    test('close button closes panel completely', () => {
      sidePanel.open('https://example.com');

      document.getElementById('side-panel-close').click();

      assert.strictEqual(sidePanel.isOpen, false);
      assert.strictEqual(sidePanel.panel.classList.contains('open'), false);
      assert.strictEqual(sidePanel.overlay.classList.contains('show'), false);
    });

    test('overlay click closes panel completely', () => {
      sidePanel.open('https://example.com');

      sidePanel.overlay.click();

      assert.strictEqual(sidePanel.isOpen, false);
      assert.strictEqual(sidePanel.panel.classList.contains('open'), false);
      assert.strictEqual(sidePanel.overlay.classList.contains('show'), false);
    });

    test('escape key closes panel when open', () => {
      sidePanel.open('https://example.com');

      const event = new window.KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(event);

      assert.strictEqual(sidePanel.isOpen, false);
      assert.strictEqual(sidePanel.panel.classList.contains('open'), false);
    });

    test('escape key does nothing when panel is closed', () => {
      assert.strictEqual(sidePanel.isOpen, false);

      const event = new window.KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(event);

      assert.strictEqual(sidePanel.isOpen, false);
    });

    test('other keys do not affect the panel', () => {
      sidePanel.open('https://example.com');

      const enterEvent = new window.KeyboardEvent('keydown', { key: 'Enter' });
      document.dispatchEvent(enterEvent);

      assert.strictEqual(sidePanel.isOpen, true);
    });
  });

  describe('window.openSidePanel()', () => {
    beforeEach(() => {
      // Set up window.openSidePanel (from side-panel.js)
      window.openSidePanel = function(url) {
        if (!window.sidePanel) {
          window.sidePanel = new SidePanel();
        }
        window.sidePanel.open(url);
      };
    });

    test('creates SidePanel instance on first call', () => {
      assert.strictEqual(window.sidePanel, undefined);

      window.openSidePanel('https://example.com');

      assert.ok(window.sidePanel);
      assert.strictEqual(window.sidePanel.isOpen, true);
    });

    test('reuses existing SidePanel instance', () => {
      window.openSidePanel('https://example.com/track1');
      const firstInstance = window.sidePanel;

      window.openSidePanel('https://example.com/track2');

      assert.strictEqual(window.sidePanel, firstInstance);
      assert.strictEqual(window.sidePanel.iframe.src, 'https://example.com/track2');
    });

    test('opens panel with Spotify embed URL', () => {
      const testUrl = 'https://open.spotify.com/embed/track/abc123';

      window.openSidePanel(testUrl);

      assert.strictEqual(window.sidePanel.iframe.src, testUrl);
      assert.strictEqual(window.sidePanel.isOpen, true);
    });
  });
});
