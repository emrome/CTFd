import json

from CTFd.models import Users
from CTFd.plugins.metricas.calculo import (
    CLAVE_CONFIG,
    datos_competencia,
    leer_umbrales,
    validar_umbrales,
)
from CTFd.utils import get_config, set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_fail,
    gen_hint,
    gen_solve,
    gen_tag,
    gen_team,
    gen_unlock,
    gen_user,
    login_as_user,
    register_user,
)

BANCO = """name: Primero
category: OSINT
value: 20
flags:
- flag{a}
pedagogy:
  concept: Huella digital
  challenge_type: Búsqueda
  cia_dimension: Confidencialidad / Integridad
  skill: Observación y búsqueda
"""


def cliente_admin(app):
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as sess:
        sess["id"] = 1
        nonce = sess.get("nonce")
    return client, nonce


def test_metricas_por_desafio(tmpdir):
    carpeta = tmpdir.mkdir("osint").mkdir("primero")
    carpeta.join("challenge.yml").write_text(BANCO, encoding="utf-8")
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = str(tmpdir)
    with app.app_context():
        primero = gen_challenge(app.db, name="Primero", category="OSINT")
        gen_tag(app.db, primero.id, value="nivel: fácil")
        segundo = gen_challenge(app.db, name="Segundo", category="Cripto")
        segundo.requirements = {"prerequisites": [primero.id]}
        app.db.session.commit()
        pista = gen_hint(app.db, primero.id)
        ana = gen_user(app.db, name="ana", email="ana@examplectf.com")
        beto = gen_user(app.db, name="beto", email="beto@examplectf.com")
        oculta = gen_user(
            app.db, name="oculta", email="oculta@examplectf.com", hidden=True
        )

        gen_fail(app.db, user_id=ana.id, challenge_id=primero.id)
        gen_solve(app.db, user_id=ana.id, challenge_id=primero.id)
        gen_unlock(app.db, user_id=ana.id, target=pista.id)
        gen_fail(app.db, user_id=ana.id, challenge_id=segundo.id)
        gen_fail(app.db, user_id=beto.id, challenge_id=primero.id)
        gen_solve(app.db, user_id=oculta.id, challenge_id=primero.id)
        # Los envios del administrador no cuentan
        gen_solve(app.db, user_id=1, challenge_id=segundo.id)

        datos = datos_competencia()
        assert datos["evento"]["equipos"] == ["ana", "beto"]
        assert datos["evento"]["equipos_registrados"] == 2
        assert datos["evento"]["modo_equipos"] is False

        d1, d2 = datos["desafios"]
        assert d1["origen"] == "banco" and d1["nivel"] == "Fácil"
        assert d1["cia"] == ["Confidencialidad", "Integridad"]
        assert d1["habilidad"] == ["Observación", "Búsqueda"]
        assert sorted(d1["acceso"]) == ["ana", "beto"]
        assert d1["por_equipo"]["ana"] == {
            "intentos": 2,
            "incorrectos": 1,
            "resuelto": True,
            "pistas": 1,
        }
        assert d1["por_equipo"]["beto"] == {
            "intentos": 1,
            "incorrectos": 1,
            "resuelto": False,
            "pistas": 0,
        }
        assert "oculta" not in d1["por_equipo"]

        # Solo ana resolvio el requisito del segundo desafio
        assert d2["origen"] == "otros" and d2["nivel"] is None
        assert d2["acceso"] == ["ana"] and d2["requisitos"] == 1
        assert d2["por_equipo"] == {
            "ana": {"intentos": 1, "incorrectos": 1, "resuelto": False, "pistas": 0}
        }
        assert [r["equipo"] for r in datos["resoluciones"]] == ["ana"]
    destroy_ctfd(app)


def test_metricas_modo_equipos():
    app = create_ctfd(user_mode="teams", enable_plugins=True)
    with app.app_context():
        reto = gen_challenge(app.db)
        rojo = gen_team(
            app.db, name="Rojo", email="rojo@examplectf.com", member_count=2
        )
        gen_team(app.db, name="Azul", email="azul@examplectf.com", member_count=1)
        integrante = rojo.members[1]
        gen_solve(app.db, user_id=integrante.id, team_id=rojo.id, challenge_id=reto.id)

        datos = datos_competencia()
        assert datos["evento"]["modo_equipos"] is True
        assert datos["evento"]["equipos"] == ["Rojo"]
        assert datos["evento"]["equipos_registrados"] == 2
        assert datos["desafios"][0]["por_equipo"]["Rojo"]["resuelto"] is True
    destroy_ctfd(app)


def test_vista_solo_admin_o_autor():
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/admin/metricas")
            assert r.status_code == 302
        register_user(app)
        client = login_as_user(app)
        assert client.get("/admin/metricas").status_code == 302

        client, _ = cliente_admin(app)
        r = client.get("/admin/metricas")
        html = r.get_data(as_text=True)
        assert r.status_code == 200
        assert "Métricas de aprendizaje" in html
        assert 'id="metricas-datos"' in html
    destroy_ctfd(app)


def test_vista_escapa_nombres():
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        reto = gen_challenge(app.db, name="</script><b>x</b>")
        alumno = gen_user(app.db, name="alumno", email="alumno@examplectf.com")
        gen_solve(app.db, user_id=alumno.id, challenge_id=reto.id)
        client, _ = cliente_admin(app)
        html = client.get("/admin/metricas").get_data(as_text=True)
        assert "</script><b>x</b>" not in html
        datos = html.split('id="metricas-datos" type="application/json">')[1].split(
            "</script>"
        )[0]
        assert json.loads(datos)["desafios"][0]["nombre"] == "</script><b>x</b>"
    destroy_ctfd(app)


