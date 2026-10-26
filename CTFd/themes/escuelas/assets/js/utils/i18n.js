// Theme strings stay in English and are looked up in window.CTFdTranslations,
// which the server fills with the msgstr of the current locale
// (see templates/components/js_translations.html).
export function t(msgid, params = {}) {
  const table = window.CTFdTranslations || {};
  const text = typeof table[msgid] === "string" && table[msgid] ? table[msgid] : msgid;
  return text.replace(/\{(\w+)\}/g, (match, key) =>
    Object.prototype.hasOwnProperty.call(params, key) ? String(params[key]) : match
  );
}

export function locale() {
  return (document.documentElement.lang || "en").slice(0, 2).toLowerCase();
}
