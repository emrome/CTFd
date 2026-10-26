from flask_babel import lazy_gettext as _l
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
        _l("Accounts"),
        description=_l(
            "Deletes all user and team accounts and their associated information"
        ),
    )
    submissions = BooleanField(
        _l("Submissions"),
        description=_l(
            "Deletes all records that accounts gained points or took an action"
        ),
    )
    challenges = BooleanField(
        _l("Challenges"), description=_l("Deletes all challenges and associated data")
    )
    pages = BooleanField(
        _l("Pages"), description=_l("Deletes all pages and their associated files")
    )
    notifications = BooleanField(
        _l("Notifications"), description=_l("Deletes all notifications")
    )
    submit = SubmitField(_l("Reset CTF"))


class AccountSettingsForm(BaseForm):
    domain_whitelist = StringField(
        _l("Account Email Whitelist"),
        description=_l(
            "Comma-seperated email domains which users can register under (e.g. ctfd.io, example.com, *.example.com)"
        ),
    )
    team_creation = SelectField(
        _l("Team Creation"),
        description=_l(
            "Control whether users can create their own teams (Teams mode only)"
        ),
        choices=[("true", _l("Enabled")), ("false", _l("Disabled"))],
        default="true",
    )
    team_size = IntegerField(
        _l("Team Size"),
        widget=NumberInput(min=0),
        description=_l("Amount of users per team (Teams mode only)"),
    )
    num_teams = IntegerField(
        _l("Total Number of Teams"),
        widget=NumberInput(min=0),
        description=_l("Max number of teams (Teams mode only)"),
    )
    num_users = IntegerField(
        _l("Total Number of Users"),
        widget=NumberInput(min=0),
        description=_l("Max number of users"),
    )
    verify_emails = SelectField(
        _l("Verify Emails"),
        description=_l(
            "Control whether users must confirm their email addresses before playing"
        ),
        choices=[("true", _l("Enabled")), ("false", _l("Disabled"))],
        default="false",
    )
    team_disbanding = SelectField(
        _l("Team Disbanding"),
        description=_l(
            "Control whether team captains are allowed to disband their own teams"
        ),
        choices=[
            ("inactive_only", _l("Enabled for Inactive Teams")),
            ("disabled", _l("Disabled")),
        ],
        default="inactive_only",
    )
    name_changes = SelectField(
        _l("Name Changes"),
        description=_l("Control whether users and teams can change their names"),
        choices=[("true", _l("Enabled")), ("false", _l("Disabled"))],
        default="true",
    )
    incorrect_submissions_per_min = IntegerField(
        _l("Incorrect Submissions per Minute"),
        widget=NumberInput(min=1),
        description=_l(
            "Amount of submissions allowed per minute for flag bruteforce protection (default: 10)"
        ),
    )

    submit = SubmitField(_l("Update"))


class ExportCSVForm(BaseForm):
    table = SelectField(_l("Database Table"), choices=get_dumpable_tables())
    submit = SubmitField(_l("Download CSV"))


class ImportCSVForm(BaseForm):
    csv_type = SelectField(
        _l("CSV Type"),
        choices=[
            ("users", _l("Users")),
            ("teams", _l("Teams")),
            ("challenges", _l("Challenges")),
        ],
        description=_l("Type of CSV data"),
    )
    csv_file = FileField(_l("CSV File"), description=_l("CSV file contents"))


class LegalSettingsForm(BaseForm):
    tos_url = URLField(
        _l("Terms of Service URL"),
        description=_l("External URL to a Terms of Service document hosted elsewhere"),
    )
    tos_text = TextAreaField(
        _l("Terms of Service"),
        description=_l("Text shown on the Terms of Service page"),
    )
    privacy_url = URLField(
        _l("Privacy Policy URL"),
        description=_l("External URL to a Privacy Policy document hosted elsewhere"),
    )
    privacy_text = TextAreaField(
        _l("Privacy Policy"),
        description=_l("Text shown on the Privacy Policy page"),
    )
    submit = SubmitField(_l("Update"))


class VisibilitySettingsForm(BaseForm):
    challenge_visibility = SelectField(
        _l("Challenge Visibility"),
        description=_l("Control whether users must be logged in to see challenges"),
        choices=[
            (ChallengeVisibilityTypes.PUBLIC, _l("Public")),
            (ChallengeVisibilityTypes.PRIVATE, _l("Private")),
            (ChallengeVisibilityTypes.ADMINS, _l("Admins Only")),
        ],
        default=ChallengeVisibilityTypes.PRIVATE,
    )
    account_visibility = SelectField(
        _l("Account Visibility"),
        description=_l(
            "Control whether accounts (users & teams) are shown to everyone, only to authenticated users, or only to admins"
        ),
        choices=[
            (AccountVisibilityTypes.PUBLIC, _l("Public")),
            (AccountVisibilityTypes.PRIVATE, _l("Private")),
            (AccountVisibilityTypes.ADMINS, _l("Admins Only")),
        ],
        default=AccountVisibilityTypes.PUBLIC,
    )
    score_visibility = SelectField(
        _l("Score Visibility"),
        description=_l(
            "Control whether solves/score are shown to the public, to logged in users, hidden to all non-admins, or only shown to admins"
        ),
        choices=[
            (ScoreVisibilityTypes.PUBLIC, _l("Public")),
            (ScoreVisibilityTypes.PRIVATE, _l("Private")),
            (ScoreVisibilityTypes.HIDDEN, _l("Hidden")),
            (ScoreVisibilityTypes.ADMINS, _l("Admins Only")),
        ],
        default=ScoreVisibilityTypes.PUBLIC,
    )
    registration_visibility = SelectField(
        _l("Registration Visibility"),
        description=_l(
            "Control whether registration is enabled for everyone or disabled"
        ),
        choices=[
            (RegistrationVisibilityTypes.PUBLIC, _l("Public")),
            (RegistrationVisibilityTypes.PRIVATE, _l("Private")),
            (RegistrationVisibilityTypes.MLC, _l("MajorLeagueCyber Only")),
        ],
        default=RegistrationVisibilityTypes.PUBLIC,
    )
