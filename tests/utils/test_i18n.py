from CTFd.models import Users, db
from CTFd.utils.i18n import JS_STRINGS, get_js_translations
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user


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
