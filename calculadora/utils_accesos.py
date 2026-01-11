from django.conf import settings
from .models import ClientePerfil

def tiene_acceso_formulario(user):
    """
    Permite acceder al formulario:
    - En DEBUG: siempre
    - En producción: solo usuarios autenticados
    """
    if settings.DEBUG:
        return True

    if not user.is_authenticated:
        return False

    return True
