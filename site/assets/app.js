(() => {
  const menuButton = document.querySelector('.menu-button');
  const navigation = document.querySelector('.site-nav');

  if (menuButton && navigation) {
    menuButton.addEventListener('click', () => {
      const expanded = menuButton.getAttribute('aria-expanded') === 'true';
      menuButton.setAttribute('aria-expanded', String(!expanded));
      navigation.classList.toggle('open', !expanded);
    });
  }

  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const evidenceCards = [...document.querySelectorAll('.evidence-card[data-status]')];

  if (filterButtons.length && evidenceCards.length) {
    filterButtons.forEach((button) => {
      button.addEventListener('click', () => {
        const filter = button.dataset.filter;
        filterButtons.forEach((item) => item.classList.toggle('active', item === button));
        evidenceCards.forEach((card) => {
          const statuses = card.dataset.status.split(/\s+/);
          card.classList.toggle('is-hidden', filter !== 'all' && !statuses.includes(filter));
        });
      });
    });
  }
})();
