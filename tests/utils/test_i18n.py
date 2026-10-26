import logging

from CTFd.config import TestingConfig
from CTFd.models import Users, db
from CTFd.utils import set_config
from CTFd.utils.i18n import (
    JS_STRINGS,
    get_js_translations,
    normalize_locale,
    resolve_default_locale,
)
from tests.helpers import create_ctfd, destroy_ctfd, gen_award, gen_user, login_as_user


def use_translated_theme():
    # The core theme is not translated, core-beta is
    set_config("ctf_theme", "core-beta")


def set_admin_language(language):
    admin = Users.query.filter_by(name="admin").first()
    admin.language = language
    db.session.commit()


def test_js_translations_follow_the_locale():
    """get_js_translations returns only the strings translated in the locale"""
    app = create_ctfd()
    with app.app_context():
        with app.test_request_context():
            assert get_js_translations() == {}
        set_admin_language("es")
        with login_as_user(app, name="admin") as client:
            r = client.get("/admin/statistics")
            html = r.get_data(as_text=True)
            assert "Estadísticas" in html
            assert "window.CTFdTranslations" in html
            assert "Borrar usuarios" in html
        assert "Delete Users" in JS_STRINGS
    destroy_ctfd(app)


def test_admin_panel_in_english():
    """The admin panel is shown in English for an English admin"""
    app = create_ctfd()
    with app.app_context():
        set_admin_language("en")
        with login_as_user(app, name="admin") as client:
            r = client.get("/admin/config")
            html = r.get_data(as_text=True)
            assert "Configuration" in html
            assert "Configuración" not in html
            assert "window.CTFdTranslations = {};" in html
    destroy_ctfd(app)


class SpanishConfig(TestingConfig):
    DEFAULT_LOCALE = "es"
    BABEL_DEFAULT_LOCALE = "es"


class RegionalSpanishConfig(TestingConfig):
    DEFAULT_LOCALE = "es-AR"
    BABEL_DEFAULT_LOCALE = "es-AR"


class UnknownLocaleConfig(TestingConfig):
    DEFAULT_LOCALE = "xx"
    BABEL_DEFAULT_LOCALE = "xx"


def test_normalize_locale():
    """Locale names are matched against the available languages"""
    assert normalize_locale("es") == "es"
    assert normalize_locale(" es ") == "es"
    assert normalize_locale("es-AR") == "es"
    assert normalize_locale("es_ar") == "es"
    assert normalize_locale("EN") == "en"
    assert normalize_locale("pt-br") == "pt_BR"
    assert normalize_locale("zh-TW") == "zh_TW"
    assert normalize_locale("xx") is None
    assert normalize_locale("") is None
    assert normalize_locale(None) is None


def test_resolve_default_locale_falls_back_to_spanish(caplog):
    """An unknown DEFAULT_LOCALE falls back to Spanish with a warning"""
    with caplog.at_level(logging.WARNING, logger="CTFd.utils.i18n"):
        assert resolve_default_locale("xx") == "es"
    assert "xx" in caplog.text
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="CTFd.utils.i18n"):
        assert resolve_default_locale("es-AR") == "es"
        assert resolve_default_locale(None) == "es"
        assert resolve_default_locale("en") == "en"
    assert caplog.text == ""


def test_regional_default_locale_serves_pages():
    """DEFAULT_LOCALE=es-AR is served as Spanish instead of failing"""
    app = create_ctfd(config=RegionalSpanishConfig)
    with app.app_context():
        use_translated_theme()
        assert app.config["DEFAULT_LOCALE"] == "es"
        assert app.config["BABEL_DEFAULT_LOCALE"] == "es"
        with app.test_client() as client:
            r = client.get("/login")
            assert r.status_code == 200
            assert "Ingresar" in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_unknown_default_locale_serves_pages():
    """An unknown DEFAULT_LOCALE does not break every request"""
    app = create_ctfd(config=UnknownLocaleConfig)
    with app.app_context():
        assert app.config["DEFAULT_LOCALE"] == "es"
        with app.test_client() as client:
            assert client.get("/login").status_code == 200
            assert client.get("/scoreboard").status_code == 200
    destroy_ctfd(app)


def test_spanish_default_locale():
    """With DEFAULT_LOCALE=es pages and API messages are in Spanish"""
    app = create_ctfd(config=SpanishConfig)
    with app.app_context():
        use_translated_theme()
        set_admin_language(None)
        with app.test_client() as client:
            r = client.get("/login")
            assert "Ingresar" in r.get_data(as_text=True)
        with login_as_user(app, name="admin") as client:
            r = client.delete("/api/v1/users/1", json="")
            assert r.status_code == 400
            assert r.get_json()["errors"]["id"] == "No podés borrarte a vos mismo"
            r = client.get("/api/v1/challenges/1000")
            assert r.status_code == 404
            assert r.get_json()["message"].startswith("No se encontró la URL")
        with login_as_user(app, name="admin") as client:
            set_admin_language("en")
            r = client.delete("/api/v1/users/1", json="")
            assert r.get_json()["errors"]["id"] == "You cannot delete yourself"
    destroy_ctfd(app)


def test_scoreboard_header_follows_each_user_language():
    """The cached scoreboard rows do not freeze the header language"""
    app = create_ctfd()
    with app.app_context():
        use_translated_theme()
        user = gen_user(app.db, name="user1", email="user1@examplectf.com")
        user.language = "es"
        app.db.session.commit()
        gen_award(app.db, user_id=user.id)
        with login_as_user(app, name="user1") as client:
            html = client.get("/scoreboard").get_data(as_text=True)
            assert "Posición" in html
            assert "user1" in html
        with app.test_client() as client:
            html = client.get("/scoreboard").get_data(as_text=True)
            assert "Place" in html
            assert "Posición" not in html
            assert "user1" in html
    destroy_ctfd(app)
