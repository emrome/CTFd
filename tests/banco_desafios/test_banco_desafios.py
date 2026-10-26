from CTFd.models import ChallengeFiles, Challenges, Flags, Hints, Tags
from CTFd.plugins.banco_desafios.banco import cargar_banco, nivel_desde_tags
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user

DESAFIO_A = """name: Primero
category: OSINT
value: 20
flags:
- type: static
  content: flag{a}
  data: case_insensitive
tags:
- 'nivel: fácil'
hints:
- content: una pista
  cost: 5
files:
- datos.txt
"""

DESAFIO_B = """name: Segundo
category: OSINT
value: 50
flags:
- flag{b}
tags:
- Intermedio
requirements:
- Primero
- Fuera del banco
"""


def crear_banco(tmpdir):
    a = tmpdir.mkdir("osint").mkdir("primero")
    a.join("challenge.yml").write_text(DESAFIO_A, encoding="utf-8")
    a.join("datos.txt").write("contenido")
    b = tmpdir.join("osint").mkdir("segundo")
    b.join("challenge.yml").write_text(DESAFIO_B, encoding="utf-8")
    return str(tmpdir)


def test_nivel_desde_tags():
    assert nivel_desde_tags(["nivel: fácil"]) == "facil"
    assert nivel_desde_tags(["Basico"]) == "facil"
    assert nivel_desde_tags(["otra", "Intermedio"]) == "medio"
    assert nivel_desde_tags(["nivel: Avanzado"]) == "avanzado"
    assert nivel_desde_tags(["sin nivel"]) is None


def test_cargar_banco(tmpdir):
    banco = cargar_banco(crear_banco(tmpdir))
    assert [d.nombre for d in banco] == ["Primero", "Segundo"]
    assert banco[0].errores() == []
    assert banco[1].requisitos == ["Primero", "Fuera del banco"]


def test_importar_con_requisitos(tmpdir):
    raiz = crear_banco(tmpdir)
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = raiz
    with app.app_context():
        with app.test_client() as client:
            client.get("/login")
            with client.session_transaction() as sess:
                sess["id"] = 1
                nonce = sess.get("nonce")
            r = client.get("/admin/banco")
            assert r.status_code == 200
            assert "Segundo" in r.get_data(as_text=True)

            r = client.post(
                "/admin/banco",
                data={"desafio": ["osint/segundo"], "requisitos": "y", "nonce": nonce},
            )
            html = r.get_data(as_text=True)
            assert r.status_code == 200
            assert "Se importaron 2" in html
            assert "Fuera del banco" in html

        primero = Challenges.query.filter_by(name="Primero").first()
        segundo = Challenges.query.filter_by(name="Segundo").first()
        assert primero.value == 20 and segundo.value == 50
        assert segundo.requirements == {"prerequisites": [primero.id]}
        assert (
            Flags.query.filter_by(challenge_id=primero.id).first().data
            == "case_insensitive"
        )
        assert (
            Flags.query.filter_by(challenge_id=segundo.id).first().content == "flag{b}"
        )
        assert Hints.query.filter_by(challenge_id=primero.id).first().cost == 5
        assert (
            Tags.query.filter_by(challenge_id=primero.id).first().value
            == "nivel: fácil"
        )
        archivo = ChallengeFiles.query.filter_by(challenge_id=primero.id).first()
        assert archivo.location.endswith("datos.txt")

        # Volver a importar no duplica
        with app.test_client() as client:
            client.get("/login")
            with client.session_transaction() as sess:
                sess["id"] = 1
                nonce = sess.get("nonce")
            r = client.post(
                "/admin/banco",
                data={"desafio": ["osint/primero"], "nonce": nonce},
            )
            assert "ya importado" in r.get_data(as_text=True)
        assert Challenges.query.filter_by(name="Primero").count() == 1
    destroy_ctfd(app)


def test_usuario_comun_no_accede(tmpdir):
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = crear_banco(tmpdir)
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/admin/banco")
        assert r.status_code == 302
    destroy_ctfd(app)
