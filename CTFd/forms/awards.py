from wtforms import RadioField, StringField, TextAreaField
from wtforms.fields.html5 import IntegerField

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class AwardCreationForm(BaseForm):
    name = StringField("Nombre")
    value = IntegerField("Puntaje")
    category = StringField("Categoría")
    description = TextAreaField("Descripción")
    submit = SubmitField("Crear")
    icon = RadioField(
        "Ícono",
        choices=[
            ("", "Ninguno"),
            ("shield", "Escudo"),
            ("bug", "Bicho"),
            ("crown", "Corona"),
            ("crosshairs", "Mira"),
            ("ban", "Prohibido"),
            ("lightning", "Rayo"),
            ("skull", "Calavera"),
            ("brain", "Cerebro"),
            ("code", "Código"),
            ("cowboy", "Vaquero"),
            ("angry", "Enojado"),
        ],
    )
