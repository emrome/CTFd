from wtforms import (
    BooleanField,
    HiddenField,
    MultipleFileField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm


class PageEditForm(BaseForm):
    title = StringField(
        "Título", description="Es el título que se muestra en la barra de navegación"
    )
    route = StringField(
        "Ruta",
        description="Es la ruta URL donde va a estar tu página (por ej.: /pagina). También podés ingresar un enlace para que apunte a esa página.",
    )
    draft = BooleanField("Borrador")
    hidden = BooleanField("Oculta")
    auth_required = BooleanField("Requiere iniciar sesión")
    content = TextAreaField("Contenido")
    format = SelectField(
        "Formato",
        choices=[("markdown", "Markdown"), ("html", "HTML")],
        default="markdown",
        validators=[InputRequired()],
        description="El formato de marcado con el que se muestra la página",
    )


class PageFilesUploadForm(BaseForm):
    file = MultipleFileField(
        "Subir archivos",
        description="Elegí varios archivos con Control+Clic o Cmd+Clic.",
        validators=[InputRequired()],
    )
    type = HiddenField("Tipo de página", default="page", validators=[InputRequired()])
