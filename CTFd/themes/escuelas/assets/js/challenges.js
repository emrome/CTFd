import Alpine from "alpinejs";
import dayjs from "dayjs";

import CTFd from "./index";

import { Modal, Tooltip } from "bootstrap";
import highlight from "./theme/highlight";
import { FORMATO_FECHA } from "./theme/times";
import {
  colorCategoria,
  siglaCategoria,
  nivelDesdeEtiquetas,
} from "./theme/categorias";
import { t } from "./utils/i18n";

function addTargetBlank(html) {
  let dom = new DOMParser();
  let view = dom.parseFromString(html, "text/html");
  let links = view.querySelectorAll('a[href*="://"]');
  links.forEach(link => {
    link.setAttribute("target", "_blank");
  });
  return view.documentElement.outerHTML;
}

window.Alpine = Alpine;

Alpine.store("challenge", {
  data: {
    view: "",
  },
});

Alpine.data("Hint", () => ({
  id: null,
  cost: 0,
  html: null,
  loading: false,

  async showHint() {
    this.loading = true;
    try {
      let response = await CTFd.pages.challenge.loadHint(this.id);
      let hint = response.data;
      if (!hint.content) {
        if (this.cost > 0) {
          const ok = window.confirm(
            this.cost === 1
              ? t("Do you want to see this hint? It will cost you 1 point.")
              : t(
                  "Do you want to see this hint? It will cost you {0} points.",
                  this.cost
                )
          );
          if (!ok) {
            return;
          }
        }
        let unlock = await CTFd.pages.challenge.loadUnlock(this.id);
        if (!unlock.success) {
          CTFd._functions.challenge.displayUnlockError(unlock);
          return;
        }
        response = await CTFd.pages.challenge.loadHint(this.id);
        hint = response.data;
      }
      this.html = addTargetBlank(hint.html);
      this.$nextTick(() => {
        if (this.$refs.texto) {
          this.$refs.texto.focus();
        }
      });
    } finally {
      this.loading = false;
    }
  },
}));

Alpine.data("Challenge", () => ({
  id: null,
  next_id: null,
  submission: "",
  tab: null,
  solves: [],
  response: null,
  share_url: null,
  submitting: false,
  solvesLoaded: false,
  maxAttempts: 0,
  attempts: 0,

  async init() {
    highlight();
  },

  t(msgid, ...args) {
    return t(msgid, ...args);
  },

  getStyles() {
    let styles = {
      "modal-dialog": true,
    };
    try {
      let size = CTFd.config.themeSettings.challenge_window_size;
      switch (size) {
        case "sm":
          styles["modal-sm"] = true;
          break;
        case "lg":
          styles["modal-lg"] = true;
          break;
        case "xl":
          styles["modal-xl"] = true;
          break;
        default:
          break;
      }
    } catch (error) {
      // Ignore errors with challenge window size
      console.log("Error processing challenge_window_size");
      console.log(error);
    }
    return styles;
  },

  async showSolves() {
    this.solves = await CTFd.pages.challenge.loadSolves(this.id);
    this.solves.forEach(solve => {
      solve.date = dayjs(solve.date).format(FORMATO_FECHA);
      return solve;
    });
    this.solvesLoaded = true;
  },

  incorrectMessage() {
    let texto = t("That is not the flag. Check the format and try again.");
    if (this.maxAttempts > 0) {
      const quedan = Math.max(this.maxAttempts - this.attempts, 0);
      texto +=
        " " +
        (quedan === 1
          ? t("You have 1 attempt left.")
          : t("You have {0} attempts left.", quedan));
    }
    return texto;
  },

  otherMessage() {
    const data = this.response.data || {};
    if (data.status === "ratelimited") {
      return t("You are going too fast. Wait a few seconds and try again.");
    }
    if (data.status === "paused") {
      return data.message || t("The competition is paused.");
    }
    if (data.status === "authentication_required") {
      return t("You must be logged in to submit an answer.");
    }
    return data.message || t("The answer could not be sent. Try again.");
  },

  getNextId() {
    let data = Alpine.store("challenge").data;
    return data.next_id;
  },

  async nextChallenge() {
    let modal = Modal.getOrCreateInstance("[x-ref='challengeWindow']");

    // TODO: Get rid of this private attribute access
    // See https://github.com/twbs/bootstrap/issues/31266
    modal._element.addEventListener(
      "hidden.bs.modal",
      event => {
        // Dispatch load-challenge event to call loadChallenge in the ChallengeBoard
        Alpine.nextTick(() => {
          this.$dispatch("load-challenge", this.getNextId());
        });
      },
      { once: true }
    );
    modal.hide();
  },

  async getShareUrl() {
    let body = {
      type: "solve",
      challenge_id: this.id,
    };
    const response = await CTFd.fetch("/api/v1/shares", {
      method: "POST",
      body: JSON.stringify(body),
    });
    const data = await response.json();
    const url = data["data"]["url"];
    this.share_url = url;
  },

  copyShareUrl() {
    navigator.clipboard.writeText(this.share_url);
    let t = Tooltip.getOrCreateInstance(this.$el);
    t.enable();
    t.show();
    setTimeout(() => {
      t.hide();
      t.disable();
    }, 2000);
  },

  async submitChallenge() {
    if (this.submitting) {
      return;
    }
    this.submitting = true;
    try {
      this.response = await CTFd.pages.challenge.submitChallenge(
        this.id,
        this.submission
      );
      if (this.response.data.status === "incorrect" && this.maxAttempts > 0) {
        this.attempts += 1;
      }
    } catch (error) {
      this.response = {
        data: {
          status: "error",
          message: t("Could not connect to the server. Try again."),
        },
      };
      return;
    } finally {
      this.submitting = false;
    }

    await this.renderSubmissionResponse();
  },

  async renderSubmissionResponse() {
    if (this.response.data.status === "correct") {
      this.submission = "";
    }

    // Dispatch load-challenges event to call loadChallenges in the ChallengeBoard
    this.$dispatch("load-challenges");
  },
}));

