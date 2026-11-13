# Banco de desafíos

Plugin de CTFd que permite a administradores y autores elegir desafíos de un
repositorio y agregarlos a la competencia desde el panel de administración, sin
usar la línea de comandos.

## Uso

1. Entrar al panel de administración y abrir **Banco de desafíos** en la barra superior.
2. Filtrar por categoría, nivel, dimensión CIA, habilidad o texto (busca en el
   nombre, las etiquetas y la metadata pedagógica) y marcar los desafíos.
3. Pulsar **Importar seleccionados**.

Opciones:

- **Agregar también los desafíos que son requisito de los elegidos**: si un desafío
  requiere otros (campo `requirements`), se importan también, para que el desafío
  elegido sea alcanzable.
- **Importarlos ocultos**: los desafíos quedan en estado `hidden` para revisarlos
  antes de publicarlos.

Los desafíos que ya existen en la instancia (mismo nombre) aparecen como
"ya importado" y no se duplican.

### Requisitos

Los nombres de `requirements` se buscan entre **todos** los desafíos de la
instancia, no solo entre los que se importan en ese momento. Además, cuando se
importa un desafío que otro desafío del banco ya importado nombra como requisito,
el enlace se agrega en ese momento (sin quitar requisitos que se hayan cambiado a
mano en CTFd).

Si al importar un desafío alguno de sus requisitos no existe en la instancia, el
desafío se importa igual y se muestra un aviso destacado: hasta que se importe el
requisito, el desafío queda disponible sin él. Si el requisito está en el banco,
se enlaza solo cuando se lo importe; si no está ni en el banco ni en la instancia,
hay que corregir el nombre en el `challenge.yml` o agregar el requisito a mano.

Los desafíos se reconocen por su nombre. Si en la instancia hay más de un desafío
con el mismo nombre, el banco no le agrega requisitos a ninguno, porque no puede
saber cuál vino del banco. Si un requisito se importa oculto, los desafíos que
dependen de él tampoco se ven hasta que se lo haga visible, y el banco lo avisa.
El listado también avisa cuando los requisitos forman un ciclo (A pide B y B pide
A), porque esos desafíos quedarían bloqueados para siempre.

Si hay requisitos que comparten todos los demás desafíos del banco (por ejemplo,
un desafío de bienvenida), el listado los nombra una vez arriba de la tabla en
lugar de repetirlos en cada fila.

### Validación

El listado marca cada desafío con:

- **Errores** (no se puede importar hasta corregirlos): falta `name`, no hay
  `flags`, `type` distinto de `standard` o `dynamic`, `value` que no es un número
  entero, `state` distinto de `visible` o `hidden` (por ejemplo, `"visible "` con un
  espacio), archivos de `files` que no existen, `challenge.yml` que no se puede
  leer, y flags mal escritas: claves distintas de `type`, `content` y `data` (por
  ejemplo `data:"case_insensitive"` sin espacio después de los dos puntos, que YAML
  lee como una clave), `type` distinto de `static` o `regex`, `data` distinto de
  `case_insensitive` o vacío, o flags sin `content`.
- **Avisos** (se puede importar): requisitos que no están ni en el banco ni en la
  instancia, y un bloque `pedagogy` mal formado o con claves desconocidas.

## Formato del banco

El banco es un directorio con una carpeta por desafío. Cada carpeta contiene un
`challenge.yml` en el formato de [ctfcli](https://github.com/CTFd/ctfcli) y los
archivos que el desafío entrega:

```
banco/
  osint/
    el_viaje_de_sofi/
      challenge.yml
      foto.jpg
  criptografia/
    ...
```

Campos que se importan: `name`, `category`, `description`, `value`, `type`
(`standard` o `dynamic`, con `extra` para los dinámicos), `attempts`,
`connection_info`, `flags`, `tags`, `hints`, `files`, `requirements` (por nombre)
y `state`.

El nivel se toma de las etiquetas. Se reconocen
`nivel: introductorio|fácil|medio|avanzado` y también
`Introductorio|Basico|Intermedio|Avanzado`, que es la convención de `ctfcli.py`
(`introduccion` y `dificil` también se aceptan, como `introductorio` y `avanzado`).
Los acentos y las mayúsculas no importan.

### Metadata pedagógica

Cada `challenge.yml` puede tener un bloque opcional `pedagogy` con la información
para docentes. Todas las claves son opcionales:

```yaml
pedagogy:
  concept: "Exposición de información en redes sociales"
  challenge_type: "Análisis de perfil público"
  cia_dimension: "Confidencialidad / Integridad"
  skill: "Observación y búsqueda"
```

- `concept`: concepto central que trabaja el desafío.
- `challenge_type`: tipo de desafío (qué hace quien juega).
- `cia_dimension`: dimensión de la tríada CIA (Confidencialidad, Integridad,
  Disponibilidad). Se pueden combinar separándolas con `/`, `,`, `;` o `y`; el
  filtro ofrece cada dimensión por separado.
- `skill`: tipo de habilidad que pone en juego. También se puede combinar
  (`"Observación, búsqueda y análisis básico"`); el filtro ofrece cada habilidad
  por separado.

Un valor vacío o `—` se toma como "no aplica". El banco muestra estos datos debajo
del nombre de cada desafío y permite filtrar por dimensión CIA y por habilidad;
la búsqueda por texto también encuentra el concepto. CTFd no guarda este bloque
al importar: solo se ve en el banco.

## Dónde poner el banco

Por defecto el plugin lee `CTFd/plugins/banco_desafios/banco/`. Hay dos formas de
cargarlo:

- Copiar o clonar ahí el repositorio de desafíos (por ejemplo, como submódulo de git).
  Si el repositorio es privado, en un servidor se lo puede clonar con una deploy key
  de solo lectura.
- Montarlo como volumen y apuntar la variable de entorno `BANCO_DESAFIOS_DIR` a ese
  directorio. En `docker-compose.yml`:

  ```yaml
  services:
    ctfd:
      environment:
        - BANCO_DESAFIOS_DIR=/opt/banco
      volumes:
        - ./banco:/opt/banco:ro
  ```

## Trabajo futuro: proponer desafíos al banco

Hoy el banco va en un solo sentido, del repositorio a la competencia: un desafío
creado desde el panel de CTFd queda solo en esa instancia. Para sumarlo al banco hay
que agregar su carpeta con el `challenge.yml` al repositorio de desafíos.

La idea a futuro es que funcione como un pull request: desde el panel, el autor envía
una propuesta con el `challenge.yml` (incluida la metadata pedagógica) y los archivos
generados a partir de su desafío. Quien mantiene el banco la revisa, pide cambios si
hace falta y, si la acepta, el desafío se suma al repositorio y queda disponible para
todas las instalaciones al actualizarlas. Así el banco sigue siendo material revisado
y los docentes pueden aportar sin usar git.

## Tests

```
pytest tests/banco_desafios
```
