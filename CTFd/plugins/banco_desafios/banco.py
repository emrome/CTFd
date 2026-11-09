"""
Lectura del banco de desafios.

Un banco es un directorio con una carpeta por desafio. Cada carpeta tiene un
challenge.yml en el formato de ctfcli y los archivos que el desafio entrega.
"""
import os
import re
import unicodedata

import yaml
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l

from CTFd.plugins.flags import FLAG_CLASSES

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

TIPOS = ("standard", "dynamic")
ESTADOS = ("visible", "hidden")
CLAVES_FLAG = ("type", "content", "data")
DATOS_FLAG = ("", "case_insensitive")
CLAVES_PEDAGOGIA = ("concept", "challenge_type", "cia_dimension", "skill")

# Separadores de un valor combinado de la metadata pedagogica, por ejemplo
# "Confidencialidad / Integridad" o "Observación, búsqueda y análisis básico".
SEPARADOR = re.compile(r"\s*(?:/|,|;|\+|&|\by\b|\band\b)\s*", re.IGNORECASE)
# Valores que significan "no aplica"
VACIOS = ("", "-", "—", "–", "n/a")

NOMBRE_NIVEL = {
    "introductorio": _l("Introductory"),
    "facil": _l("Easy"),
    "medio": _l("Medium"),
    "avanzado": _l("Advanced"),
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().lower()


def texto_o_vacio(valor):
    """Devuelve el valor como texto sin espacios, o '' si es un marcador de vacio."""
    if valor is None:
        return ""
    texto = str(valor).strip()
    return "" if texto.lower() in VACIOS else texto


def separar(texto):
    """
    Separa un valor combinado (dimension CIA, habilidad) en sus partes, sin
    repetir y con la primera letra en mayuscula.
    """
    partes = []
    for parte in SEPARADOR.split(texto_o_vacio(texto)):
        parte = texto_o_vacio(parte)
        if parte and normalizar(parte) not in [normalizar(p) for p in partes]:
            partes.append(parte[0].upper() + parte[1:])
    return partes


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
    def __init__(self, ruta, datos, raiz, error_lectura=None):
        self.ruta = ruta
        self.datos = datos
        self.error_lectura = error_lectura
        self.id = os.path.relpath(ruta, raiz).replace(os.sep, "/")

    @property
    def nombre(self):
        return str(self.datos.get("name", "")).strip()

    @property
    def categoria(self):
        return str(self.datos.get("category", "") or _("Uncategorized")).strip()

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
        return NOMBRE_NIVEL.get(self.nivel, _("No level"))

    @property
    def requisitos(self):
        reqs = self.datos.get("requirements") or []
        if isinstance(reqs, dict):
            reqs = reqs.get("prerequisites") or []
        if isinstance(reqs, str):
            reqs = [reqs]
        return [str(r).strip() for r in reqs if str(r).strip()]

    @property
    def archivos(self):
        return [os.path.join(self.ruta, f) for f in self.datos.get("files") or []]

    @property
    def autor(self):
        return str(self.datos.get("author") or "").strip()

    @property
    def pedagogia(self):
        """
        Bloque opcional `pedagogy` del challenge.yml. Devuelve un diccionario con
        las claves de CLAVES_PEDAGOGIA (vacias si faltan). CTFd no lo guarda; solo
        se muestra en el banco.
        """
        bloque = self.datos.get("pedagogy")
        if not isinstance(bloque, dict):
            bloque = {}
        return {clave: texto_o_vacio(bloque.get(clave)) for clave in CLAVES_PEDAGOGIA}

    @property
    def dimensiones_cia(self):
        return separar(self.pedagogia["cia_dimension"])

    @property
    def habilidades(self):
        return separar(self.pedagogia["skill"])

    @property
    def claves_cia(self):
        """Dimensiones CIA normalizadas, para el filtro del listado."""
        return [normalizar(d) for d in self.dimensiones_cia]

    @property
    def claves_habilidad(self):
        """Habilidades normalizadas, para el filtro del listado."""
        return [normalizar(h) for h in self.habilidades]

    @property
    def texto_busqueda(self):
        """Texto en el que busca el filtro libre: nombre, tags y metadata pedagogica."""
        p = self.pedagogia
        partes = [self.nombre] + self.tags
        partes += [p["concept"], p["skill"], p["challenge_type"]]
        return " ".join(x for x in partes if x).lower()

    def errores(self):
        """Problemas que impiden importar el desafio."""
        if self.error_lectura:
            return [_("cannot read challenge.yml: %(error)s", error=self.error_lectura)]
        errores = []
        if not self.nombre:
            errores.append(_("missing name"))
        tipo = self.datos.get("type", "standard")
        if tipo not in TIPOS:
            errores.append(_("unsupported type: %(type)s", type=tipo))
        valor = self.datos.get("value")
        if valor is not None and (
            isinstance(valor, bool) or not isinstance(valor, int)
        ):
            errores.append(_("value must be a whole number: %(value)s", value=valor))
        if "state" in self.datos and self.datos.get("state") not in ESTADOS:
            errores.append(
                _(
                    'invalid state "%(state)s" (use visible or hidden)',
                    state=self.datos.get("state"),
                )
            )
        errores.extend(self.errores_flags())
        for archivo in self.archivos:
            if not os.path.isfile(archivo):
                errores.append(
                    _("missing file %(file)s", file=os.path.basename(archivo))
                )
        return errores

    def errores_flags(self):
        flags = self.datos.get("flags")
        if not flags:
            return [_("has no flags")]
        if not isinstance(flags, list):
            return [_("flags must be a list")]
        errores = []
        for numero, flag in enumerate(flags, start=1):
            if isinstance(flag, (str, int, float)) and not isinstance(flag, bool):
                if not str(flag).strip():
                    errores.append(_("flag %(number)s is empty", number=numero))
                continue
            if not isinstance(flag, dict):
                errores.append(_("flag %(number)s is malformed", number=numero))
                continue
            for clave in flag:
                if clave in CLAVES_FLAG:
                    continue
                if ":" in str(clave):
                    errores.append(
                        _(
                            'flag %(number)s has an unknown key "%(key)s" '
                            '(missing space after ":"?)',
                            number=numero,
                            key=clave,
                        )
                    )
                else:
                    errores.append(
                        _(
                            'flag %(number)s has an unknown key "%(key)s"',
                            number=numero,
                            key=clave,
                        )
                    )
            contenido = flag.get("content")
            if contenido is None or not str(contenido).strip():
                errores.append(_("flag %(number)s has no content", number=numero))
            tipo = flag.get("type", "static")
            if tipo not in FLAG_CLASSES:
                errores.append(
                    _(
                        'flag %(number)s has an unknown type "%(type)s"',
                        number=numero,
                        type=tipo,
                    )
                )
            if (flag.get("data") or "") not in DATOS_FLAG:
                errores.append(
                    _(
                        'flag %(number)s has an invalid data value "%(data)s" '
                        "(use case_insensitive or leave it empty)",
                        number=numero,
                        data=flag.get("data"),
                    )
                )
        return errores

    def avisos(self, nombres_conocidos=None):
        """
        Problemas que no impiden importar. `nombres_conocidos` son los nombres de
        los desafios del banco y de la instancia; si se pasa, se avisa de los
        requisitos que no estan en ninguno de los dos.
        """
        avisos = []
        if nombres_conocidos is not None:
            for requisito in self.requisitos:
                if requisito not in nombres_conocidos:
                    avisos.append(
                        _(
                            'requires "%(requirement)s", which is neither in the bank '
                            "nor in this instance",
                            requirement=requisito,
                        )
                    )
        bloque = self.datos.get("pedagogy")
        if bloque is not None:
            if not isinstance(bloque, dict):
                avisos.append(_("the pedagogy block is not a mapping; it is ignored"))
            else:
                for clave in bloque:
                    if clave not in CLAVES_PEDAGOGIA:
                        avisos.append(_('unknown pedagogy key "%(key)s"', key=clave))
        return avisos


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
                error = None
                try:
                    with open(os.path.join(actual, nombre), encoding="utf-8") as f:
                        datos = yaml.safe_load(f) or {}
                except (yaml.YAMLError, UnicodeDecodeError) as e:
                    datos, error = {}, str(e).splitlines()[0]
                if not isinstance(datos, dict):
                    datos, error = {}, _("challenge.yml is not a mapping")
                desafios.append(Desafio(actual, datos, raiz, error_lectura=error))
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


def opciones_filtro(valores):
    """Opciones (clave normalizada, texto) sin repetir, ordenadas por la clave."""
    opciones = {}
    for valor in valores:
        if valor:
            opciones.setdefault(normalizar(valor), valor)
    return sorted(opciones.items())


def requisitos_universales(banco):
    """
    Requisitos que comparten todos los demas desafios del banco, directa o
    indirectamente (por ejemplo, un desafio de bienvenida). El listado los
    muestra una sola vez en lugar de repetirlos en cada fila. Solo se calcula con
    tres desafios o mas, para no esconder la unica relacion de un banco chico.
    """
    if len(banco) < 3:
        return []
    por_nombre = {d.nombre: d for d in banco}
    cache = {}

    def todos_los_requisitos(desafio, camino=()):
        if desafio.nombre in cache:
            return cache[desafio.nombre]
        resultado = set()
        for requisito in desafio.requisitos:
            resultado.add(requisito)
            previo = por_nombre.get(requisito)
            if previo is not None and requisito not in camino:
                resultado |= todos_los_requisitos(previo, camino + (desafio.nombre,))
        cache[desafio.nombre] = resultado
        return resultado

    universales = []
    for candidato in banco:
        nombre = candidato.nombre
        if nombre and all(
            nombre in todos_los_requisitos(d) for d in banco if d is not candidato
        ):
            universales.append(nombre)
    return universales
