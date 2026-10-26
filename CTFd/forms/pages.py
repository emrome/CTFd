from flask_babel import lazy_gettext as _l
from flask_babel import lazy_pgettext
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
        _l("Title"), description=_l("This is the title shown on the navigation bar")
    )
    route = StringField(
        _l("Route"),
        description=_l(
            "This is the URL route that your page will be at (e.g. /page). You can also enter links to link to that page."
        ),
    )
    draft = BooleanField(_l("Draft"))
    hidden = BooleanField(lazy_pgettext("page", "Hidden"))
    auth_required = BooleanField(_l("Authentication Required"))
    content = TextAreaField(_l("Content"))
    format = SelectField(
        _l("Format"),
        choices=[("markdown", "Markdown"), ("html", "HTML")],
        default="markdown",
        validators=[InputRequired()],
        description=_l("The markup format used to render the page"),
    )


class PageFilesUploadForm(BaseForm):
    file = MultipleFileField(
        _l("Upload Files"),
        description=_l("Attach multiple files using Control+Click or Cmd+Click."),
        validators=[InputRequired()],
    )
    type = HiddenField(_l("Page Type"), default="page", validators=[InputRequired()])
