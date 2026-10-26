"""
Translations for text that is rendered by JavaScript.

JavaScript can't call gettext, so every English string that a theme's JS shows
is listed in JS_STRINGS below. N_() only marks the string for `pybabel extract`
(N_ is one of Babel's default keywords); the catalogs translate it like any
other msgid.

How a theme uses it:

1. In the base template, before loading the theme's scripts:

       <script>
           window.CTFdTranslations = {{ get_js_translations()|tojson }};
       </script>

2. In JS, wrap the English text with the helper from
   CTFd/themes/core/assets/js/i18n.js (`import { t } from "core/i18n"` in
   webpack builds, or a copy of its few lines in other themes):

       t("Delete Users")
       t("Are you sure you want to delete {0} {1}?", count, target)

   t() returns the translation for the current locale, or the English text when
   there is none, and fills {0}, {1}... with the extra arguments.

3. Add any new string to JS_STRINGS, then run `make translations-extract`,
   `make translations-update`, translate it in each messages.po and run
   `make translations-compile`.
"""
import logging

from flask_babel import gettext

from CTFd.constants.languages import Languages

FALLBACK_LOCALE = Languages.SPANISH.value

log = logging.getLogger(__name__)


def normalize_locale(value):
    """
    Turn a locale setting like " es-AR" into one of the available Languages
    ("es"). Returns None when the value is empty or not available.
    """
    if value is None:
        return None
    value = str(value).strip().replace("-", "_")
    if not value:
        return None
    available = {str(lang).lower(): str(lang) for lang in Languages}
    if value.lower() in available:
        return available[value.lower()]
    # Fall back to the base language (es_AR -> es)
    return available.get(value.split("_")[0].lower())


def resolve_default_locale(value):
    """
    Validate the DEFAULT_LOCALE setting, warning and falling back to Spanish
    when it isn't an available language.
    """
    locale = normalize_locale(value)
    if locale is None:
        if value is not None and str(value).strip():
            log.warning(
                "DEFAULT_LOCALE %r is not an available language, using %r",
                value,
                FALLBACK_LOCALE,
            )
        return FALLBACK_LOCALE
    return locale


def N_(message):
    """Mark a string for extraction without translating it."""
    return message


