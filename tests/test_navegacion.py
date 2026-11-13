import time

from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_solve,
    login_as_user,
    register_user,
)

MENU_DESAFIOS = 'href="/challenges" class="menu-link"'
MENU_RANKING = 'href="/scoreboard" class="menu-link"'
BOTON_DESAFIOS = 'href="/challenges" class="btn'


def html(client, url):
    return client.get(url).get_data(as_text=True)


def test_menu_sin_sesion_no_muestra_desafios():
    """Without logging in, the challenges are private, so the menu leaves them out."""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "private")
        with app.test_client() as client:
            inicio = html(client, "/")
            assert MENU_DESAFIOS not in inicio
            assert MENU_RANKING in inicio
            # The 404 page does not offer a link that would fail too
            assert BOTON_DESAFIOS not in html(client, "/no-existe")

        set_config("challenge_visibility", "public")
        with app.test_client() as client:
            assert MENU_DESAFIOS in html(client, "/")
    destroy_ctfd(app)


def test_menu_con_sesion_sigue_las_fechas():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        inicio = html(client, "/")
        assert MENU_DESAFIOS in inicio
        assert BOTON_DESAFIOS in inicio

        # Once the competition is over the challenges page answers 403
        set_config("end", int(time.time()) - 60)
        assert client.get("/challenges").status_code == 403
        inicio = html(client, "/")
        assert MENU_DESAFIOS not in inicio
        assert BOTON_DESAFIOS not in inicio
        # The main button leads to the scoreboard instead
        assert 'href="/scoreboard" class="btn btn-primary btn-grande"' in inicio
        assert BOTON_DESAFIOS not in html(client, "/challenges")

        # Unless the challenges stay open after the end
        set_config("view_after_ctf", True)
        assert MENU_DESAFIOS in html(client, "/")
        set_config("view_after_ctf", False)

        # Before the start they cannot be opened either
        set_config("end", None)
        set_config("start", int(time.time()) + 3600)
        assert MENU_DESAFIOS not in html(client, "/")

        # With the scoreboard hidden, neither the link nor the button show up
        set_config("score_visibility", "hidden")
        inicio = html(client, "/")
        assert MENU_RANKING not in inicio
        assert "btn-primary btn-grande" not in inicio
    destroy_ctfd(app)


def test_menu_admin_siempre_ve_desafios():
    app = create_ctfd()
    with app.app_context():
        set_config("end", int(time.time()) - 60)
        client = login_as_user(app, name="admin", password="password")
        assert MENU_DESAFIOS in html(client, "/")
    destroy_ctfd(app)


def test_ranking_sigue_la_visibilidad_de_cuentas():
    """The scoreboard also needs the accounts to be visible."""
    app = create_ctfd()
    with app.app_context():
        set_config("account_visibility", "admins")
        register_user(app)
        client = login_as_user(app)
        assert client.get("/scoreboard").status_code == 404
        assert MENU_RANKING not in html(client, "/")

        # An admin can always open it, even with the scoreboard hidden
        set_config("score_visibility", "hidden")
        admin = login_as_user(app, name="admin", password="password")
        assert admin.get("/scoreboard").status_code == 200
        assert MENU_RANKING in html(admin, "/")
    destroy_ctfd(app)


def test_resueltos_sin_enlace_cuando_cerro():
    app = create_ctfd()
    with app.app_context():
        reto_id = gen_challenge(app.db, name="Reto").id
        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=reto_id)
        client = login_as_user(app)
        enlace = 'href="/challenges#Reto-{}"'.format(reto_id)
        assert enlace in html(client, "/user")

        set_config("end", int(time.time()) - 60)
        perfil = html(client, "/user")
        assert enlace not in perfil and "Reto" in perfil
    destroy_ctfd(app)
