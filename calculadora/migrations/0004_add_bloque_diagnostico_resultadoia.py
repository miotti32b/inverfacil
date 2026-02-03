from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calculadora", "0003_add_objetivos_clienteperfil"),
    ]

    operations = [
        migrations.AddField(
            model_name="resultadoia",
            name="bloque_diagnostico",
            field=models.JSONField(default=dict, blank=True),
        ),
    ]
