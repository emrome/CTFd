import "./main";
import $ from "jquery";
import { ezQuery } from "core/ezq";

function reset(event) {
  event.preventDefault();
  ezQuery({
    title: "¿Reiniciar el CTF?",
    body: "¿Seguro que querés reiniciar tu instancia de CTFd?",
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
