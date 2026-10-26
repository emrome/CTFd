import "./main";
import $ from "jquery";
import { ezQuery } from "core/ezq";
import { t } from "core/i18n";

function reset(event) {
  event.preventDefault();
  ezQuery({
    title: t("Reset CTF?"),
    body: t("Are you sure you want to reset your CTFd instance?"),
    success: function() {
      $("#reset-ctf-form")
        .off("submit")
        .submit();
    }
  });
}

$(() => {
  $("#reset-ctf-form").submit(reset);
});
