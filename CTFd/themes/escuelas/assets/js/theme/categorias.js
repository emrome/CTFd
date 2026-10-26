// Color y sigla de cada categoría, según la guía de estilo.
// Mantener en sincronía con templates/macros/categorias.html.
import { t } from "../utils/i18n";

const CATEGORIAS = [
  { prefijos: ["intro"], sigla: ">_", color: "#E4E7EE" },
  { prefijos: ["cripto"], sigla: "#", color: "#D6E0FF" },
  { prefijos: ["contrasen", "autentic", "password"], sigla: "**", color: "#FFD6CC" },
  { prefijos: ["phishing"], sigla: "@", color: "#FFE08A" },
  { prefijos: ["osint"], sigla: "?", color: "#C5EBDB" },
  { prefijos: ["ingenieria"], sigla: "!", color: "#EBD9F5" },
];

const NIVELES = {
  facil: "Basic",
  basico: "Basic",
  medio: "Intermediate",
  intermedio: "Intermediate",
  avanzado: "Advanced",
  introductorio: "Introductory",
};

export function normalizar(texto) {
  return (texto || "")
    .toString()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/-/g, " ")
    .trim();
}

function buscar(nombre) {
  const clave = normalizar(nombre);
  return CATEGORIAS.find(c => c.prefijos.some(p => clave.startsWith(p)));
}

// Key of the style-guide group a category belongs to ("cripto", "osint"...), or "".
export function grupoCategoria(nombre) {
  const c = buscar(nombre);
  return c ? c.prefijos[0] : "";
}

export function colorCategoria(nombre) {
  const c = buscar(nombre);
  return c ? c.color : "#E4E7EE";
}

export function siglaCategoria(nombre) {
  const c = buscar(nombre);
  if (c) {
    return c.sigla;
  }
  const limpio = (nombre || "?").trim();
  return limpio ? limpio[0].toUpperCase() : "?";
}

// Busca una etiqueta con la forma «nivel: fácil» y devuelve el nivel legible.
export function nivelDesdeEtiquetas(tags) {
  for (const tag of tags || []) {
    const valor = normalizar(typeof tag === "string" ? tag : tag.value);
    if (valor.startsWith("nivel")) {
      const nivel = valor.slice(5).replace(":", "").trim();
      return NIVELES[nivel]
        ? t(NIVELES[nivel])
        : nivel.charAt(0).toUpperCase() + nivel.slice(1);
    }
  }
  return "";
}
