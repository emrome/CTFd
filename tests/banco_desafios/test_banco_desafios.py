import os
import re
import warnings

from CTFd.cache import clear_user_session
from CTFd.models import ChallengeFiles, Challenges, Flags, Hints, Tags, Users, db
from CTFd.plugins import banco_desafios
from CTFd.plugins.banco_desafios.banco import (
    cargar_banco,
    nivel_desde_tags,
    opciones_filtro,
    requisitos_en_ciclo,
    requisitos_universales,
    separar,
)
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
    assert nivel_desde_tags(["nivel: introductorio"]) == "introductorio"
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
            assert "Imported 2 challenges" in html
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
            assert "already imported" in r.get_data(as_text=True)
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


def cliente_admin(app):
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as sess:
        sess["id"] = 1
    return client


def importar_http(client, ids, requisitos=False):
    with client.session_transaction() as sess:
        nonce = sess.get("nonce")
    data = {"desafio": ids, "nonce": nonce}
    if requisitos:
        data["requisitos"] = "y"
    r = client.post("/admin/banco", data=data)
    assert r.status_code == 200
    return r.get_data(as_text=True)


def prerequisitos(nombre):
    challenge = Challenges.query.filter_by(name=nombre).first()
    return (challenge.requirements or {}).get("prerequisites", [])


