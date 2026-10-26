import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezQuery } from "core/ezq";
import { t } from "core/i18n";

function deleteSelectedUsers(_event) {
  let pageIDs = $("input[data-page-id]:checked").map(function() {
    return $(this).data("page-id");
  });
  let target = pageIDs.length === 1 ? t("page") : t("pages");

  ezQuery({
    title: t("Delete Pages"),
    body: t("Are you sure you want to delete {0} {1}?", pageIDs.length, target),
    success: function() {
      const reqs = [];
      for (var pageID of pageIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/pages/${pageID}`, {
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

$(() => {
  $("#pages-delete-button").click(deleteSelectedUsers);
});
