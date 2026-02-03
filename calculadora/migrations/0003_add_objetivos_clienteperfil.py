from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calculadora", "0002_alter_diagnosticofinanciero_horas_trabajadas"),
    ]

    operations = [
        migrations.AddField(
            model_name="clienteperfil",
            name="objetivos",
            field=models.JSONField(default=list, blank=True),
        ),
    ]
