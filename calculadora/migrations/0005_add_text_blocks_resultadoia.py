from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calculadora", "0004_add_bloque_diagnostico_resultadoia"),
    ]

    operations = [
        migrations.AddField(
            model_name="resultadoia",
            name="bloque_estructura",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="resultadoia",
            name="bloque_sesgo",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="resultadoia",
            name="bloque_proyeccion",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="resultadoia",
            name="bloque_accion",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="resultadoia",
            name="bloque_cierre",
            field=models.TextField(default=""),
        ),
    ]
