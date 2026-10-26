<template>
  <div class="card bg-light mb-4">
    <button
      type="button"
      :data-notif-id="this.id"
      class="delete-notification close position-absolute p-3"
      style="right:0;"
      data-dismiss="alert"
      :aria-label="t('Close')"
      @click="deleteNotification()"
    >
      <span aria-hidden="true">&times;</span>
    </button>
    <div class="card-body">
      <h3 class="card-title">{{ title }}</h3>
      <blockquote class="blockquote mb-0">
        <p v-html="this.html"></p>
        <small class="text-muted">
          <span :data-time="this.date">{{ this.localDate() }}</span>
        </small>
      </blockquote>
    </div>
  </div>
</template>

<script>
import CTFd from "core/CTFd";
import dayjs from "dayjs";
import hljs from "highlight.js";
import { t } from "core/i18n";
export default {
  props: {
    id: Number,
    title: String,
    content: String,
    html: String,
    date: String
  },
  methods: {
    t,
    localDate: function() {
      return dayjs(this.date).format("MMMM Do, h:mm:ss A");
    },
    deleteNotification: function() {
      if (confirm(t("Are you sure you want to delete this notification?"))) {
        CTFd.api
          .delete_notification({ notificationId: this.id })
          .then(response => {
            if (response.success) {
              // Delete the current component
              // https://stackoverflow.com/a/55384005
              this.$destroy();
              this.$el.parentNode.removeChild(this.$el);
            }
          });
      }
    }
  },
  mounted() {
    this.$el.querySelectorAll("pre code").forEach(block => {
      hljs.highlightBlock(block);
    });
  }
};
</script>
