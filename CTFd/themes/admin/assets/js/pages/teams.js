import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezAlert, ezQuery } from "core/ezq";
import { t } from "core/i18n";

function deleteSelectedTeams(_event) {
  let teamIDs = $("input[data-team-id]:checked").map(function() {
    return $(this).data("team-id");
  });
  let target = teamIDs.length === 1 ? t("team") : t("teams");

  ezQuery({
    title: t("Delete Teams"),
    body: t("Are you sure you want to delete {0} {1}?", teamIDs.length, target),
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
    title: t("Edit Teams"),
    body: $(`
    <form id="teams-bulk-edit">
      <div class="form-group">
        <label>${t("Banned")}</label>
        <select name="banned" data-initial="">
          <option value="">--</option>
          <option value="true">${t("True")}</option>
          <option value="false">${t("False")}</option>
        </select>
      </div>
      <div class="form-group">
        <label>${t("Hidden")}</label>
        <select name="hidden" data-initial="">
          <option value="">--</option>
          <option value="true">${t("True")}</option>
          <option value="false">${t("False")}</option>
        </select>
      </div>
    </form>
    `),
    button: t("Submit"),
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
