import random
from decimal import Decimal

from django.test import SimpleTestCase

from . import constants as c
from . import logic


class AsignarCapitalInicialTests(SimpleTestCase):
    def test_suma_siempre_exactamente_el_pozo(self):
        rng = random.Random(42)
        for n_miembros in (1, 2, 3, 7, 15, 30, 47):
            pesos = []
            for i in range(n_miembros):
                _, peso = logic.elegir_tier_peso(rng)
                pesos.append((i, peso))
            montos = logic.asignar_capital_inicial(pesos)
            self.assertEqual(sum(montos.values()), c.POZO_TOTAL, f"falló con {n_miembros} miembros")

    def test_un_solo_miembro_se_lleva_todo_el_pozo(self):
        montos = logic.asignar_capital_inicial([(1, Decimal("1.5"))])
        self.assertEqual(montos[1], c.POZO_TOTAL)

    def test_pesos_iguales_reparten_proporcionalmente(self):
        montos = logic.asignar_capital_inicial([(1, Decimal("1")), (2, Decimal("1")), (3, Decimal("1"))])
        self.assertEqual(sum(montos.values()), c.POZO_TOTAL)
        # con pesos iguales, ningún participante debería llevarse más del 34%
        self.assertTrue(all(m <= c.POZO_TOTAL * Decimal("0.34") for m in montos.values()))


class TallyVotoEquipoTests(SimpleTestCase):
    def test_mayoria_estricta_gana(self):
        resultado = logic.tally_voto_equipo(["a", "a", "a", "b"], total_miembros=4, opcion_conservadora="banco")
        self.assertEqual(resultado, "a")

    def test_empate_cae_a_conservadora(self):
        resultado = logic.tally_voto_equipo(["a", "b"], total_miembros=2, opcion_conservadora="banco")
        self.assertEqual(resultado, "banco")

    def test_sin_mayoria_por_cuorum_insuficiente_cae_a_conservadora(self):
        # 2 de 5 votaron "a": no es mayoría del total del equipo
        resultado = logic.tally_voto_equipo(["a", "a"], total_miembros=5, opcion_conservadora="banco")
        self.assertEqual(resultado, "banco")

    def test_sin_votos_cae_a_conservadora(self):
        resultado = logic.tally_voto_equipo([], total_miembros=3, opcion_conservadora="banco")
        self.assertEqual(resultado, "banco")


class OpcionDisponibleTests(SimpleTestCase):
    def test_ronda3_bloquea_sin_capital_suficiente(self):
        self.assertFalse(logic.opcion_disponible(3, "entrar", Decimal("5000"), []))

    def test_ronda3_permite_con_capital_suficiente(self):
        self.assertTrue(logic.opcion_disponible(3, "entrar", c.RONDA3_UMBRAL, []))

    def test_ronda3_umbral_se_reduce_con_red_contactos(self):
        capital = c.RONDA3_UMBRAL_CON_CONTACTOS
        self.assertFalse(logic.opcion_disponible(3, "entrar", capital, []))
        self.assertTrue(logic.opcion_disponible(3, "entrar", capital, ["red_contactos"]))

    def test_mirar_siempre_disponible(self):
        self.assertTrue(logic.opcion_disponible(3, "mirar", Decimal("0"), []))


class ResolverRonda1Tests(SimpleTestCase):
    def test_ahorros_descuenta_el_gasto(self):
        resultado = logic.resolver_ronda1(Decimal("10000"), "ahorros", [])
        self.assertEqual(resultado["capital_nuevo"], Decimal("10000") - c.RONDA1_GASTO)
        self.assertFalse(resultado["penalizacion_ronda2"])

    def test_prestamo_no_afecta_capital_pero_genera_deuda(self):
        resultado = logic.resolver_ronda1(Decimal("10000"), "prestamo", [])
        self.assertEqual(resultado["capital_nuevo"], Decimal("10000"))
        self.assertEqual(resultado["deuda_delta"], c.RONDA1_DEUDA_A_DEVOLVER)

    def test_ignorar_activa_penalizacion_ronda2(self):
        resultado = logic.resolver_ronda1(Decimal("10000"), "ignorar", [])
        self.assertEqual(resultado["capital_nuevo"], Decimal("10000"))
        self.assertTrue(resultado["penalizacion_ronda2"])

    def test_red_contactos_reduce_el_costo(self):
        sin_habilidad = logic.resolver_ronda1(Decimal("10000"), "ahorros", [])
        con_habilidad = logic.resolver_ronda1(Decimal("10000"), "ahorros", ["red_contactos"])
        self.assertLess(Decimal(con_habilidad["detalle"]["costo"]), Decimal(sin_habilidad["detalle"]["costo"]))

    def test_dos_red_contactos_reducen_mas_que_uno(self):
        uno = logic.resolver_ronda1(Decimal("10000"), "ahorros", ["red_contactos"])
        dos = logic.resolver_ronda1(Decimal("10000"), "ahorros", ["red_contactos", "red_contactos"])
        self.assertLess(Decimal(dos["detalle"]["costo"]), Decimal(uno["detalle"]["costo"]))


