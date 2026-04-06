from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from calculadora.models import ClientePerfil, DiagnosticoFinanciero
from calculadora.services.resultado import construir_resultado


class ConstruirResultadoTests(TestCase):
    @patch("calculadora.services.resultado.generar_acciones_inteligentes")
    @patch("calculadora.services.resultado.generar_feedback_meta")
    @patch("calculadora.services.resultado.generar_radiografia_ia")
    def test_construir_resultado_guarda_proyecciones_e_input_hash(
        self,
        mock_radiografia,
        mock_feedback,
        mock_acciones,
    ):
        mock_radiografia.return_value = "Radiografia de prueba"
        mock_feedback.return_value = "Feedback de prueba"
        mock_acciones.return_value = {
            "corto_plazo": ["Accion corta"],
            "mediano_plazo": ["Accion media"],
            "largo_plazo": ["Accion larga"],
        }

        user = User.objects.create_user(username="tester", password="secret")
        perfil = ClientePerfil.objects.get(user=user)
        perfil.objetivos = ["independencia_financiera"]
        perfil.experiencia_emprendimientos = 3
        perfil.hijos_a_cargo = 1
        perfil.save()

        diagnostico = DiagnosticoFinanciero.objects.create(
            cliente=perfil,
            horas_trabajadas=8,
            ingreso_trabajo=3000,
            gasto_necesarios=1200,
            gasto_innecesarios=300,
            gasto_financieros=100,
            patrimonio_comp={
                "pat_inmuebles": 10000,
                "pat_inversiones": 5000,
                "pat_cash": 2000,
            },
            deuda_comp={"deu_tarjetas": 500},
        )

        resultado = construir_resultado(perfil, diagnostico, permitir_ver=True)

        self.assertEqual(resultado.usuario, user)
        self.assertEqual(len(resultado.input_hash), 64)
        self.assertFalse(resultado.esta_bloqueado)
        self.assertEqual(len(resultado.proy_pos), 10)
        self.assertEqual(len(resultado.proy_med), 10)
        self.assertEqual(len(resultado.proy_neg), 10)
        self.assertTrue(all(isinstance(valor, float) for valor in resultado.proy_pos))
        self.assertTrue(all(isinstance(valor, float) for valor in resultado.proy_med))
        self.assertTrue(all(isinstance(valor, float) for valor in resultado.proy_neg))

    @patch("calculadora.services.resultado.generar_acciones_inteligentes")
    @patch("calculadora.services.resultado.generar_feedback_meta")
    @patch("calculadora.services.resultado.generar_radiografia_ia")
    def test_construir_resultado_reutiliza_registro_existente(
        self,
        mock_radiografia,
        mock_feedback,
        mock_acciones,
    ):
        mock_radiografia.return_value = "Radiografia de prueba"
        mock_feedback.return_value = "Feedback de prueba"
        mock_acciones.return_value = {
            "corto_plazo": ["Accion corta"],
            "mediano_plazo": ["Accion media"],
            "largo_plazo": ["Accion larga"],
        }

        user = User.objects.create_user(username="tester2", password="secret")
        perfil = ClientePerfil.objects.get(user=user)
        perfil.objetivos = ["independencia_financiera"]
        perfil.save()

        diagnostico = DiagnosticoFinanciero.objects.create(
            cliente=perfil,
            horas_trabajadas=8,
            ingreso_trabajo=2500,
            gasto_necesarios=1000,
            patrimonio_comp={"pat_cash": 3000},
            deuda_comp={},
        )

        primero = construir_resultado(perfil, diagnostico, permitir_ver=False)
        segundo = construir_resultado(perfil, diagnostico, permitir_ver=True)

        self.assertEqual(primero.pk, segundo.pk)
        self.assertFalse(segundo.esta_bloqueado)
