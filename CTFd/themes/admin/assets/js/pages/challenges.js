import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezAlert, ezQuery } from "core/ezq";
import { t } from "core/i18n";

function deleteSelectedChallenges(_event) {
  let challengeIDs = $("input[data-challenge-id]:checked").map(function() {
    return $(this).data("challenge-id");
  });
  let target = challengeIDs.length === 1 ? t("challenge") : t("challenges");

  ezQuery({
    title: t("Delete Challenges"),
    body: t(
      "Are you sure you want to delete {0} {1}?",
      challengeIDs.length,
      target
    ),
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
    title: t("Edit Challenges"),
    body: $(`
    <form id="challenges-bulk-edit">
      <div class="form-group">
        <label>${t("Category")}</label>
        <input type="text" name="category" data-initial="" value="">
      </div>
      <div class="form-group">
        <label>${t("Value")}</label>
        <input type="number" name="value" data-initial="" value="">
      </div>
      <div class="form-group">
        <label>${t("State")}</label>
        <select name="state" data-initial="">
          <option value="">--</option>
          <option value="visible">${t("Visible")}</option>
          <option value="hidden">${t("Hidden")}</option>
        </select>
      </div>
    </form>
    `),
    button: t("Submit"),
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
