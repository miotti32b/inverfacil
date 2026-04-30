from decimal import Decimal, ROUND_HALF_UP
import random

from django.db import transaction

from .models import Company


SECTOR_MULTIPLIERS = {
    Company.TECH: Decimal("6.0"),
    Company.AGRO: Decimal("2.5"),
    Company.RETAIL: Decimal("1.2"),
    Company.SERVICIOS: Decimal("1.8"),
    Company.INDUSTRIA: Decimal("2.2"),
    Company.GASTRONOMIA: Decimal("1.4"),
    Company.FINANZAS: Decimal("3.2"),
    Company.ENTRETENIMIENTO: Decimal("1.6"),
    Company.INMOBILIARIO: Decimal("2.0"),
}

SHARES_PER_COMPANY = Decimal("10000")
MONEY_QUANT = Decimal("0.01")


def quantize_money(value):
    return Decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def calculate_initial_price(revenue, sector, growth_rate):
    multiplier = SECTOR_MULTIPLIERS.get(sector, Decimal("1.0"))
    growth = Decimal(str(growth_rate or 0))
    price = (Decimal(str(revenue or 0)) * multiplier * (Decimal("1") + growth)) / SHARES_PER_COMPANY
    return max(quantize_money(price), MONEY_QUANT)


def price_company(company):
    price = calculate_initial_price(company.revenue, company.sector, company.growth_rate)
    company.valuation_initial = price
    company.previous_price = price
    company.current_price = price
    company.last_noise_percent = Decimal("0")
    return company


def generate_market_noise():
    updates = []
    with transaction.atomic():
        for company in Company.objects.select_for_update():
            noise = Decimal(str(random.uniform(-1.5, 1.5))).quantize(Decimal("0.0001"))
            previous_price = company.current_price
            next_price = previous_price * (Decimal("1") + (noise / Decimal("100")))

            company.previous_price = previous_price
            company.current_price = max(quantize_money(next_price), MONEY_QUANT)
            company.last_noise_percent = noise
            company.save(update_fields=["previous_price", "current_price", "last_noise_percent", "updated_at"])
            updates.append(company)
    return updates
