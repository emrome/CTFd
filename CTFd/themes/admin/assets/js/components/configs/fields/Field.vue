<template>
  <div class="border-bottom">
    <div>
      <button
        type="button"
        class="close float-right"
        aria-label="Cerrar"
        @click="deleteField()"
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </div>

    <div class="row">
      <div class="col-md-3">
        <div class="form-group">
          <label>Tipo de campo</label>
          <select
            class="form-control custom-select"
            v-model.lazy="field.field_type"
          >
            <option value="text">Campo de texto</option>
            <option value="boolean">Casilla de verificación</option>
          </select>
          <small class="form-text text-muted"
            >Tipo de campo que ve el usuario</small
          >
        </div>
      </div>
      <div class="col-md-9">
        <div class="form-group">
          <label>Nombre del campo</label>
          <input type="text" class="form-control" v-model.lazy="field.name" />
          <small class="form-text text-muted">Nombre del campo</small>
        </div>
      </div>

      <div class="col-md-12">
        <div class="form-group">
          <label>Descripción del campo</label>
          <input
            type="text"
            class="form-control"
            v-model.lazy="field.description"
          />
          <small id="emailHelp" class="form-text text-muted"
            >Descripción del campo</small
          >
        </div>
      </div>

      <div class="col-md-12">
        <div class="form-check">
          <label class="form-check-label">
            <input
              class="form-check-input"
              type="checkbox"
              v-model.lazy="field.editable"
            />
            El usuario lo puede editar en su perfil
          </label>
        </div>
        <div class="form-check">
          <label class="form-check-label">
            <input
              class="form-check-input"
              type="checkbox"
              v-model.lazy="field.required"
            />
            Obligatorio en el registro
          </label>
        </div>
        <div class="form-check">
          <label class="form-check-label">
            <input
              class="form-check-input"
              type="checkbox"
              v-model.lazy="field.public"
            />
            Se muestra en el perfil público
          </label>
        </div>
      </div>
    </div>

    <div class="row pb-3">
      <div class="col-md-12">
        <div class="d-block">
          <button
            class="btn btn-sm btn-success btn-outlined float-right"
            type="button"
            @click="saveField()"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "core/CTFd";
import { ezToast } from "core/ezq";

export default {
  props: {
    index: Number,
    initialField: Object
  },
  data: function() {
    return {
      field: this.initialField
    };
  },
  methods: {
    persistedField: function() {
      // We're using Math.random() for unique IDs so new items have IDs < 1
      // Real items will have an ID > 1
      return this.field.id >= 1;
    },
    saveField: function() {
      let body = this.field;
      if (this.persistedField()) {
        CTFd.fetch(`/api/v1/configs/fields/${this.field.id}`, {
          method: "PATCH",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify(body)
        })
          .then(response => {
            return response.json();
          })
          .then(response => {
            if (response.success === true) {
              this.field = response.data;
              ezToast({
                title: "Listo",
                body: "¡Se actualizó el campo!",
                delay: 1000
              });
            }
          });
      } else {
        CTFd.fetch(`/api/v1/configs/fields`, {
          method: "POST",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify(body)
        })
          .then(response => {
            return response.json();
          })
          .then(response => {
            if (response.success === true) {
              this.field = response.data;
              ezToast({
                title: "Listo",
                body: "¡Se creó el campo!",
                delay: 1000
              });
            }
          });
      }
    },
    deleteField: function() {
      if (confirm("¿Seguro que querés borrar este campo?")) {
        if (this.persistedField()) {
          CTFd.fetch(`/api/v1/configs/fields/${this.field.id}`, {
            method: "DELETE",
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
              if (response.success === true) {
                this.$emit("remove-field", this.index);
              }
            });
        } else {
          this.$emit("remove-field", this.index);
        }
      }
    }
  }
};
</script>

<style scoped></style>
