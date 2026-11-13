
# ![](https://github.com/CTFd/CTFd/blob/master/CTFd/themes/core/static/img/logo.png?raw=true)

## Qué es CTFd?

CTFd es una herramienta desarrollada específicamente para la organización y ejecución de competiciones de CTF. Proporciona una interfaz fácil de usar que permite al administrador crear, administrar y distribuir desafíos de manera efectiva.

![CTFd is a CTF in a can.](https://github.com/CTFd/CTFd/blob/master/CTFd/themes/core/static/img/scoreboard.png?raw=true)

## Adaptación "CTF en escuelas secundarias"
Esta adaptación presenta una nueva versión de la herramienta *CTFd* orientada a la organización y gestión de competencias de ciberseguridad en las escuelas, promoviendo la autonomía y participación de los equipos escolares. Para ello se ofrecen nuevas funcionalidades.
- **Automatización de la carga de desafíos:** facilitando la carga masiva y organizada de desafíos por categoría de contenido y nivel de dificultad, mediante un script en Python que integra la herramienta ctfcli (ofrecida por CTFd).
- **Unirse a equipos:** se buscó simplificar la incorporación de estudiantes a equipos de la competencia sin necesidad de recordar el nombre del equipo, mediante un acceso directo en la tabla de equipos.
- **Rol Autor:** para poder cargar y gestionar desafíos sin necesidad de contar con privilegios administrativos en la plataforma, mediante un nuevo rol que cuenta con permisos específicos de acceso.
- **Repositorio base de desafíos:** para disponer de un punto de partida sobre contenidos de seguridad informática para facilitar la creación de la competencia en las escuelas. Esto mediante un acceso a un [repositorio público en GitHub](https://github.com/Bemyi/ctfd-challenges/).
- **Documentación:** Disponer de documentación simple sobre la configuración de la plataforma.

## CTF en escuelas secundarias 2.0
Esta versión continúa la adaptación anterior como parte de la tesina de grado *«Diseño e integración de contenidos/desafíos en la herramienta "CTF en escuelas secundarias 2.0". Aportes a la formación en Informática para jóvenes»*, de María Emilia Romero (Facultad de Informática, UNLP), dirigida por Claudia Queiruga y Paula Venosa. Suma:

- **Banco de desafíos** (`/admin/banco`): el administrador o el autor ve los desafíos disponibles en formato `challenge.yml` (ctfcli), los filtra por categoría, nivel, dimensión de seguridad (confidencialidad, integridad, disponibilidad) y habilidad, y los importa a la instancia con un clic, con sus flags, pistas, archivos y requisitos. Antes de importar, el banco valida cada desafío y avisa si hay errores. Ver [la documentación del plugin](CTFd/plugins/banco_desafios/README.md).
- **Desafíos de la tesina:** 32 desafíos de OSINT, ingeniería social, criptografía, phishing y contraseñas, organizados en cuatro niveles (introductorio, fácil, medio y avanzado) y probados en la jornada CTF Interescuelas del 11/11/2025. Están en el repositorio [emrome/ctf-challenges](https://github.com/emrome/ctf-challenges), bajo licencia CC BY-SA 4.0. Ese repositorio es privado porque incluye las flags; para usarlos hay que pedirle acceso a la autora. Cada desafío incluye metadata pedagógica (concepto central, tipo de desafío, dimensión de seguridad y habilidad) que solo ven el administrador y el autor en el banco; los estudiantes no la ven.
- **Herramienta en español:** toda la interfaz, incluido el panel de administración, está traducida. El idioma por defecto es español (`DEFAULT_LOCALE`) y cada usuario puede elegir inglés.
- **Nueva interfaz "escuelas":** un tema pensado para estudiantes de secundaria, que es el tema por defecto y se puede cambiar desde Admin → Configuración → Tema.

## Créditos y licencia
- [CTFd](https://github.com/CTFd/CTFd), de CTFd LLC, es la plataforma de base (versión 3.6.1).
- La adaptación "CTF en escuelas secundarias" (rol autor, carga de desafíos, unirse a equipos) es de Benjamín Freccero Starnari, como parte de su tesina *«Una plataforma libre y personalizable para "CTF en escuelas secundarias"»* ([Bemyi/CTFd](https://github.com/Bemyi/CTFd)).
- Este repositorio modifica el código original de CTFd y se distribuye, como él, bajo la [licencia Apache 2.0](LICENSE).
- Los desafíos del repositorio [emrome/ctf-challenges](https://github.com/emrome/ctf-challenges) se publican bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es).

## Instalación

Prerrequisitos:

 - La PC debe contar con [Docker](https://www.docker.com/) instalado.
 - Preferentemente utilizar sistema operativo Linux.
 - Tener instalado [Python 3](https://www.python.org/downloads/) >= 3.10.
 - Tener instalado [pip](https://pypi.org/project/pip/).

Una vez clonado el repositorio, nos colocamos en el directorio raíz de la plataforma y ejecutamos el siguiente comando:

`docker-compose up`

Para tener los desafíos de la tesina en el banco, cloná el repositorio de desafíos dentro de la carpeta del banco. Es privado para que los estudiantes no encuentren las flags, así que hace falta una cuenta de GitHub con acceso (se le pide a la autora). Con una clave SSH cargada en esa cuenta:

`git clone git@github.com:emrome/ctf-challenges.git CTFd/plugins/banco_desafios/banco/ctf-challenges`

Por HTTPS, GitHub pide un token de acceso personal en lugar de la contraseña.

En un servidor conviene usar una [deploy key](https://docs.github.com/es/authentication/connecting-to-github-with-ssh/managing-deploy-keys#deploy-keys), que da acceso de solo lectura a ese repositorio y a ningún otro: se genera un par de claves en el servidor (`ssh-keygen -t ed25519`), se le manda la clave pública a la autora para que la agregue al repositorio como deploy key de solo lectura, y se clona con el mismo comando de arriba.

Para actualizar el banco alcanza con `git pull` dentro de esa carpeta. Con el `docker-compose.yml` incluido no hace falta reiniciar CTFd, porque la carpeta del proyecto se monta en el contenedor y el banco se lee cada vez que se abre. Si la imagen se construye sin ese montaje, los desafíos quedan copiados adentro de la imagen y hay que reconstruirla.

También se puede usar otra carpeta con la variable `BANCO_DESAFIOS_DIR`, como explica [la documentación del plugin](CTFd/plugins/banco_desafios/README.md).

Para continuar con la instalación te recomendamos seguir la guía realizada para instanciación de [CTF en escuelas secundarias](https://docs.google.com/document/d/1tBe47xcGkL5nekVN6Vl18kCik0Pmn6ZIODSYpaBsLFQ/edit?tab=t.0#heading=h.yq18kulgr7bh).
