// ui-interactions.test.cjs
const assert = require('assert');
const fs = require('fs');
const { JSDOM } = require('jsdom');

// Track test results
const results = [];

function recordResult(name, passed, error) {
  results.push({ name, passed, error });
}

// Setup JSDOM for DOM testing
const dom = new JSDOM(`
  <html>
    <body>
      <button id="settings-btn">Open Settings</button>
      <div id="settings-popup" class="">Settings Popup</div>
      <button id="close-btn">Close</button>
      <button id="theme-btn">Toggle Theme</button>
    </body>
  </html>
`);

const document = dom.window.document;

// Simulate your script (attach listeners)
try {
  const settingsBtn = document.getElementById('settings-btn');
  const closeBtn = document.getElementById('close-btn');
  const popup = document.getElementById('settings-popup');
  const themeBtn = document.getElementById('theme-btn');

  if (!settingsBtn || !closeBtn || !popup || !themeBtn) {
    throw new Error('One or more elements not found in DOM');
  }

  settingsBtn.addEventListener('click', () => popup.classList.add('open'));
  closeBtn.addEventListener('click', () => popup.classList.remove('open'));
  themeBtn.addEventListener('click', () => {
    popup.classList.toggle('dark-theme');
  });

} catch (err) {
  console.error('Error setting up DOM listeners:', err);
}

// TESTS
try {
  // Test opening popup
  const popup = document.getElementById('settings-popup');
  const settingsBtn = document.getElementById('settings-btn');

  settingsBtn.click();
  recordResult('opens settings popup on button click', popup.classList.contains('open'));

  // Test closing popup
  const closeBtn = document.getElementById('close-btn');
  closeBtn.click();
  recordResult('closes settings popup on close button click', !popup.classList.contains('open'));

  // Test toggling theme
  const themeBtn = document.getElementById('theme-btn');
  themeBtn.click();
  recordResult('toggles theme on theme button click', popup.classList.contains('dark-theme'));

} catch (err) {
  recordResult('test error', false, err);
}

// GENERATE HTML REPORT
const htmlReport = `
<html>
<head>
  <title>Settings Popup Test Results</title>
  <style>
    body { font-family: sans-serif; padding: 2rem; }
    .passed { color: green; }
    .failed { color: red; }
    li { margin-bottom: 0.5rem; }
  </style>
</head>
<body>
  <h1>Settings Popup Test Results</h1>
  <ul>
    ${results.map(r => `
      <li class="${r.passed ? 'passed' : 'failed'}">
        ${r.name}: ${r.passed ? 'PASS' : 'FAIL'}
        ${r.error ? `<pre>${r.error.stack}</pre>` : ''}
      </li>
    `).join('')}
  </ul>
</body>
</html>
`;

fs.writeFileSync('ui-interactions-test-results.html', htmlReport);
console.log('HTML test report generated: ui-interactions-test-results.html');
