(function () {
  const STORAGE_KEY = 'faxcloud_theme';
  const CLASS_DARK = 'theme-dark';

  function getPreferredTheme() {
    const saved = (localStorage.getItem(STORAGE_KEY) || '').toLowerCase();
    if (saved === 'dark' || saved === 'light') return saved;

    try {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
    } catch (_) {}
    return 'light';
  }

  function applyTheme(theme) {
    const isDark = theme === 'dark';
    document.documentElement.classList.toggle(CLASS_DARK, isDark);

    const btn = document.getElementById('themeToggle');
    if (btn) {
      btn.textContent = isDark ? 'Mode clair' : 'Mode sombre';
      btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
    }
  }

  function setTheme(theme) {
    localStorage.setItem(STORAGE_KEY, theme);
    applyTheme(theme);
  }

  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(getPreferredTheme());

    const btn = document.getElementById('themeToggle');
    if (!btn) return;

    btn.addEventListener('click', () => {
      const isDark = document.documentElement.classList.contains(CLASS_DARK);
      setTheme(isDark ? 'light' : 'dark');
    });
  });
})();
