from django.core.management.base import BaseCommand
from calculadora.models import Plan

class Command(BaseCommand):
    help = "Crea o actualiza los planes de suscripción"

    def handle(self, *args, **kwargs):
        planes = [
            {
                "id": 1,
                "nombre": "Plan Starter",
                "tipo": "FIN",
                "precio_mensual": 3990,
                "mercadopago_preapproval_url": "https://www.mercadopago.com/checkout1",
                "activo": True,
            },
            {
                "id": 2,
                "nombre": "Plan Pro",
                "tipo": "FIN",
                "precio_mensual": 9990,
                "mercadopago_preapproval_url": "https://www.mercadopago.com/checkout2",
                "activo": True,
            },
            {
                "id": 3,
                "nombre": "Plan Empresas Básico",
                "tipo": "ERP",
                "precio_mensual": 19990,
                "mercadopago_preapproval_url": "https://www.mercadopago.com/checkout3",
                "activo": True,
            },
            {
                "id": 4,
                "nombre": "Plan Empresas Full",
                "tipo": "ERP",
                "precio_mensual": 49990,
                "mercadopago_preapproval_url": "https://www.mercadopago.com/checkout4",
                "activo": True,
            },
        ]

        for p in planes:
            obj, created = Plan.objects.update_or_create(
                id=p["id"],
                defaults={
                    "nombre": p["nombre"],
                    "tipo": p["tipo"],
                    "precio_mensual": p["precio_mensual"],
                    "mercadopago_preapproval_url": p["mercadopago_preapproval_url"],
                    "activo": p["activo"],
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Plan creado: {obj.nombre}"))
            else:
                self.stdout.write(self.style.WARNING(f"↻ Plan actualizado: {obj.nombre}"))

        self.stdout.write(self.style.SUCCESS("✔ Seed de planes completado"))
