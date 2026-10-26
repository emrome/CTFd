import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezAlert, ezQuery } from "core/ezq";
import { t } from "core/i18n";

function deleteSelectedUsers(_event) {
  let userIDs = $("input[data-user-id]:checked").map(function() {
    return $(this).data("user-id");
  });
  let target = userIDs.length === 1 ? t("user") : t("users");

  ezQuery({
    title: t("Delete Users"),
    body: t("Are you sure you want to delete {0} {1}?", userIDs.length, target),
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
    title: t("Edit Users"),
    body: $(`
    <form id="users-bulk-edit">
      <div class="form-group">
        <label>${t("Verified")}</label>
        <select name="verified" data-initial="">
          <option value="">--</option>
          <option value="true">${t("True")}</option>
          <option value="false">${t("False")}</option>
        </select>
      </div>
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
