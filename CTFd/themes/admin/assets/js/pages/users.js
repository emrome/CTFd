import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezAlert, ezQuery } from "core/ezq";

function deleteSelectedUsers(_event) {
  let userIDs = $("input[data-user-id]:checked").map(function() {
    return $(this).data("user-id");
  });
  let target = userIDs.length === 1 ? "usuario" : "usuarios";

  ezQuery({
    title: "Borrar usuarios",
    body: `¿Seguro que querés borrar ${userIDs.length} ${target}?`,
    success: function() {
      const reqs = [];
      for (var userID of userIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/users/${userID}`, {
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

function bulkEditUsers(_event) {
  let userIDs = $("input[data-user-id]:checked").map(function() {
    return $(this).data("user-id");
  });

  ezAlert({
    title: "Editar usuarios",
    body: $(`
    <form id="users-bulk-edit">
      <div class="form-group">
        <label>Verificado</label>
        <select name="verified" data-initial="">
          <option value="">--</option>
          <option value="true">Sí</option>
          <option value="false">No</option>
        </select>
      </div>
      <div class="form-group">
        <label>Suspendido</label>
        <select name="banned" data-initial="">
          <option value="">--</option>
          <option value="true">Sí</option>
          <option value="false">No</option>
        </select>
      </div>
      <div class="form-group">
        <label>Oculto</label>
        <select name="hidden" data-initial="">
          <option value="">--</option>
          <option value="true">Sí</option>
          <option value="false">No</option>
        </select>
      </div>
    </form>
    `),
    button: "Enviar",
    success: function() {
      let data = $("#users-bulk-edit").serializeJSON(true);
      const reqs = [];
      for (var userID of userIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/users/${userID}`, {
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
  $("#users-delete-button").click(deleteSelectedUsers);
  $("#users-edit-button").click(bulkEditUsers);
});
