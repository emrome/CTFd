"""
Metricas de aprendizaje: una pagina del panel de administracion que muestra,
para cada desafio de la competencia, como les fue a los equipos (acceso,
resolucion, intentos incorrectos, pistas, tiempos y dificultad observada),
agrupado por nivel, categoria y la metadata pedagogica del banco de desafios.

Solo lee lo que CTFd ya guarda. Lo unico que escribe son los umbrales de
"Para revisar", en la configuracion de la competencia.
"""
import json

from flask import Blueprint, redirect, render_template, request, url_for

from CTFd.plugins import register_admin_plugin_menu_bar
from CTFd.plugins.metricas.calculo import (
    CLAVE_CONFIG,
    datos_competencia,
    leer_umbrales,
    validar_umbrales,
)
from CTFd.utils import set_config
from CTFd.utils.decorators import admin_or_author

metricas = Blueprint("metricas", __name__, template_folder="templates")


@metricas.route("/admin/metricas", methods=["GET"])
@admin_or_author
def vista():
    return render_template(
        "metricas/metricas.html",
        datos=datos_competencia(),
        umbrales=leer_umbrales(),
        guardado=request.args.get("guardado") == "1",
        error=None,
    )


@metricas.route("/admin/metricas/umbrales", methods=["POST"])
@admin_or_author
def guardar_umbrales():
    umbrales, error = validar_umbrales(request.form)
    if error:
        return (
            render_template(
                "metricas/metricas.html",
                datos=datos_competencia(),
                umbrales=leer_umbrales(),
                guardado=False,
                error=error,
            ),
            400,
        )
    set_config(CLAVE_CONFIG, json.dumps(umbrales))
    return redirect(url_for("metricas.vista", guardado=1))


def load(app):
    app.register_blueprint(metricas)
    register_admin_plugin_menu_bar(title="Métricas", route="/admin/metricas")