def test_requisito_importado_despues_se_enlaza(tmpdir):
    """El desafio se importa sin su requisito y el requisito llega despues."""
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = crear_banco(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        html = importar_http(client, ["osint/segundo"], requisitos=False)
        assert "Imported 1 challenge: Segundo" in html
        assert '<div class="alert alert-warning">' in html
        assert "which was not imported" in html
        assert prerequisitos("Segundo") == []

        html = importar_http(client, ["osint/primero"])
        primero = Challenges.query.filter_by(name="Primero").first()
        assert prerequisitos("Segundo") == [primero.id]
        assert '"Segundo" now requires "Primero"' in html

        # Importar otra vez no duplica el enlace
        importar_http(client, ["osint/primero", "osint/segundo"], requisitos=True)
        assert prerequisitos("Segundo") == [primero.id]
    destroy_ctfd(app)


def test_requisito_importado_antes_se_enlaza(tmpdir):
    """El requisito ya estaba en la instancia antes de importar el desafio."""
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = crear_banco(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        importar_http(client, ["osint/primero"])
        html = importar_http(client, ["osint/segundo"], requisitos=False)
        assert "Imported 1 challenge: Segundo" in html
        primero = Challenges.query.filter_by(name="Primero").first()
        assert prerequisitos("Segundo") == [primero.id]
        assert "which was not imported" not in html
    destroy_ctfd(app)


def test_requisito_inexistente_avisa(tmpdir):
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = crear_banco(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        html = client.get("/admin/banco").get_data(as_text=True)
        assert "has warnings" in html
        assert (
            "requires &#34;Fuera del banco&#34;, which is neither in the bank nor"
            " in this instance" in html
        )

        html = importar_http(client, ["osint/segundo"], requisitos=True)
        assert '<div class="alert alert-warning">' in html
        assert "Prerequisites missing:" in html
        assert "which is neither in this instance nor in the bank" in html
        # El desafio se importa igual, con el requisito que si existe
        primero = Challenges.query.filter_by(name="Primero").first()
        assert prerequisitos("Segundo") == [primero.id]

        # Si el requisito aparece en la instancia, el aviso del listado desaparece
        db.session.add(Challenges(name="Fuera del banco", value=1, state="visible"))
        db.session.commit()
        html = client.get("/admin/banco").get_data(as_text=True)
        assert "which is neither in the bank nor in this instance" not in html
    destroy_ctfd(app)


DESAFIO_MAL = """name: Mal escrito
category: Phishing
value: 20
state: "visible "
flags:
  - { type: "static", content: "flag{a}", data:"case_insensitive"}
  - { type: "static", content: "flag{b}", data: "mayusculas" }
  - { type: "otro", content: "flag{c}" }
  - { type: "regex", content: "flag{d.*}", data: "case_insensitive" }
  - flag{e}
  - { type: "static" }
"""


def test_validacion_flags_y_estado(tmpdir):
    d = tmpdir.mkdir("phishing").mkdir("mal")
    d.join("challenge.yml").write_text(DESAFIO_MAL, encoding="utf-8")
    desafio = cargar_banco(str(tmpdir))[0]
    errores = desafio.errores()
    assert 'invalid state "visible " (use visible or hidden)' in errores
    assert (
        'flag 1 has an unknown key "data:"case_insensitive"" '
        '(missing space after ":"?)' in errores
    )
    assert (
        'flag 2 has an invalid data value "mayusculas" '
        "(use case_insensitive or leave it empty)" in errores
    )
    assert 'flag 3 has an unknown type "otro"' in errores
    assert "flag 6 has no content" in errores
    assert len(errores) == 5

    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = str(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        html = client.get("/admin/banco").get_data(as_text=True)
        assert "has errors" in html
        assert 'value="phishing/mal" disabled' in html
        assert "missing space after" in html

        html = importar_http(client, ["phishing/mal"])
        assert "Not imported:" in html
        assert Challenges.query.count() == 0
    destroy_ctfd(app)


def test_validacion_otros_errores(tmpdir):
    for carpeta, contenido in {
        "tipo": "name: Tipo\nvalue: 1\ntype: docker\nflags: [x]\n",
        "valor": "name: Valor\nvalue: veinte\nflags: [x]\n",
        "archivo": "name: Archivo\nvalue: 1\nflags: [x]\nfiles: [no.txt]\n",
        "roto": "name: [sin cerrar\n",
    }.items():
        tmpdir.mkdir(carpeta).join("challenge.yml").write_text(
            contenido, encoding="utf-8"
        )
    errores = {d.id: d.errores() for d in cargar_banco(str(tmpdir))}
    assert errores["tipo"] == ["unsupported type: docker"]
    assert errores["valor"] == ["value must be a whole number: veinte"]
    assert errores["archivo"] == ["missing file no.txt"]
    assert errores["roto"][0].startswith("cannot read challenge.yml")


def test_importar_flags_sin_aviso_de_sqlalchemy(tmpdir):
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = crear_banco(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        with warnings.catch_warnings(record=True) as avisos:
            warnings.simplefilter("always")
            importar_http(client, ["osint/primero", "osint/segundo"])
        assert not [a for a in avisos if "polymorphic" in str(a.message)]
        assert [(f.type, f.content, f.data) for f in Flags.query.all()] == [
            ("static", "flag{a}", "case_insensitive"),
            ("static", "flag{b}", ""),
        ]
    destroy_ctfd(app)


PEDAGOGIA = {
    "uno": """name: Uno
category: OSINT
value: 10
flags: ["flag{1}"]
tags: ['nivel: fácil']
pedagogy:
  concept: "Exposición de información en redes sociales"
  challenge_type: "Análisis de perfil público"
  cia_dimension: "Confidencialidad / Integridad"
  skill: "Observación"
""",
    "dos": """name: Dos
category: OSINT
value: 10
flags: ["flag{2}"]
pedagogy:
  cia_dimension: "integridad"
  skill: "Análisis crítico y observación"
""",
    "tres": """name: Tres
category: OSINT
value: 10
flags: ["flag{3}"]
pedagogy:
  concept: "Dinámica CTF"
  cia_dimension: "—"
""",
    "cuatro": """name: Cuatro
category: OSINT
value: 10
flags: ["flag{4}"]
pedagogy: "texto suelto"
""",
}


def crear_banco_pedagogia(tmpdir):
    for carpeta, contenido in PEDAGOGIA.items():
        tmpdir.mkdir(carpeta).join("challenge.yml").write_text(
            contenido, encoding="utf-8"
        )
    return {d.id: d for d in cargar_banco(str(tmpdir))}


def test_pedagogia_parseo(tmpdir):
    banco = crear_banco_pedagogia(tmpdir)
    assert banco["uno"].pedagogia == {
        "concept": "Exposición de información en redes sociales",
        "challenge_type": "Análisis de perfil público",
        "cia_dimension": "Confidencialidad / Integridad",
        "skill": "Observación",
    }
    assert banco["uno"].dimensiones_cia == ["Confidencialidad", "Integridad"]
    assert banco["uno"].claves_cia == ["confidencialidad", "integridad"]
    assert banco["dos"].pedagogia["concept"] == ""
    assert banco["tres"].pedagogia["cia_dimension"] == ""
    assert banco["tres"].dimensiones_cia == []
    assert banco["cuatro"].pedagogia == {
        "concept": "",
        "challenge_type": "",
        "cia_dimension": "",
        "skill": "",
    }
    assert banco["cuatro"].avisos() == [
        "the pedagogy block is not a mapping; it is ignored"
    ]
    assert banco["cuatro"].errores() == []
    assert separar("Confidencialidad y Disponibilidad") == [
        "Confidencialidad",
        "Disponibilidad",
    ]
    assert separar("Integridad;confidencialidad;integridad") == [
        "Integridad",
        "Confidencialidad",
    ]
    assert separar("Observación, búsqueda y análisis básico") == [
        "Observación",
        "Búsqueda",
        "Análisis básico",
    ]
    assert opciones_filtro(c for d in banco.values() for c in d.dimensiones_cia) == [
        ("confidencialidad", "Confidencialidad"),
        ("integridad", "Integridad"),
    ]
    assert "dinámica ctf" in banco["tres"].texto_busqueda


def test_pedagogia_en_listado_y_filtros(tmpdir):
    crear_banco_pedagogia(tmpdir)
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = str(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        html = client.get("/admin/banco").get_data(as_text=True)
        assert 'id="filtro-cia"' in html
        assert '<option value="confidencialidad">Confidencialidad</option>' in html
        assert '<option value="integridad">Integridad</option>' in html
        assert 'id="filtro-habilidad"' in html
        assert '<option value="analisis critico">Análisis crítico</option>' in html
        assert '<option value="observacion">Observación</option>' in html
        assert 'data-cia="confidencialidad|integridad"' in html
        assert 'data-habilidad="observacion"' in html
        assert 'data-habilidad="analisis critico|observacion"' in html
        assert "exposición de información en redes sociales" in html  # data-texto
        assert "<strong>Concept:</strong> Exposición de información" in html
        assert "<strong>CIA dimension:</strong> Confidencialidad / Integridad" in html
        assert "<strong>Skill:</strong> Observación" in html
        assert "<strong>Challenge type:</strong> Análisis de perfil público" in html
        assert "Search by name, tag or concept" in html

        # En espanol
        Users.query.filter_by(id=1).first().language = "es"
        db.session.commit()
        clear_user_session(user_id=1)
        html = client.get("/admin/banco").get_data(as_text=True)
        assert "<strong>Concepto:</strong>" in html
        assert "<strong>Dimensión CIA:</strong>" in html
        assert "Todas las dimensiones CIA" in html
    destroy_ctfd(app)


def test_listado_sin_pedagogia_no_muestra_filtros_vacios(tmpdir):
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = crear_banco(tmpdir)
    with app.app_context():
        html = cliente_admin(app).get("/admin/banco").get_data(as_text=True)
        assert 'id="filtro-cia"' not in html
        assert 'id="filtro-habilidad"' not in html
        assert 'class="d-block text-muted pedagogia"' not in html
    destroy_ctfd(app)


def test_requisitos_universales_se_muestran_una_vez(tmpdir):
    banco = {
        "bienvenida": "name: Bienvenida\nvalue: 1\nflags: [x]\n",
        "a": "name: A\nvalue: 1\nflags: [x]\nrequirements: [Bienvenida]\n",
        "b": "name: B\nvalue: 1\nflags: [x]\nrequirements: [Bienvenida, A]\n",
        # Solo la requiere a traves de A
        "c": "name: C\nvalue: 1\nflags: [x]\nrequirements: [A]\n",
    }
    for carpeta, contenido in banco.items():
        tmpdir.mkdir(carpeta).join("challenge.yml").write_text(
            contenido, encoding="utf-8"
        )
    desafios = cargar_banco(str(tmpdir))
    assert requisitos_universales(desafios) == ["Bienvenida"]
    assert requisitos_universales(desafios[:2]) == []

    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = str(tmpdir)
    with app.app_context():
        html = cliente_admin(app).get("/admin/banco").get_data(as_text=True)
        assert "Every other challenge requires Bienvenida" in html
        celdas = re.findall(r"<td><small>(.*?)</small></td>", html)
        assert sorted(celdas) == ["", "", "A", "A"]
    destroy_ctfd(app)


def desafio_simple(nombre, requisitos=(), flag_type="static"):
    yml = (
        "name: {}\ncategory: Prueba\nvalue: 10\n"
        "flags:\n- type: {}\n  content: flag{{x}}\n"
    ).format(nombre, flag_type)
    if requisitos:
        yml += "requirements:\n" + "".join("- {}\n".format(r) for r in requisitos)
    return yml


def escribir(tmpdir, carpeta, yml):
    d = tmpdir.mkdir(carpeta)
    d.join("challenge.yml").write_text(yml, encoding="utf-8")


def test_requisito_oculto_avisa_que_bloquea(tmpdir):
    """Si el requisito llega oculto, se avisa que el desafio deja de verse."""
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = crear_banco(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        importar_http(client, ["osint/segundo"], requisitos=False)
        with client.session_transaction() as sess:
            nonce = sess.get("nonce")
        r = client.post(
            "/admin/banco",
            data={"desafio": ["osint/primero"], "nonce": nonce, "ocultos": "y"},
        )
        html = r.get_data(as_text=True)
        assert '"Segundo" now requires "Primero"' in html
        assert "which was imported hidden" in html
    destroy_ctfd(app)


def test_nombre_duplicado_no_se_enlaza(tmpdir):
    """Con dos desafios del mismo nombre no se elige uno al azar."""
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = crear_banco(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        importar_http(client, ["osint/segundo"], requisitos=False)
        db.session.add(Challenges(name="Segundo", category="x", value=1))
        db.session.commit()
        importar_http(client, ["osint/primero"])
        for c in Challenges.query.filter_by(name="Segundo").all():
            assert not (c.requirements or {}).get("prerequisites")
    destroy_ctfd(app)


def test_ciclo_y_autorrequisito_avisan(tmpdir):
    escribir(tmpdir, "a", desafio_simple("A", ["B"]))
    escribir(tmpdir, "b", desafio_simple("B", ["A"]))
    escribir(tmpdir, "c", desafio_simple("C", ["C"]))
    assert requisitos_en_ciclo(cargar_banco(str(tmpdir))) == {"A", "B"}
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = str(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        html = client.get("/admin/banco").get_data(as_text=True)
        assert "form a cycle" in html
        assert "lists itself as a prerequisite" in html
    destroy_ctfd(app)


def test_yml_raro_no_rompe_el_listado(tmpdir):
    escribir(tmpdir, "lista", desafio_simple("Lista", flag_type="[static]"))
    d = tmpdir.join("lista")
    d.join("challenge.yml").write_text(
        desafio_simple("Lista", flag_type="[static]") + "files: datos.txt\n",
        encoding="utf-8",
    )
    d.join("datos.txt").write("x")
    banco = cargar_banco(str(tmpdir))
    assert banco[0].archivos == [str(d.join("datos.txt"))]
    app = create_ctfd(enable_plugins=True)
    app.config["BANCO_DESAFIOS_DIR"] = str(tmpdir)
    with app.app_context():
        client = cliente_admin(app)
        r = client.get("/admin/banco")
        assert r.status_code == 200
        assert "unknown type" in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_banco_incluido_sin_errores():
    """Los desafios de la tesina vienen con el plugin y se pueden importar todos."""
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        banco = cargar_banco(
            os.path.join(os.path.dirname(banco_desafios.__file__), "banco")
        )
        assert len(banco) == 32
        nombres = [d.nombre for d in banco]
        assert len(set(nombres)) == len(nombres)
        en_ciclo = requisitos_en_ciclo(banco)
        for d in banco:
            assert d.errores() == [], d.nombre
            assert d.avisos(set(nombres), en_ciclo) == [], d.nombre
            assert d.nivel, d.nombre
    destroy_ctfd(app)
