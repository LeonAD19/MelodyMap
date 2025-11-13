// Show profile only after the user clicks Login in THIS TAB.
// sessionStorage is tab-scoped, so closing the tab clears this flag.


// Topbar — Settings Popup

  (function () {
    const btn = document.getElementById('settings-btn');
    const popup = document.getElementById('settings-popup');
    const toggleTheme = document.getElementById('toggle-theme');
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
    toggleTheme.addEventListener('click', () => {
      document.body.classList.toggle('dark-mode');
      popup.classList.remove('show');
    });

    resetBtn.addEventListener('click', () => {
      localStorage.clear();
      alert('Settings reset!');
      popup.classList.remove('show');
      window.location.reload(true);
    });
  })();

// Load topbar profile info
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

  // Apply saved settings
  const savedAvatar = localStorage.getItem('selectedAvatar');
  const savedAvatarUrl = localStorage.getItem('selectedAvatarUrl');
  const savedCard = localStorage.getItem('selectedPlayerCard');
  const savedName = localStorage.getItem('spotifyUsername');

  // Show saved avatar immediately
  if (savedAvatarUrl) {
    pic.src = savedAvatarUrl;
    pic.style.opacity = '1';
  }

  // Show saved username immediately
  if (savedName && name) {
    name.textContent = savedName;
  }

  // Apply saved player card immediately
  if (savedCard && userWrap) {
    userWrap.classList.add(savedCard);
  }

  // Show profile immediately if we have cached data
  if ((savedAvatarUrl || savedName) && userWrap) {
    userWrap.style.display = 'flex';
  }

  // Validate & update in background
  // Fetch profile data in real time & updates cached data
  (async () => {
    try {
      const res = await fetch('/spotify/profile?_' + Date.now(), {
        method: 'GET',
        credentials: 'same-origin',
        cache: 'no-store'
      });

      const data = await res.json();
      if (res.ok && data && data.username) {
        // Cache username for next load
        localStorage.setItem('spotifyUsername', data.username);
        
        // Only update if different from cached
        if (name && name.textContent !== data.username) {
          name.textContent = data.username;
        }

        // Only fetch avatar list if user has custom avatar selected
        if (!localStorage.getItem('selectedAvatar') && data.profile_pic) {
          pic.src = data.profile_pic;
          pic.style.opacity = '1';
}
        
        if (userWrap) userWrap.style.display = 'flex';
      } else {
        if (userWrap) userWrap.style.display = 'none';
      }
    } catch (err) {
      // Keep showing cached data even on error
      if ((savedAvatar || savedName) && userWrap) {
        userWrap.style.display = 'flex';
      } else {
        if (userWrap) userWrap.style.display = 'none';
      }
    }
  })();
})();

// Avatar + Player Card Buttons (Handles opening modals)
(function initCustomizationButtons() {
  const avatarBtn = document.getElementById('pref-avatar');
  const cardBtn = document.getElementById('pref-card');
  
  // Avatar button click
  if (avatarBtn) {
    avatarBtn.addEventListener('click', () => {
      openAvatarModal();
      document.getElementById('settings-popup')?.classList.remove('show');
    });
  }

  // Player card button click
  if (cardBtn) {
    cardBtn.addEventListener('click', () => {
      openCardModal();
      document.getElementById('settings-popup')?.classList.remove('show');
    });
  }
})();

