from wtforms import BooleanField, FileField, SelectField, StringField, TextAreaField
from wtforms.fields.html5 import IntegerField, URLField
from wtforms.widgets.html5 import NumberInput

from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    RegistrationVisibilityTypes,
    ScoreVisibilityTypes,
)
from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.utils.csv import get_dumpable_tables


class ResetInstanceForm(BaseForm):
    accounts = BooleanField(
        "Cuentas",
        description="Borra todas las cuentas de usuarios y equipos, y su información asociada",
    )
    submissions = BooleanField(
        "Envíos",
        description="Borra todos los registros de puntos obtenidos o acciones realizadas por las cuentas",
    )
    challenges = BooleanField(
        "Desafíos", description="Borra todos los desafíos y sus datos asociados"
    )
    pages = BooleanField(
        "Páginas", description="Borra todas las páginas y sus archivos asociados"
    )
    notifications = BooleanField(
        "Notificaciones", description="Borra todas las notificaciones"
    )
    submit = SubmitField("Reiniciar CTF")


class AccountSettingsForm(BaseForm):
    domain_whitelist = StringField(
        "Dominios de correo permitidos",
        description="Dominios de correo, separados por comas, con los que se pueden registrar los usuarios (por ej.: ctfd.io, example.com, *.example.com)",
    )
    team_creation = SelectField(
        "Creación de equipos",
        description="Define si los usuarios pueden crear sus propios equipos (solo en modo por equipos)",
        choices=[("true", "Habilitado"), ("false", "Deshabilitado")],
        default="true",
    )
    team_size = IntegerField(
        "Tamaño de los equipos",
        widget=NumberInput(min=0),
        description="Cantidad de usuarios por equipo (solo en modo por equipos)",
    )
    num_teams = IntegerField(
        "Cantidad máxima de equipos",
        widget=NumberInput(min=0),
        description="Cantidad máxima de equipos (solo en modo por equipos)",
    )
    num_users = IntegerField(
        "Cantidad máxima de usuarios",
        widget=NumberInput(min=0),
        description="Cantidad máxima de usuarios",
    )
    verify_emails = SelectField(
        "Verificar correos",
        description="Define si los usuarios tienen que confirmar su correo antes de jugar",
        choices=[("true", "Habilitado"), ("false", "Deshabilitado")],
        default="false",
    )
    team_disbanding = SelectField(
        "Disolución de equipos",
        description="Define si los capitanes pueden disolver sus propios equipos",
        choices=[
            ("inactive_only", "Habilitado para equipos inactivos"),
            ("disabled", "Deshabilitado"),
        ],
        default="inactive_only",
    )
    name_changes = SelectField(
        "Cambios de nombre",
        description="Define si los usuarios y equipos pueden cambiar su nombre",
        choices=[("true", "Habilitado"), ("false", "Deshabilitado")],
        default="true",
    )
    incorrect_submissions_per_min = IntegerField(
        "Envíos incorrectos por minuto",
        widget=NumberInput(min=1),
        description="Cantidad de envíos permitidos por minuto, para proteger contra ataques de fuerza bruta a las flags (predeterminado: 10)",
    )

    submit = SubmitField("Actualizar")


class ExportCSVForm(BaseForm):
    table = SelectField("Tabla de la base de datos", choices=get_dumpable_tables())
    submit = SubmitField("Descargar CSV")


class ImportCSVForm(BaseForm):
    csv_type = SelectField(
        "Tipo de CSV",
        choices=[("users", "Usuarios"), ("teams", "Equipos"), ("challenges", "Desafíos")],
        description="Tipo de datos del CSV",
    )
    csv_file = FileField("Archivo CSV", description="Contenido del archivo CSV")


class LegalSettingsForm(BaseForm):
    tos_url = URLField(
        "URL de los Términos de servicio",
        description="URL externa de un documento de Términos de servicio alojado en otro sitio",
    )
    tos_text = TextAreaField(
        "Términos de servicio",
        description="Texto que se muestra en la página de Términos de servicio",
    )
    privacy_url = URLField(
        "URL de la Política de privacidad",
        description="URL externa de un documento de Política de privacidad alojado en otro sitio",
    )
    privacy_text = TextAreaField(
        "Política de privacidad",
        description="Texto que se muestra en la página de Política de privacidad",
    )
    submit = SubmitField("Actualizar")


class VisibilitySettingsForm(BaseForm):
    challenge_visibility = SelectField(
        "Visibilidad de los desafíos",
        description="Define si los usuarios tienen que iniciar sesión para ver los desafíos",
        choices=[
            (ChallengeVisibilityTypes.PUBLIC, "Pública"),
            (ChallengeVisibilityTypes.PRIVATE, "Privada"),
            (ChallengeVisibilityTypes.ADMINS, "Solo administradores"),
        ],
        default=ChallengeVisibilityTypes.PRIVATE,
    )
    account_visibility = SelectField(
        "Visibilidad de las cuentas",
        description="Define si las cuentas (usuarios y equipos) se muestran a todos, solo a usuarios con sesión iniciada o solo a administradores",
        choices=[
            (AccountVisibilityTypes.PUBLIC, "Pública"),
            (AccountVisibilityTypes.PRIVATE, "Privada"),
            (AccountVisibilityTypes.ADMINS, "Solo administradores"),
        ],
        default=AccountVisibilityTypes.PUBLIC,
    )
    score_visibility = SelectField(
        "Visibilidad del puntaje",
        description="Define si las resoluciones y el puntaje se muestran al público, a usuarios con sesión iniciada, se ocultan a todos los que no son administradores o solo se muestran a administradores",
        choices=[
            (ScoreVisibilityTypes.PUBLIC, "Pública"),
            (ScoreVisibilityTypes.PRIVATE, "Privada"),
            (ScoreVisibilityTypes.HIDDEN, "Oculta"),
            (ScoreVisibilityTypes.ADMINS, "Solo administradores"),
        ],
        default=ScoreVisibilityTypes.PUBLIC,
    )
    registration_visibility = SelectField(
        "Visibilidad del registro",
        description="Define si el registro está habilitado para todos o deshabilitado",
        choices=[
            (RegistrationVisibilityTypes.PUBLIC, "Pública"),
            (RegistrationVisibilityTypes.PRIVATE, "Privada"),
            (RegistrationVisibilityTypes.MLC, "Solo MajorLeagueCyber"),
        ],
        default=RegistrationVisibilityTypes.PUBLIC,
    )
