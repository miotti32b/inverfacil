"""Datos fijos del juego 'Kahoot financiero'. Ajustables sin tocar la lógica."""

DURACION_PREGUNTA_SEGUNDOS = 20

# cuántas preguntas de cada dificultad entran en una partida, en orden fácil -> difícil
PREGUNTAS_FACILES = 4
PREGUNTAS_MEDIAS = 4
PREGUNTAS_DIFICILES = 3
TOTAL_PREGUNTAS = PREGUNTAS_FACILES + PREGUNTAS_MEDIAS + PREGUNTAS_DIFICILES

# puntaje individual: más rápido = más puntos, con piso si contestás justo al límite
PUNTOS_MAX_INDIVIDUAL = 1000
PUNTOS_MIN_INDIVIDUAL = 500

# equipo: puntaje plano por acierto, sin bono de velocidad (ver plan: evita penalizar
# el tiempo que tarda el equipo en ponerse de acuerdo)
PUNTOS_EQUIPO_CORRECTO = 1000

MAX_INTEGRANTES_EQUIPO = 4
