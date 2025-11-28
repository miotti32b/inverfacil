from django.core.management.base import BaseCommand
from calculadora.models import Plan

class Command(BaseCommand):
    help = "Crea o actualiza los planes de suscripción"

    def handle(self, *args, **kwargs):

        planes = [
            # ----------------------------
            # PLANES FINANZAS
            # ----------------------------

            {
                "id": 1,
                "nombre": "Plan Inicio",
                "precio": 5000,
                "tipo_pago": "anual",
                "mercadopago_preapproval_url": "https://www.mercadopago.com.ar/subscriptions/checkout?preapproval_plan_id=cfaa311ddaeb4b77af89ae8eb4447906",
            },
            {
                "id": 2,
                "nombre": "Plan Intermedio",
                "precio": 25000,
                "tipo_pago": "cuatrimestral",
                "mercadopago_preapproval_url": "https://www.mercadopago.com.ar/subscriptions/checkout?preapproval_plan_id=161ff1bfb1b44e79a82e8858736824ae",
            },
            {
                "id": 3,
                "nombre": "Plan Personal",
                "precio": 35000,
                "tipo_pago": "trimestral",
                "mercadopago_preapproval_url": "https://www.mercadopago.com.ar/subscriptions/checkout?preapproval_plan_id=ef471ea9060f4aaa8effc7e61aafadb9",
            },

            # ----------------------------
            # PLANES ERP
            # ----------------------------

            {
                "id": 4,
                "nombre": "ERP Básico",
                "precio": 40000,
                "tipo_pago": "mensual",
                "mercadopago_preapproval_url": "https://www.mercadopago.com.ar/subscriptions/checkout?preapproval_plan_id=d00205c610094266857e4c87245e8627",
            },
            {
                "id": 5,
                "nombre": "ERP Intermedio",
                "precio": 90000,
                "tipo_pago": "mensual",
                "mercadopago_preapproval_url": "https://www.mercadopago.com.ar/subscriptions/checkout?preapproval_plan_id=c152dbdda1e94c7ebc386fb1eba09604",
            },
            {
                "id": 6,
                "nombre": "ERP Avanzado",
                "precio": 380000,
                "tipo_pago": "mensual",
                "mercadopago_preapproval_url": "https://www.mercadopago.com.ar/subscriptions/checkout?preapproval_plan_id=79a4a5d6aab8415fa502f1a952f8ad12",
            },
        ]

        for p in planes:
            obj, created = Plan.objects.update_or_create(
                id=p["id"],
                defaults={
                    "nombre": p["nombre"],
                    "precio": p["precio"],
                    "tipo_pago": p["tipo_pago"],
                    "mercadopago_preapproval_url": p["mercadopago_preapproval_url"],
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Plan creado: {obj.nombre}"))
            else:
                self.stdout.write(self.style.WARNING(f"↻ Plan actualizado: {obj.nombre}"))

        self.stdout.write(self.style.SUCCESS("\n✔ Seed de planes completado correctamente"))
