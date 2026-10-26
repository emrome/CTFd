"""
Banco de desafios: permite a administradores y autores elegir desafios de un
repositorio (directorio con challenge.yml en formato ctfcli) e importarlos a la
instancia sin usar la linea de comandos.
"""
from flask import Blueprint, render_template, request
from flask_babel import lazy_gettext as _l

from CTFd.models import Challenges
from CTFd.plugins import register_admin_plugin_menu_bar
from CTFd.plugins.banco_desafios.banco import (
    NIVELES,
    NOMBRE_NIVEL,
    cargar_banco,
    directorio_banco,
)
from CTFd.plugins.banco_desafios.importar import importar
from CTFd.utils.decorators import admin_or_author

banco_desafios = Blueprint("banco_desafios", __name__, template_folder="templates")


def _vista(resultado=None):
    from flask import current_app

    raiz = directorio_banco(current_app)
    banco = cargar_banco(raiz)
    existentes = {c.name for c in Challenges.query.with_entities(Challenges.name)}
    categorias = sorted({d.categoria for d in banco})
    return render_template(
        "banco_desafios/listado.html",
        banco=banco,
        raiz=raiz,
        existentes=existentes,
        categorias=categorias,
        niveles=[(n, NOMBRE_NIVEL[n]) for n in NIVELES],
        resultado=resultado,
    )


@banco_desafios.route("/admin/banco", methods=["GET"])
@admin_or_author
def listado():
    return _vista()


@banco_desafios.route("/admin/banco", methods=["POST"])
@admin_or_author
def importar_seleccionados():
    from flask import current_app

    banco = cargar_banco(directorio_banco(current_app))
    elegidos = set(request.form.getlist("desafio"))
    seleccionados = [d for d in banco if d.id in elegidos]
    resultado = importar(
        seleccionados,
        banco,
        incluir_requisitos=request.form.get("requisitos") == "y",
        ocultos=request.form.get("ocultos") == "y",
    )
    return _vista(resultado=resultado)


def load(app):
    app.register_blueprint(banco_desafios)
    register_admin_plugin_menu_bar(title=_l("Challenge Bank"), route="/admin/banco")
