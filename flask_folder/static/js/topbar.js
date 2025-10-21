// Show profile only after the user clicks Login in THIS TAB.
// sessionStorage is tab-scoped, so closing the tab clears this flag.

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