JS_STRINGS = (
    # admin/assets/js/challenges/challenge.js
    N_("Solves"),
    # admin/assets/js/components/comments/CommentBox.vue
    N_("Add comment"),
    N_("Are you sure you'd like to delete this comment?"),
    N_("Close"),
    N_("Comment"),
    N_("Page {0} of {1} comments"),
    # admin/assets/js/components/configs/fields/Field.vue
    N_("Are you sure you'd like to delete this field?"),
    N_("Checkbox"),
    N_("Editable by user in profile"),
    N_("Field Description"),
    N_("Field Name"),
    N_("Field Type"),
    N_("Field has been created!"),
    N_("Field has been updated!"),
    N_("Field name"),
    N_("Required on registration"),
    N_("Save"),
    N_("Shown on public profile"),
    N_("Success"),
    N_("Text Field"),
    N_("Type of field shown to the user"),
    # admin/assets/js/components/configs/fields/FieldList.vue
    N_("Add New Field"),
    # admin/assets/js/components/files/ChallengeFilesList.vue
    N_("Are you sure you want to delete this file?"),
    N_("Attach multiple files using Control+Click or Cmd+Click."),
    N_("Delete Files"),
    N_("File"),
    N_("Settings"),
    N_("Upload"),
    # admin/assets/js/components/files/MediaLibrary.vue
    N_("Delete file"),
    N_("Download file"),
    N_("Insert"),
    N_("Insert link into editor"),
    N_("Link:"),
    N_("Media Details"),
    N_("Media Library"),
    N_("Upload Files"),
    # admin/assets/js/components/flags/FlagCreationForm.vue
    N_("Choose Flag Type"),
    N_("Create Flag"),
    # admin/assets/js/components/flags/FlagEditForm.vue
    N_("Edit Flag"),
    # admin/assets/js/components/flags/FlagList.vue
    N_("Are you sure you'd like to delete this flag?"),
    N_("Type"),
    # admin/assets/js/components/hints/HintCreationForm.vue
    N_("Cost"),
    N_("Hint"),
    N_("Hints that must be unlocked before unlocking this hint"),
    N_("How many points it costs to see your hint."),
    N_("Markdown & HTML are supported"),
    N_("Requirements"),
    N_("Submit"),
    # admin/assets/js/components/hints/HintsList.vue
    N_("Are you sure you want to delete this hint?"),
    N_("Create Hint"),
    N_("Delete Hint"),
    # admin/assets/js/components/next/NextChallenge.vue
    N_("Challenge to recommend after solving this challenge"),
    N_("Next Challenge"),
    # admin/assets/js/components/notifications/Notification.vue
    N_("Are you sure you want to delete this notification?"),
    # admin/assets/js/components/requirements/Requirements.vue
    N_("Anonymized"),
    N_("Behavior if not unlocked"),
    N_("Hidden"),
    # admin/assets/js/components/tags/TagsList.vue
    N_("Tag"),
    N_("Type tag and press Enter"),
    # admin/assets/js/components/teams/UserAddForm.vue
    N_("Add Users"),
    N_("Confirm Team Removal"),
    N_("No users found"),
    N_("Search Users"),
    N_("Search for users"),
    N_(
        "The following users are currently in teams:<br><br> {0} <br><br>Are you sure you want to remove them from their current teams and add them to this one? <br><br>All of their challenge solves, attempts, awards, and unlocked hints will also be deleted!"
    ),
    N_("already in a team"),
    # admin/assets/js/components/topics/TopicsList.vue
    N_("Topic"),
    N_("Type topic and press Enter"),
    # admin/assets/js/pages/challenge.js
    N_("Are you sure you want to delete {0}"),
    N_("Delete Challenge"),
    N_("Missing Flags"),
    N_(
        "This challenge does not have any flags meaning it may be unsolveable. Are you sure you'd like to update this challenge?"
    ),
    N_("Your challenge has been updated!"),
    N_("hidden"),
    N_("visible"),
    # admin/assets/js/pages/challenges.js
    N_("Are you sure you want to delete {0} {1}?"),
    N_("Category"),
    N_("Delete Challenges"),
    N_("Edit Challenges"),
    N_("State"),
    N_("Value"),
    N_("Visible"),
    N_("challenge"),
    N_("challenges"),
    # admin/assets/js/pages/configs.js
    N_("Are you sure you'd like to remove the CTF logo?"),
    N_("Are you sure you'd like to remove the small site icon?"),
    N_(
        "Are you sure you'd like to switch user modes?\n\nAll user submissions, awards, unlocks, and tracking will be deleted!"
    ),
    N_("Error!"),
    N_("Icon uploading failed!"),
    N_("Line {0}"),
    N_("Logo uploading failed!"),
    N_("Okay"),
    N_("Remove icon"),
    N_("Remove logo"),
    N_("Upload Progress"),
    # admin/assets/js/pages/editor.js
    N_("Saved"),
    N_("Your changes have been saved"),
    # admin/assets/js/pages/notifications.js
    N_("Could not send notification. Please try again."),
    # admin/assets/js/pages/pages.js
    N_("Delete Pages"),
    N_("page"),
    N_("pages"),
    # admin/assets/js/pages/reset.js
    N_("Are you sure you want to reset your CTFd instance?"),
    N_("Reset CTF?"),
    # admin/assets/js/pages/scoreboard.js
    N_("Toggle Visibility"),
    N_("Visibility"),
    # admin/assets/js/pages/statistics.js
    N_("Category Breakdown"),
    N_("Challenge Name"),
    N_("Fails"),
    N_("Number of Teams"),
    N_("Number of Users"),
    N_("Percentage of Teams (%)"),
    N_("Percentage of Users (%)"),
    N_("Score Bracket"),
    N_("Score Distribution"),
    N_("Solve Count"),
    N_("Solve Counts"),
    N_("Solve Percentages per Challenge"),
    N_("Submission Percentages"),
    # admin/assets/js/pages/submissions.js
    N_("Are you sure you want to delete correct submission from {0} for challenge {1}"),
    N_("Are you sure you want to mark 1 {0} correct?"),
    N_("Are you sure you want to mark {0} {1} correct?"),
    N_("Copied!"),
    N_("Delete Submission"),
    N_("Delete Submissions"),
    N_("Mark submissions correct"),
    N_("submission"),
    N_("submissions"),
    # admin/assets/js/pages/team.js
    N_("Are you sure you want to mark 1 {0} correct for {1}?"),
    N_("Are you sure you want to mark {0} {1} correct for {2}?"),
    N_(
        "Are you sure you want to remove {0} from {1}? <br><br><strong>All of their challenge solves, attempts, awards, and unlocked hints will also be deleted!</strong>"
    ),
    N_("Delete Awards"),
    N_("Delete Fails"),
    N_("Delete Solves"),
    N_("Delete Team"),
    N_("Mark Correct"),
    N_("Please select a team member"),
    N_("Remove Member"),
    N_("User Attribution"),
    N_("Which user on {0} solved these challenges?"),
    N_("award"),
    N_("awards"),
    N_("fail"),
    N_("fails"),
    N_("solve"),
    N_("solves"),
    # admin/assets/js/pages/teams.js
    N_("Banned"),
    N_("Delete Teams"),
    N_("Edit Teams"),
    N_("False"),
    N_("True"),
    N_("team"),
    N_("teams"),
    # admin/assets/js/pages/user.js
    N_("Delete User"),
    N_("E-Mail sent successfully!"),
    # admin/assets/js/pages/users.js
    N_("Delete Users"),
    N_("Edit Users"),
    N_("Verified"),
    N_("user"),
    N_("users"),
    # core/assets/js/graphs.js
    N_("Score over Time"),
    N_("Solve Percentages"),
    # core/assets/js/ezq.js
    N_("Yes"),
    N_("No"),
    # plugins/flags/assets (nunjucks templates rendered in the browser)
    N_("Accept flags with or without the flag format prefix:"),
    N_("Case Insensitive"),
    N_("Case Sensitive"),
    N_("Description"),
    N_("Enter regex flag data"),
    N_("Enter regex key data"),
    N_("Enter static flag data"),
    N_("Examples"),
    N_("Match any content inside of flag{}:"),
    N_("Match numeric flags:"),
    N_("Regex Flag"),
    N_("Static"),
    N_("Update"),
    # escuelas/assets/js (and Alpine expressions in escuelas templates)
    N_("You have no attempts left for this challenge."),
    N_("1 challenge"),
    N_("{0} challenges"),
    N_("Show"),
    N_("Hide"),
    N_("Do you want to see this hint? It will cost you points."),
    N_("Do you want to see this hint? It will cost you 1 point."),
    N_("Do you want to see this hint? It will cost you {0} points."),
    N_("The hint could not be opened. Try again."),
    N_("That is not the flag. Check the format and try again."),
    N_("You have 1 attempt left."),
    N_("You have {0} attempts left."),
    N_("You are going too fast. Wait a few seconds and try again."),
    N_("The competition is paused."),
    N_("You must be logged in to submit an answer."),
    N_("The answer could not be sent. Try again."),
    N_("Could not connect to the server. Try again."),
    N_("Attempts used: {0} of {1}"),
    N_("#{0}"),
    N_("of {0}"),
    N_("{0} pts"),
    N_("{0} of {1} solved"),
    N_("{0} locked"),
    N_("Basic"),
    N_("Intermediate"),
    N_("Advanced"),
    N_("Introductory"),
    N_("MMMM D, HH:mm"),
    N_("MM/DD HH:mm"),
    N_("Top 10 Teams"),
    N_("Top 10 Users"),
    N_("Save as image"),
    N_("Zoom"),
    N_("Undo zoom"),
    N_("Already Configured"),
    N_(
        "This image file is larger than {0} KB which may result in increased load times. Are you sure you'd like to use this file?"
    ),
)


def get_js_translations():
    """
    Return {msgid: translation} for the current locale, leaving out strings
    that are not translated (t() falls back to the msgid for those).
    """
    translations = {}
    for msgid in JS_STRINGS:
        translated = gettext(msgid)
        if translated != msgid:
            translations[msgid] = translated
    return translations
