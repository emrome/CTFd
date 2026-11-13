# Métricas de aprendizaje

Plugin de CTFd que agrega la página **Métricas** al panel de administración (`/admin/metricas`). La ven los administradores y los autores. Muestra cómo les fue a los equipos con cada desafío de la competencia, para que el autor pueda revisar y mejorar los desafíos.

Solo lee lo que CTFd ya guarda: envíos, pistas desbloqueadas, requisitos de los desafíos y fechas de la competencia. No pide datos nuevos a los estudiantes. Lo único que escribe son los umbrales de "Para revisar", en la configuración de la competencia.

## Qué muestra

- Un resumen de la competencia y los desafíos resueltos por cada equipo a lo largo de la jornada.
- **Para revisar**: los desafíos que quedan por debajo de los umbrales o que se comportaron como más difíciles que el nivel declarado.
- Tablas por desafío, por nivel, por categoría, por dimensión CIA, por habilidad y por equipo, que se pueden ordenar y descargar en CSV.
- La tabla de nivel declarado contra dificultad observada.

Los filtros permiten ver solo los desafíos del banco o todos, y elegir categoría, nivel, dimensión CIA, habilidad o un equipo.

## Cómo se calcula

| Indicador                       | Cálculo                                                                                                                                                                               |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Equipos que jugaron             | Equipos (o usuarios, en modo usuarios) con al menos un envío de una cuenta de estudiante durante la competencia. No cuentan administradores, autores ni cuentas ocultas o bloqueadas. |
| Con acceso                      | Equipos activos que resolvieron todos los requisitos previos antes del cierre, o que intentaron el desafío (por si los requisitos cambiaron durante la jornada).                      |
| Tasa de resolución              | Resolvieron ÷ equipos con acceso, y resolvieron ÷ equipos que jugaron.                                                                                                                |
| Incorrectos y pistas por equipo | Envíos incorrectos y pistas desbloqueadas ÷ equipos que lo intentaron.                                                                                                                |
| 1.ª resolución                  | Minutos desde el inicio de la competencia hasta la primera resolución.                                                                                                                |
| Dificultad observada            | Según la tasa con acceso: Fácil desde el 80 %, Medio desde el 50 %, si no Avanzado. Solo con al menos 3 equipos con acceso.                                                           |
| Avance por nivel                | Desafíos del nivel que resolvió el equipo ÷ desafíos del nivel.                                                                                                                       |

Solo cuentan los envíos y las pistas entre el inicio y el fin de la competencia. Los desafíos ocultos aparecen solo si alguien los jugó, y los requisitos que apuntan a desafíos borrados se ignoran, como hace CTFd. Los cortes son configurables desde el botón **Umbrales**. El nivel declarado sale de las etiquetas del desafío (por ejemplo `nivel: fácil`). La dimensión CIA y la habilidad salen del bloque `pedagogy` del desafío en el [banco de desafíos](../banco_desafios/README.md), así que esas vistas solo incluyen desafíos del banco.

Las métricas describen el desempeño en la plataforma, no el aprendizaje. Para hablar de aprendizaje conviene leerlas junto con otras fuentes, como una encuesta o la observación docente.
