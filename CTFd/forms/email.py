from wtforms import TextAreaField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class SendEmailForm(BaseForm):
    text = TextAreaField("Mensaje", validators=[InputRequired()])
    submit = SubmitField("Enviar")
