import random
from datetime import timedelta

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from . import constants as c
from . import logic
from .models import Pregunta


def _crear_preguntas(dificultad, cantidad):
    for i in range(cantidad):
        Pregunta.objects.create(
            texto=f"Pregunta {dificultad} #{i}",
            opciones=["a", "b", "c", "d"],
            respuesta_correcta=0,
            dificultad=dificultad,
            activa=True,
        )


class SeleccionarPreguntasTests(TestCase):
    def setUp(self):
        _crear_preguntas(Pregunta.FACIL, 7)
        _crear_preguntas(Pregunta.MEDIA, 7)
        _crear_preguntas(Pregunta.DIFICIL, 6)

    def test_cantidad_por_tier_y_total(self):
        seleccion = logic.seleccionar_preguntas(random.Random(1))
        self.assertEqual(len(seleccion), c.TOTAL_PREGUNTAS)

    def test_orden_facil_a_dificil(self):
        seleccion = logic.seleccionar_preguntas(random.Random(1))
        dificultades = [p.dificultad for p in seleccion]
        self.assertEqual(
            dificultades,
            [Pregunta.FACIL] * c.PREGUNTAS_FACILES
            + [Pregunta.MEDIA] * c.PREGUNTAS_MEDIAS
            + [Pregunta.DIFICIL] * c.PREGUNTAS_DIFICILES,
        )

    def test_ignora_preguntas_inactivas(self):
        Pregunta.objects.filter(dificultad=Pregunta.FACIL).update(activa=False)
        seleccion = logic.seleccionar_preguntas(random.Random(1))
        self.assertEqual(sum(1 for p in seleccion if p.dificultad == Pregunta.FACIL), 0)

    def test_no_explota_si_hay_menos_disponibles_que_las_pedidas(self):
        Pregunta.objects.filter(dificultad=Pregunta.DIFICIL).delete()
        Pregunta.objects.create(
            texto="Única difícil", opciones=["a", "b", "c", "d"],
            respuesta_correcta=0, dificultad=Pregunta.DIFICIL, activa=True,
        )
        seleccion = logic.seleccionar_preguntas(random.Random(1))
        self.assertEqual(sum(1 for p in seleccion if p.dificultad == Pregunta.DIFICIL), 1)


class PuntajeIndividualTests(SimpleTestCase):
    def test_correcta_instantanea_da_el_maximo(self):
        puntos = logic.calcular_puntos_individual(True, tiempo_ms=0, duracion_seg=20)
        self.assertEqual(puntos, c.PUNTOS_MAX_INDIVIDUAL)

    def test_correcta_justo_al_limite_da_el_minimo(self):
        puntos = logic.calcular_puntos_individual(True, tiempo_ms=20_000, duracion_seg=20)
        self.assertEqual(puntos, c.PUNTOS_MIN_INDIVIDUAL)

    def test_correcta_a_mitad_de_tiempo_da_un_valor_intermedio(self):
        puntos = logic.calcular_puntos_individual(True, tiempo_ms=10_000, duracion_seg=20)
        self.assertTrue(c.PUNTOS_MIN_INDIVIDUAL < puntos < c.PUNTOS_MAX_INDIVIDUAL)

    def test_incorrecta_da_cero(self):
        self.assertEqual(logic.calcular_puntos_individual(False, tiempo_ms=0, duracion_seg=20), 0)

    def test_sin_responder_da_cero(self):
        self.assertEqual(logic.calcular_puntos_individual(True, tiempo_ms=None, duracion_seg=20), 0)

    def test_nunca_supera_el_maximo_aunque_el_tiempo_sea_negativo(self):
        puntos = logic.calcular_puntos_individual(True, tiempo_ms=-500, duracion_seg=20)
        self.assertEqual(puntos, c.PUNTOS_MAX_INDIVIDUAL)


class PuntajeEquipoTests(SimpleTestCase):
    def test_correcta_da_puntaje_plano(self):
        self.assertEqual(logic.calcular_puntos_equipo(True), c.PUNTOS_EQUIPO_CORRECTO)

    def test_incorrecta_da_cero(self):
        self.assertEqual(logic.calcular_puntos_equipo(False), 0)


class TallyVotoEquipoTests(SimpleTestCase):
    def test_mayoria_estricta_gana(self):
        self.assertEqual(logic.tally_voto_equipo([1, 1, 1, 2], total_miembros=4), 1)

    def test_empate_no_hay_respuesta(self):
        self.assertIsNone(logic.tally_voto_equipo([1, 2], total_miembros=2))

    def test_cuorum_insuficiente_no_hay_respuesta(self):
        # 2 de 5 votaron la misma opción: no es mayoría del equipo completo
        self.assertIsNone(logic.tally_voto_equipo([1, 1], total_miembros=5))

    def test_sin_votos_no_hay_respuesta(self):
        self.assertIsNone(logic.tally_voto_equipo([], total_miembros=3))


class TiempoAgotadoTests(SimpleTestCase):
    def test_dentro_del_limite(self):
        inicio = timezone.now()
        ahora = inicio + timedelta(seconds=10)
        self.assertFalse(logic.tiempo_agotado(inicio, ahora, duracion_seg=20))

    def test_fuera_del_limite(self):
        inicio = timezone.now()
        ahora = inicio + timedelta(seconds=25)
        self.assertTrue(logic.tiempo_agotado(inicio, ahora, duracion_seg=20))

    def test_sin_iniciar_cuenta_como_agotado(self):
        self.assertTrue(logic.tiempo_agotado(None, timezone.now(), duracion_seg=20))
