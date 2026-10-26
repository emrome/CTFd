import CTFd from "@ctfdio/ctfd-js";

import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";
import "dayjs/locale/es";

import { Dropdown } from "bootstrap";

import times from "./theme/times";
import styles from "./theme/styles";
import highlight from "./theme/highlight";

import alerts from "./utils/alerts";
import tooltips from "./utils/tooltips";
import collapse from "./utils/collapse";

import eventAlerts from "./utils/notifications/alerts";
import eventToasts from "./utils/notifications/toasts";
import eventRead from "./utils/notifications/read";
import { t, locale } from "./utils/i18n";

dayjs.extend(advancedFormat);
dayjs.locale(locale() === "es" ? "es" : "en");
CTFd.init(window.init);

// Translatable texts for the dialogs that come with ctfd-js
CTFd._functions.challenge.displayHint = hint => {
  window.alert(hint.content);
};

CTFd._functions.challenge.displayUnlock = () => {
  return window.confirm(t("Do you want to see this hint? It will cost you points."));
};

CTFd._functions.challenge.displayUnlockError = unlock => {
  const mensajes = Object.keys(unlock.errors || {}).map(k => unlock.errors[k]);
  window.alert(mensajes.join("\n") || t("The hint could not be opened. Try again."));
};

// Show / Hide buttons for password fields
function passwordToggles() {
  document.querySelectorAll("[data-mostrar-clave]").forEach($btn => {
    const $input = document.getElementById($btn.dataset.mostrarClave);
    if (!$input) {
      return;
    }
    $btn.setAttribute("aria-controls", $input.id);
    $btn.addEventListener("click", () => {
      const visible = $input.type === "password";
      $input.type = visible ? "text" : "password";
      $btn.textContent = visible ? t("Hide") : t("Show");
      $btn.setAttribute("aria-pressed", visible ? "true" : "false");
    });
  });
}

function dropdowns() {
  document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach($el => {
    Dropdown.getOrCreateInstance($el);
  });
}

(() => {
  styles();
  times();
  highlight();

  alerts();
  tooltips();
  collapse();
  dropdowns();
  passwordToggles();

  eventRead();
  eventAlerts();
  eventToasts();
})();

export default CTFd;