// Avatar modal (Lets user choose new avatar)
let cachedAvatars = null;
async function openAvatarModal() {
  const modal = document.getElementById('avatar-modal');
  const grid = document.getElementById('avatar-grid');
  
  if (!modal || !grid) return;

  try {
    // Check localStorage cache first
    let avatars = null;
    const cachedAvatarsJson = localStorage.getItem('cachedAvatars');
    const cacheTime = localStorage.getItem('cachedAvatarsTime');
    const now = Date.now();
    
    // Use cache if less than 1 hour old
    if (cachedAvatarsJson && cacheTime && (now - parseInt(cacheTime)) < 3600000) {
      avatars = JSON.parse(cachedAvatarsJson);
    } else {
      // Fetch fresh data
      const res = await fetch('/spotify/avatars');
      avatars = await res.json();
      
      // Cache for next time
      localStorage.setItem('cachedAvatars', JSON.stringify(avatars));
      localStorage.setItem('cachedAvatarsTime', now.toString());
    }
    
    const currentAvatar = localStorage.getItem('selectedAvatar');

    // Render avatar options
    grid.innerHTML = '';
    avatars.forEach(avatar => {
      const wrapper = document.createElement('div');
      wrapper.className = 'avatar-option-wrapper';
      
      const img = document.createElement('img');
      img.src = avatar.url;
      img.className = 'avatar-option' + (currentAvatar === avatar.id ? ' selected' : '');
      
      const label = document.createElement('span');
      label.className = 'avatar-label';
      label.textContent = avatar.name;

      // Save both ID and URL for instant load next time      
      img.onclick = () => {
        localStorage.setItem('selectedAvatar', avatar.id);
        localStorage.setItem('selectedAvatarUrl', avatar.url);
        document.getElementById('header-pic').src = avatar.url;
        modal.classList.add('hidden');
      };
      
      wrapper.appendChild(img);
      wrapper.appendChild(label);
      grid.appendChild(wrapper);
    });

    modal.classList.remove('hidden');
    
  } catch (err) {
    alert('Failed to load avatars');
  }
}

// PLayer Card Modal (Lets user choose new player card)
let cachedCards = null;
async function openCardModal() {
  const modal = document.getElementById('card-modal');
  const grid = document.getElementById('card-grid');
  
  if (!modal || !grid) return;

  try {
    // Fetch only if not cached
    if (!cachedCards) {
      const res = await fetch('/spotify/player_cards');
      cachedCards = await res.json();
    }
    
    const cards = cachedCards;
    const currentCard = localStorage.getItem('selectedPlayerCard');

    const descriptions = {
      'card-simple': 'Purple gradient with glow',
      'card-compact': 'Dark theme with orange accent',
      'card-spotify': 'Official Spotify green style',
      'card-neon': 'Blue neon glow',
      'card-glass': 'Glassmorphism transparency'
    };

    grid.innerHTML = '';
    // Render card options
    cards.forEach(card => {
      const div = document.createElement('div');
      div.className = 'card-option' + (currentCard === card.id ? ' selected' : '');
      div.innerHTML = `
        <div class="card-option-title">${card.name}</div>
        <div class="card-option-desc">${descriptions[card.id] || ''}</div>
      `;
      
      // On click, save selected card
      div.onclick = () => {
        localStorage.setItem('selectedPlayerCard', card.id);
        
        // Apply to topbar.js profile
        const headerUser = document.getElementById('header-user');
        if (headerUser) {
          // Remove old card classes
          headerUser.className = headerUser.className
            .split(' ')
            .filter(c => !c.startsWith('card-'))
            .join(' ');
          
          // Add new card class
          headerUser.classList.add(card.id);
        }
        
        modal.classList.add('hidden');
      };
      
      grid.appendChild(div);
    });

    modal.classList.remove('hidden');
    
  } catch (err) {
    alert('Failed to load player cards');
  }
}

// Modal close handlers
document.addEventListener('DOMContentLoaded', () => {
  // Avatar modal
  document.getElementById('avatar-close')?.addEventListener('click', () => {
    document.getElementById('avatar-modal')?.classList.add('hidden');
  });
  
  document.getElementById('avatar-modal')?.querySelector('.modal-overlay')?.addEventListener('click', () => {
    document.getElementById('avatar-modal')?.classList.add('hidden');
  });
  
  // Card modal
  document.getElementById('card-close')?.addEventListener('click', () => {
    document.getElementById('card-modal')?.classList.add('hidden');
  });
  
  document.getElementById('card-modal')?.querySelector('.modal-overlay')?.addEventListener('click', () => {
    document.getElementById('card-modal')?.classList.add('hidden');
  });
});