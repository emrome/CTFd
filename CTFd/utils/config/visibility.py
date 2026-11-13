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
    Whether the challenges page would open for the current visitor right now: it
    combines the challenge visibility with the competition dates, as the
    challenges listing does.
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
