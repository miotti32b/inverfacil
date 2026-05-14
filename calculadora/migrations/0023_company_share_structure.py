from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calculadora", "0022_company_created_by_company_guest_session_key_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="public_float_percent",
            field=models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=5),
        ),
        migrations.AddField(
            model_name="company",
            name="total_shares",
            field=models.PositiveIntegerField(default=10000),
        ),
    ]
