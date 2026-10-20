"""
Importacion de desafios del banco a la instancia de CTFd.
"""
import os

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
    estado = "hidden" if ocultos else datos.get("state", "visible")
    if estado not in ("visible", "hidden"):
        estado = "visible"

    campos = dict(
        name=desafio.nombre,
        description=datos.get("description", ""),
        connection_info=datos.get("connection_info"),
        max_attempts=datos.get("attempts") or 0,
        category=desafio.categoria,
        state=estado,
        type=tipo,
    )
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

    for flag in datos.get("flags") or []:
        if isinstance(flag, dict):
            db.session.add(
                Flags(
                    challenge_id=challenge.id,
                    type=flag.get("type", "static"),
                    content=flag.get("content", ""),
                    data=flag.get("data", ""),
                )
            )
        else:
            db.session.add(
                Flags(challenge_id=challenge.id, type="static", content=str(flag))
            )

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


def importar(seleccionados, banco, incluir_requisitos=True, ocultos=False):
    """
    Importa los desafios seleccionados.

    Devuelve un diccionario con los nombres creados, los omitidos (con motivo)
    y avisos sobre requisitos que no se pudieron resolver.
    """
    por_nombre = {d.nombre: d for d in banco}
    if incluir_requisitos:
        a_importar = con_requisitos(seleccionados, por_nombre)
    else:
        a_importar = list(seleccionados)

    resultado = {"creados": [], "omitidos": [], "avisos": [], "agregados": []}
    nombres_pedidos = {d.nombre for d in seleccionados}
    creados = []

    for desafio in a_importar:
        errores = desafio.errores()
        if errores:
            resultado["omitidos"].append((desafio.nombre or desafio.id, ", ".join(errores)))
            continue
        if Challenges.query.filter_by(name=desafio.nombre).first():
            resultado["omitidos"].append((desafio.nombre, "ya existe en la instancia"))
            continue
        creados.append((desafio, crear_desafio(desafio, ocultos=ocultos)))
        resultado["creados"].append(desafio.nombre)
        if desafio.nombre not in nombres_pedidos:
            resultado["agregados"].append(desafio.nombre)

    # Los requisitos se resuelven al final, cuando ya existen todos los desafios
    for desafio, challenge in creados:
        ids = []
        for requisito in desafio.requisitos:
            previo = Challenges.query.filter_by(name=requisito).first()
            if previo:
                ids.append(previo.id)
            else:
                resultado["avisos"].append(
                    '"{}" requiere "{}", que no está en la instancia; '
                    "se importó sin ese requisito".format(desafio.nombre, requisito)
                )
        if ids:
            challenge.requirements = {"prerequisites": ids}
    db.session.commit()

    return resultado
