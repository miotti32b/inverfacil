from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


def _whole_number(value):
    try:
        number = Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        number = Decimal("0")
    return int(number.quantize(Decimal("1")))


@register.filter
def ars(value):
    return f"$ {_whole_number(value):,}".replace(",", ".")


@register.filter
def whole(value):
    return f"{_whole_number(value):,}".replace(",", ".")
