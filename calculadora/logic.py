from decimal import Decimal, ROUND_HALF_UP
import random

from django.db import transaction

from .models import Company


SECTOR_MULTIPLIER_RANGES = {
    Company.TECH: (Decimal("1.0"), Decimal("2.5")),
    Company.FINANZAS: (Decimal("1.0"), Decimal("2.2")),
    Company.SERVICIOS: (Decimal("0.5"), Decimal("1.2")),
    Company.AGRO: (Decimal("0.3"), Decimal("0.8")),
    Company.INDUSTRIA: (Decimal("0.4"), Decimal("1.0")),
    Company.INMOBILIARIO: (Decimal("0.5"), Decimal("1.2")),
    Company.ENTRETENIMIENTO: (Decimal("0.4"), Decimal("1.0")),
    Company.RETAIL: (Decimal("0.25"), Decimal("0.6")),
    Company.GASTRONOMIA: (Decimal("0.2"), Decimal("0.45")),
}
DEFAULT_MULTIPLIER_RANGE = (Decimal("0.5"), Decimal("1.0"))

QUALITY_MIN = Decimal("0.30")
QUALITY_MAX = Decimal("1.65")

SHARES_PER_COMPANY = Decimal("10000")
MONEY_QUANT = Decimal("0.01")


def quantize_money(value):
    return Decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _clamp(value, low, high):
    return max(low, min(value, high))


def _percent_factor(value, weight, low=Decimal("-0.35"), high=Decimal("0.35")):
    return _clamp(Decimal(str(value or 0)) * weight, low, high)


def _company_quality(company):
    growth = Decimal(str(company.growth_rate or 0))
    ebitda_margin = Decimal(str(company.ebitda_margin or 0))
    gross_margin = Decimal(str(company.gross_margin or 0))
    employees = Decimal(str(company.employees or 1))
    years = Decimal(str(company.years_active or 0))
    customers = Decimal(str(company.active_customers or 0))
    advantages = [item for item in (company.competitive_advantage or "").split(",") if item]
    reasons = [item for item in (company.quote_reason or "").split(",") if item]

    quality = Decimal("0.85")
    quality += _percent_factor(growth, Decimal("0.65"), Decimal("-0.18"), Decimal("0.30"))
    quality += _percent_factor(ebitda_margin, Decimal("1.00"), Decimal("-0.30"), Decimal("0.35"))
    quality += _percent_factor(gross_margin, Decimal("0.18"), Decimal("-0.08"), Decimal("0.12"))
    quality += min(years, Decimal("25")) * Decimal("0.010")
    quality += min(employees, Decimal("120")) * Decimal("0.0008")
    quality += min(customers, Decimal("1000")) * Decimal("0.00012")
    quality += min(Decimal(len(advantages)), Decimal("2")) * Decimal("0.04")
    quality += Decimal("0.03") if "inversores" in reasons or "expansion" in reasons else Decimal("0")
    if years < 2:
        quality *= Decimal("0.65")
    elif years < 4:
        quality *= Decimal("0.82")
    if company.sector == Company.TECH and years < 2 and employees <= 3:
        quality *= Decimal("0.70")
    return _clamp(quality, QUALITY_MIN, QUALITY_MAX)


def calculate_company_valuation_range(company):
    """Devuelve un desglose con el rango [minimo, maximo] de equity value y un
    punto fijo dentro de ese rango (usado para el market cap del simulador),
    ubicado segun que tan solido es el negocio (factor de calidad)."""
    multiplier_low, multiplier_high = SECTOR_MULTIPLIER_RANGES.get(
        company.sector, DEFAULT_MULTIPLIER_RANGE
    )
    revenue = Decimal(str(company.revenue or 0))
    assets = Decimal(str(company.total_assets or 0))
    debt = Decimal(str(company.debt_level or 0))
    quality = _company_quality(company)

    asset_floor = assets * Decimal("0.55")
    equity_floor = MONEY_QUANT * SHARES_PER_COMPANY

    enterprise_low = max(revenue * multiplier_low * quality, asset_floor)
    enterprise_high = max(revenue * multiplier_high * quality, asset_floor)
    equity_low = max(enterprise_low - debt, equity_floor)
    equity_high = max(enterprise_high - debt, max(equity_low, equity_floor))

    quality_position = _clamp(
        (quality - QUALITY_MIN) / (QUALITY_MAX - QUALITY_MIN), Decimal("0"), Decimal("1")
    )
    equity_point = equity_low + quality_position * (equity_high - equity_low)

    return {
        "multiplier_low": multiplier_low,
        "multiplier_high": multiplier_high,
        "quality": quality,
        "quality_position": quality_position,
        "asset_floor": asset_floor,
        "equity_low": quantize_money(equity_low),
        "equity_high": quantize_money(equity_high),
        "equity_point": quantize_money(equity_point),
    }


def calculate_company_equity_value(company):
    """Punto fijo de equity value (compatibilidad con el simulador de mercado)."""
    return calculate_company_valuation_range(company)["equity_point"]


def calculate_initial_price(revenue, sector, growth_rate):
    multiplier_low, multiplier_high = SECTOR_MULTIPLIER_RANGES.get(sector, DEFAULT_MULTIPLIER_RANGE)
    multiplier = (multiplier_low + multiplier_high) / Decimal("2")
    growth = Decimal(str(growth_rate or 0))
    price = (Decimal(str(revenue or 0)) * multiplier * (Decimal("1") + growth)) / SHARES_PER_COMPANY
    return max(quantize_money(price), MONEY_QUANT)


def price_company(company):
    breakdown = calculate_company_valuation_range(company)
    shares = Decimal(str(company.total_shares or SHARES_PER_COMPANY))
    price = quantize_money(breakdown["equity_point"] / shares)
    company.valuation_initial = price
    company.previous_price = price
    company.current_price = price
    company.last_noise_percent = Decimal("0")
    company.valuation_low = breakdown["equity_low"]
    company.valuation_high = breakdown["equity_high"]
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
