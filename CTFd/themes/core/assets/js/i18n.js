// Translations for strings rendered by JavaScript.
//
// The page template defines `window.CTFdTranslations` with
// `{{ get_js_translations()|tojson }}` (see CTFd/utils/i18n/__init__.py).
// `t("English text")` returns the translation for the current locale, or the
// English text itself when there is none. Positional placeholders `{0}`, `{1}`
// are replaced by the extra arguments.
export function t(msgid, ...args) {
  const translations = window.CTFdTranslations || {};
  let text = translations[msgid] || msgid;
  args.forEach((value, i) => {
    text = text.split(`{${i}}`).join(value);
  });
  return text;
}

export default t;
