<template>
  <div>
    <div>
      <HintCreationForm
        ref="HintCreationForm"
        :challenge_id="challenge_id"
        :hints="hints"
        @refreshHints="refreshHints"
      />
    </div>

    <div>
      <HintEditForm
        ref="HintEditForm"
        :challenge_id="challenge_id"
        :hint_id="editing_hint_id"
        :hints="hints"
        @refreshHints="refreshHints"
      />
    </div>

    <table class="table table-striped">
      <thead>
        <tr>
          <td class="text-center"><b>ID</b></td>
          <td class="text-center"><b>Pista</b></td>
          <td class="text-center"><b>Costo</b></td>
          <td class="text-center"><b>Ajustes</b></td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="hint in hints" :key="hint.id">
          <td class="text-center">{{ hint.type }}</td>
          <td class="text-break">
            <pre>{{ hint.content }}</pre>
          </td>
          <td class="text-center">{{ hint.cost }}</td>
          <td class="text-center">
            <i
              role="button"
              class="btn-fa fas fa-edit"
              @click="editHint(hint.id)"
            ></i>
            <i
              role="button"
              class="btn-fa fas fa-times"
              @click="deleteHint(hint.id)"
            ></i>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="col-md-12">
      <button class="btn btn-success float-right" @click="addHint">
        Crear pista
      </button>
    </div>
  </div>
</template>

<script>
import { ezQuery } from "core/ezq";
import CTFd from "core/CTFd";
import HintCreationForm from "./HintCreationForm.vue";
import HintEditForm from "./HintEditForm.vue";

export default {
  components: {
    HintCreationForm,
    HintEditForm
  },
  props: {
    challenge_id: Number
  },
  data: function() {
    return {
      hints: [],
      editing_hint_id: null
    };
  },
  methods: {
    loadHints: function() {
      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}/hints`, {
        method: "GET",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        }
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.hints = response.data;
          }
        });
    },
    addHint: function() {
      let modal = this.$refs.HintCreationForm.$el;
      $(modal).modal();
    },
    editHint: function(hintId) {
      this.editing_hint_id = hintId;
      let modal = this.$refs.HintEditForm.$el;
      $(modal).modal();
    },
    refreshHints: function(caller) {
      this.loadHints();
      let modal;
      switch (caller) {
        case "HintCreationForm":
          modal = this.$refs.HintCreationForm.$el;
          console.log(modal);
          $(modal).modal("hide");
          break;
        case "HintEditForm":
          modal = this.$refs.HintEditForm.$el;
          $(modal).modal("hide");
          break;
        default:
          break;
      }
    },
    deleteHint: function(hintId) {
      ezQuery({
        title: "Borrar pista",
        body: "¿Seguro que querés borrar esta pista?",
        success: () => {
          CTFd.fetch(`/api/v1/hints/${hintId}`, {
            method: "DELETE"
          })
            .then(response => {
              return response.json();
            })
            .then(data => {
              if (data.success) {
                this.loadHints();
              }
            });
        }
      });
    }
  },
  created() {
    this.loadHints();
  }
};
</script>

<style scoped></style>