def test_guardar_umbrales():
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        client, nonce = cliente_admin(app)
        valores = {
            "uTasa": "40",
            "uInc": "10",
            "uFacil": "85",
            "uMedio": "55",
            "uMin": "4",
        }
        r = client.post("/admin/metricas/umbrales", data=dict(valores, nonce=nonce))
        assert r.status_code == 302
        assert json.loads(get_config(CLAVE_CONFIG)) == {
            k: int(v) for k, v in valores.items()
        }
        assert leer_umbrales()["uFacil"] == 85

        r = client.post(
            "/admin/metricas/umbrales", data=dict(valores, uMedio="90", nonce=nonce)
        )
        assert r.status_code == 400
        assert leer_umbrales()["uMedio"] == 55

        # Sin nonce no se guarda nada
        r = client.post("/admin/metricas/umbrales", data=dict(valores, uTasa="10"))
        assert r.status_code == 403
        assert leer_umbrales()["uTasa"] == 40
    destroy_ctfd(app)


def test_umbrales_invalidos():
    assert validar_umbrales({"uTasa": "x"})[1]
    assert validar_umbrales(
        {"uTasa": "30", "uInc": "15", "uFacil": "80", "uMedio": "50", "uMin": "0"}
    )[1]
    umbrales, error = validar_umbrales(
        {"uTasa": "30", "uInc": "15", "uFacil": "80", "uMedio": "50", "uMin": "3"}
    )
    assert error is None and umbrales["uMin"] == 3

    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        set_config(CLAVE_CONFIG, "no es json")
        assert leer_umbrales() == {
            "uTasa": 30,
            "uInc": 15,
            "uFacil": 80,
            "uMedio": 50,
            "uMin": 3,
        }
        set_config(CLAVE_CONFIG, json.dumps({"uTasa": 500, "uFacil": 40, "uMedio": 60}))
        assert leer_umbrales() == {
            "uTasa": 100,
            "uInc": 15,
            "uFacil": 80,
            "uMedio": 50,
            "uMin": 3,
        }
    destroy_ctfd(app)


def test_casos_borde():
    import datetime

    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        reto = gen_challenge(app.db, name="Reto")
        otro = gen_challenge(app.db, name="Otro")
        otro.requirements = {"prerequisites": [999]}  # desafio borrado
        gen_challenge(app.db, name="Oculto sin jugar", state="hidden")
        pista = gen_hint(app.db, reto.id)
        uno = gen_user(app.db, name="dup", email="dup1@examplectf.com")
        dos = gen_user(app.db, name="dup", email="dup2@examplectf.com")
        solo_pista = gen_user(app.db, name="pista", email="pista@examplectf.com")
        app.db.session.commit()

        gen_solve(app.db, user_id=uno.id, challenge_id=reto.id)
        gen_fail(app.db, user_id=dos.id, challenge_id=reto.id)
        gen_fail(app.db, user_id=solo_pista.id, challenge_id=otro.id)
        gen_unlock(app.db, user_id=solo_pista.id, target=pista.id)
        fin = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        set_config("end", int(fin.replace(tzinfo=datetime.timezone.utc).timestamp()))
        tarde = gen_solve(app.db, user_id=dos.id, challenge_id=otro.id)
        tarde.date = fin + datetime.timedelta(hours=1)
        app.db.session.commit()

        datos = datos_competencia()
        nombres = [d["nombre"] for d in datos["desafios"]]
        assert nombres == ["Reto", "Otro"]  # el oculto que nadie jugo no aparece

        r, o = datos["desafios"]
        # Los nombres repetidos no se mezclan
        assert r["por_equipo"]["dup (#{})".format(uno.id)]["resuelto"] is True
        assert r["por_equipo"]["dup (#{})".format(dos.id)]["resuelto"] is False
        # Quien solo desbloqueo una pista cuenta sus pistas, con 0 intentos
        assert r["por_equipo"]["pista"] == {
            "intentos": 0,
            "incorrectos": 0,
            "resuelto": False,
            "pistas": 1,
        }
        # El requisito borrado se ignora: todos tienen acceso
        assert o["requisitos"] == 0 and len(o["acceso"]) == 3
        # La resolucion despues del cierre no cuenta
        assert "dup (#{})".format(dos.id) not in o["por_equipo"]
        assert all(x["challenge"] != o["id"] for x in datos["resoluciones"])
    destroy_ctfd(app)


def test_autor_y_error_conserva_valores():
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        register_user(app, name="autora", email="autora@examplectf.com")
        autora = Users.query.filter_by(name="autora").first()
        autora.type = "author"
        app.db.session.commit()
        client = login_as_user(app, name="autora")
        assert client.get("/admin/metricas").status_code == 200

        client, nonce = cliente_admin(app)
        r = client.post(
            "/admin/metricas/umbrales",
            data={
                "uTasa": "30",
                "uInc": "15",
                "uFacil": "40",
                "uMedio": "60",
                "uMin": "3",
                "nonce": nonce,
            },
        )
        html = r.get_data(as_text=True)
        assert r.status_code == 400
        assert 'value="40"' in html and 'value="60"' in html
        assert 'class="border p-3 mb-3" id="umbrales"' in html
    destroy_ctfd(app)
