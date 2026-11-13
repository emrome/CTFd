from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    ConfigTypes,
    RegistrationVisibilityTypes,
    ScoreVisibilityTypes,
)
from CTFd.utils import get_config
from CTFd.utils.dates import ctf_ended, ctftime, view_after_ctf
from CTFd.utils.user import authed, is_admin


def challenges_visible():
    v = get_config(ConfigTypes.CHALLENGE_VISIBILITY)
    if v == ChallengeVisibilityTypes.PUBLIC:
        return True
    elif v == ChallengeVisibilityTypes.PRIVATE:
        return authed()
    elif v == ChallengeVisibilityTypes.ADMINS:
        return is_admin()


def challenges_reachable():
    """
    Whether the challenge visibility and the competition dates let the current
    visitor into the challenges page right now, as the challenges listing checks.
    The listing may still send them elsewhere first (to pick a team, confirm their
    email or complete their profile).
    """
    if is_admin():
        return True
    if not challenges_visible():
        return False
    if ctftime():
        return True
    return ctf_ended() and view_after_ctf()


def scores_visible():
    v = get_config(ConfigTypes.SCORE_VISIBILITY)
    if v == ScoreVisibilityTypes.PUBLIC:
        return True
    elif v == ScoreVisibilityTypes.PRIVATE:
        return authed()
    elif v == ScoreVisibilityTypes.HIDDEN:
        return False
    elif v == ScoreVisibilityTypes.ADMINS:
        return is_admin()


def scoreboard_reachable():
    """
    Whether the scoreboard page opens for the current visitor: it checks both the
    score visibility and the account visibility, as the scoreboard listing does.
    """
    if is_admin():
        return True
    return bool(scores_visible() and accounts_visible())


def accounts_visible():
    v = get_config(ConfigTypes.ACCOUNT_VISIBILITY)
    if v == AccountVisibilityTypes.PUBLIC:
        return True
    elif v == AccountVisibilityTypes.PRIVATE:
        return authed()
    elif v == AccountVisibilityTypes.ADMINS:
        return is_admin()


def registration_visible():
    v = get_config(ConfigTypes.REGISTRATION_VISIBILITY)
    if v == RegistrationVisibilityTypes.PUBLIC:
        return True
    elif v == RegistrationVisibilityTypes.PRIVATE:
        return False
    else:
        return False
