# CTF en Escuelas Secundarias

Desafíos tipo **Capture The Flag (CTF)** para la enseñanza introductoria de ciberseguridad en escuelas secundarias.

Este repositorio reúne desafíos diseñados para trabajar conceptos de seguridad digital a través de actividades prácticas, progresivas y contextualizadas. Cada desafío propone una situación simulada que los estudiantes deben analizar para encontrar una **flag** y resolver el reto.

---

## Sobre este repositorio

Este repositorio contiene **32 desafíos** organizados por categoría y nivel de dificultad, diseñados en el contexto del proyecto de extensión **“Extensión en vínculo con escuelas secundarias”** de la Facultad de Informática de la Universidad Nacional de La Plata (UNLP).

Los desafíos fueron pensados para actividades de formación y concientización en seguridad digital con estudiantes de nivel secundario. Su objetivo no es formar especialistas técnicos en ciberseguridad, sino acercar conceptos fundamentales mediante experiencias de aprendizaje accesibles, lúdicas y orientadas a la reflexión.

---

## Objetivo educativo

El objetivo del repositorio es ofrecer un banco inicial de desafíos CTF que permita:

- introducir conceptos fundamentales de ciberseguridad;
- fomentar la observación crítica y el razonamiento lógico;
- concientizar sobre buenas y malas prácticas de seguridad digital;
- promover el aprendizaje basado en desafíos;
- trabajar problemáticas cercanas a la vida digital cotidiana de los estudiantes;
- acompañar actividades educativas, talleres o jornadas CTF en escuelas secundarias.

---

## Estructura del repositorio

```text
├── introduccion/
├── autenticacion/
│   └── contrasenas/
├── fraude/
│   └── phishing/
├── osint/
├── criptografia/
├── ingenieria-social/
└── docs/
    └── descripcion-desafios.pdf
```

Las carpetas reflejan las categorías y subcategorías conceptuales utilizadas en el diseño pedagógico de los desafíos.

Cada desafío puede incluir, según corresponda:

- consigna;
- archivos necesarios para resolverlo;
- pistas;
- flag;
- configuración para CTFd;
- materiales complementarios;
- descripción pedagógica.

---

## Categorías

| Categoría | Cantidad de desafíos | Niveles | Conceptos principales |
|---|---:|---|---|
| **Introducción** | 1 | Introductorio | Dinámica CTF, formato de flags |
| **Contraseñas** | 7 | Fácil a Avanzado | Contraseñas débiles, patrones, reutilización, exposición de credenciales |
| **Phishing** | 6 | Fácil a Avanzado | Suplantación, dominios falsos, quishing, mensajes fraudulentos |
| **OSINT** | 7 | Fácil a Avanzado | Huella digital, geolocalización, metadatos, correlación de fuentes |
| **Criptografía** | 8 | Fácil a Avanzado | Cifrado clásico, codificación, representación binaria, integridad |
| **Ingeniería Social** | 3 | Fácil a Avanzado | Urgencia, autoridad, manipulación, identidades falsas, acceso físico |

Ver tabla completa con puntajes y metadatos en [`DESAFIOS.md`](./DESAFIOS.md).

---

## Niveles de dificultad

Los desafíos están organizados en niveles de dificultad progresiva:

| Nivel | Descripción |
|---|---|
| **Introductorio** | Presenta la dinámica del CTF y permite practicar el formato de respuesta. |
| **Fácil** | Requiere observación, lectura atenta o razonamientos simples. |
| **Medio** | Requiere combinar información, analizar más de una fuente o utilizar herramientas básicas. |
| **Avanzado** | Requiere mayor autonomía, correlación de datos, razonamiento abstracto o análisis técnico más elaborado. |

---

## Enfoque pedagógico

Los desafíos no están pensados únicamente como ejercicios técnicos, sino como recursos didácticos.

Cada reto busca trabajar un concepto de ciberseguridad a partir de una situación concreta, por ejemplo:

