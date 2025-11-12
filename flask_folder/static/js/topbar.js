// Show profile only after the user clicks Login in THIS TAB.
// sessionStorage is tab-scoped, so closing the tab clears this flag.


// Topbar — Settings Popup

  (function () {
    const btn = document.getElementById('settings-btn');
    const popup = document.getElementById('settings-popup');
    const darkBtn = document.getElementById('pref-dark');
    const resetBtn = document.getElementById('pref-reset');

    if (!btn || !popup) return;

    // Toggle popup
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      popup.classList.toggle('show');
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!popup.contains(e.target) && !btn.contains(e.target)) {
        popup.classList.remove('show');
      }
    });

    // Placeholder button functions
    darkBtn.addEventListener('click', () => {
      document.body.classList.toggle('dark-mode');
      popup.classList.remove('show');
    });

    resetBtn.addEventListener('click', () => {
      localStorage.clear();
      alert('Settings reset!');
      popup.classList.remove('show');
    });
  })();


(function () {
  const userWrap = document.getElementById('header-user');
  const pic = document.getElementById('header-pic');
  const name = document.getElementById('header-name');

  // If user hasn't clicked Login in this tab yet, don't fetch profile
  const allowProfile = sessionStorage.getItem('mm-auth-ok') === '1';
  if (!allowProfile) {
    if (userWrap) userWrap.style.display = 'none';
    // Attach a listener to set the flag when Login is clicked
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href="/login"], a[href*="/login"]');
      if (a) {
        try { sessionStorage.setItem('mm-auth-ok', '1'); } catch {}
      }
    });
    return;
  }

  // User clicked Login in this tab → fetch profile and show it
  (async () => {
    try {
      const res = await fetch('/spotify/profile?_' + Date.now(), {
        method: 'GET',
        credentials: 'same-origin',
        cache: 'no-store'
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data && data.username) {
        if (pic) pic.src = data.profile_pic || '/static/img/default-avatar.png';
        if (name) name.textContent = data.username || 'Spotify User';
        if (userWrap) userWrap.style.display = 'flex';
      } else {
        if (userWrap) userWrap.style.display = 'none';
      }
    } catch (err) {
      if (userWrap) userWrap.style.display = 'none';
    }
  })();
})();