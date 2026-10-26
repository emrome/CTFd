import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";
import "dayjs/locale/es";
import { t, locale } from "../utils/i18n";

dayjs.extend(advancedFormat);
dayjs.locale(locale() === "es" ? "es" : "en");

// dayjs format; translators can reorder it (e.g. "D [de] MMMM, HH:mm")
export const FORMATO_FECHA = t("MMMM D, HH:mm");

export default () => {
  document.querySelectorAll("[data-time]").forEach($el => {
    const time = $el.getAttribute("data-time");
    const format = $el.getAttribute("data-time-format") || FORMATO_FECHA;
    $el.innerText = dayjs(time).format(format);
  });
};