- una contraseña expuesta o predecible;
- un correo fraudulento;
- una imagen que revela información sensible;
- un código QR sospechoso;
- un mensaje codificado o cifrado;
- una identidad digital construida para generar confianza.

Se recomienda acompañar la resolución con una instancia de reflexión posterior que permita conectar el desafío con situaciones reales de seguridad digital.

Algunas preguntas posibles para esa instancia son:

- ¿Qué riesgo aparece en este desafío?
- ¿Qué información permitió resolverlo?
- ¿Qué práctica insegura se observa?
- ¿Cómo podría prevenirse en una situación real?
- ¿Qué decisión tomarías distinto después de resolverlo?

---

## Documentación

La descripción pedagógica completa de cada desafío se encuentra en:

[`docs/descripcion-desafios.pdf`](./docs/descripcion-desafios.pdf)

Allí se detallan los objetivos pedagógicos, las descripciones de los desafíos y los aprendizajes esperados.

---

## Metadatos pedagógicos en `challenge.yml`

Además de los campos que usa CTFd (`name`, `category`, `value`, `flags`, `hints`, etc.), cada `challenge.yml` termina con un bloque `pedagogy` que resume la clasificación pedagógica del desafío. Los valores salen del catálogo de desafíos de la tesina (el mismo que resume [`DESAFIOS.md`](./DESAFIOS.md)):

```yaml
pedagogy:
  concept: "Exposición física de credenciales"
  challenge_type: "Observación de evidencia visual"
  cia_dimension: "Confidencialidad"
  skill: "Observación y concientización"
```

| Campo | Significado |
|---|---|
| `concept` | Concepto central de seguridad que trabaja el desafío. |
| `challenge_type` | Tipo de desafío: qué actividad hace el estudiante para resolverlo (observar, correlacionar fuentes, decodificar, etc.). |
| `cia_dimension` | Dimensión de la tríada CIA (Confidencialidad, Integridad, Disponibilidad) involucrada. Si son varias, se separan con `;`. |
| `skill` | Tipo de habilidad que se pone en juego. |

Todos los campos son opcionales: si un dato no aplica (por ejemplo, la dimensión CIA del desafío introductorio), la clave se omite.

CTFd ignora este bloque al importar el desafío, así que no afecta el juego. El plugin del banco de desafíos de CTFd (`banco_desafios`) lo lee para mostrar esta información a docentes y administradores al elegir qué desafíos importar.

---

## Consideraciones éticas y de seguridad

Los desafíos fueron diseñados con fines educativos y de concientización.

Para su uso en contextos escolares se recomienda:

- trabajar con escenarios ficticios o simulados;
- evitar el uso de datos personales reales;
- no utilizar perfiles reales de estudiantes o docentes;
- no promover ataques sobre sistemas reales;
- orientar la actividad hacia el cuidado, la prevención y el uso responsable de la tecnología;
- revisar qué materiales se publican antes de una competencia o taller.

---

## Estado del repositorio

Repositorio en desarrollo como parte de una tesina de grado sobre el diseño e integración de desafíos para la herramienta **CTF en escuelas secundarias 2.0**.

Los desafíos pueden ser ajustados, ampliados o reorganizados a partir de nuevas pruebas, implementaciones o retroalimentación de estudiantes, docentes y tutores.

---

## Licencia

Los desafíos y su documentación se publican bajo la licencia [Creative Commons Atribución-CompartirIgual 4.0 Internacional (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/deed.es). El texto completo está en [LICENSE](LICENSE).

Podés usarlos, copiarlos y adaptarlos, también en otras escuelas o competencias, siempre que:

- cites la autoría: *María Emilia Romero, «CTF en escuelas secundarias 2.0», Facultad de Informática, UNLP*;
- indiques si hiciste cambios;
- compartas lo que derives bajo la misma licencia.

Las marcas y logos de terceros que aparecen en algunas imágenes (por ejemplo Netflix, Apple, Instagram o Discord) se usan solo con fines educativos, para simular escenarios de phishing, y no quedan cubiertos por esta licencia.