Alpine.data("ChallengeBoard", () => ({
  loaded: false,
  challenges: [],
  challenge: null,
  filter: null,
  place: null,

  async init() {
    this.challenges = await CTFd.pages.challenges.getChallenges();
    this.loaded = true;
    this.loadPlace();

    if (window.location.hash) {
      let chalHash = decodeURIComponent(window.location.hash.substring(1));
      let idx = chalHash.lastIndexOf("-");
      if (idx >= 0) {
        let pieces = [chalHash.slice(0, idx), chalHash.slice(idx + 1)];
        let id = pieces[1];
        await this.loadChallenge(id);
      }
    }
  },

  // Desafíos con requisitos sin cumplir que CTFd muestra anonimizados
  locked() {
    return this.challenges.filter(c => c.type === "hidden");
  },

  playable() {
    return this.challenges.filter(c => c.type !== "hidden");
  },

  visibleCategories() {
    const categories = this.getCategories();
    if (this.filter === null) {
      return categories;
    }
    return categories.filter(c => c === this.filter);
  },

  categoryColor(category) {
    return colorCategoria(category);
  },

  categorySigla(category) {
    return siglaCategoria(category);
  },

  level(challenge) {
    return nivelDesdeEtiquetas(challenge.tags);
  },

  solvedIn(category) {
    return this.getChallenges(category).filter(c => c.solved_by_me).length;
  },

  solvedCount() {
    return this.playable().filter(c => c.solved_by_me).length;
  },

  totalCount() {
    return this.playable().length;
  },

  suggested() {
    for (const category of this.getCategories()) {
      const next = this.getChallenges(category).find(c => !c.solved_by_me);
      if (next) {
        return next;
      }
    }
    return null;
  },

  async loadPlace() {
    const accountId = CTFd.config.userMode === "teams" ? CTFd.team.id : CTFd.user.id;
    if (!accountId) {
      return;
    }
    try {
      const response = await CTFd.fetch("/api/v1/scoreboard", { method: "GET" });
      if (!response.ok) {
        return;
      }
      const body = await response.json();
      const standings = body.data || [];
      const idx = standings.findIndex(s => s.account_id === accountId);
      if (idx >= 0) {
        this.place = {
          text: t("#{0}", idx + 1),
          of: t("of {0}", standings.length),
        };
      } else if (standings.length > 0) {
        this.place = { text: "—", of: t("of {0}", standings.length) };
      }
    } catch (error) {
      // Si el ranking está oculto, no se muestra el puesto
    }
  },

  t(msgid, ...args) {
    return t(msgid, ...args);
  },

  getCategories() {
    const categories = [];

    this.playable().forEach(challenge => {
      const { category } = challenge;

      if (!categories.includes(category)) {
        categories.push(category);
      }
    });

    try {
      const f = CTFd.config.themeSettings.challenge_category_order;
      if (f) {
        const getSort = new Function(`return (${f})`);
        categories.sort(getSort());
      }
    } catch (error) {
      // Ignore errors with theme category sorting
      console.log("Error running challenge_category_order function");
      console.log(error);
    }

    return categories;
  },

  getChallenges(category) {
    let challenges = this.playable();

    if (category !== null) {
      challenges = challenges.filter(challenge => challenge.category === category);
    }

    try {
      const f = CTFd.config.themeSettings.challenge_order;
      if (f) {
        const getSort = new Function(`return (${f})`);
        challenges.sort(getSort());
      }
    } catch (error) {
      // Ignore errors with theme challenge sorting
      console.log("Error running challenge_order function");
      console.log(error);
    }

    return challenges;
  },

  async loadChallenges() {
    this.challenges = await CTFd.pages.challenges.getChallenges();
  },

  async loadChallenge(challengeId) {
    await CTFd.pages.challenge.displayChallenge(challengeId, challenge => {
      challenge.data.view = addTargetBlank(challenge.data.view);
      Alpine.store("challenge").data = challenge.data;

      // nextTick is required here because we're working in a callback
      Alpine.nextTick(() => {
        let modal = Modal.getOrCreateInstance("[x-ref='challengeWindow']");
        // TODO: Get rid of this private attribute access
        // See https://github.com/twbs/bootstrap/issues/31266
        modal._element.addEventListener(
          "hidden.bs.modal",
          event => {
            // Remove location hash
            history.replaceState(null, null, " ");
          },
          { once: true }
        );
        modal.show();
        history.replaceState(null, null, `#${challenge.data.name}-${challengeId}`);
      });
    });
  },
}));

Alpine.start();
