import jinja2.exceptions
from flask import render_template
from flask_babel import gettext as _
from werkzeug.exceptions import (
    BadRequest,
    Forbidden,
    InternalServerError,
    NotFound,
    TooManyRequests,
    Unauthorized,
)


def get_default_error_descriptions():
    """
    Translated replacements for Werkzeug's default (English) error descriptions
    """
    return {
        BadRequest.description: _(
            "The request could not be understood. Please check it and try again."
        ),
        Unauthorized.description: _("You need to log in to access this page."),
        Forbidden.description: _("You don't have permission to access this page."),
        NotFound.description: _(
            "The page you are looking for doesn't exist or was moved."
        ),
        TooManyRequests.description: _(
            "You have made too many requests. Please wait a moment and try again."
        ),
        InternalServerError.description: _("An Internal Server Error has occurred"),
    }


def render_error(error):
    description = get_default_error_descriptions().get(
        error.description, error.description
    )
    try:
        return (
            render_template(
                "errors/{}.html".format(error.code),
                error=description,
            ),
            error.code,
        )
    except jinja2.exceptions.TemplateNotFound:
        return error.get_response()
