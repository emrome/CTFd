import Alpine from "alpinejs";
import CTFd from "./index";
import { getOption } from "./utils/graphs/echarts/scoreboard";
import { embed } from "./utils/graphs/echarts";

window.Alpine = Alpine;
window.CTFd = CTFd;

// La tabla se guarda en caché para todos, así que la fila propia y la cantidad
// de desafíos resueltos se completan acá, en el navegador.
function marcarFilaPropia() {
  const propia = CTFd.config.userMode === "teams" ? CTFd.team.id : CTFd.user.id;
  if (!propia) {
    return;
  }
  const $fila = document.querySelector(`#scoreboard tr[data-cuenta="${propia}"]`);
  if ($fila) {
    $fila.classList.add("propio");
    $fila.setAttribute("aria-current", "true");
    const $marca = $fila.querySelector("[data-propio]");
    if ($marca) {
      $marca.classList.remove("d-none");
    }
  }
}

function completarResueltos(detalle) {
  Object.values(detalle || {}).forEach(cuenta => {
    const $celda = document.querySelector(
      `#scoreboard tr[data-cuenta="${cuenta.id}"] [data-resueltos]`
    );
    if ($celda) {
      const resueltos = (cuenta.solves || []).filter(s => s.challenge_id !== null);
      $celda.textContent = resueltos.length;
    }
  });
}

Alpine.data("Ranking", () => ({
  init() {
    marcarFilaPropia();
  },
}));

Alpine.data("ScoreboardDetail", () => ({
  data: null,

  async init() {
    const filas = document.querySelectorAll("#scoreboard tbody tr").length;
    const detalle = await CTFd.pages.scoreboard.getScoreboardDetail(
      Math.max(filas, 10)
    );
    completarResueltos(detalle);

    // El gráfico muestra solo los 10 primeros
    const top = {};
    Object.keys(detalle)
      .slice(0, 10)
      .forEach(k => {
        top[k] = detalle[k];
      });
    this.data = top;

    let option = getOption(CTFd.config.userMode, this.data);
    embed(this.$refs.scoregraph, option);
  },
}));

Alpine.start();
