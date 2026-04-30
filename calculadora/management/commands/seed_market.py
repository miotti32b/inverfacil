from decimal import Decimal

from django.core.management.base import BaseCommand

from calculadora.logic import price_company
from calculadora.models import Company


class Command(BaseCommand):
    help = "Carga empresas ancla para Wall Street Cordobes."

    def handle(self, *args, **options):
        profiles = [
            {
                "name": "Arcor",
                "ticker": "ARCR",
                "sector": Company.INDUSTRIA,
                "revenue": Decimal("4200000000.00"),
                "employees": 500,
                "years_active": 70,
                "growth_rate": Decimal("0.08"),
                "ebitda_margin": Decimal("0.18"),
                "debt_level": Decimal("650000000.00"),
                "competitive_advantage": "marca",
                "quote_reason": "competencia",
            },
            {
                "name": "Prity",
                "ticker": "PRTY",
                "sector": Company.RETAIL,
                "revenue": Decimal("950000000.00"),
                "employees": 180,
                "years_active": 55,
                "growth_rate": Decimal("0.12"),
                "ebitda_margin": Decimal("0.14"),
                "debt_level": Decimal("130000000.00"),
                "competitive_advantage": "marca",
                "quote_reason": "competencia",
            },
            {
                "name": "Almacor",
                "ticker": "ALMC",
                "sector": Company.RETAIL,
                "revenue": Decimal("380000000.00"),
                "employees": 90,
                "years_active": 18,
                "growth_rate": Decimal("0.04"),
                "ebitda_margin": Decimal("0.06"),
                "debt_level": Decimal("90000000.00"),
                "competitive_advantage": "ubicacion",
                "quote_reason": "inversores",
            },
            {
                "name": "Policia Caminera",
                "ticker": "PCAM",
                "sector": Company.SERVICIOS,
                "revenue": Decimal("260000000.00"),
                "employees": 120,
                "years_active": 25,
                "growth_rate": Decimal("0.03"),
                "ebitda_margin": Decimal("0.22"),
                "debt_level": Decimal("10000000.00"),
                "competitive_advantage": "equipo",
                "quote_reason": "curiosidad",
            },
            {
                "name": "Maria Maria Disco",
                "ticker": "MMD",
                "sector": Company.SERVICIOS,
                "revenue": Decimal("145000000.00"),
                "employees": 45,
                "years_active": 12,
                "growth_rate": Decimal("0.10"),
                "ebitda_margin": Decimal("0.20"),
                "debt_level": Decimal("18000000.00"),
                "competitive_advantage": "marca",
                "quote_reason": "competencia",
            },
            {
                "name": "Patio Olmos Shopping",
                "ticker": "POLS",
                "sector": Company.RETAIL,
                "revenue": Decimal("1300000000.00"),
                "employees": 260,
                "years_active": 30,
                "growth_rate": Decimal("0.06"),
                "ebitda_margin": Decimal("0.24"),
                "debt_level": Decimal("210000000.00"),
                "competitive_advantage": "ubicacion",
                "quote_reason": "competencia",
            },
            {
                "name": "El Dante Carro de Choripan",
                "ticker": "CHRP",
                "sector": Company.RETAIL,
                "revenue": Decimal("78000000.00"),
                "employees": 18,
                "years_active": 16,
                "growth_rate": Decimal("0.18"),
                "ebitda_margin": Decimal("0.28"),
                "debt_level": Decimal("4500000.00"),
                "competitive_advantage": "marca",
                "quote_reason": "curiosidad",
            },
            {
                "name": "Fernet Branca",
                "ticker": "BRNC",
                "sector": Company.INDUSTRIA,
                "revenue": Decimal("3100000000.00"),
                "employees": 420,
                "years_active": 75,
                "growth_rate": Decimal("0.07"),
                "ebitda_margin": Decimal("0.26"),
                "debt_level": Decimal("380000000.00"),
                "competitive_advantage": "marca",
                "quote_reason": "competencia",
            },
            {
                "name": "Bancor",
                "ticker": "BANC",
                "sector": Company.SERVICIOS,
                "revenue": Decimal("2400000000.00"),
                "employees": 500,
                "years_active": 150,
                "growth_rate": Decimal("0.05"),
                "ebitda_margin": Decimal("0.19"),
                "debt_level": Decimal("300000000.00"),
                "competitive_advantage": "equipo",
                "quote_reason": "competencia",
            },
            {
                "name": "Tarjeta Naranja",
                "ticker": "NRJA",
                "sector": Company.TECH,
                "revenue": Decimal("2600000000.00"),
                "employees": 500,
                "years_active": 38,
                "growth_rate": Decimal("0.14"),
                "ebitda_margin": Decimal("0.21"),
                "debt_level": Decimal("420000000.00"),
                "competitive_advantage": "tecnologia",
                "quote_reason": "competencia",
            },
        ]

        for profile in profiles:
            company, _ = Company.objects.update_or_create(
                name=profile["name"],
                defaults={**profile, "is_anonymous": False},
            )
            price_company(company)
            company.save()
            self.stdout.write(self.style.SUCCESS(f"{company.name}: ${company.current_price}"))
