"""
Lectura del banco de desafios.

Un banco es un directorio con una carpeta por desafio. Cada carpeta tiene un
challenge.yml en el formato de ctfcli y los archivos que el desafio entrega.
"""
import os
import unicodedata

import yaml

NIVELES = ["introductorio", "facil", "medio", "avanzado"]

# Equivalencias entre las etiquetas de nivel usadas en los distintos repositorios
# (ctfcli.py de este proyecto usa basico/intermedio/avanzado).
ALIAS_NIVEL = {
    "introductorio": "introductorio",
    "introduccion": "introductorio",
    "facil": "facil",
    "basico": "facil",
    "medio": "medio",
    "intermedio": "medio",
    "avanzado": "avanzado",
    "dificil": "avanzado",
}

NOMBRE_NIVEL = {
    "introductorio": "Introductorio",
    "facil": "Fácil",
    "medio": "Medio",
    "avanzado": "Avanzado",
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().lower()


def nivel_desde_tags(tags):
    """Devuelve la clave de nivel a partir de tags como 'nivel: fácil' o 'Basico'."""
    for tag in tags or []:
        valor = tag.get("value") if isinstance(tag, dict) else tag
        valor = normalizar(valor)
        if valor.startswith("nivel:"):
            valor = valor.split(":", 1)[1].strip()
        if valor in ALIAS_NIVEL:
            return ALIAS_NIVEL[valor]
    return None


class Desafio(object):
    def __init__(self, ruta, datos, raiz):
        self.ruta = ruta
        self.datos = datos
        self.id = os.path.relpath(ruta, raiz).replace(os.sep, "/")

    @property
    def nombre(self):
        return str(self.datos.get("name", "")).strip()

    @property
    def categoria(self):
        return str(self.datos.get("category", "") or "Sin categoría").strip()

    @property
    def valor(self):
        return self.datos.get("value") or 0

    @property
    def tags(self):
        tags = []
        for tag in self.datos.get("tags") or []:
            valor = tag.get("value") if isinstance(tag, dict) else tag
            if valor is not None:
                tags.append(str(valor))
        return tags

    @property
    def nivel(self):
        return nivel_desde_tags(self.tags)

    @property
    def nombre_nivel(self):
        return NOMBRE_NIVEL.get(self.nivel, "Sin nivel")

    @property
    def requisitos(self):
        reqs = self.datos.get("requirements") or []
        if isinstance(reqs, dict):
            reqs = reqs.get("prerequisites") or []
        return [str(r).strip() for r in reqs]

    @property
    def archivos(self):
        return [os.path.join(self.ruta, f) for f in self.datos.get("files") or []]

    @property
    def autor(self):
        return str(self.datos.get("author") or "").strip()

    def errores(self):
        errores = []
        if not self.nombre:
            errores.append("falta el nombre")
        if not self.datos.get("flags"):
            errores.append("no tiene flags")
        tipo = self.datos.get("type", "standard")
        if tipo not in ("standard", "dynamic"):
            errores.append("tipo no soportado: {}".format(tipo))
        for archivo in self.archivos:
            if not os.path.isfile(archivo):
                errores.append("falta el archivo {}".format(os.path.basename(archivo)))
        return errores


def directorio_banco(app):
    return app.config.get("BANCO_DESAFIOS_DIR") or os.environ.get(
        "BANCO_DESAFIOS_DIR",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "banco"),
    )


def cargar_banco(raiz):
    """Recorre el directorio y devuelve los desafios ordenados por categoria y nivel."""
    desafios = []
    if not os.path.isdir(raiz):
        return desafios
    for actual, carpetas, archivos in os.walk(raiz):
        carpetas[:] = sorted(c for c in carpetas if not c.startswith("."))
        for nombre in ("challenge.yml", "challenge.yaml"):
            if nombre in archivos:
                with open(os.path.join(actual, nombre), encoding="utf-8") as f:
                    datos = yaml.safe_load(f) or {}
                desafios.append(Desafio(actual, datos, raiz))
                break
    orden = {n: i for i, n in enumerate(NIVELES)}
    desafios.sort(
        key=lambda d: (
            normalizar(d.categoria),
            orden.get(d.nivel, len(NIVELES)),
            normalizar(d.nombre),
        )
    )
    return desafios
