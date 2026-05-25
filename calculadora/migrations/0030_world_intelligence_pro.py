from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def actualizar_planes_intelligence(apps, schema_editor):
    Plan = apps.get_model("calculadora", "Plan")
    planes = [
        (4, "InverFacil Intelligence Pro", 200000),
        (6, "MarchanDesign + Naipes", 50000),
    ]
    for plan_id, nombre, precio in planes:
        Plan.objects.update_or_create(
            id=plan_id,
            defaults={"nombre": nombre, "precio": precio},
        )


def revertir_planes_intelligence(apps, schema_editor):
    Plan = apps.get_model("calculadora", "Plan")
    Plan.objects.update_or_create(
        id=4,
        defaults={"nombre": "MarchanDesign + Naipes", "precio": 50000},
    )
    Plan.objects.filter(id=6, nombre="MarchanDesign + Naipes").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("calculadora", "0029_actualiza_planes_comerciales"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WorldCeoBrief",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField(unique=True)),
                ("contenido", models.TextField(blank=True, default="")),
                ("modelo", models.CharField(blank=True, default="", max_length=80)),
                ("generado_en", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-fecha"]},
        ),
        migrations.CreateModel(
            name="WorldDashboardSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField(unique=True)),
                ("stress_score", models.PositiveSmallIntegerField(default=50)),
                ("stress_label", models.CharField(default="Vigilancia", max_length=40)),
                ("category_scores", models.JSONField(blank=True, default=dict)),
                ("metrics", models.JSONField(blank=True, default=dict)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-fecha"]},
        ),
        migrations.CreateModel(
            name="WorldDashboardAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120)),
                ("metric_key", models.CharField(max_length=80)),
                ("operator", models.CharField(choices=[("gt", "Mayor que"), ("lt", "Menor que"), ("eq", "Igual a"), ("contains", "Contiene")], default="gt", max_length=20)),
                ("threshold", models.CharField(blank=True, default="", max_length=80)),
                ("activa", models.BooleanField(default=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="world_alerts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-actualizado_en"]},
        ),
        migrations.RunPython(actualizar_planes_intelligence, revertir_planes_intelligence),
    ]
