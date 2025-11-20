// Side panel that slides in from the right to show Spotify embeds
// Called from map.js when clicking on markers

class SidePanel {
  constructor() {
    this.panel = null;      // Main container
    this.overlay = null;    // Dark backdrop
    this.iframe = null;     // Spotify embed
    this.isOpen = false;

    this.createPanel();
    this.attachEventListeners();
  }

  createPanel() {
    // Create backdrop overlay (click to close)
    this.overlay = document.createElement('div');
    this.overlay.id = 'side-panel-overlay';
    this.overlay.addEventListener('click', () => this.close());
    document.body.appendChild(this.overlay);

    // Create panel with close button and iframe
    this.panel = document.createElement('div');
    this.panel.id = 'side-panel';
    this.panel.innerHTML = `
      <div id="side-panel-header">
        <button id="side-panel-close" aria-label="Close panel">&times;</button>
      </div>
      <div id="side-panel-content">
        <iframe id="side-panel-iframe" title="Spotify Player"></iframe>
      </div>
    `;
    document.body.appendChild(this.panel);

    this.iframe = document.getElementById('side-panel-iframe');
  }

  attachEventListeners() {
    // Close button
    const closeBtn = document.getElementById('side-panel-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.close());
    }

    // Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });
  }

  open(url) {
    if (!url) return;

    this.iframe.src = url;
    this.panel.classList.add('open');
    this.overlay.classList.add('show');
    this.isOpen = true;
  }

  close() {
    this.panel.classList.remove('open');
    this.overlay.classList.remove('show');
    this.isOpen = false;
  }
}

// Global function called from map.js
// Example: openSidePanel('https://open.spotify.com/embed/track/abc123')
window.openSidePanel = function(url) {
  if (!window.sidePanel) {
    window.sidePanel = new SidePanel();
  }
  window.sidePanel.open(url);
};
