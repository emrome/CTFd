"""
Calculo de las metricas de aprendizaje a partir de lo que CTFd ya guarda:
envios, pistas desbloqueadas, requisitos de los desafios y fechas de la competencia.

Devuelve un diccionario listo para la vista, que hace el resto del calculo
(filtros, tasas, dificultad observada) en el navegador.
"""
import datetime
import json
from collections import defaultdict

from CTFd.models import Challenges, Hints, Submissions, Tags, Teams, Unlocks, Users, db
from CTFd.utils import get_config
from CTFd.utils.modes import TEAMS_MODE

NOMBRES_NIVEL = {
    "introductorio": "Introductorio",
    "facil": "Fácil",
    "medio": "Medio",
    "avanzado": "Avanzado",
}

UMBRALES = {"uTasa": 30, "uInc": 15, "uFacil": 80, "uMedio": 50, "uMin": 3}
LIMITES = {
    "uTasa": (0, 100),
    "uInc": (0, 999),
    "uFacil": (1, 100),
    "uMedio": (0, 99),
    "uMin": (1, 99),
}
CLAVE_CONFIG = "metricas_umbrales"


def leer_umbrales():
    umbrales = dict(UMBRALES)
    try:
        guardados = json.loads(get_config(CLAVE_CONFIG) or "{}")
    except (TypeError, ValueError):
        guardados = {}
    if isinstance(guardados, dict):
        for clave, (minimo, maximo) in LIMITES.items():
            valor = guardados.get(clave)
            if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                umbrales[clave] = int(min(maximo, max(minimo, valor)))
    if umbrales["uFacil"] <= umbrales["uMedio"]:
        umbrales["uFacil"], umbrales["uMedio"] = UMBRALES["uFacil"], UMBRALES["uMedio"]
    return umbrales


def validar_umbrales(form):
    """Devuelve (umbrales, error). Solo acepta enteros dentro de los limites."""
    umbrales = {}
    for clave, (minimo, maximo) in LIMITES.items():
        try:
            valor = int(form.get(clave, ""))
        except (TypeError, ValueError):
            return None, "Los umbrales tienen que ser números enteros."
        if not minimo <= valor <= maximo:
            return None, "Hay un umbral fuera de rango."
        umbrales[clave] = valor
    if umbrales["uFacil"] <= umbrales["uMedio"]:
        return None, "El umbral de Fácil tiene que ser mayor que el de Medio."
    return umbrales, None


def _fecha_config(clave):
    valor = get_config(clave)
    try:
        if not valor:
            return None
        fecha = datetime.datetime.fromtimestamp(int(valor), datetime.timezone.utc)
        return fecha.replace(tzinfo=None)
    except (TypeError, ValueError):
        return None


def _banco():
    """Desafios del banco por nombre, si el plugin del banco esta instalado."""
    try:
        from flask import current_app

        from CTFd.plugins.banco_desafios.banco import cargar_banco, directorio_banco
    except ImportError:
        return {}
    return {
        d.nombre: d for d in cargar_banco(directorio_banco(current_app)) if d.nombre
    }


def _nivel(tags):
    try:
        from CTFd.plugins.banco_desafios.banco import nivel_desde_tags
    except ImportError:
        return None
    return NOMBRES_NIVEL.get(nivel_desde_tags(tags))


