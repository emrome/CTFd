import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezAlert, ezQuery } from "core/ezq";

function deleteSelectedTeams(_event) {
  let teamIDs = $("input[data-team-id]:checked").map(function() {
    return $(this).data("team-id");
  });
  let target = teamIDs.length === 1 ? "equipo" : "equipos";

  ezQuery({
    title: "Borrar equipos",
    body: `¿Seguro que querés borrar ${teamIDs.length} ${target}?`,
    success: function() {
      const reqs = [];
      for (var teamID of teamIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/teams/${teamID}`, {
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

function bulkEditTeams(_event) {
  let teamIDs = $("input[data-team-id]:checked").map(function() {
    return $(this).data("team-id");
  });

  ezAlert({
    title: "Editar equipos",
    body: $(`
    <form id="teams-bulk-edit">
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
      let data = $("#teams-bulk-edit").serializeJSON(true);
      const reqs = [];
      for (var teamID of teamIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/teams/${teamID}`, {
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
  $("#teams-delete-button").click(deleteSelectedTeams);
  $("#teams-edit-button").click(bulkEditTeams);
});
