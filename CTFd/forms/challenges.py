from wtforms import MultipleFileField, SelectField, StringField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class ChallengeSearchForm(BaseForm):
    field = SelectField(
        "Buscar por",
        choices=[
            ("name", "Nombre"),
            ("id", "ID"),
            ("category", "Categoría"),
            ("type", "Tipo"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Término de búsqueda", validators=[InputRequired()])
    submit = SubmitField("Buscar")


class ChallengeFilesUploadForm(BaseForm):
    file = MultipleFileField(
        "Subir archivos",
        description="Elegí varios archivos con Control+Clic o Cmd+Clic.",
        validators=[InputRequired()],
    )
    submit = SubmitField("Subir")
