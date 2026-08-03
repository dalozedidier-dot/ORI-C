(() => {
  const menuButton = document.querySelector('.menu-button');
  const navigation = document.querySelector('.site-nav');

  const closeMenu = () => {
    if (!menuButton || !navigation) return;
    menuButton.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('open');
  };

  if (menuButton && navigation) {
    menuButton.addEventListener('click', () => {
      const expanded = menuButton.getAttribute('aria-expanded') === 'true';
      menuButton.setAttribute('aria-expanded', String(!expanded));
      navigation.classList.toggle('open', !expanded);
    });

    navigation.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeMenu();
        menuButton.focus();
      }
    });
    document.addEventListener('click', (event) => {
      if (!navigation.contains(event.target) && !menuButton.contains(event.target)) closeMenu();
    });
  }

  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const evidenceCards = [...document.querySelectorAll('.evidence-card[data-status]')];
  const filterSummary = document.querySelector('#filter-summary');

  const updateFilter = (filter, activeButton) => {
    filterButtons.forEach((button) => {
      const active = button === activeButton;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });

    let visible = 0;
    evidenceCards.forEach((card) => {
      const statuses = card.dataset.status.split(/\s+/);
      const show = filter === 'all' || statuses.includes(filter);
      card.classList.toggle('is-hidden', !show);
      if (show) visible += 1;
    });

    if (filterSummary) {
      filterSummary.textContent = `${visible} résultat${visible > 1 ? 's' : ''} affiché${visible > 1 ? 's' : ''}.`;
    }
  };

  if (filterButtons.length && evidenceCards.length) {
    filterButtons.forEach((button) => {
      button.addEventListener('click', () => updateFilter(button.dataset.filter, button));
    });
    updateFilter('all', filterButtons.find((button) => button.dataset.filter === 'all') || filterButtons[0]);
  }

  const commitNodes = [...document.querySelectorAll('[data-build-commit]')];
  const dateNodes = [...document.querySelectorAll('[data-build-date]')];
  const linkNodes = [...document.querySelectorAll('[data-build-link]')];

  if (commitNodes.length || dateNodes.length) {
    fetch('build.json', { cache: 'no-store' })
      .then((response) => {
        if (!response.ok) throw new Error('Métadonnées de build indisponibles');
        return response.json();
      })
      .then((build) => {
        commitNodes.forEach((node) => { node.textContent = build.short || build.commit || 'inconnu'; });
        dateNodes.forEach((node) => {
          node.textContent = build.built_at_display || build.built_at || 'date inconnue';
          if (build.built_at) node.setAttribute('datetime', build.built_at);
        });
        if (build.commit) {
          linkNodes.forEach((node) => { node.href = `https://github.com/dalozedidier-dot/ORI-C/commit/${build.commit}`; });
        }
      })
      .catch(() => {
        commitNodes.forEach((node) => { node.textContent = 'métadonnées indisponibles'; });
        dateNodes.forEach((node) => { node.textContent = 'voir GitHub Actions'; });
      });
  }
})();
