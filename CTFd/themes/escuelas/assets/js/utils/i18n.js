// Same helper as CTFd/themes/core/assets/js/i18n.js: the page defines
// window.CTFdTranslations with get_js_translations() (see templates/base.html and
// CTFd/utils/i18n/__init__.py). t("English text") returns the translation for the
// current locale, or the English text; {0}, {1}... are replaced by the extra arguments.
export function t(msgid, ...args) {
  const translations = window.CTFdTranslations || {};
  let text = translations[msgid] || msgid;
  args.forEach((value, i) => {
    text = text.split(`{${i}}`).join(value);
  });
  return text;
}

export function locale() {
  return (document.documentElement.lang || "en").slice(0, 2).toLowerCase();
}

export default t;
