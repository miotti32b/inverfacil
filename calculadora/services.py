from decimal import Decimal
from calculadora.models import Subscripcion, ClientePerfil


def activate_plan(
    *,
    user,
    plan,
    source,
    reference=None,
    regalo=None,
):
    """
    Activa un plan para un usuario.

    source:
        - mercadopago
        - promo
        - gift
        - manual
    reference:
        payment_id, código promo, etc.
    regalo:
        instancia de RegaloPendiente (si aplica)
    """

    # 1️⃣ Si viene de regalo, lo marcamos como activado
    if regalo:
        regalo.destinatario = user
        regalo.activado = True
        regalo.save(update_fields=["destinatario", "activado"])

    # 2️⃣ Crear o actualizar la suscripción
    Subscripcion.objects.update_or_create(
        usuario=user,
        plan=plan,
        defaults={
            "preapproval_id": reference,
            "estado": "active",
        }
    )

    # 3️⃣ Actualizar perfil del cliente
    perfil, _ = ClientePerfil.objects.get_or_create(user=user)
    perfil.plan_activo = plan.id
    perfil.save(update_fields=["plan_activo"])

    # 4️⃣ Log simple (útil en prod y shell)
    print(
        f"✅ Plan '{plan.nombre}' activado para {user.email} "
        f"(source={source}, ref={reference})"
    )

from calculadora.models import ClientePerfil

def get_or_create_clienteperfil(user):
    perfil, _ = ClientePerfil.objects.get_or_create(user=user)
    return perfil
