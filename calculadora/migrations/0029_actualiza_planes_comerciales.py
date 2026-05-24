from django.db import migrations


def actualizar_planes(apps, schema_editor):
    Plan = apps.get_model("calculadora", "Plan")

    planes = [
        (2, "Esencial", 30000),
        (3, "Premium", 100000),
        (4, "MarchanDesign + Naipes", 50000),
        (5, "Consulta Financiera Puntual", 25000),
    ]

    for plan_id, nombre, precio in planes:
        Plan.objects.update_or_create(
            id=plan_id,
            defaults={
                "nombre": nombre,
                "precio": precio,
            },
        )


def revertir_planes(apps, schema_editor):
    Plan = apps.get_model("calculadora", "Plan")
    Plan.objects.filter(id=2, nombre="Esencial").update(precio=25000)
    Plan.objects.filter(id__in=[4, 5]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("calculadora", "0028_companyfollow"),
    ]

    operations = [
        migrations.RunPython(actualizar_planes, revertir_planes),
    ]
