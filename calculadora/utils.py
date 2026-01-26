from .models import ClientePerfil

def aplicar_referido(request, user):
    ref_code = request.session.get("referral_code")

    if not ref_code:
        return

    try:
        referidor = ClientePerfil.objects.get(referral_code=ref_code)
        perfil = get_or_create_clienteperfil(user)


        # Evitar autoreferido o doble asignación
        if perfil.referido_por is None and referidor != perfil:
            perfil.referido_por = referidor
            perfil.save()

            referidor.total_referred += 1
            referidor.save()

            # Limpiar sesión
            del request.session["referral_code"]

    except ClientePerfil.DoesNotExist:
        pass


from decimal import Decimal

def pagar_comision(perfil_referido, monto_plan):
    if not perfil_referido.referido_por:
        return

    referidor = perfil_referido.referido_por

    # Ejemplo: 10% de comisión
    comision = monto_plan * Decimal("0.10")

    referidor.referral_earnings += comision
    referidor.save()
