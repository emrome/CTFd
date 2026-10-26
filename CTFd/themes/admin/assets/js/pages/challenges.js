import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezAlert, ezQuery } from "core/ezq";

function deleteSelectedChallenges(_event) {
  let challengeIDs = $("input[data-challenge-id]:checked").map(function() {
    return $(this).data("challenge-id");
  });
  let target = challengeIDs.length === 1 ? "desafío" : "desafíos";

  ezQuery({
    title: "Borrar desafíos",
    body: `¿Seguro que querés borrar ${challengeIDs.length} ${target}?`,
    success: function() {
      const reqs = [];
      for (var chalID of challengeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/challenges/${chalID}`, {
            method: "DELETE"
          })
        );
      }
      Promise.all(reqs).then(_responses => {
        window.location.reload();
      });
    }
  });
}

function bulkEditChallenges(_event) {
  let challengeIDs = $("input[data-challenge-id]:checked").map(function() {
    return $(this).data("challenge-id");
  });

  ezAlert({
    title: "Editar desafíos",
    body: $(`
    <form id="challenges-bulk-edit">
      <div class="form-group">
        <label>Categoría</label>
        <input type="text" name="category" data-initial="" value="">
      </div>
      <div class="form-group">
        <label>Puntaje</label>
        <input type="number" name="value" data-initial="" value="">
      </div>
      <div class="form-group">
        <label>Estado</label>
        <select name="state" data-initial="">
          <option value="">--</option>
          <option value="visible">Visible</option>
          <option value="hidden">Oculto</option>
        </select>
      </div>
    </form>
    `),
    button: "Enviar",
    success: function() {
      let data = $("#challenges-bulk-edit").serializeJSON(true);
      const reqs = [];
      for (var chalID of challengeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/challenges/${chalID}`, {
            method: "PATCH",
            body: JSON.stringify(data)
          })
        );
      }
      Promise.all(reqs).then(_responses => {
        window.location.reload();
      });
    }
  });
}

$(() => {
  $("#challenges-delete-button").click(deleteSelectedChallenges);
  $("#challenges-edit-button").click(bulkEditChallenges);
});