def datos_competencia():
    modo_equipos = get_config("user_mode") == TEAMS_MODE

    # Solo cuentas de estudiantes: fuera administradores, autores y cuentas ocultas o bloqueadas
    estudiantes = {
        u.id
        for u in Users.query.filter_by(
            type="user", hidden=False, banned=False
        ).with_entities(Users.id)
    }
    if modo_equipos:
        cuentas = {
            t.id: t.name for t in Teams.query.filter_by(hidden=False, banned=False)
        }
    else:
        cuentas = {
            u.id: u.name
            for u in Users.query.filter_by(
                type="user", hidden=False, banned=False
            ).with_entities(Users.id, Users.name)
        }

    # Los nombres no son unicos en la base: si se repiten, se agrega el id
    repetidos = {n for n in cuentas.values() if list(cuentas.values()).count(n) > 1}
    cuentas = {
        i: "{} (#{})".format(n, i) if n in repetidos else n for i, n in cuentas.items()
    }

    def cuenta(fila):
        return fila.team_id if modo_equipos else fila.user_id

    envios = [
        s
        for s in db.session.query(
            Submissions.challenge_id,
            Submissions.user_id,
            Submissions.team_id,
            Submissions.type,
            Submissions.date,
        )
        .filter(Submissions.type.in_(("correct", "incorrect")))
        .order_by(Submissions.date, Submissions.id)
        if s.user_id in estudiantes and cuenta(s) in cuentas
    ]

    inicio = _fecha_config("start") or (envios[0].date if envios else None)
    fin = _fecha_config("end") or (envios[-1].date if envios else None)
    # Solo cuenta lo que paso durante la competencia
    envios = [
        s
        for s in envios
        if (inicio is None or s.date >= inicio) and (fin is None or s.date <= fin)
    ]

    primer_envio = {}
    for s in envios:
        primer_envio.setdefault(cuenta(s), s.date)
    activos = sorted(primer_envio, key=lambda c: (primer_envio[c], c))

    resuelto_por = defaultdict(set)
    for s in envios:
        if s.type == "correct":
            resuelto_por[s.challenge_id].add(cuenta(s))

    tags = defaultdict(list)
    for t in Tags.query.with_entities(Tags.challenge_id, Tags.value):
        tags[t.challenge_id].append(t.value)
    pista_desafio = {
        h.id: h.challenge_id
        for h in Hints.query.with_entities(Hints.id, Hints.challenge_id)
    }
    pistas = defaultdict(lambda: defaultdict(int))
    for u in db.session.query(
        Unlocks.target, Unlocks.user_id, Unlocks.team_id, Unlocks.date
    ).filter(Unlocks.type == "hints"):
        if (
            u.user_id in estudiantes
            and cuenta(u) in cuentas
            and u.target in pista_desafio
            and (inicio is None or u.date is None or u.date >= inicio)
            and (fin is None or u.date is None or u.date <= fin)
        ):
            pistas[pista_desafio[u.target]][cuenta(u)] += 1

    por_desafio = defaultdict(
        lambda: defaultdict(
            lambda: {"intentos": 0, "incorrectos": 0, "resuelto": False}
        )
    )
    for s in envios:
        p = por_desafio[s.challenge_id][cuenta(s)]
        p["intentos"] += 1
        if s.type == "incorrect":
            p["incorrectos"] += 1
        else:
            p["resuelto"] = True

    banco = _banco()
    retos = Challenges.query.order_by(Challenges.id).all()
    ids = {c.id for c in retos}
    desafios = []
    for c in retos:
        # Los ocultos solo entran si los jugaron (por ejemplo, si se ocultaron despues)
        if c.state == "hidden" and not por_desafio[c.id]:
            continue
        # Como CTFd, ignora los requisitos que apuntan a desafios borrados
        requisitos = [
            r for r in (c.requirements or {}).get("prerequisites") or [] if r in ids
        ]
        # Tambien tuvo acceso quien lo intento, por si los requisitos cambiaron durante la jornada
        acceso = [
            a
            for a in activos
            if por_desafio[c.id].get(a) or all(a in resuelto_por[r] for r in requisitos)
        ]
        del_banco = banco.get(c.name)
        por_equipo = {}
        # Tambien entra quien solo desbloqueo pistas, con 0 intentos
        for a in set(por_desafio[c.id]) | set(pistas[c.id]):
            p = por_desafio[c.id].get(a) or {
                "intentos": 0,
                "incorrectos": 0,
                "resuelto": False,
            }
            por_equipo[cuentas[a]] = dict(p, pistas=pistas[c.id].get(a, 0))
        desafios.append(
            {
                "id": c.id,
                "nombre": c.name,
                "categoria": c.category,
                "nivel": _nivel(tags[c.id]),
                "puntaje": c.value,
                "origen": "banco" if del_banco else "otros",
                "cia": list(del_banco.dimensiones_cia) if del_banco else [],
                "habilidad": list(del_banco.habilidades) if del_banco else [],
                "requisitos": len(requisitos),
                "acceso": [cuentas[a] for a in acceso],
                "por_equipo": por_equipo,
            }
        )

    resoluciones = []
    if inicio is not None:
        resoluciones = [
            {
                "equipo": cuentas[cuenta(s)],
                "challenge": s.challenge_id,
                "seg": round((s.date - inicio).total_seconds(), 3),
            }
            for s in envios
            if s.type == "correct"
        ]

    return {
        "evento": {
            "inicio": inicio.replace(tzinfo=datetime.timezone.utc).isoformat(
                timespec="seconds"
            )
            if inicio
            else None,
            "duracion_min": int((fin - inicio).total_seconds() // 60)
            if inicio and fin and fin > inicio
            else 0,
            "equipos": [cuentas[a] for a in activos],
            "equipos_registrados": len(cuentas),
            "modo_equipos": modo_equipos,
        },
        "desafios": desafios,
        "resoluciones": resoluciones,
    }
