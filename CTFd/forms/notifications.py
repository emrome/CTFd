from wtforms import BooleanField, RadioField, StringField, TextAreaField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class NotificationForm(BaseForm):
    title = StringField("Título", description="Título de la notificación")
    content = TextAreaField(
        "Contenido",
        description="Contenido de la notificación. Puede incluir HTML y/o Markdown.",
    )
    type = RadioField(
        "Tipo de notificación",
        choices=[
            ("toast", "Emergente"),
            ("alert", "Alerta"),
            ("background", "En segundo plano"),
        ],
        default="toast",
        description="Qué tipo de notificación reciben los usuarios",
        validators=[InputRequired()],
    )
    sound = BooleanField(
        "Reproducir sonido",
        default=True,
        description="Reproduce un sonido cuando los usuarios reciben la notificación",
    )
    submit = SubmitField("Enviar")
