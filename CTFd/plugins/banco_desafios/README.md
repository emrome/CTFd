# Banco de desafíos

Plugin de CTFd que permite a administradores y autores elegir desafíos de un
repositorio y agregarlos a la competencia desde el panel de administración, sin
usar la línea de comandos.

## Uso

1. Entrar al panel de administración y abrir **Banco de desafíos** en la barra superior.
2. Filtrar por categoría, nivel o texto y marcar los desafíos.
3. Pulsar **Importar seleccionados**.

Opciones:

- **Agregar también los desafíos que son requisito de los elegidos**: si un desafío
  requiere otros (campo `requirements`), se importan también, para que el desafío
  elegido sea alcanzable.
- **Importarlos ocultos**: los desafíos quedan en estado `hidden` para revisarlos
  antes de publicarlos.

Los desafíos que ya existen en la instancia (mismo nombre) aparecen como
"ya importado" y no se duplican.

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

El nivel se toma de las etiquetas. Se reconocen `nivel: fácil|medio|avanzado`
y también `Basico|Intermedio|Avanzado`, que es la convención de `ctfcli.py`.

## Dónde poner el banco

Por defecto el plugin lee `CTFd/plugins/banco_desafios/banco/`. Hay dos formas de
cargarlo:

- Copiar o clonar ahí el repositorio de desafíos (por ejemplo, como submódulo de git).
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

## Tests

```
pytest tests/banco_desafios
```
