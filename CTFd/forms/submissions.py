from wtforms import SelectField, StringField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class SubmissionSearchForm(BaseForm):
    field = SelectField(
        "Buscar por",
        choices=[
            ("provided", "Respuesta enviada"),
            ("id", "ID"),
            ("account_id", "ID de cuenta"),
            ("challenge_id", "ID de desafío"),
            ("challenge_name", "Nombre del desafío"),
        ],
        default="provided",
        validators=[InputRequired()],
    )
    q = StringField("Término de búsqueda", validators=[InputRequired()])
    submit = SubmitField("Buscar")
