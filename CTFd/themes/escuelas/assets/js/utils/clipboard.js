import { Tooltip } from "bootstrap";
import { t } from "./i18n";

export function copyToClipboard($input) {
  const tooltip = new Tooltip($input, {
    title: t("Copied!"),
    trigger: "manual",
  });

  navigator.clipboard.writeText($input.value).then(() => {
    tooltip.show();
    setTimeout(() => {
      tooltip.hide();
    }, 1500);
  });
}
