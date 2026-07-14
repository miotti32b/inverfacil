from decimal import Decimal

from django.db import migrations


def bump_existing_5m_offerings(apps, schema_editor):
    CapitalOffering = apps.get_model("calculadora", "CapitalOffering")
    CapitalOffering.objects.filter(
        capital_target=Decimal("5000000.00"),
    ).update(capital_target=Decimal("10000000.00"))


class Migration(migrations.Migration):
    dependencies = [
        ("calculadora", "0035_company_market_visibility_and_more"),
    ]

    operations = [
        migrations.RunPython(bump_existing_5m_offerings, migrations.RunPython.noop),
    ]
