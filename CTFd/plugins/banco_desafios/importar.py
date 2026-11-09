"""
Importacion de desafios del banco a la instancia de CTFd.
"""
import os

from flask_babel import gettext as _
from werkzeug.datastructures import FileStorage

from CTFd.models import Challenges, Flags, Hints, Tags, db
from CTFd.plugins.dynamic_challenges import DynamicChallenge
from CTFd.utils.uploads import upload_file


def con_requisitos(seleccionados, por_nombre):
    """Agrega recursivamente los requisitos que estan en el banco."""
    resultado = []
    vistos = set()

    def agregar(desafio):
        if desafio.nombre in vistos:
            return
        vistos.add(desafio.nombre)
        for requisito in desafio.requisitos:
            if requisito in por_nombre:
                agregar(por_nombre[requisito])
        resultado.append(desafio)

    for desafio in seleccionados:
        agregar(desafio)
    return resultado


def crear_desafio(desafio, ocultos=False):
    datos = desafio.datos
    tipo = datos.get("type", "standard")
    # Un state invalido es un error de validacion (Desafio.errores), asi que
    # aca solo llegan "visible" o "hidden".
    estado = "hidden" if ocultos else datos.get("state", "visible")

    campos = {
        "name": desafio.nombre,
        "description": datos.get("description", ""),
        "connection_info": datos.get("connection_info"),
        "max_attempts": datos.get("attempts") or 0,
        "category": desafio.categoria,
        "state": estado,
        "type": tipo,
    }
    if tipo == "dynamic":
        extra = datos.get("extra") or {}
        campos.update(
            initial=extra.get("initial", desafio.valor),
            minimum=extra.get("minimum", desafio.valor),
            decay=extra.get("decay", 0),
            function=extra.get("function", "logarithmic"),
        )
        challenge = DynamicChallenge(**campos)
    else:
        challenge = Challenges(value=desafio.valor, **campos)
    db.session.add(challenge)
    db.session.commit()

    # Las flags se insertan directo en la tabla: el modelo Flags usa "type" como
    # discriminador polimorfico sin subclases, y crearlas con el ORM produce el
    # aviso "Flushing object ... with incompatible polymorphic identity".
    flags = []
    for flag in datos.get("flags") or []:
        if isinstance(flag, dict):
            flags.append(
                {
                    "challenge_id": challenge.id,
                    "type": flag.get("type", "static"),
                    "content": str(flag.get("content", "")),
                    "data": flag.get("data") or "",
                }
            )
        else:
            flags.append(
                {
                    "challenge_id": challenge.id,
                    "type": "static",
                    "content": str(flag),
                    "data": "",
                }
            )
    if flags:
        db.session.execute(Flags.__table__.insert(), flags)

    for valor in desafio.tags:
        db.session.add(Tags(challenge_id=challenge.id, value=valor[:80]))

    for hint in datos.get("hints") or []:
        if isinstance(hint, dict):
            db.session.add(
                Hints(
                    challenge_id=challenge.id,
                    content=hint.get("content", ""),
                    cost=hint.get("cost", 0) or 0,
                )
            )
        else:
            db.session.add(Hints(challenge_id=challenge.id, content=str(hint), cost=0))
    db.session.commit()

    for ruta in desafio.archivos:
        with open(ruta, "rb") as f:
            upload_file(
                file=FileStorage(stream=f, filename=os.path.basename(ruta)),
                challenge_id=challenge.id,
                type="challenge",
            )

    return challenge


def agregar_requisitos(challenge, ids):
    """
    Agrega ids a los prerequisitos del desafio sin quitar los que ya tiene.
    Devuelve los ids que agrego.
    """
    requisitos = dict(challenge.requirements or {})
    actuales = list(requisitos.get("prerequisites") or [])
    nuevos = []
    for i in ids:
        if i not in actuales and i not in nuevos and i != challenge.id:
            nuevos.append(i)
    if nuevos:
        requisitos["prerequisites"] = actuales + nuevos
        # Se asigna un diccionario nuevo para que SQLAlchemy detecte el cambio
        challenge.requirements = requisitos
    return nuevos


def importar(seleccionados, banco, incluir_requisitos=True, ocultos=False):
    """
    Importa los desafios seleccionados.

    Devuelve un diccionario con los nombres creados, los omitidos (con motivo),
    avisos sobre requisitos que no se pudieron resolver y los requisitos que se
    enlazaron en desafios importados antes.

    Los requisitos se buscan por nombre entre todos los desafios de la instancia,
    no solo entre los creados en esta importacion. Ademas, si un desafio importado
    antes nombra como requisito a uno que se crea ahora, se enlaza en ese momento.
    """
    por_nombre = {d.nombre: d for d in banco}
    if incluir_requisitos:
        a_importar = con_requisitos(seleccionados, por_nombre)
    else:
        a_importar = list(seleccionados)

    resultado = {
        "creados": [],
        "omitidos": [],
        "avisos": [],
        "agregados": [],
        "enlazados": [],
    }
    nombres_pedidos = {d.nombre for d in seleccionados}
    creados = []

    for desafio in a_importar:
        errores = desafio.errores()
        if errores:
            resultado["omitidos"].append(
                (desafio.nombre or desafio.id, ", ".join(errores))
            )
            continue
        if Challenges.query.filter_by(name=desafio.nombre).first():
            resultado["omitidos"].append(
                (desafio.nombre, _("already exists in this instance"))
            )
            continue
        creados.append((desafio, crear_desafio(desafio, ocultos=ocultos)))
        resultado["creados"].append(desafio.nombre)
        if desafio.nombre not in nombres_pedidos:
            resultado["agregados"].append(desafio.nombre)

    # Los requisitos se resuelven al final, cuando ya existen todos los desafios
    # de esta importacion, contra todos los desafios de la instancia.
    for desafio, challenge in creados:
        ids = []
        for requisito in desafio.requisitos:
            previo = Challenges.query.filter_by(name=requisito).first()
            if previo:
                ids.append(previo.id)
            elif requisito in por_nombre:
                resultado["avisos"].append(
                    _(
                        '"%(challenge)s" requires "%(requirement)s", which was not '
                        'imported. Until you import it, "%(challenge)s" is open '
                        "without that prerequisite; it will be linked automatically "
                        "when you import it from the bank.",
                        challenge=desafio.nombre,
                        requirement=requisito,
                    )
                )
            else:
                resultado["avisos"].append(
                    _(
                        '"%(challenge)s" requires "%(requirement)s", which is neither '
                        'in this instance nor in the bank. "%(challenge)s" is open '
                        "without that prerequisite: fix the name in its challenge.yml "
                        "or add the prerequisite by hand.",
                        challenge=desafio.nombre,
                        requirement=requisito,
                    )
                )
        agregar_requisitos(challenge, ids)

    # Caso inverso: desafios del banco importados antes que nombran como
    # requisito a alguno de los recien creados. Solo se agregan enlaces hacia los
    # nuevos, para no deshacer cambios hechos a mano en los requisitos.
    nuevos = {desafio.nombre: challenge.id for desafio, challenge in creados}
    if nuevos:
        for desafio in banco:
            if desafio.nombre in nuevos:
                continue
            faltan = [r for r in desafio.requisitos if r in nuevos]
            if not faltan:
                continue
            previo = Challenges.query.filter_by(name=desafio.nombre).first()
            if previo is None:
                continue
            agregados = agregar_requisitos(previo, [nuevos[r] for r in faltan])
            for requisito in faltan:
                if nuevos[requisito] in agregados:
                    resultado["enlazados"].append((desafio.nombre, requisito))
    db.session.commit()

    return resultado
