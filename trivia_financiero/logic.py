"""Lógica de negocio pura del trivia. Sin acceso a request/session ni escrituras a DB.

Toda la aleatoriedad recibe un random.Random explícito para que sea determinística
y testeable.
"""
import random
import string

from . import constants as c
from .models import Pregunta

CODIGO_ALFABETO = "".join(ch for ch in string.ascii_uppercase + "23456789" if ch not in "O0I1L")


def generar_codigo(longitud=6):
    return "".join(random.choice(CODIGO_ALFABETO) for _ in range(longitud))


def seleccionar_preguntas(rng):
    """Arma el set de preguntas de una partida: N por dificultad (constants.py),
    elegidas al azar dentro de cada tier (variedad entre charlas repetidas),
    concatenadas en orden fácil -> difícil. Devuelve una lista de instancias Pregunta."""
    tiers = [
        (Pregunta.FACIL, c.PREGUNTAS_FACILES),
        (Pregunta.MEDIA, c.PREGUNTAS_MEDIAS),
        (Pregunta.DIFICIL, c.PREGUNTAS_DIFICILES),
    ]
    seleccion = []
    for dificultad, cantidad in tiers:
        disponibles = list(Pregunta.objects.filter(dificultad=dificultad, activa=True))
        cantidad_real = min(cantidad, len(disponibles))
        seleccion.extend(rng.sample(disponibles, cantidad_real))
    return seleccion


def calcular_puntos_individual(es_correcta, tiempo_ms, duracion_seg):
    if not es_correcta or tiempo_ms is None:
        return 0
    duracion_ms = duracion_seg * 1000
    fraccion_transcurrida = max(0.0, min(1.0, tiempo_ms / duracion_ms))
    puntos = c.PUNTOS_MIN_INDIVIDUAL + (c.PUNTOS_MAX_INDIVIDUAL - c.PUNTOS_MIN_INDIVIDUAL) * (
        1 - fraccion_transcurrida
    )
    return round(max(c.PUNTOS_MIN_INDIVIDUAL, min(c.PUNTOS_MAX_INDIVIDUAL, puntos)))


def calcular_puntos_equipo(es_correcta):
    return c.PUNTOS_EQUIPO_CORRECTO if es_correcta else 0


def tally_voto_equipo(votos, total_miembros):
    """Mayoría estricta (>50%) del total de integrantes del equipo, no solo de
    quienes votaron. Sin mayoría (empate o cuórum insuficiente) -> None (sin
    respuesta): en trivia no hay una 'opción conservadora' natural a la que caer."""
    votos = [v for v in votos if v is not None]
    if not votos or total_miembros <= 0:
        return None
    conteo = {}
    for v in votos:
        conteo[v] = conteo.get(v, 0) + 1
    opcion_top, count_top = max(conteo.items(), key=lambda kv: kv[1])
    empatados = [k for k, cnt in conteo.items() if cnt == count_top]
    if len(empatados) > 1:
        return None
    if count_top > total_miembros / 2:
        return opcion_top
    return None


def tiempo_agotado(pregunta_iniciada_en, ahora, duracion_seg):
    if pregunta_iniciada_en is None:
        return True
    return (ahora - pregunta_iniciada_en).total_seconds() > duracion_seg
