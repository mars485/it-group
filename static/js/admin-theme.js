(() => {
  const key = "theme";
  let current = "light";
  try {
    const saved = localStorage.getItem(key);
    if (saved === "dark" || saved === "light") current = saved;
  } catch (_) {}
  document.documentElement.dataset.theme = current;

  function updateControls() {
    document.querySelectorAll("[data-it-theme-choice]").forEach((button) => {
      const active = button.dataset.itThemeChoice === current;
      button.setAttribute("aria-pressed", String(active));
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    updateControls();
    document.querySelectorAll("[data-it-theme-choice]").forEach((button) => {
      button.addEventListener("click", () => {
        current = button.dataset.itThemeChoice;
        document.documentElement.dataset.theme = current;
        try { localStorage.setItem(key, current); } catch (_) {}
        updateControls();
      });
    });
  });
})();
