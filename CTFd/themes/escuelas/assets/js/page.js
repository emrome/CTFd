import Alpine from "alpinejs";
import CTFd from "./index";
import { grupoCategoria, nivelDesdeEtiquetas } from "./theme/categorias";
import { t } from "./utils/i18n";

window.CTFd = CTFd;
window.Alpine = Alpine;

// Numbers on the home page, computed from the challenges this visitor can see.
// When the challenges are not visible (e.g. not logged in) the numbers stay hidden.
Alpine.store("inicio", {
  loaded: false,
  total: 0,
  categories: 0,
  levels: 0,
  byGroup: {},

  count(group) {
    return this.byGroup[group] || 0;
  },

  challengesText(group) {
    const n = this.count(group);
    return n === 1 ? t("1 challenge") : t("{0} challenges", n);
  },
});

async function loadNumbers() {
  if (!document.querySelector("[data-inicio-numeros]")) {
    return;
  }
  try {
    // Teachers without a team get a 403 here, so they don't see the numbers
    const response = await CTFd.fetch("/api/v1/challenges", { method: "GET" });
    if (!response.ok) {
      return;
    }
    const body = await response.json();
    const challenges = (body.data || []).filter(c => c.type !== "hidden");
    const store = Alpine.store("inicio");
    const byGroup = {};
    const levels = new Set();
    challenges.forEach(c => {
      const group = grupoCategoria(c.category);
      byGroup[group] = (byGroup[group] || 0) + 1;
      const level = nivelDesdeEtiquetas(c.tags);
      if (level) {
        levels.add(level);
      }
    });
    store.byGroup = byGroup;
    store.total = challenges.length;
    store.categories = new Set(challenges.map(c => c.category)).size;
    store.levels = levels.size;
    store.loaded = challenges.length > 0;
  } catch (error) {
    // Keep the numbers hidden
  }
}

Alpine.start();
loadNumbers();