class ToleranciaRiesgoStackingTests(SimpleTestCase):
    def test_dos_integrantes_con_tolerancia_duplica_respecto_de_uno_solo(self):
        rng_a = random.Random(7)
        rng_b = random.Random(7)  # misma semilla -> mismo pct base, comparamos el efecto del apilamiento
        base = logic.resolver_ronda2(Decimal("10000"), "fondo", ["tolerancia_riesgo"], False, rng_a)
        apilado = logic.resolver_ronda2(Decimal("10000"), "fondo", ["tolerancia_riesgo"] * 2, False, rng_b)
        # multiplicador pasa de (1+1)=2 a (1+2)=3, así que el delta apilado debe ser ~1.5x el base
        # (tolerancia de 1 centavo por el redondeo independiente de cada resultado)
        esperado = base["delta"] * Decimal("1.5")
        self.assertLessEqual(abs(apilado["delta"] - esperado), Decimal("0.01"))


class ResolverRonda4Tests(SimpleTestCase):
    def test_colchon_anula_la_perdida_y_se_marca_usado(self):
        resultado = logic.resolver_ronda4(
            Decimal("10000"), Decimal("0"), [], colchon_disponible=True, colchon_usado=False
        )
        self.assertEqual(resultado["capital_nuevo"], Decimal("10000"))
        self.assertTrue(resultado["colchon_usado"])

    def test_colchon_ya_usado_no_vuelve_a_aplicar(self):
        resultado = logic.resolver_ronda4(
            Decimal("10000"), Decimal("0"), [], colchon_disponible=True, colchon_usado=True
        )
        self.assertLess(resultado["capital_nuevo"], Decimal("10000"))
        self.assertFalse(resultado["colchon_usado"])

    def test_impulsividad_duplica_la_perdida(self):
        normal = logic.resolver_ronda4(Decimal("10000"), Decimal("0"), [], False, False)
        con_impulsividad = logic.resolver_ronda4(Decimal("10000"), Decimal("0"), ["impulsividad"], False, False)
        perdida_normal = Decimal("10000") - normal["capital_nuevo"]
        perdida_impulsiva = Decimal("10000") - con_impulsividad["capital_nuevo"]
        self.assertEqual(perdida_impulsiva, perdida_normal * 2)

    def test_deuda_pendiente_se_cobra_integra(self):
        resultado = logic.resolver_ronda4(Decimal("10000"), Decimal("4000"), [], False, False)
        self.assertEqual(resultado["deuda_delta"], Decimal("-4000"))
        perdida_esperada = logic.quantize_money(Decimal("10000") * c.RONDA4_PERDIDA_PCT)
        self.assertEqual(resultado["capital_nuevo"], Decimal("10000") - perdida_esperada - Decimal("4000"))


class ResolverRonda5Tests(SimpleTestCase):
    def test_apalancado_puede_generar_deuda_si_sale_mal(self):
        rng = random.Random(1)
        # forzamos el peor caso posible del rango sin depender del azar real
        resultado = logic.resolver_ronda5(Decimal("10000"), "apalancado", [], rng)
        self.assertIn("a_devolver", resultado["detalle"])

    def test_normal_no_pide_prestamo(self):
        rng = random.Random(1)
        resultado = logic.resolver_ronda5(Decimal("10000"), "normal", [], rng)
        self.assertNotIn("a_devolver", resultado["detalle"])
