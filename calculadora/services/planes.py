from decimal import Decimal

from calculadora.models import ClientePerfil, Subscripcion
from calculadora.utils import pagar_comision


def activate_plan(
    *,
    user,
    plan,
    source,
    reference=None,
    regalo=None,
):
    """
    Activa un plan validado para un usuario.

    source:
        - mercadopago
        - promo
        - gift
        - manual
    """

    if regalo:
        regalo.destinatario = user
        regalo.activado = True
        regalo.save(update_fields=["destinatario", "activado"])

    Subscripcion.objects.update_or_create(
        usuario=user,
        defaults={
            "plan": plan,
            "preapproval_id": reference or f"{source}:{user.id}:{plan.id}",
            "estado": "active",
        },
    )

    perfil, _ = ClientePerfil.objects.get_or_create(user=user)
    perfil.plan_activo = plan.id
    perfil.save(update_fields=["plan_activo"])

    comision = Decimal("0")
    if source in {"mercadopago", "promo"}:
        comision = pagar_comision(
            perfil_referido=perfil,
            monto_plan=Decimal(plan.precio),
        )

    print(
        f"Plan '{plan.nombre}' activado para {user.email} "
        f"(source={source}, ref={reference}, comision={comision})"
    )

    return perfil


def get_or_create_clienteperfil(user):
    perfil, _ = ClientePerfil.objects.get_or_create(user=user)
    return perfil
