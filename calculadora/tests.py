from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from calculadora.models import ClientePerfil, DiagnosticoFinanciero
from calculadora.services.resultado import construir_resultado
from calculadora.models import CapitalOffering, CapitalReservation, Company
from calculadora.logic import price_company
from calculadora.services.cordoba_street_agents import build_ceo_agent_report


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


class CapitalOfferingFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="secret", email="owner@example.com")
        self.investor = User.objects.create_user(username="investor", password="secret", email="investor@example.com")
        self.company = Company.objects.create(
            name="Retail Piloto",
            created_by=self.owner,
            sector=Company.RETAIL,
            revenue=100000,
            employees=4,
            years_active=3,
            growth_rate="0.1000",
            ebitda_margin="0.1200",
            gross_margin="0.3000",
            debt_level=10000,
            total_assets=80000,
            active_customers=200,
            valuation_initial=500000,
            previous_price=50,
            current_price=50,
            total_shares=10000,
        )
        self.payload = {
            "documentation_status": CapitalOffering.DOC_SELF_DECLARED,
            "instrument_stage": CapitalOffering.INSTRUMENT_PRIVATE_CONTACT,
            "summary": "Retail local con plan de expansion verificable.",
            "location": "Cordoba, Argentina",
            "founder_name": "Fundador Piloto",
            "public_contact": "owner@example.com",
            "capital_target": "100000",
            "minimum_reservation": "1000",
            "offered_percent": "20",
            "expansion_plan": "Abrir una nueva unidad.",
            "use_of_funds": "Stock, equipamiento y capital de trabajo.",
            "milestone_1": "Firmar contrato del nuevo local.",
            "milestone_2": "Comprar equipamiento.",
            "milestone_3": "Abrir al publico.",
            "reporting_frequency": "Mensual",
            "information_commitment": "Ventas, margen, caja y avance de hitos.",
            "shareholder_decisions": "Nueva deuda o emision de acciones.",
            "capital_release_terms": "Liberacion en tres tramos contra evidencia.",
            "risks": "Demoras, menor demanda y aumento de costos.",
            "contract_terms": "La empresa se compromete a informar y documentar cada hito.",
        }

    def test_owner_can_publish_offering(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            f"/mercado/ipos/{self.company.id}/apertura/",
            {**self.payload, "action": "publish"},
        )

        offering = CapitalOffering.objects.get(company=self.company)
        self.assertRedirects(response, f"/mercado/ipos/{self.company.id}/apertura/")
        self.assertEqual(offering.status, CapitalOffering.OPEN)
        self.assertEqual(offering.contract_version, 1)
        self.assertIsNotNone(offering.published_at)

    def test_authenticated_investor_can_reserve_without_charging_portfolio(self):
        offering = CapitalOffering.objects.create(
            company=self.company,
            status=CapitalOffering.OPEN,
            published_at="2026-06-04T12:00:00Z",
            **self.payload,
        )
        self.client.force_login(self.investor)

        response = self.client.post(
            f"/mercado/aperturas/{offering.id}/",
            {
                "action": "reserve",
                "amount": "2500",
                "accept_contract": "on",
                "full_name": "Inversor Real",
                "document_id": "30111222",
                "tax_id": "20301112223",
                "phone": "3515555555",
                "city": "Cordoba",
                "risk_acknowledged": "on",
                "data_consent": "on",
            },
        )

        reservation = CapitalReservation.objects.get(offering=offering, user=self.investor)
        self.assertRedirects(response, f"/mercado/aperturas/{offering.id}/")
        self.assertEqual(reservation.amount, 2500)
        self.assertEqual(reservation.accepted_contract_version, offering.contract_version)
        self.assertFalse(hasattr(self.investor, "market_portfolio"))

    def test_ceo_agent_report_summarizes_market(self):
        CapitalOffering.objects.create(
            company=self.company,
            status=CapitalOffering.OPEN,
            published_at="2026-06-28T12:00:00Z",
            **self.payload,
        )

        report = build_ceo_agent_report()

        self.assertEqual(report["metrics"]["companies"], 1)
        self.assertEqual(report["metrics"]["open_offerings"], 1)
        self.assertGreaterEqual(len(report["agents"]), 5)
        self.assertTrue(report["next_actions"])


class MarketProductCorrectionsTests(TestCase):
    def test_solid_retail_can_value_above_early_tech(self):
        retail = Company(
            name="Minimercado Solido",
            sector=Company.RETAIL,
            revenue=300000,
            employees=8,
            years_active=7,
            growth_rate="0.0500",
            ebitda_margin="0.1200",
            gross_margin="0.3200",
            debt_level=20000,
            total_assets=180000,
            active_customers=900,
            competitive_advantage="ubicacion,proveedores",
            quote_reason="expansion",
            total_shares=10000,
        )
        tech = Company(
            name="Tech Incipiente",
            sector=Company.TECH,
            revenue=90000,
            employees=2,
            years_active=0,
            growth_rate="0.2800",
            ebitda_margin="0.0500",
            gross_margin="0.8000",
            debt_level=0,
            total_assets=15000,
            active_customers=20,
            competitive_advantage="tecnologia",
            quote_reason="inversores",
            total_shares=10000,
        )

        price_company(retail)
        price_company(tech)

        self.assertGreater(retail.market_cap, tech.market_cap)

    def test_post_login_respects_market_next_url(self):
        user = User.objects.create_user(username="market-user", password="secret")
        self.client.force_login(user)

        response = self.client.get("/redirect-post-login/?next=/mercado/cotizaciones/")

        self.assertRedirects(response, "/mercado/cotizaciones/", fetch_redirect_response=False)
