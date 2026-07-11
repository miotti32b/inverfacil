from decimal import Decimal

from .models import ClientePerfil


def aplicar_referido(request, user):
    ref_code = request.session.get("referral_code")

    if not ref_code:
        return None

    try:
        referidor = ClientePerfil.objects.get(referral_code=ref_code)
        perfil, _ = ClientePerfil.objects.get_or_create(user=user)

        # Evitar autoreferido o doble asignacion.
        if perfil.referido_por is None and referidor != perfil:
            perfil.referido_por = referidor
            perfil.save(update_fields=["referido_por"])

            referidor.total_referred += 1
            referidor.save(update_fields=["total_referred"])

            del request.session["referral_code"]
            request.session.modified = True
            return referidor

    except ClientePerfil.DoesNotExist:
        pass

    return None


def pagar_comision(perfil_referido, monto_plan):
    if not perfil_referido.referido_por:
        return Decimal("0")

    if perfil_referido.referral_commission_paid:
        return Decimal("0")

    referidor = perfil_referido.referido_por
    comision = monto_plan * Decimal("0.50")

    referidor.referral_earnings += comision
    referidor.save(update_fields=["referral_earnings"])

    perfil_referido.referral_commission_paid = True
    perfil_referido.save(update_fields=["referral_commission_paid"])

    return comision
