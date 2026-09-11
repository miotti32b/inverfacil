import plotly.graph_objs as go
import os
import uuid
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.templatetags.static import static
from calculadora.services.resultado import construir_resultado, METAS_MAP
import json
import requests

from django.db import models  # ðŸ”¥ Agrega esto
from django.db.models.functions import ExtractMonth, ExtractYear
from .forms import CarreraRataForm


def carrera_rata_view(request):
    if request.GET.get("volver") == "clasico":
        request.session["carrera_rata_modo"] = "clasico"
    elif request.method == "GET" and request.session.get("carrera_rata_modo") == "inmersiva":
        from django.shortcuts import redirect
        return redirect("carrera_rata_inmersiva")

    if request.method == "POST":
        form = CarreraRataForm(request.POST)
        if form.is_valid():
            carrera_rata = form.save()
            return render(request, 'calculadora/resultado.html', {'carrera_rata': carrera_rata})
    else:
        form = CarreraRataForm()
    return render(request, 'calculadora/carrerarata.html', {'form': form})


def carrera_rata_inmersiva_view(request):
    request.session["carrera_rata_modo"] = "inmersiva"
    form = CarreraRataForm()
    return render(request, 'calculadora/carrerarata_inmersiva.html', {'form': form})


def inversiones_view(request):
    return render(request, 'calculadora/inversiones.html')


def practica_importacion_lifecycle_view(request):
    template_path = (
        Path(__file__).resolve().parent
        / 'templates'
        / 'calculadora'
        / 'PrÃ¡ctica de ImportaciÃ³n - LifecycleArgentina WPC.html'
    )
    html = template_path.read_text(encoding='utf-8')
    html = html.replace(
        './PrÃ¡ctica de ImportaciÃ³n - LifecycleArgentina WPC_files/css2',
        static('css/lifecycleargentina-wpc-fonts.css'),
    )
    return HttpResponse(html)



from django.shortcuts import render
from django.conf import settings
from django.contrib.sites.models import Site
from calculadora.services.portal_financiero import build_portal_context


def _capture_referral_code(request):
    ref_code = (request.GET.get("ref") or "").strip().upper()
    if ref_code:
        request.session["referral_code"] = ref_code
        request.session.modified = True


def home(request):
    if settings.DEBUG:
        current_site = Site.objects.get(id=settings.SITE_ID)
        sites_list = list(Site.objects.values_list('id', 'domain'))
        print("DEBUG SITE INFO")
        print("SITE_ID usado:", settings.SITE_ID)
        print("Dominio del SITE_ID:", current_site.domain)
        print("Todos los sites:", sites_list)

    _capture_referral_code(request)

    return render(request, "home_prototipo.html")


def home_prototipo(request):
    _capture_referral_code(request)
    return render(request, "home_prototipo.html")


def asesor_financiero_cordoba(request):
    return render(request, "asesor_financiero_cordoba.html")


def voice_clone_landing(request):
    return render(request, "calculadora/voice_clone_landing.html")


@require_POST
def generate_voice_clone_audio(request):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return JsonResponse(
            {"error": "Falta configurar ELEVENLABS_API_KEY en el archivo .env."},
            status=500,
        )

    uploaded_audio = request.FILES.get("voice_file")
    dialogue = (request.POST.get("dialogue") or "").strip()
    consent = request.POST.get("consent") == "on"

    if not uploaded_audio:
        return JsonResponse({"error": "Adjunta un archivo de audio."}, status=400)
    if not dialogue:
        return JsonResponse({"error": "Escribe el dialogo que queres generar."}, status=400)
    if len(dialogue) > 1200:
        return JsonResponse({"error": "El dialogo supera los 1200 caracteres."}, status=400)
    if not consent:
        return JsonResponse({"error": "Necesitas confirmar el permiso de uso de la voz."}, status=400)
    if uploaded_audio.size > 20 * 1024 * 1024:
        return JsonResponse({"error": "El audio no puede superar los 20 MB."}, status=400)

    content_type = uploaded_audio.content_type or "application/octet-stream"
    if not content_type.startswith("audio/"):
        return JsonResponse({"error": "El archivo debe ser de audio."}, status=400)

    headers = {"xi-api-key": api_key}
    voice_id = None

    try:
        clone_response = requests.post(
            "https://api.elevenlabs.io/v1/voices/add",
            headers=headers,
            data={
                "name": f"IEF voz temporal {uuid.uuid4().hex[:8]}",
                "description": "Clon temporal generado desde la landing Voz IA de IEF.",
                "remove_background_noise": "true",
            },
            files={
                "files": (
                    uploaded_audio.name,
                    uploaded_audio.read(),
                    content_type,
                )
            },
            timeout=90,
        )
        if clone_response.status_code >= 400:
            return JsonResponse(
                {"error": _elevenlabs_error_message(clone_response)},
                status=clone_response.status_code,
            )

        voice_id = clone_response.json().get("voice_id")
        if not voice_id:
            return JsonResponse({"error": "ElevenLabs no devolvio un voice_id."}, status=502)

        speech_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={**headers, "Content-Type": "application/json"},
            params={"output_format": "mp3_44100_128"},
            json={
                "text": dialogue,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.42,
                    "similarity_boost": 0.82,
                    "style": 0.28,
                    "use_speaker_boost": True,
                },
            },
            timeout=120,
        )
        if speech_response.status_code >= 400:
            return JsonResponse(
                {"error": _elevenlabs_error_message(speech_response)},
                status=speech_response.status_code,
            )

        response = HttpResponse(speech_response.content, content_type="audio/mpeg")
        response["Content-Disposition"] = 'inline; filename="voz-ia.mp3"'
        character_count = speech_response.headers.get("x-character-count")
        if character_count:
            response["X-Character-Count"] = character_count
        return response
    except requests.RequestException:
        return JsonResponse(
            {"error": "No pude conectar con ElevenLabs. Proba de nuevo en unos minutos."},
            status=502,
        )
    finally:
        if voice_id and os.getenv("ELEVENLABS_KEEP_CLONES") != "1":
            try:
                requests.delete(
                    f"https://api.elevenlabs.io/v1/voices/{voice_id}",
                    headers=headers,
                    timeout=20,
                )
            except requests.RequestException:
                pass


def _elevenlabs_error_message(response):
    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = response.text
    if isinstance(detail, dict):
        return detail.get("message") or detail.get("status") or "ElevenLabs rechazo la solicitud."
    if isinstance(detail, list) and detail:
        return detail[0].get("msg", "ElevenLabs rechazo la solicitud.") if isinstance(detail[0], dict) else str(detail[0])
    return str(detail or "ElevenLabs rechazo la solicitud.")


def calculadora_interes_compuesto(request):
    if request.method == "POST":
        # Obtener los datos del formulario
        principal = int(request.POST.get('principal', 0))
        additional_investment = int(request.POST.get('additional_investment', 0))
        investment_period = request.POST.get('investment_period')
        time = int(request.POST.get('time', 0))
        time_period = request.POST.get('time_period')
        rate = float(request.POST.get('rate', 0)) / 100
        rate_period = request.POST.get('rate_period')

        # Determinar el nÃºmero total de perÃ­odos
        if time_period == 'daily':
            total_periods = int(time)
        elif time_period == 'weekly':
            total_periods = int(time * 7)
        elif time_period == 'monthly':
            total_periods = int(time * 365 / 12)
        else:  # yearly
            total_periods = int(time * 365)

        # Inicializar el monto total con la inversiÃ³n inicial
        total_amount = principal
        total_contributions = principal

        # Ajustar la tasa de interÃ©s segÃºn su frecuencia
        if rate_period == 'daily':
            rate_per_period = rate
        elif rate_period == 'weekly':
            rate_per_period = rate / 7
        elif rate_period == 'monthly':
            rate_per_period = rate / 30
        else:  # yearly
            rate_per_period = rate / 365

        # Resultados para el grÃ¡fico
        periods = []
        contributions = []
        interests = []

        # Iterar sobre cada perÃ­odo total
        for period in range(1, total_periods + 1):
            # Aplicar los aportes adicionales segÃºn la frecuencia seleccionada
            if (investment_period == 'daily' and period % 1 == 0) or \
               (investment_period == 'weekly' and period % 7 == 0) or \
               (investment_period == 'monthly' and period % 30 == 0) or \
               (investment_period == 'yearly' and period % 365 == 0):
                total_amount += additional_investment
                total_contributions += additional_investment

            # Aplicar el interÃ©s compuesto
            total_amount *= (1 + rate_per_period)

            # Guardar resultados significativos (mensuales o anuales) para el grÃ¡fico
            if period % (total_periods // time) == 0 or period == total_periods:
                periods.append(f"Periodo {len(periods) + 1}")
                contributions.append(total_contributions)
                interests.append(total_amount - total_contributions)

        # Pasar los datos a la plantilla en formato JSON seguro
        return render(request, 'calculadora/calculadora.html', {
            'amount': round(total_amount, 2),  # Monto final
            'total_contributions': round(total_contributions, 2),  # Monto aportado
            'interests_generated': round(total_amount - total_contributions, 2),  # Intereses ganados
            'periods': json.dumps(periods),
            'contributions': json.dumps([round(c, 2) for c in contributions]),
            'interests': json.dumps([round(i, 2) for i in interests]),
            # Mantener los valores ingresados en el formulario
            'principal': principal,
            'additional_investment': additional_investment,
            'investment_period': investment_period,
            'time': time,
            'time_period': time_period,
            'rate': rate * 100,
            'rate_period': rate_period,
        })

    # Si no es POST, renderizar formulario vacÃ­o
    return render(request, 'calculadora/calculadora.html')


import random
import base64

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Player

def start_game(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        age = data.get("age")
        gender = data.get("gender")

        if username and age and gender:
            player = Player.objects.create(username=username, age=age, gender=gender)
            request.session["username"] = username  # ðŸ”¥ Guarda el usuario en la sesiÃ³n
            return JsonResponse({"success": True, "player_id": player.id})  

    return render(request, "calculadora/start.html")


def game_view(request):
    return render(request, "calculadora/game.html")

from django.http import JsonResponse
from .models import Player

from django.db import models  # ðŸ”¥ Agrega esto





def guardar_puntaje(request):
    if request.method == "POST":  # âœ… SOLO PERMITIMOS POST
        try:
            data = json.loads(request.body)  # ðŸ“Œ Leer JSON correctamente

            player_id = data.get("player_id")
            score = data.get("score")
            
            if player_id is None or score is None:
                return JsonResponse({"success": False, "error": "Datos incompletos."}, status=400)

            # Buscar al jugador en la base de datos
            jugador = Player.objects.get(id=int(player_id))
            jugador.score = score
            jugador.save()

            return JsonResponse({"success": True})
        except Player.DoesNotExist:
            return JsonResponse({"success": False, "error": "Jugador no encontrado."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Error en el formato de datos."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    else:
        return JsonResponse({"success": False, "error": "MÃ©todo no permitido."}, status=405)  # âŒ Bloqueamos GET



from django.db.models import Count, Avg, Max



from django.shortcuts import render
from .models import Player

def ranking_view(request):
    jugadores = Player.objects.order_by('-score')[:10]  # ðŸ”¥ Top 10 jugadores
    usuario_actual = Player.objects.filter(username=request.session.get("username")).first()
    ids_top10 = {jugador.id for jugador in jugadores}  # ðŸ”¥ IDs de los top 10

    posicion_real = None
    promedio = 0

    if usuario_actual:
        # ðŸ”¥ Contar cuÃ¡ntos jugadores tienen un puntaje mayor
        posicion_real = Player.objects.filter(score__gt=usuario_actual.score).count() + 1
        
        # ðŸ”¥ Calcular porcentaje de jugadores superados
        jugadores_inferiores = Player.objects.filter(score__lt=usuario_actual.score).count()
        total_jugadores = Player.objects.count()
        promedio = (jugadores_inferiores / total_jugadores) * 100 if total_jugadores > 0 else 0

    return render(request, "calculadora/ranking.html", {
        "jugadores": jugadores,
        "usuario_actual": usuario_actual,
        "promedio": promedio,
        "posicion_real": posicion_real,
        "ids_top10": ids_top10
    })






def obtener_id_jugador(request):
    try:
        jugador = Player.objects.latest('id')  # Obtiene el Ãºltimo jugador registrado
        return JsonResponse({"player_id": jugador.id})
    except Player.DoesNotExist:
        return JsonResponse({"error": "No hay jugadores registrados."}, status=404)

from django.http import JsonResponse

def api_endpoint(request):
    return JsonResponse({"message": "API funcionando correctamente"})

def instrucciones_view(request):
    return render(request, "calculadora/instrucciones.html")


# views.py
from django.shortcuts import render

def landing(request):
    return render(request, 'landing.html')


def distribuidora_portal(request):
    context = {"show_login": request.GET.get("login") == "1"}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if username == "jota" and password == "jota":
            request.session["erp_demo_auth"] = True
            return redirect("demo_erp")
        context.update({"show_login": True, "login_error": "Usuario o contrasena incorrectos."})
    return render(request, 'calculadora/distribuidora_portal.html', context)


def demo_erp(request):
    if not request.session.get("erp_demo_auth"):
        return redirect("/distribuidora/?login=1")
    return render(request, 'calculadora/demo_erp.html')


NAIF_PRODUCT_CHOICES = [
    ("1", "Arabes"),
    ("2", "Saladas"),
    ("3", "Dulces"),
    ("4", "Pollo"),
    ("5", "Jamon y queso"),
    ("6", "Salame y muzza"),
    ("7", "Fugazza"),
    ("8", "Abiertas"),
    ("9", "caprese"),
    ("10", "picantes"),
    ("11", "envio"),
]

NAIF_COST_ITEMS = [
    "MOLIDA COM",
    "MOLIDA ESP",
    "POLLO",
    "AJO",
    "CEBOLLA",
    "TOMATE",
    "LIMON",
    "VERDEO",
    "PEREJIL",
    "PIM ROJO",
    "HUEVOS",
    "AZUCAR",
    "HARINA",
    "LEVADURA",
    "CAJA GRAN",
    "CAJA CHIC",
    "PAPEL SERV",
    "FOLEX GRAN",
    "FOLEX CHIC",
    "BOLSA CEBOL",
    "BOLSA MASA",
    "BOLSA BASURA",
    "BOLSA CAMISETA",
    "HILO",
    "GUANTES",
    "CAJA PIZA",
    "ACEITE",
    "SAL",
    "PIMIENTA",
]

NAIF_COST_CATEGORY_ITEMS = {
    "CARNE": ["MOLIDA COM", "MOLIDA ESP", "POLLO"],
    "VERDURA": ["AJO", "CEBOLLA", "TOMATE", "LIMON", "VERDEO", "PEREJIL", "PIM ROJO"],
    "MASA": ["HARINA", "LEVADURA", "AZUCAR", "HUEVOS", "ACEITE", "SAL"],
    "DESCARTABLE": [
        "CAJA GRAN",
        "CAJA CHIC",
        "PAPEL SERV",
        "FOLEX GRAN",
        "FOLEX CHIC",
        "BOLSA CEBOL",
        "BOLSA MASA",
        "BOLSA BASURA",
        "BOLSA CAMISETA",
        "HILO",
        "GUANTES",
        "CAJA PIZA",
    ],
    "ESPECIAS": ["ACEITE", "SAL", "PIMIENTA"],
    "EMBUTIDO": ["JAMONADA", "SALAME", "MUZZA"],
    "LIMPIEZA": ["CLORO", "DETERGENTE", "DESINFECTANTE"],
    "EMPLEADOS": ["MELINA"],
    "SOCIA MARI": ["SOCIA MARI"],
    "OTRO": ["Costo general"],
}

NAIF_CLIENT_SUGGESTIONS = [
    "Particular",
    "Ricardo",
    "laprida",
    "Club Maipu",
    "Saul",
    "Belen",
    "Illia 2",
    "Maxi",
    "Roxana",
    "USA",
    "Pausa",
    "M.Moreno",
    "Villalpando",
    "Viandas",
    "Solares",
    "terminal",
    "Agustin",
    "Santi",
    "Duarte Quiros",
    "Colegium",
]


RODRIGUEZ_PRODUCT_CHOICES = [
    ("pollo-entero", "Pollo entero"),
    ("pechuga", "Pechuga"),
    ("pata-muslo", "Pata muslo"),
    ("alitas", "Alitas"),
    ("milanesas-pollo", "Milanesas de pollo"),
    ("hamburguesas-pollo", "Hamburguesas de pollo"),
    ("huevos-maple", "Maple de huevos"),
    ("huevos-docena", "Docena de huevos"),
    ("suprema", "Suprema"),
    ("menudos", "Menudos"),
    ("envio", "Envio"),
]

RODRIGUEZ_COST_ITEMS = [
    "POLLO ENTERO",
    "PECHUGA",
    "PATA MUSLO",
    "ALITAS",
    "SUPREMA",
    "MILANESAS",
    "HAMBURGUESAS",
    "HUEVOS",
    "MAPLES",
    "BOLSAS",
    "BANDEJAS",
    "FILM",
    "ETIQUETAS",
    "CAJAS",
    "HIELO",
    "COMBUSTIBLE",
    "MANTENIMIENTO",
    "LIMPIEZA",
    "LUZ",
    "GAS",
]

RODRIGUEZ_COST_CATEGORY_ITEMS = {
    "MERCADERIA": ["POLLO ENTERO", "PECHUGA", "PATA MUSLO", "ALITAS", "SUPREMA", "HUEVOS"],
    "ELABORADOS": ["MILANESAS", "HAMBURGUESAS"],
    "EMPAQUE": ["MAPLES", "BOLSAS", "BANDEJAS", "FILM", "ETIQUETAS", "CAJAS"],
    "FRIO": ["HIELO", "MANTENIMIENTO"],
    "LOGISTICA": ["COMBUSTIBLE", "REPARTO", "FLETE"],
    "SERVICIOS": ["LUZ", "GAS", "INTERNET", "TELEFONO"],
    "LIMPIEZA": ["LIMPIEZA", "DETERGENTE", "DESINFECTANTE"],
    "SUELDOS": ["REPARTIDOR", "OPERARIO", "ADMINISTRACION"],
    "OTRO": ["Costo general"],
}

RODRIGUEZ_CLIENT_SUGGESTIONS = [
    "Particular",
    "Carniceria Centro",
    "Rotiseria Avenida",
    "Almacen Norte",
    "Super Barrio",
    "Polleria San Martin",
    "Comedor Escolar",
    "Restaurant Plaza",
    "Kiosco Terminal",
    "Distribucion mayorista",
]


def _ensure_naif_user():
    from django.contrib.auth.models import User

    user, created = User.objects.get_or_create(
        username="dino",
        defaults={"first_name": "Dino", "email": "dino@naif.local"},
    )
    if created or not user.check_password("naif"):
        user.set_password("naif")
        user.save(update_fields=["password"])
    return user


def _ensure_rodriguez_user():
    from django.contrib.auth.models import User

    user, created = User.objects.get_or_create(
        username="joel",
        defaults={"first_name": "Joel", "email": "joel@distribuidorarodriguez.local"},
    )
    if created or not user.check_password("distribucion"):
        user.set_password("distribucion")
        user.save(update_fields=["password"])
    return user


def _money_from_post(value):
    raw = str(value or "0").strip().replace("$", "").replace(" ", "")
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        decimals = raw.rsplit(",", 1)[1]
        raw = raw.replace(",", "") if len(decimals) == 3 else raw.replace(",", ".")
    elif "." in raw:
        decimals = raw.rsplit(".", 1)[1]
        if len(decimals) == 3:
            raw = raw.replace(".", "")
    else:
        raw = raw.replace(",", ".")
    try:
        return Decimal(raw or "0")
    except Exception:
        return Decimal("0")


def _naif_date(value):
    from django.utils.dateparse import parse_date

    return parse_date(value or "") or timezone.localdate()


def _month_start(value):
    return date(value.year, value.month, 1)


def _add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def _month_range(start, end):
    current = _month_start(start)
    last = _month_start(end)
    while current <= last:
        yield current
        current = _add_months(current, 1)


def _naif_required(request):
    return request.session.get("naif_pymes_auth") and request.user.is_authenticated and request.user.username == "dino"


def _rodriguez_required(request):
    return request.session.get("rodriguez_pymes_auth") and request.user.is_authenticated and request.user.username == "joel"


def pymes_naif(request):
    from django.contrib.auth import login, logout
    from django.contrib import messages
    from django.db.models import Avg, Count, Sum
    from django.shortcuts import get_object_or_404
    from .models import NaifClient, NaifCost, NaifCostCategory, NaifCostItem, NaifProduct, NaifSale

    _ensure_naif_user()

    if request.GET.get("salir") == "1":
        request.session.pop("naif_pymes_auth", None)
        logout(request)
        return redirect("pymes_naif")

    if not _naif_required(request):
        context = {"login_error": ""}
        if request.method == "POST":
            username = request.POST.get("username", "").strip().lower()
            password = request.POST.get("password", "")
            user = _ensure_naif_user()
            if username == "dino" and user.check_password(password):
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
                request.session["naif_pymes_auth"] = True
                return redirect("pymes_naif")
            context["login_error"] = "Usuario o contrasena incorrectos."
        return render(request, "calculadora/pymes_naif.html", context)

    selected_date = _naif_date(request.GET.get("fecha") or request.POST.get("date") or request.POST.get("return_fecha"))

    def redirect_selected_date(date_value=None):
        target_date = _naif_date(date_value) if date_value else selected_date
        return redirect(f"{request.path}?fecha={target_date.isoformat()}")

    if request.method == "POST":
        action = request.POST.get("action")
        def product_name_for(code):
            product_name = dict(NAIF_PRODUCT_CHOICES).get(code, code)
            custom_product = NaifProduct.objects.filter(code=code, active=True).first()
            return custom_product.name if custom_product else product_name

        if action == "sale":
            code = request.POST.get("product_code", "").strip()
            client_name = request.POST.get("client", "").strip() or "Particular"
            client_obj = NaifClient.objects.filter(name__iexact=client_name).first()
            if not client_obj:
                client_obj = NaifClient.objects.create(name=client_name)
            unit_price = _money_from_post(request.POST.get("unit_price"))
            if unit_price <= 0 and client_obj.current_price > 0:
                unit_price = client_obj.current_price
            NaifSale.objects.create(
                created_by=request.user,
                date=_naif_date(request.POST.get("date")),
                client=client_name,
                product_code=code,
                product_name=product_name_for(code),
                quantity=_money_from_post(request.POST.get("quantity")),
                unit_price=unit_price,
                paid=request.POST.get("paid") == "on",
                notes=request.POST.get("notes", "").strip(),
            )
            messages.success(request, "Venta guardada.")
            return redirect_selected_date(request.POST.get("date"))
        if action == "sale_update":
            sale = get_object_or_404(NaifSale, pk=request.POST.get("sale_id"))
            code = request.POST.get("product_code", "").strip()
            client_name = request.POST.get("client", "").strip() or "Particular"
            client_obj, _created = NaifClient.objects.get_or_create(name=client_name)
            unit_price = _money_from_post(request.POST.get("unit_price"))
            if unit_price <= 0 and client_obj.current_price > 0:
                unit_price = client_obj.current_price
            sale.date = _naif_date(request.POST.get("date"))
            sale.client = client_name
            sale.product_code = code
            sale.product_name = product_name_for(code)
            sale.quantity = _money_from_post(request.POST.get("quantity"))
            sale.unit_price = unit_price
            sale.paid = request.POST.get("paid") == "on"
            sale.notes = request.POST.get("notes", "").strip()
            sale.save()
            messages.success(request, "Venta actualizada.")
            return redirect_selected_date(request.POST.get("date"))
        if action == "sale_delete":
            sale = get_object_or_404(NaifSale, pk=request.POST.get("sale_id"))
            sale.delete()
            messages.success(request, "Venta eliminada.")
            return redirect_selected_date()
        if action == "product":
            name = request.POST.get("product_name", "").strip()
            price = _money_from_post(request.POST.get("suggested_price"))
            if name:
                code = f"custom-{uuid.uuid4().hex[:10]}"
                NaifProduct.objects.create(code=code, name=name, suggested_price=price)
                messages.success(request, "Producto agregado.")
            return redirect_selected_date()
        if action == "client":
            name = request.POST.get("client_name", "").strip()
            if name:
                client, _created = NaifClient.objects.get_or_create(name=name, defaults={"active": True})
                price = _money_from_post(request.POST.get("current_price"))
                if price > 0:
                    client.current_price = price
                    client.save(update_fields=["current_price"])
                messages.success(request, "Cliente agregado.")
            return redirect_selected_date()
        if action == "client_price_update":
            client_id = request.POST.get("client_id")
            if client_id:
                client = get_object_or_404(NaifClient, pk=client_id)
            else:
                client_name = request.POST.get("client_name", "").strip()
                client, _created = NaifClient.objects.get_or_create(name=client_name, defaults={"active": True})
            client.current_price = _money_from_post(request.POST.get("current_price"))
            client.active = request.POST.get("active") == "on"
            client.save(update_fields=["current_price", "active"])
            messages.success(request, "Precio del cliente actualizado.")
            return redirect(f"{request.path}?tab=clientes")
        if action == "cost_type":
            category_name = request.POST.get("category_name", "").strip().upper()
            item_name = request.POST.get("item_name", "").strip().upper()
            if category_name:
                category, _created = NaifCostCategory.objects.get_or_create(name=category_name, defaults={"active": True})
                if item_name:
                    NaifCostItem.objects.get_or_create(category=category, name=item_name, defaults={"active": True})
                messages.success(request, "Tipo de costo agregado.")
            return redirect_selected_date()
        if action == "cost_category_metrics_toggle":
            category_name = request.POST.get("category_name", "").strip()
            if category_name:
                category, _created = NaifCostCategory.objects.get_or_create(name=category_name, defaults={"active": True})
                category.show_in_metrics = not category.show_in_metrics
                category.save(update_fields=["show_in_metrics"])
                messages.success(request, "Vista del rubro actualizada.")
            return redirect(f"{request.path}?tab=metricas")
        if action == "cost":
            NaifCost.objects.create(
                created_by=request.user,
                date=_naif_date(request.POST.get("date")),
                category=request.POST.get("category", "").strip(),
                item=request.POST.get("item", "").strip() or "Costo general",
                supplier=request.POST.get("supplier", "").strip(),
                amount=_money_from_post(request.POST.get("amount")),
                paid=request.POST.get("paid") == "on",
                notes=request.POST.get("notes", "").strip(),
            )
            messages.success(request, "Costo guardado.")
            return redirect_selected_date(request.POST.get("date"))
        if action == "cost_update":
            cost = get_object_or_404(NaifCost, pk=request.POST.get("cost_id"))
            cost.date = _naif_date(request.POST.get("date"))
            cost.category = request.POST.get("category", "").strip()
            cost.item = request.POST.get("item", "").strip() or "Costo general"
            cost.supplier = request.POST.get("supplier", "").strip()
            cost.amount = _money_from_post(request.POST.get("amount"))
            cost.paid = request.POST.get("paid") == "on"
            cost.notes = request.POST.get("notes", "").strip()
            cost.save()
            messages.success(request, "Costo actualizado.")
            return redirect_selected_date(request.POST.get("date"))
        if action == "cost_delete":
            cost = get_object_or_404(NaifCost, pk=request.POST.get("cost_id"))
            cost.delete()
            messages.success(request, "Costo eliminado.")
            return redirect_selected_date()

    today = timezone.localdate()
    available_years = sorted(
        {year_date.year for year_date in NaifSale.objects.dates("date", "year")}
        | {year_date.year for year_date in NaifCost.objects.dates("date", "year")}
        | {today.year},
        reverse=True,
    )
    months = [
        (1, "Enero"),
        (2, "Febrero"),
        (3, "Marzo"),
        (4, "Abril"),
        (5, "Mayo"),
        (6, "Junio"),
        (7, "Julio"),
        (8, "Agosto"),
        (9, "Septiembre"),
        (10, "Octubre"),
        (11, "Noviembre"),
        (12, "Diciembre"),
    ]
    selected_years = []
    for value in request.GET.getlist("anio"):
        try:
            year = int(value)
        except (TypeError, ValueError):
            continue
        if year in available_years:
            selected_years.append(year)
    if not selected_years:
        selected_years = [selected_date.year]

    selected_months = []
    for value in request.GET.getlist("mes"):
        try:
            month = int(value)
        except (TypeError, ValueError):
            continue
        if 1 <= month <= 12:
            selected_months.append(month)
    has_manual_period = bool(request.GET.getlist("anio") or request.GET.getlist("mes"))
    period_range = request.GET.get("rango", "6m")
    if has_manual_period:
        period_range = "custom"
        if not selected_months:
            selected_months = [selected_date.month]
    elif period_range not in {"6m", "12m", "ytd"}:
        period_range = "6m"

    range_end = today
    if period_range == "12m":
        range_start = _add_months(_month_start(today), -11)
    elif period_range == "ytd":
        range_start = date(today.year, 1, 1)
    elif period_range == "custom":
        range_start = None
    else:
        range_start = _add_months(_month_start(today), -5)

    if not has_manual_period:
        range_months = list(_month_range(range_start, range_end))
        selected_years = sorted({month_date.year for month_date in range_months}, reverse=True)
        selected_months = sorted({month_date.month for month_date in range_months})
    selected_month_names = [name for number, name in months if number in selected_months]
    range_labels = {"6m": "Ultimos 6 meses", "12m": "Ultimos 12 meses", "ytd": f"Anio actual {today.year}"}
    period_label = range_labels.get(period_range) or f"{', '.join(str(year) for year in selected_years)} - {', '.join(selected_month_names)}"

    day_sales = NaifSale.objects.filter(date=selected_date)
    day_costs = NaifCost.objects.filter(date=selected_date)
    sales_total = day_sales.aggregate(total=Sum("total"))["total"] or Decimal("0")
    costs_total = day_costs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    if period_range == "custom":
        period_sales_qs = NaifSale.objects.filter(date__year__in=selected_years, date__month__in=selected_months)
        period_costs_qs = NaifCost.objects.filter(date__year__in=selected_years, date__month__in=selected_months)
    else:
        period_sales_qs = NaifSale.objects.filter(date__gte=range_start, date__lte=range_end)
        period_costs_qs = NaifCost.objects.filter(date__gte=range_start, date__lte=range_end)
    period_sales = period_sales_qs.aggregate(total=Sum("total"))["total"] or Decimal("0")
    period_costs = period_costs_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    period_result = period_sales - period_costs
    sale_count = period_sales_qs.count()
    cost_count = period_costs_qs.count()
    units_sold = period_sales_qs.aggregate(total=Sum("quantity"))["total"] or Decimal("0")
    avg_price_per_unit = (period_sales / units_sold) if units_sold else Decimal("0")
    margin_percent = (period_result / period_sales * Decimal("100")) if period_sales else Decimal("0")
    top_product = (
        period_sales_qs.exclude(product_name="")
        .values("product_name")
        .annotate(total=Sum("total"), units=Sum("quantity"), count=Count("id"))
        .order_by("-total")
        .first()
    )
    top_client = (
        period_sales_qs.values("client")
        .annotate(total=Sum("total"), count=Count("id"))
        .order_by("-total")
        .first()
    )
    product_choices = list(NAIF_PRODUCT_CHOICES)
    custom_products = list(NaifProduct.objects.filter(active=True).values_list("code", "name"))
    product_choices.extend(custom_products)
    product_prices = {}
    for code, _name in product_choices:
        last_sale = NaifSale.objects.filter(product_code=code, unit_price__gt=0).order_by("-date", "-created_at").first()
        custom_product = NaifProduct.objects.filter(code=code, active=True).first()
        product_prices[code] = str(last_sale.unit_price) if last_sale else (str(custom_product.suggested_price) if custom_product else "")
    client_prices = {
        client.name: str(client.current_price)
        for client in NaifClient.objects.filter(active=True, current_price__gt=0)
    }

    sales_by_day = {
        row["date"]: row["total"] or Decimal("0")
        for row in period_sales_qs.values("date").annotate(total=Sum("total"))
    }
    units_by_day = {
        row["date"]: row["units"] or Decimal("0")
        for row in period_sales_qs.values("date").annotate(units=Sum("quantity"))
    }
    costs_by_day = {
        row["date"]: row["total"] or Decimal("0")
        for row in period_costs_qs.values("date").annotate(total=Sum("amount"))
    }
    daily_rows = []
    for day in sorted(set(sales_by_day) | set(costs_by_day)):
        day_sale_total = sales_by_day.get(day, Decimal("0"))
        day_cost_total = costs_by_day.get(day, Decimal("0"))
        daily_rows.append({
            "label": day.strftime("%d/%m/%y"),
            "sales": day_sale_total,
            "units": units_by_day.get(day, Decimal("0")),
            "costs": day_cost_total,
            "result": day_sale_total - day_cost_total,
        })
    if len(daily_rows) > 18:
        daily_rows = daily_rows[-18:]
    daily_average = {"sales": Decimal("0"), "units": Decimal("0")}
    if daily_rows:
        daily_average = {
            "sales": sum(row["sales"] for row in daily_rows) / Decimal(len(daily_rows)),
            "units": sum(row["units"] for row in daily_rows) / Decimal(len(daily_rows)),
        }
    max_daily = max([row["sales"] for row in daily_rows] + [Decimal("1")])
    for row in daily_rows:
        row["sales_percent"] = int((row["sales"] / max_daily) * Decimal("100")) if max_daily else 0
        row["costs_percent"] = int((row["costs"] / max_daily) * Decimal("100")) if max_daily else 0

    existing_cost_categories = set(
        NaifCost.objects.exclude(category="").values_list("category", flat=True).distinct()
    )
    for category_name in existing_cost_categories | set(NAIF_COST_CATEGORY_ITEMS.keys()):
        NaifCostCategory.objects.get_or_create(name=category_name, defaults={"active": True, "show_in_metrics": True})
    hidden_metric_categories = set(
        NaifCostCategory.objects.filter(show_in_metrics=False).values_list("name", flat=True)
    )
    cost_bars = list(
        period_costs_qs.exclude(category="").exclude(category__in=hidden_metric_categories)
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    max_cost = max([row["total"] for row in cost_bars] + [Decimal("1")])
    for row in cost_bars:
        row["percent"] = int((row["total"] / max_cost) * Decimal("100")) if max_cost else 0
    hidden_cost_bars = [
        {"category": name}
        for name in sorted(hidden_metric_categories)
        if name in existing_cost_categories or name in NAIF_COST_CATEGORY_ITEMS
    ]
    max_period = max(period_sales, period_costs, Decimal("1"))
    period_bars = [
        {"label": "Ventas", "total": period_sales, "percent": int((period_sales / max_period) * Decimal("100"))},
        {"label": "Costos", "total": period_costs, "percent": int((period_costs / max_period) * Decimal("100"))},
    ]
    month_names = dict(months)
    monthly_sales = {
        (row["year"], row["month"]): row["total"] or Decimal("0")
        for row in period_sales_qs.annotate(year=ExtractYear("date"), month=ExtractMonth("date"))
        .values("year", "month")
        .annotate(total=Sum("total"))
    }
    monthly_costs = {
        (row["year"], row["month"]): row["total"] or Decimal("0")
        for row in period_costs_qs.annotate(year=ExtractYear("date"), month=ExtractMonth("date"))
        .values("year", "month")
        .annotate(total=Sum("amount"))
    }
    monthly_units_map = {
        (row["year"], row["month"]): row["units"] or Decimal("0")
        for row in period_sales_qs.annotate(year=ExtractYear("date"), month=ExtractMonth("date"))
        .values("year", "month")
        .annotate(units=Sum("quantity"))
    }
    if period_range == "custom":
        monthly_keys = sorted(set(monthly_sales) | set(monthly_costs) | set(monthly_units_map))
    else:
        monthly_keys = [(month_date.year, month_date.month) for month_date in _month_range(range_start, range_end)]
    monthly_units = []
    for year, month in monthly_keys:
        sales = monthly_sales.get((year, month), Decimal("0"))
        costs = monthly_costs.get((year, month), Decimal("0"))
        monthly_units.append({
            "year": year,
            "month": month,
            "label": f"{month_names.get(month, month)[:3]} {str(year)[-2:]}",
            "units": monthly_units_map.get((year, month), Decimal("0")),
            "sales": sales,
            "costs": costs,
            "result": sales - costs,
        })
    max_units = max([row["units"] for row in monthly_units] + [Decimal("1")])
    result_values = [row["result"] for row in monthly_units]
    min_result = min(result_values + [Decimal("0")])
    max_result = max(result_values + [Decimal("1")])
    result_range = max_result - min_result or Decimal("1")
    line_points = []
    line_count = len(monthly_units)
    for row in monthly_units:
        row["percent"] = int((row["units"] / max_units) * Decimal("100")) if max_units else 0
        row["result_percent"] = int(((row["result"] - min_result) / result_range) * Decimal("100"))
        if line_count == 1:
            x = Decimal("50")
        else:
            x = (Decimal(str(monthly_units.index(row))) / Decimal(line_count - 1)) * Decimal("100")
        y = Decimal("92") - ((row["result"] - min_result) / result_range) * Decimal("78")
        line_points.append(f"{x:.2f},{y:.2f}")
    monthly_result_points = " ".join(line_points)

    cost_category_items = {category: set(items) for category, items in NAIF_COST_CATEGORY_ITEMS.items()}
    for category in NaifCostCategory.objects.filter(active=True):
        cost_category_items.setdefault(category.name, set())
    for item in NaifCostItem.objects.filter(active=True).select_related("category"):
        cost_category_items.setdefault(item.category.name, set()).add(item.name)
    for category, item in NaifCost.objects.exclude(category="").exclude(item="").values_list("category", "item").distinct():
        cost_category_items.setdefault(category, set()).add(item)
    cost_category_items = {
        category: sorted(items)
        for category, items in sorted(cost_category_items.items())
    }
    cost_per_unit = (period_costs / units_sold) if units_sold else Decimal("0")
    client_sales = {
        row["client"]: row
        for row in period_sales_qs.values("client")
        .annotate(total=Sum("total"), units=Sum("quantity"), avg_price=Avg("unit_price"), count=Count("id"))
    }
    client_objects = {client.name: client for client in NaifClient.objects.all()}
    client_names = sorted(set(client_sales) | set(client_objects), key=lambda value: value.lower())
    client_rows = []
    for name in client_names:
        sale_data = client_sales.get(name, {})
        total = sale_data.get("total") or Decimal("0")
        units = sale_data.get("units") or Decimal("0")
        client_obj = client_objects.get(name)
        latest_sale = NaifSale.objects.filter(client__iexact=name, unit_price__gt=0).order_by("-date", "-created_at").first()
        current_price = client_obj.current_price if client_obj else Decimal("0")
        client_rows.append({
            "id": client_obj.id if client_obj else "",
            "name": name,
            "units": units,
            "total": total,
            "gain": total - (cost_per_unit * units),
            "avg_price": sale_data.get("avg_price") or Decimal("0"),
            "current_price": current_price,
            "latest_price": latest_sale.unit_price if latest_sale else Decimal("0"),
            "active": client_obj.active if client_obj else True,
        })
    client_rows.sort(key=lambda row: row["total"], reverse=True)

    context = {
        "is_naif_auth": True,
        "selected_date": selected_date,
        "today": today,
        "period_label": period_label,
        "period_range": period_range,
        "selected_years": selected_years,
        "selected_months": selected_months,
        "available_years": available_years,
        "months": months,
        "product_choices": product_choices,
        "product_choices_json": json.dumps(product_choices),
        "product_prices_json": json.dumps(product_prices),
        "client_prices_json": json.dumps(client_prices),
        "cost_categories": list(cost_category_items.keys()),
        "cost_category_items": cost_category_items,
        "cost_category_items_json": json.dumps(cost_category_items),
        "cost_items": sorted(set(NAIF_COST_ITEMS)),
        "client_suggestions": sorted(
            set(NAIF_CLIENT_SUGGESTIONS)
            | set(NaifClient.objects.filter(active=True).values_list("name", flat=True))
        ),
        "day_sales": day_sales[:80],
        "day_costs": day_costs[:80],
        "recent_sales": NaifSale.objects.all()[:5],
        "recent_costs": NaifCost.objects.all()[:5],
        "sales_total": sales_total,
        "costs_total": costs_total,
        "day_result": sales_total - costs_total,
        "period_sales": period_sales,
        "period_costs": period_costs,
        "period_result": period_result,
        "avg_price_per_unit": avg_price_per_unit,
        "sale_count": sale_count,
        "cost_count": cost_count,
        "units_sold": units_sold,
        "margin_percent": margin_percent,
        "top_product": top_product,
        "top_client": top_client,
        "daily_rows": daily_rows,
        "daily_average": daily_average,
        "period_bars": period_bars,
        "cost_bars": cost_bars,
        "hidden_cost_bars": hidden_cost_bars,
        "monthly_units": monthly_units,
        "monthly_result_points": monthly_result_points,
        "client_rows": client_rows,
        "cost_per_unit": cost_per_unit,
        "unpaid_total": day_sales.filter(paid=False).aggregate(total=Sum("total"))["total"] or Decimal("0"),
        "period_unpaid_total": period_sales_qs.filter(paid=False).aggregate(total=Sum("total"))["total"] or Decimal("0"),
    }
    return render(request, "calculadora/pymes_naif.html", context)


def distribuidora_rodriguez(request):
    from django.contrib.auth import login, logout
    from django.contrib import messages
    from django.db.models import Avg, Count, Sum
    from django.shortcuts import get_object_or_404
    from .models import RodriguezClient, RodriguezCost, RodriguezCostCategory, RodriguezCostItem, RodriguezProduct, RodriguezSale

    _ensure_rodriguez_user()

    if request.GET.get("salir") == "1":
        request.session.pop("rodriguez_pymes_auth", None)
        logout(request)
        return redirect("distribuidora_rodriguez")

    if not _rodriguez_required(request):
        context = {"login_error": ""}
        if request.method == "POST":
            username = request.POST.get("username", "").strip().lower()
            password = request.POST.get("password", "")
            user = _ensure_rodriguez_user()
            if username == "joel" and user.check_password(password):
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
                request.session["rodriguez_pymes_auth"] = True
                return redirect("distribuidora_rodriguez")
            context["login_error"] = "Usuario o contrasena incorrectos."
        return render(request, "calculadora/distribuidora_rodriguez.html", context)

    selected_date = _naif_date(request.GET.get("fecha") or request.POST.get("date") or request.POST.get("return_fecha"))

    def redirect_selected_date(date_value=None):
        target_date = _naif_date(date_value) if date_value else selected_date
        return redirect(f"{request.path}?fecha={target_date.isoformat()}")

    if request.method == "POST":
        action = request.POST.get("action")
        def product_name_for(code):
            product_name = dict(RODRIGUEZ_PRODUCT_CHOICES).get(code, code)
            custom_product = RodriguezProduct.objects.filter(code=code, active=True).first()
            return custom_product.name if custom_product else product_name

        if action == "sale":
            code = request.POST.get("product_code", "").strip()
            client_name = request.POST.get("client", "").strip() or "Particular"
            client_obj = RodriguezClient.objects.filter(name__iexact=client_name).first()
            if not client_obj:
                client_obj = RodriguezClient.objects.create(name=client_name)
            unit_price = _money_from_post(request.POST.get("unit_price"))
            if unit_price <= 0 and client_obj.current_price > 0:
                unit_price = client_obj.current_price
            RodriguezSale.objects.create(
                created_by=request.user,
                date=_naif_date(request.POST.get("date")),
                client=client_name,
                product_code=code,
                product_name=product_name_for(code),
                quantity=_money_from_post(request.POST.get("quantity")),
                unit_price=unit_price,
                paid=request.POST.get("paid") == "on",
                notes=request.POST.get("notes", "").strip(),
            )
            messages.success(request, "Venta guardada.")
            return redirect_selected_date(request.POST.get("date"))
        if action == "sale_update":
            sale = get_object_or_404(RodriguezSale, pk=request.POST.get("sale_id"))
            code = request.POST.get("product_code", "").strip()
            client_name = request.POST.get("client", "").strip() or "Particular"
            client_obj, _created = RodriguezClient.objects.get_or_create(name=client_name)
            unit_price = _money_from_post(request.POST.get("unit_price"))
            if unit_price <= 0 and client_obj.current_price > 0:
                unit_price = client_obj.current_price
            sale.date = _naif_date(request.POST.get("date"))
            sale.client = client_name
            sale.product_code = code
            sale.product_name = product_name_for(code)
            sale.quantity = _money_from_post(request.POST.get("quantity"))
            sale.unit_price = unit_price
            sale.paid = request.POST.get("paid") == "on"
            sale.notes = request.POST.get("notes", "").strip()
            sale.save()
            messages.success(request, "Venta actualizada.")
            return redirect_selected_date(request.POST.get("date"))
        if action == "sale_delete":
            sale = get_object_or_404(RodriguezSale, pk=request.POST.get("sale_id"))
            sale.delete()
            messages.success(request, "Venta eliminada.")
            return redirect_selected_date()
        if action == "product":
            name = request.POST.get("product_name", "").strip()
            price = _money_from_post(request.POST.get("suggested_price"))
            if name:
                code = f"custom-{uuid.uuid4().hex[:10]}"
                RodriguezProduct.objects.create(code=code, name=name, suggested_price=price)
                messages.success(request, "Producto agregado.")
            return redirect_selected_date()
        if action == "client":
            name = request.POST.get("client_name", "").strip()
            if name:
                client, _created = RodriguezClient.objects.get_or_create(name=name, defaults={"active": True})
                price = _money_from_post(request.POST.get("current_price"))
                if price > 0:
                    client.current_price = price
                    client.save(update_fields=["current_price"])
                messages.success(request, "Cliente agregado.")
            return redirect_selected_date()
        if action == "client_price_update":
            client_id = request.POST.get("client_id")
            if client_id:
                client = get_object_or_404(RodriguezClient, pk=client_id)
            else:
                client_name = request.POST.get("client_name", "").strip()
                client, _created = RodriguezClient.objects.get_or_create(name=client_name, defaults={"active": True})
            client.current_price = _money_from_post(request.POST.get("current_price"))
            client.active = request.POST.get("active") == "on"
            client.save(update_fields=["current_price", "active"])
            messages.success(request, "Precio del cliente actualizado.")
            return redirect(f"{request.path}?tab=clientes")
        if action == "cost_type":
            category_name = request.POST.get("category_name", "").strip().upper()
            item_name = request.POST.get("item_name", "").strip().upper()
            if category_name:
                category, _created = RodriguezCostCategory.objects.get_or_create(name=category_name, defaults={"active": True})
                if item_name:
                    RodriguezCostItem.objects.get_or_create(category=category, name=item_name, defaults={"active": True})
                messages.success(request, "Tipo de costo agregado.")
            return redirect_selected_date()
        if action == "cost_category_metrics_toggle":
            category_name = request.POST.get("category_name", "").strip()
            if category_name:
                category, _created = RodriguezCostCategory.objects.get_or_create(name=category_name, defaults={"active": True})
                category.show_in_metrics = not category.show_in_metrics
                category.save(update_fields=["show_in_metrics"])
                messages.success(request, "Vista del rubro actualizada.")
            return redirect(f"{request.path}?tab=metricas")
        if action == "cost":
            RodriguezCost.objects.create(
                created_by=request.user,
                date=_naif_date(request.POST.get("date")),
                category=request.POST.get("category", "").strip(),
                item=request.POST.get("item", "").strip() or "Costo general",
                supplier=request.POST.get("supplier", "").strip(),
                amount=_money_from_post(request.POST.get("amount")),
                paid=request.POST.get("paid") == "on",
                notes=request.POST.get("notes", "").strip(),
            )
            messages.success(request, "Costo guardado.")
            return redirect_selected_date(request.POST.get("date"))
        if action == "cost_update":
            cost = get_object_or_404(RodriguezCost, pk=request.POST.get("cost_id"))
            cost.date = _naif_date(request.POST.get("date"))
            cost.category = request.POST.get("category", "").strip()
            cost.item = request.POST.get("item", "").strip() or "Costo general"
            cost.supplier = request.POST.get("supplier", "").strip()
            cost.amount = _money_from_post(request.POST.get("amount"))
            cost.paid = request.POST.get("paid") == "on"
            cost.notes = request.POST.get("notes", "").strip()
            cost.save()
            messages.success(request, "Costo actualizado.")
            return redirect_selected_date(request.POST.get("date"))
        if action == "cost_delete":
            cost = get_object_or_404(RodriguezCost, pk=request.POST.get("cost_id"))
            cost.delete()
            messages.success(request, "Costo eliminado.")
            return redirect_selected_date()

    today = timezone.localdate()
    available_years = sorted(
        {year_date.year for year_date in RodriguezSale.objects.dates("date", "year")}
        | {year_date.year for year_date in RodriguezCost.objects.dates("date", "year")}
        | {today.year},
        reverse=True,
    )
    months = [
        (1, "Enero"),
        (2, "Febrero"),
        (3, "Marzo"),
        (4, "Abril"),
        (5, "Mayo"),
        (6, "Junio"),
        (7, "Julio"),
        (8, "Agosto"),
        (9, "Septiembre"),
        (10, "Octubre"),
        (11, "Noviembre"),
        (12, "Diciembre"),
    ]
    selected_years = []
    for value in request.GET.getlist("anio"):
        try:
            year = int(value)
        except (TypeError, ValueError):
            continue
        if year in available_years:
            selected_years.append(year)
    if not selected_years:
        selected_years = [selected_date.year]

    selected_months = []
    for value in request.GET.getlist("mes"):
        try:
            month = int(value)
        except (TypeError, ValueError):
            continue
        if 1 <= month <= 12:
            selected_months.append(month)
    has_manual_period = bool(request.GET.getlist("anio") or request.GET.getlist("mes"))
    period_range = request.GET.get("rango", "6m")
    if has_manual_period:
        period_range = "custom"
        if not selected_months:
            selected_months = [selected_date.month]
    elif period_range not in {"6m", "12m", "ytd"}:
        period_range = "6m"

    range_end = today
    if period_range == "12m":
        range_start = _add_months(_month_start(today), -11)
    elif period_range == "ytd":
        range_start = date(today.year, 1, 1)
    elif period_range == "custom":
        range_start = None
    else:
        range_start = _add_months(_month_start(today), -5)

    if not has_manual_period:
        range_months = list(_month_range(range_start, range_end))
        selected_years = sorted({month_date.year for month_date in range_months}, reverse=True)
        selected_months = sorted({month_date.month for month_date in range_months})
    selected_month_names = [name for number, name in months if number in selected_months]
    range_labels = {"6m": "Ultimos 6 meses", "12m": "Ultimos 12 meses", "ytd": f"Anio actual {today.year}"}
    period_label = range_labels.get(period_range) or f"{', '.join(str(year) for year in selected_years)} - {', '.join(selected_month_names)}"

    day_sales = RodriguezSale.objects.filter(date=selected_date)
    day_costs = RodriguezCost.objects.filter(date=selected_date)
    sales_total = day_sales.aggregate(total=Sum("total"))["total"] or Decimal("0")
    costs_total = day_costs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    if period_range == "custom":
        period_sales_qs = RodriguezSale.objects.filter(date__year__in=selected_years, date__month__in=selected_months)
        period_costs_qs = RodriguezCost.objects.filter(date__year__in=selected_years, date__month__in=selected_months)
    else:
        period_sales_qs = RodriguezSale.objects.filter(date__gte=range_start, date__lte=range_end)
        period_costs_qs = RodriguezCost.objects.filter(date__gte=range_start, date__lte=range_end)
    period_sales = period_sales_qs.aggregate(total=Sum("total"))["total"] or Decimal("0")
    period_costs = period_costs_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    period_result = period_sales - period_costs
    sale_count = period_sales_qs.count()
    cost_count = period_costs_qs.count()
    units_sold = period_sales_qs.aggregate(total=Sum("quantity"))["total"] or Decimal("0")
    avg_price_per_unit = (period_sales / units_sold) if units_sold else Decimal("0")
    margin_percent = (period_result / period_sales * Decimal("100")) if period_sales else Decimal("0")
    top_product = (
        period_sales_qs.exclude(product_name="")
        .values("product_name")
        .annotate(total=Sum("total"), units=Sum("quantity"), count=Count("id"))
        .order_by("-total")
        .first()
    )
    top_client = (
        period_sales_qs.values("client")
        .annotate(total=Sum("total"), count=Count("id"))
        .order_by("-total")
        .first()
    )
    product_choices = list(RODRIGUEZ_PRODUCT_CHOICES)
    custom_products = list(RodriguezProduct.objects.filter(active=True).values_list("code", "name"))
    product_choices.extend(custom_products)
    product_prices = {}
    for code, _name in product_choices:
        last_sale = RodriguezSale.objects.filter(product_code=code, unit_price__gt=0).order_by("-date", "-created_at").first()
        custom_product = RodriguezProduct.objects.filter(code=code, active=True).first()
        product_prices[code] = str(last_sale.unit_price) if last_sale else (str(custom_product.suggested_price) if custom_product else "")
    client_prices = {
        client.name: str(client.current_price)
        for client in RodriguezClient.objects.filter(active=True, current_price__gt=0)
    }

    sales_by_day = {
        row["date"]: row["total"] or Decimal("0")
        for row in period_sales_qs.values("date").annotate(total=Sum("total"))
    }
    units_by_day = {
        row["date"]: row["units"] or Decimal("0")
        for row in period_sales_qs.values("date").annotate(units=Sum("quantity"))
    }
    costs_by_day = {
        row["date"]: row["total"] or Decimal("0")
        for row in period_costs_qs.values("date").annotate(total=Sum("amount"))
    }
    daily_rows = []
    for day in sorted(set(sales_by_day) | set(costs_by_day)):
        day_sale_total = sales_by_day.get(day, Decimal("0"))
        day_cost_total = costs_by_day.get(day, Decimal("0"))
        daily_rows.append({
            "label": day.strftime("%d/%m/%y"),
            "sales": day_sale_total,
            "units": units_by_day.get(day, Decimal("0")),
            "costs": day_cost_total,
            "result": day_sale_total - day_cost_total,
        })
    if len(daily_rows) > 18:
        daily_rows = daily_rows[-18:]
    daily_average = {"sales": Decimal("0"), "units": Decimal("0")}
    if daily_rows:
        daily_average = {
            "sales": sum(row["sales"] for row in daily_rows) / Decimal(len(daily_rows)),
            "units": sum(row["units"] for row in daily_rows) / Decimal(len(daily_rows)),
        }
    max_daily = max([row["sales"] for row in daily_rows] + [Decimal("1")])
    for row in daily_rows:
        row["sales_percent"] = int((row["sales"] / max_daily) * Decimal("100")) if max_daily else 0
        row["costs_percent"] = int((row["costs"] / max_daily) * Decimal("100")) if max_daily else 0

    existing_cost_categories = set(
        RodriguezCost.objects.exclude(category="").values_list("category", flat=True).distinct()
    )
    for category_name in existing_cost_categories | set(RODRIGUEZ_COST_CATEGORY_ITEMS.keys()):
        RodriguezCostCategory.objects.get_or_create(name=category_name, defaults={"active": True, "show_in_metrics": True})
    hidden_metric_categories = set(
        RodriguezCostCategory.objects.filter(show_in_metrics=False).values_list("name", flat=True)
    )
    cost_bars = list(
        period_costs_qs.exclude(category="").exclude(category__in=hidden_metric_categories)
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    max_cost = max([row["total"] for row in cost_bars] + [Decimal("1")])
    for row in cost_bars:
        row["percent"] = int((row["total"] / max_cost) * Decimal("100")) if max_cost else 0
    hidden_cost_bars = [
        {"category": name}
        for name in sorted(hidden_metric_categories)
        if name in existing_cost_categories or name in RODRIGUEZ_COST_CATEGORY_ITEMS
    ]
    max_period = max(period_sales, period_costs, Decimal("1"))
    period_bars = [
        {"label": "Ventas", "total": period_sales, "percent": int((period_sales / max_period) * Decimal("100"))},
        {"label": "Costos", "total": period_costs, "percent": int((period_costs / max_period) * Decimal("100"))},
    ]
    month_names = dict(months)
    monthly_sales = {
        (row["year"], row["month"]): row["total"] or Decimal("0")
        for row in period_sales_qs.annotate(year=ExtractYear("date"), month=ExtractMonth("date"))
        .values("year", "month")
        .annotate(total=Sum("total"))
    }
    monthly_costs = {
        (row["year"], row["month"]): row["total"] or Decimal("0")
        for row in period_costs_qs.annotate(year=ExtractYear("date"), month=ExtractMonth("date"))
        .values("year", "month")
        .annotate(total=Sum("amount"))
    }
    monthly_units_map = {
        (row["year"], row["month"]): row["units"] or Decimal("0")
        for row in period_sales_qs.annotate(year=ExtractYear("date"), month=ExtractMonth("date"))
        .values("year", "month")
        .annotate(units=Sum("quantity"))
    }
    if period_range == "custom":
        monthly_keys = sorted(set(monthly_sales) | set(monthly_costs) | set(monthly_units_map))
    else:
        monthly_keys = [(month_date.year, month_date.month) for month_date in _month_range(range_start, range_end)]
    monthly_units = []
    for year, month in monthly_keys:
        sales = monthly_sales.get((year, month), Decimal("0"))
        costs = monthly_costs.get((year, month), Decimal("0"))
        monthly_units.append({
            "year": year,
            "month": month,
            "label": f"{month_names.get(month, month)[:3]} {str(year)[-2:]}",
            "units": monthly_units_map.get((year, month), Decimal("0")),
            "sales": sales,
            "costs": costs,
            "result": sales - costs,
        })
    max_units = max([row["units"] for row in monthly_units] + [Decimal("1")])
    result_values = [row["result"] for row in monthly_units]
    min_result = min(result_values + [Decimal("0")])
    max_result = max(result_values + [Decimal("1")])
    result_range = max_result - min_result or Decimal("1")
    line_points = []
    line_count = len(monthly_units)
    for row in monthly_units:
        row["percent"] = int((row["units"] / max_units) * Decimal("100")) if max_units else 0
        row["result_percent"] = int(((row["result"] - min_result) / result_range) * Decimal("100"))
        if line_count == 1:
            x = Decimal("50")
        else:
            x = (Decimal(str(monthly_units.index(row))) / Decimal(line_count - 1)) * Decimal("100")
        y = Decimal("92") - ((row["result"] - min_result) / result_range) * Decimal("78")
        line_points.append(f"{x:.2f},{y:.2f}")
    monthly_result_points = " ".join(line_points)

    cost_category_items = {category: set(items) for category, items in RODRIGUEZ_COST_CATEGORY_ITEMS.items()}
    for category in RodriguezCostCategory.objects.filter(active=True):
        cost_category_items.setdefault(category.name, set())
    for item in RodriguezCostItem.objects.filter(active=True).select_related("category"):
        cost_category_items.setdefault(item.category.name, set()).add(item.name)
    for category, item in RodriguezCost.objects.exclude(category="").exclude(item="").values_list("category", "item").distinct():
        cost_category_items.setdefault(category, set()).add(item)
    cost_category_items = {
        category: sorted(items)
        for category, items in sorted(cost_category_items.items())
    }
    cost_per_unit = (period_costs / units_sold) if units_sold else Decimal("0")
    client_sales = {
        row["client"]: row
        for row in period_sales_qs.values("client")
        .annotate(total=Sum("total"), units=Sum("quantity"), avg_price=Avg("unit_price"), count=Count("id"))
    }
    client_objects = {client.name: client for client in RodriguezClient.objects.all()}
    client_names = sorted(set(client_sales) | set(client_objects), key=lambda value: value.lower())
    client_rows = []
    for name in client_names:
        sale_data = client_sales.get(name, {})
        total = sale_data.get("total") or Decimal("0")
        units = sale_data.get("units") or Decimal("0")
        client_obj = client_objects.get(name)
        latest_sale = RodriguezSale.objects.filter(client__iexact=name, unit_price__gt=0).order_by("-date", "-created_at").first()
        current_price = client_obj.current_price if client_obj else Decimal("0")
        client_rows.append({
            "id": client_obj.id if client_obj else "",
            "name": name,
            "units": units,
            "total": total,
            "gain": total - (cost_per_unit * units),
            "avg_price": sale_data.get("avg_price") or Decimal("0"),
            "current_price": current_price,
            "latest_price": latest_sale.unit_price if latest_sale else Decimal("0"),
            "active": client_obj.active if client_obj else True,
        })
    client_rows.sort(key=lambda row: row["total"], reverse=True)

    context = {
        "is_naif_auth": True,
        "selected_date": selected_date,
        "today": today,
        "period_label": period_label,
        "period_range": period_range,
        "selected_years": selected_years,
        "selected_months": selected_months,
        "available_years": available_years,
        "months": months,
        "product_choices": product_choices,
        "product_choices_json": json.dumps(product_choices),
        "product_prices_json": json.dumps(product_prices),
        "client_prices_json": json.dumps(client_prices),
        "cost_categories": list(cost_category_items.keys()),
        "cost_category_items": cost_category_items,
        "cost_category_items_json": json.dumps(cost_category_items),
        "cost_items": sorted(set(RODRIGUEZ_COST_ITEMS)),
        "client_suggestions": sorted(
            set(RODRIGUEZ_CLIENT_SUGGESTIONS)
            | set(RodriguezClient.objects.filter(active=True).values_list("name", flat=True))
        ),
        "day_sales": day_sales[:80],
        "day_costs": day_costs[:80],
        "recent_sales": RodriguezSale.objects.all()[:5],
        "recent_costs": RodriguezCost.objects.all()[:5],
        "sales_total": sales_total,
        "costs_total": costs_total,
        "day_result": sales_total - costs_total,
        "period_sales": period_sales,
        "period_costs": period_costs,
        "period_result": period_result,
        "avg_price_per_unit": avg_price_per_unit,
        "sale_count": sale_count,
        "cost_count": cost_count,
        "units_sold": units_sold,
        "margin_percent": margin_percent,
        "top_product": top_product,
        "top_client": top_client,
        "daily_rows": daily_rows,
        "daily_average": daily_average,
        "period_bars": period_bars,
        "cost_bars": cost_bars,
        "hidden_cost_bars": hidden_cost_bars,
        "monthly_units": monthly_units,
        "monthly_result_points": monthly_result_points,
        "client_rows": client_rows,
        "cost_per_unit": cost_per_unit,
        "unpaid_total": day_sales.filter(paid=False).aggregate(total=Sum("total"))["total"] or Decimal("0"),
        "period_unpaid_total": period_sales_qs.filter(paid=False).aggregate(total=Sum("total"))["total"] or Decimal("0"),
    }
    return render(request, "calculadora/distribuidora_rodriguez.html", context)




def pymes_naif_export(request):
    import csv

    from .models import NaifSale, NaifCost

    if not _naif_required(request):
        return redirect("pymes_naif")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="naif_pymes_export.csv"'
    writer = csv.writer(response)
    writer.writerow(["tipo", "fecha", "cliente/proveedor", "codigo", "producto/item", "cantidad", "precio", "total", "pagado", "notas"])
    for sale in NaifSale.objects.all().order_by("-date", "-created_at"):
        writer.writerow(["venta", sale.date, sale.client, sale.product_code, sale.product_name, sale.quantity, sale.unit_price, sale.total, "si" if sale.paid else "no", sale.notes])
    for cost in NaifCost.objects.all().order_by("-date", "-created_at"):
        writer.writerow(["costo", cost.date, cost.supplier, cost.category, cost.item, "", "", cost.amount, "si" if cost.paid else "no", cost.notes])
    return response


PERSONAL_WALLET_DEFAULT_CATEGORIES = [
    ("Alimentacion", "#22a06b"),
    ("Vivienda", "#f04438"),
    ("Transporte", "#0e7490"),
    ("Salud", "#c026d3"),
    ("Educacion", "#7c3aed"),
    ("Familia", "#ea580c"),
    ("Viajes", "#0284c7"),
    ("Entretenimiento", "#db2777"),
    ("Indumentaria", "#475569"),
    ("Tecnologia", "#4f46e5"),
    ("Servicios", "#ca8a04"),
    ("Impuestos", "#b91c1c"),
    ("Inversiones", "#087443"),
    ("Ahorro", "#15803d"),
    ("Otros", "#776b5e"),
]


def _ensure_wallet_defaults():
    from .models import PersonalExpenseCategory, PersonalWalletSettings

    settings_obj, _created = PersonalWalletSettings.objects.get_or_create(pk=1)
    for name, color in PERSONAL_WALLET_DEFAULT_CATEGORIES:
        PersonalExpenseCategory.objects.get_or_create(name=name, defaults={"color": color, "active": True})
    return settings_obj


def _wallet_period_bounds(request):
    today = timezone.localdate()
    try:
        year = int(request.GET.get("anio") or today.year)
    except (TypeError, ValueError):
        year = today.year
    try:
        month = int(request.GET.get("mes") or today.month)
    except (TypeError, ValueError):
        month = today.month
    month = min(max(month, 1), 12)
    period_range = request.GET.get("rango") or "month"
    if period_range == "7d":
        start = today - timedelta(days=6)
        end = today
    elif period_range == "30d":
        start = today - timedelta(days=29)
        end = today
    elif period_range == "ytd":
        start = date(today.year, 1, 1)
        end = today
        year = today.year
    else:
        period_range = "month"
        start = date(year, month, 1)
        end = _add_months(start, 1) - timedelta(days=1)
    return year, month, period_range, start, end


def _blue_rate_for(day, cache):
    if not cache:
        return Decimal("0")
    available = [rate_day for rate_day in cache if rate_day <= day]
    if not available:
        available = list(cache)
    return cache[max(available)]


def _display_money(value, day, currency, rate_cache):
    amount = Decimal(str(value or 0))
    rate = _blue_rate_for(day, rate_cache)
    if currency == "USD" and rate:
        return amount / rate
    return amount


def naif_wallet(request):
    from django.contrib import messages
    from django.core.paginator import Paginator
    from django.db.models import Sum
    from django.shortcuts import get_object_or_404
    from django.utils.dateparse import parse_date
    from .models import (
        BlueDollarRate,
        NaifCost,
        NaifSale,
        PersonalBudget,
        PersonalExpenseCategory,
        PersonalWalletMovement,
        PersonalWalletSettings,
    )

    _ensure_naif_user()
    if not _naif_required(request):
        return redirect("pymes_naif")

    wallet_settings = _ensure_wallet_defaults()
    selected_year, selected_month, period_range, period_start, period_end = _wallet_period_bounds(request)

    def wallet_redirect(tab="panel"):
        return redirect(f"{request.path}?tab={tab}&anio={selected_year}&mes={selected_month}&rango={period_range}")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "currency":
            currency = request.POST.get("display_currency")
            if currency in {"ARS", "USD"}:
                wallet_settings.display_currency = currency
                wallet_settings.save(update_fields=["display_currency", "updated_at"])
            return wallet_redirect(request.POST.get("return_tab") or "panel")
        if action == "category":
            name = request.POST.get("category_name", "").strip()
            if name:
                PersonalExpenseCategory.objects.get_or_create(
                    name=name,
                    defaults={"active": True, "color": request.POST.get("color", "").strip() or "#776b5e"},
                )
                messages.success(request, "Categoria agregada.")
            return wallet_redirect("config")
        if action == "category_toggle":
            category = get_object_or_404(PersonalExpenseCategory, pk=request.POST.get("category_id"))
            category.active = not category.active
            category.save(update_fields=["active"])
            return wallet_redirect("config")
        if action in {"expense", "income"}:
            category = None
            category_id = request.POST.get("category_id")
            if category_id:
                category = get_object_or_404(PersonalExpenseCategory, pk=category_id)
            PersonalWalletMovement.objects.create(
                created_by=request.user,
                date=_naif_date(request.POST.get("date")),
                kind=PersonalWalletMovement.EXPENSE if action == "expense" else PersonalWalletMovement.INCOME,
                category=category,
                description=request.POST.get("description", "").strip(),
                amount=_money_from_post(request.POST.get("amount")),
                payment_method=request.POST.get("payment_method", "").strip(),
                notes=request.POST.get("notes", "").strip(),
            )
            messages.success(request, "Movimiento guardado.")
            return wallet_redirect("panel")
        if action == "movement_update":
            movement = get_object_or_404(PersonalWalletMovement, pk=request.POST.get("movement_id"))
            category_id = request.POST.get("category_id")
            movement.date = _naif_date(request.POST.get("date"))
            movement.kind = request.POST.get("kind") if request.POST.get("kind") in {"expense", "income"} else movement.kind
            movement.category = get_object_or_404(PersonalExpenseCategory, pk=category_id) if category_id else None
            movement.description = request.POST.get("description", "").strip()
            movement.amount = _money_from_post(request.POST.get("amount"))
            movement.payment_method = request.POST.get("payment_method", "").strip()
            movement.notes = request.POST.get("notes", "").strip()
            movement.save()
            messages.success(request, "Movimiento actualizado.")
            return wallet_redirect("historial")
        if action == "movement_delete":
            movement = get_object_or_404(PersonalWalletMovement, pk=request.POST.get("movement_id"))
            movement.delete()
            messages.success(request, "Movimiento eliminado.")
            return wallet_redirect("historial")
        if action == "budget":
            category = get_object_or_404(PersonalExpenseCategory, pk=request.POST.get("category_id"))
            PersonalBudget.objects.update_or_create(
                category=category,
                year=selected_year,
                month=selected_month,
                defaults={"amount": _money_from_post(request.POST.get("amount"))},
            )
            return wallet_redirect("config")

    categories = list(PersonalExpenseCategory.objects.all())
    active_categories = [category for category in categories if category.active]
    movements_qs = PersonalWalletMovement.objects.filter(date__gte=period_start, date__lte=period_end)
    expenses_qs = movements_qs.filter(kind=PersonalWalletMovement.EXPENSE)
    incomes_qs = movements_qs.filter(kind=PersonalWalletMovement.INCOME)
    naif_sales = NaifSale.objects.filter(date__gte=period_start, date__lte=period_end).aggregate(total=Sum("total"))["total"] or Decimal("0")
    naif_costs = NaifCost.objects.filter(date__gte=period_start, date__lte=period_end).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    naif_profit = naif_sales - naif_costs
    expenses_total = expenses_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    incomes_total = incomes_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    available_total = incomes_total + naif_profit
    balance = available_total - expenses_total
    investment_suggestion = max(available_total, Decimal("0")) * wallet_settings.investment_suggestion_percent / Decimal("100")

    rate_cache = {
        rate.date: rate.sell
        for rate in BlueDollarRate.objects.filter(date__lte=period_end).order_by("date")
    }
    currency = wallet_settings.display_currency
    today = timezone.localdate()
    currency_warning = currency == "USD" and not rate_cache
    def show(value, day=None):
        return _display_money(value, day or period_end, currency, rate_cache)

    expense_bars = []
    category_totals = expenses_qs.values("category__name", "category__color").annotate(total=Sum("amount")).order_by("-total")
    max_category = max([row["total"] for row in category_totals] + [Decimal("1")])
    for row in category_totals:
        expense_bars.append({
            "name": row["category__name"] or "Sin categoria",
            "color": row["category__color"] or "#f31313",
            "total": show(row["total"]),
            "percent": int((row["total"] / max_category) * Decimal("100")),
        })

    daily_map = {}
    for movement in movements_qs:
        row = daily_map.setdefault(movement.date, {"date": movement.date, "expenses": Decimal("0"), "incomes": Decimal("0")})
        row["expenses" if movement.kind == PersonalWalletMovement.EXPENSE else "incomes"] += movement.amount
    daily_rows = []
    for day, row in sorted(daily_map.items()):
        daily_rows.append({
            "label": day.strftime("%d/%m"),
            "expenses": show(row["expenses"], day),
            "incomes": show(row["incomes"], day),
            "net": show(row["incomes"] - row["expenses"], day),
        })

    history_date = parse_date(request.GET.get("hist_fecha") or "")
    history_qs = PersonalWalletMovement.objects.all()
    if history_date:
        history_qs = history_qs.filter(date=history_date)
    history_paginator = Paginator(history_qs, 10)
    history_page = history_paginator.get_page(request.GET.get("page") or 1)
    movement_rows = list(history_page.object_list)
    for movement in movement_rows:
        movement.display_amount = show(movement.amount, movement.date)

    budget_rows = []
    budget_map = {budget.category_id: budget for budget in PersonalBudget.objects.filter(year=selected_year, month=selected_month)}
    spent_map = {
        row["category_id"]: row["total"] or Decimal("0")
        for row in expenses_qs.values("category_id").annotate(total=Sum("amount"))
    }
    for category in active_categories:
        budget = budget_map.get(category.id)
        amount = budget.amount if budget else Decimal("0")
        spent = spent_map.get(category.id, Decimal("0"))
        percent = int((spent / amount) * Decimal("100")) if amount else 0
        budget_rows.append({
            "category": category,
            "amount": show(amount),
            "spent": show(spent),
            "percent": min(percent, 140),
        })

    years = sorted(
        {year_date.year for year_date in PersonalWalletMovement.objects.dates("date", "year")}
        | {year_date.year for year_date in NaifSale.objects.dates("date", "year")}
        | {today.year},
        reverse=True,
    )
    months = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"), (5, "Mayo"), (6, "Junio"),
        (7, "Julio"), (8, "Agosto"), (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
    ]

    context = {
        "today": today,
        "settings": wallet_settings,
        "currency": currency,
        "currency_symbol": "US$" if currency == "USD" else "$",
        "currency_warning": currency_warning,
        "selected_year": selected_year,
        "selected_month": selected_month,
        "period_range": period_range,
        "period_start": period_start,
        "period_end": period_end,
        "history_date": history_date,
        "history_page": history_page,
        "history_query_base": (
            f"tab=historial&anio={selected_year}&mes={selected_month}&rango={period_range}"
            + (f"&hist_fecha={history_date.isoformat()}" if history_date else "")
        ),
        "years": years,
        "months": months,
        "categories": categories,
        "active_categories": active_categories,
        "movements": movement_rows,
        "expenses_total": show(expenses_total),
        "incomes_total": show(incomes_total),
        "naif_profit": show(naif_profit),
        "available_total": show(available_total),
        "balance": show(balance),
        "investment_suggestion": show(investment_suggestion),
        "expense_bars": expense_bars,
        "daily_rows": daily_rows[-18:],
        "budget_rows": budget_rows,
    }
    return render(request, "calculadora/naif_wallet.html", context)


def andex_landing(request):
    return render(request, 'calculadora/andex_landing.html')


def distribuidora_asistente_247(request):
    if not request.session.get("erp_demo_auth"):
        return JsonResponse({"ok": False, "reply": "Necesitas iniciar sesion para usar Asistente 247."}, status=403)
    if request.method != "POST":
        return JsonResponse({"ok": False, "reply": "Metodo no permitido."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "reply": "No pude leer el mensaje. Probemos de nuevo."}, status=400)

    message = str(payload.get("message", "")).strip()
    snapshot = payload.get("state") or {}
    text = message.lower()

    products = snapshot.get("products") or []
    clients = snapshot.get("clients") or []
    orders = snapshot.get("orders") or []
    cashflow = snapshot.get("cashflow") or []
    totals = snapshot.get("totals") or {}

    def money(value):
        try:
            return "$" + f"{int(round(float(value or 0))):,}".replace(",", ".")
        except (TypeError, ValueError):
            return "$0"

    def find_by_name(items, field="name"):
        clean_text = text.replace(",", " ")
        best = None
        for item in items:
            name = str(item.get(field, "")).lower()
            if name and name in clean_text:
                return item
            tokens = [token for token in name.split() if len(token) > 3]
            score = sum(1 for token in tokens if token in clean_text)
            if score and (not best or score > best[0]):
                best = (score, item)
        return best[1] if best else None

    def first_number(default=None):
        import re
        match = re.search(r"(\d+(?:[.,]\d+)?)", text)
        if not match:
            return default
        return float(match.group(1).replace(",", "."))

    try:
        import os
        from openai import OpenAI

        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            compact_state = {
                "products": products[:90],
                "clients": clients,
                "orders": orders,
                "cashflow": cashflow,
                "totals": totals,
            }
            system_prompt = (
                "Sos Asistente 247, una IA real dentro de un ERP demo para una distribuidora de alimentos. "
                "Tu tono es calido, simple, inteligente y operativo. Ayudas a trabajar, no haces humo.\n"
                "LeÃ© el estado actual del portal que recibis en JSON y respondÃ© con datos concretos.\n"
                "PodÃ©s guiar al usuario por estos mÃ³dulos: dashboard, tienda-publica, marketplace, ventas, "
                "armado, facturacion, logistica, stock, compras, clientes, finanzas y rrhh.\n"
                "Si el usuario pide ver stock o flujo de caja, respondÃ© con anÃ¡lisis breve y accion de navegar.\n"
                "Si pide cargar venta o registrar compra, preparÃ¡ una acciÃ³n, pero siempre needs_confirmation=true. "
                "No digas que ya ejecutaste una venta o compra si todavÃ­a no fue confirmada.\n"
                "Para preparar una venta necesitÃ¡s client_code, product_code y qty. Para preparar una compra necesitÃ¡s "
                "provider, product_code, qty y cost. Si faltan datos, pedilos y navegÃ¡ al mÃ³dulo correcto.\n"
                "DevolvÃ© SOLO JSON vÃ¡lido con esta forma exacta: "
                "{\"ok\":true,\"reply\":\"texto\",\"action\":null|{\"type\":\"navigate\",\"view\":\"stock\"}|"
                "{\"type\":\"prepare_sale\",\"client_code\":44,\"product_code\":101,\"qty\":20,\"amount\":123,\"feasible\":true}|"
                "{\"type\":\"prepare_purchase\",\"provider\":\"Campo Sur\",\"product_code\":104,\"qty\":50,\"cost\":1800},"
                "\"needs_confirmation\":false,\"confirm_label\":\"Confirmar\"}."
            )
            user_prompt = (
                "Mensaje del usuario:\n"
                f"{message}\n\n"
                "Estado actual del ERP demo:\n"
                f"{json.dumps(compact_state, ensure_ascii=False)}"
            )
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=360,
                temperature=0.35,
            )
            ai_payload = json.loads(response.choices[0].message.content or "{}")
            action = ai_payload.get("action")
            allowed_views = {
                "dashboard", "tienda-publica", "marketplace", "ventas", "armado",
                "facturacion", "logistica", "stock", "compras", "clientes", "finanzas", "rrhh"
            }
            allowed_actions = {"navigate", "prepare_sale", "prepare_purchase"}
            if isinstance(action, dict):
                if action.get("type") not in allowed_actions:
                    action = None
                if action and action.get("type") == "navigate" and action.get("view") not in allowed_views:
                    action = None
            else:
                action = None
            return JsonResponse({
                "ok": bool(ai_payload.get("ok", True)),
                "reply": str(ai_payload.get("reply") or "Estoy mirando el portal. Decime que queres hacer y te guio."),
                "action": action,
                "needs_confirmation": bool(ai_payload.get("needs_confirmation", False)),
                "confirm_label": ai_payload.get("confirm_label") or "Confirmar",
                "engine": "openai",
            })
    except Exception as e:
        print(f"[Asistente 247] OpenAI fallback local: {e}")

    if any(word in text for word in ["stock", "inventario", "faltante", "critico", "crÃ­tico"]):
        critical = [p for p in products if float(p.get("stock") or 0) <= float(p.get("min") or 0)]
        low = sorted(products, key=lambda p: float(p.get("stock") or 0))[:5]
        critical_names = ", ".join(p.get("name", "") for p in critical[:4]) or "sin productos criticos"
        low_names = ", ".join(f"{p.get('name')} ({p.get('stock')})" for p in low[:4])
        return JsonResponse({
            "ok": True,
            "reply": (
                f"Te llevo a Stock. Hoy veo {len(critical)} productos por debajo del minimo: {critical_names}. "
                f"Los niveles mas bajos son {low_names}. Conviene revisar reposicion antes de vender fuerte esos articulos."
            ),
            "action": {"type": "navigate", "view": "stock"},
            "needs_confirmation": False,
        })

    if any(word in text for word in ["caja", "flujo", "finanza", "finanzas", "mes", "vencimiento", "cobro"]):
        month_net = sum((1 if m.get("type") == "cobro" else -1) * float(m.get("amount") or 0) for m in cashflow)
        incoming = sum(float(m.get("amount") or 0) for m in cashflow if m.get("type") == "cobro")
        outgoing = sum(float(m.get("amount") or 0) for m in cashflow if m.get("type") != "cobro")
        next_items = sorted(cashflow, key=lambda m: str(m.get("date", "")))[:3]
        next_text = "; ".join(f"{m.get('date')} {m.get('concept')} {money(m.get('amount'))}" for m in next_items) or "sin movimientos agendados"
        return JsonResponse({
            "ok": True,
            "reply": (
                f"Te abro Finanzas. El flujo mensual agendado da {money(month_net)}: "
                f"cobros por {money(incoming)} y pagos por {money(outgoing)}. Proximos movimientos: {next_text}."
            ),
            "action": {"type": "navigate", "view": "finanzas"},
            "needs_confirmation": False,
        })

    if any(word in text for word in ["compra", "comprÃ©", "compre", "proveedor", "insumo", "gasto"]):
        product = find_by_name(products)
        qty = first_number(50)
        cost = None
        if " a " in text:
            numbers = []
            import re
            for match in re.findall(r"(\d+(?:[.,]\d+)?)", text):
                numbers.append(float(match.replace(",", ".")))
            if len(numbers) > 1:
                cost = numbers[-1]
        cost = cost or float((product or {}).get("cost") or 1)
        provider = "Campo Sur" if "campo" in text else "Distribuidora Centro" if "centro" in text else "Servicios generales" if "servicio" in text else "Frigorifico Norte"
        if not product:
            return JsonResponse({
                "ok": True,
                "reply": "Vamos a cargar una compra. Decime producto, cantidad y costo unitario. Ejemplo: compre 50 kg de papa lavada a 1800.",
                "action": {"type": "navigate", "view": "compras"},
                "needs_confirmation": False,
            })
        total = qty * cost
        return JsonResponse({
            "ok": True,
            "reply": f"Entendi una compra a {provider}: {qty:g} {product.get('mode')} de {product.get('name')} a {money(cost)}. Total estimado {money(total)}. Confirmame y la dejo cargada en compras.",
            "action": {
                "type": "prepare_purchase",
                "provider": provider,
                "product_code": product.get("code"),
                "qty": qty,
                "cost": cost,
            },
            "needs_confirmation": True,
            "confirm_label": "Confirmar compra",
        })

    if any(word in text for word in ["venta", "pedido", "vender", "cliente"]):
        product = find_by_name(products)
        client = find_by_name(clients)
        qty = first_number(1)
        if not product or not client:
            return JsonResponse({
                "ok": True,
                "reply": "Vamos con una venta. Decime cliente, producto y cantidad. Ejemplo: cargar venta a Mercado Centro de 20 kg de tomate redondo.",
                "action": {"type": "navigate", "view": "ventas"},
                "needs_confirmation": False,
            })
        amount = qty * float(product.get("price") or 0)
        feasible = qty <= float(product.get("stock") or 0)
        return JsonResponse({
            "ok": True,
            "reply": f"PreparÃ© el pedido para {client.get('name')}: {qty:g} {product.get('mode')} de {product.get('name')} por {money(amount)}. Stock actual {product.get('stock')}. {'Es factible.' if feasible else 'Ojo: supera el stock disponible.'} Confirmame antes de cargarlo.",
            "action": {
                "type": "prepare_sale",
                "client_code": client.get("code"),
                "product_code": product.get("code"),
                "qty": qty,
                "amount": amount,
                "feasible": feasible,
            },
            "needs_confirmation": True,
            "confirm_label": "Confirmar venta",
        })

    modules = "Ventas, Cargar compra, Stock, Finanzas, Logistica, Clientes, Facturacion, Armado pedidos, Marketplace y RRHH"
    return JsonResponse({
        "ok": True,
        "reply": f"Estoy para guiarte por el portal. Puedo ayudarte con {modules}. Decime algo como: cargar venta, registrar compra, controlar stock o ver flujo de caja del mes.",
        "action": None,
        "needs_confirmation": False,
    })




from django.shortcuts import render
from .models import Player  # o lo que corresponda

def ranking(request):
    jugadores = Player.objects.all().order_by('-score')[:10]  # o tu lÃ³gica
    usuario_actual = None  # buscÃ¡s el usuario actual si querÃ©s
    promedio = 80  # por ejemplo

    context = {
        'jugadores': jugadores,
        'usuario_actual': usuario_actual,
        'promedio': promedio,
        # lo que quieras pasar
    }
    return render(request, 'ranking.html', context)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Player, PlayerResult

from django.utils import timezone
from .models import QuizQuestion, QuizParticipacion

from django.shortcuts import render, get_object_or_404



@csrf_exempt
def guardar_perfil(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            perfil_nombre = data.get("perfil_generado")
            resultados = data.get("resultados")
            player_id = data.get("player_id") or request.session.get("player_id")  # âœ… Esta es la lÃ­nea clave

            if not (perfil_nombre and resultados and player_id):
                return JsonResponse({"error": "Faltan datos"}, status=400)

            jugador = Player.objects.get(id=player_id)

            PlayerResult.objects.create(
                player=jugador,
                vehicle_percentage=resultados.get("vehicle", 0),
                property_percentage=resultados.get("property", 0),
                education_percentage=resultados.get("education", 0),
                investment_percentage=resultados.get("investment", 0),
                leisure_percentage=resultados.get("leisure", 0),
                business_percentage=resultados.get("business", 0),
                score=0,  # PodÃ©s calcularlo y guardar si querÃ©s
                perfil_generado=perfil_nombre
            )

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "MÃ©todo no permitido"}, status=405)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

def require_login_action(request, redirect_to):
    """ Guarda la acciÃ³n solicitada para despuÃ©s del login """
    request.session["next_url"] = redirect_to
    return redirect("login_google")


# Mostrar la pregunta del dÃ­a
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.mail import send_mail
from .models import ClientePerfil, QuizParticipacion

from django.contrib.auth.models import User

@login_required
def alias_modal_view(request):
    profile, _ = ClientePerfil.objects.get_or_create(user=request.user)
    if profile.alias and profile.alias != f"usuario_{request.user.id}":
        return redirect('daily_quiz')

    if request.method == 'POST':
        alias = request.POST.get('alias').strip()
        if alias and not ClientePerfil.objects.filter(alias=alias).exists():
            profile.alias = alias
            profile.save()
            send_mail(
                'Â¡Bienvenido a InvertiresFÃ¡cil!',
                'Gracias por unirte a InvertiresFÃ¡cil, tu alias ya estÃ¡ activo y puedes empezar a jugar. Â¡Mucha suerte!',
                'no-reply@invertiresfacil.com',
                [request.user.email],
                fail_silently=True,
            )
            return redirect('daily_quiz')
        else:
            return render(request, 'alias_modal.html', {'error': 'Alias no disponible o invÃ¡lido.'})
    
    return render(request, 'alias_modal.html')

from django.utils import timezone

def ranking_view(request):
    filtro = request.GET.get('filtro', 'historico')
    if filtro == 'mes':
        desde = timezone.now() - timezone.timedelta(days=30)
        scores = UserScore.objects.filter(created_at__gte=desde)
    elif filtro == 'semana':
        desde = timezone.now() - timezone.timedelta(days=7)
        scores = UserScore.objects.filter(created_at__gte=desde)
    else:
        scores = UserScore.objects.all()

    scores = scores.order_by('-score', 'time_taken')
    paginator = Paginator(scores, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rankingquiz.html', {'page_obj': page_obj, 'filtro': filtro})





# Mostrar la pregunta del dÃ­a
import os as _os

_QUIZ_OFFSET_FILE = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), 'quiz_offset.json')

def _get_quiz_offset():
    try:
        import json as _json
        with open(_QUIZ_OFFSET_FILE) as f:
            return _json.load(f).get('offset', 0)
    except Exception:
        return 0

def _set_quiz_offset(offset):
    import json as _json
    with open(_QUIZ_OFFSET_FILE, 'w') as f:
        _json.dump({'offset': offset}, f)


# ============================================================
# REEMPLAZÃ las vistas del quiz en tu views.py con este bloque.
# BuscÃ¡ desde "_quiz_limite" hasta el final de "ranking_quiz_view"
# y reemplazalo completo.
# ============================================================

import os as _os
import json
import random as _random

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import (
    ClientePerfil, QuizQuestion, QuizOption,
    QuizParticipacion,
)

# â”€â”€ Archivo de offset (rotaciÃ³n diaria de preguntas) â”€â”€â”€â”€â”€â”€â”€â”€
_QUIZ_OFFSET_FILE = _os.path.join(
    _os.path.dirname(_os.path.dirname(__file__)), 'quiz_offset.json'
)

def _get_quiz_offset():
    try:
        with open(_QUIZ_OFFSET_FILE) as f:
            return json.load(f).get('offset', 0)
    except Exception:
        return 0

def _set_quiz_offset(offset):
    with open(_QUIZ_OFFSET_FILE, 'w') as f:
        json.dump({'offset': offset}, f)


# â”€â”€ CategorÃ­as de la ruleta â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CATEGORIAS = [
    ('acciones',              'ðŸ“ˆ Acciones'),
    ('matematica_financiera', 'ðŸ§® MatemÃ¡tica Financiera'),
    ('fci_etf',               'ðŸ“Š FCI o ETF'),
    ('internacional',         'ðŸŒ Internacional'),
    ('argentina',             'ðŸ‡¦ðŸ‡· Argentina'),
    ('fintech',               'ðŸ’¡ Fintech'),
]
CATEGORIAS_KEYS = [c[0] for c in CATEGORIAS]


# â”€â”€ LÃ­mite diario unificado: 3 para TODOS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _quiz_limite(request):
    """Retorna (jugadas_hoy, limite_diario, es_premium)."""
    today = timezone.now().date()
    LIMITE = 3  # igual para todos

    if request.user.is_authenticated:
        perfil = getattr(request.user, 'clienteperfil', None)
        plan   = getattr(perfil, 'plan_activo', 1) or 1
        es_premium = plan == 3
        jugadas = (
            QuizParticipacion.objects.filter(cliente=perfil, fecha=today).count()
            if perfil else 0
        )
    else:
        es_premium = False
        jugadas    = request.session.get(f'quiz_count_{today}', 0)

    return jugadas, LIMITE, es_premium


# â”€â”€ Vista principal del quiz â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def daily_question_view(request):
    today         = timezone.now().date()
    guest_skipped = request.session.get('quiz_guest_skipped', False)

    # POST = invitado eligiendo alias
    if request.method == 'POST' and not request.user.is_authenticated:
        alias = request.POST.get('alias', '').strip()
        if alias:
            if ClientePerfil.objects.filter(alias__iexact=alias).exists():
                return render(request, 'calculadora/daily_question.html', {
                    'pedir_alias': True,
                    'alias_error': 'Ese alias ya estÃ¡ en uso. ElegÃ­ otro.',
                })
            request.session['quiz_guest_alias']   = alias
            request.session['quiz_guest_skipped'] = True
        return redirect('daily_quiz')

    # Primer acceso sin cuenta â†’ modal login
    if not request.user.is_authenticated and not guest_skipped:
        return render(request, 'calculadora/daily_question.html', {
            'mostrar_login_modal': True,
        })

    # Invitado sin alias
    if not request.user.is_authenticated and not request.session.get('quiz_guest_alias'):
        return render(request, 'calculadora/daily_question.html', {'pedir_alias': True})

    # LÃ­mite diario alcanzado
    jugadas_hoy, limite, es_premium = _quiz_limite(request)
    if jugadas_hoy >= limite:
        return render(request, 'calculadora/daily_question.html', {
            'ya_jugo'        : True,
            'limite_alcanzado': True,
            'es_premium'     : es_premium,
            'jugadas_hoy'    : jugadas_hoy,
            'limite'         : limite,
        })

    # â”€â”€ CategorÃ­a elegida por la ruleta â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    categoria_key = request.GET.get('cat', '').strip()
    auto_spin     = request.GET.get('auto_spin', '0') == '1'

    # Si no hay categorÃ­a vÃ¡lida â†’ mostrar ruleta
    if categoria_key not in CATEGORIAS_KEYS:
        return render(request, 'calculadora/daily_question.html', {
            'mostrar_ruleta' : True,
            'categorias'     : CATEGORIAS,
            'jugadas_hoy'    : jugadas_hoy,
            'limite'         : limite,
            'es_premium'     : es_premium,
            'auto_spin'      : auto_spin,
        })

    # Buscar pregunta vÃ¡lida en esa categorÃ­a (debe tener opciÃ³n correcta)
    qs = QuizQuestion.objects.filter(
        categoria=categoria_key,
        options__is_correct=True,
    ).distinct()

    if not qs.exists():
        # Sin preguntas vÃ¡lidas en esta categorÃ­a â†’ fallback server-side a cualquier categorÃ­a
        # (sin redirect al cliente, evita el doble giro y el loop infinito)
        qs = QuizQuestion.objects.filter(options__is_correct=True).distinct()
        if not qs.exists():
            return render(request, 'calculadora/daily_question.html', {
                'question'    : None,
                'mostrar_ruleta': False,
                'jugadas_hoy' : jugadas_hoy,
                'limite'      : limite,
                'es_premium'  : es_premium,
            })

    # Elegir pregunta del dÃ­a
    total     = qs.count()
    base_idx  = (today.toordinal() + _get_quiz_offset() + jugadas_hoy) % total
    question  = qs.order_by('id')[base_idx]

    correct_option = question.options.filter(is_correct=True).first()
    options        = list(question.options.all())

    # Guardia adicional: pregunta sin opciones en DB (dato corrupto)
    if not correct_option or not options:
        return render(request, 'calculadora/daily_question.html', {
            'question'    : None,
            'mostrar_ruleta': False,
            'jugadas_hoy' : jugadas_hoy,
            'limite'      : limite,
            'es_premium'  : es_premium,
        })

    _random.Random(question.id * 1000 + today.toordinal()).shuffle(options)

    # Usar la categorÃ­a real de la pregunta (puede diferir si hubo fallback)
    categoria_key   = question.categoria
    categoria_label = dict(CATEGORIAS).get(categoria_key, categoria_key)

    return render(request, 'calculadora/daily_question.html', {
        'question'           : question,
        'shuffled_options'   : options,
        'correct_option_text': correct_option.text,
        'ya_jugo'            : False,
        'jugadas_hoy'        : jugadas_hoy,
        'limite'             : limite,
        'es_premium'         : es_premium,
        'categoria_key'      : categoria_key,
        'categoria_label'    : categoria_label,
        'mostrar_ruleta'     : True,
        'mostrar_popup'      : True,
        'auto_spin'          : False,
    })


# â”€â”€ Endpoint: registrar respuesta â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def submit_answer_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    data          = json.loads(request.body)
    question_id   = data.get('question_id')
    selected      = data.get('selected_option')
    used_help     = data.get('used_help', False)
    time_taken    = data.get('time_taken', 60)
    today         = timezone.now().date()

    question       = get_object_or_404(QuizQuestion, id=question_id)
    correct_option = question.options.filter(is_correct=True).first()

    jugadas_hoy, limite, es_premium = _quiz_limite(request)
    if jugadas_hoy >= limite:
        return JsonResponse({'success': False, 'limit_reached': True, 'es_premium': es_premium})

    # Puntaje
    was_correct = bool(correct_option and selected == correct_option.text)
    if was_correct:
        base_score = max(10, 100 - int(time_taken * 1.5))
        score      = int(base_score * 0.7) if used_help else base_score
    else:
        score = 0

    # Guardar
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'clienteperfil', None)
        if perfil:
            QuizParticipacion.objects.create(
                cliente=perfil, fecha=today, puntaje=score,
                correctas=1 if was_correct else 0,
                usadas_ayuda=used_help, duracion=int(time_taken),
            )
            perfil.quiz_score_total = (perfil.quiz_score_total or 0) + score
            perfil.save(update_fields=['quiz_score_total'])
    else:
        guest_alias = request.session.get('quiz_guest_alias', '')
        if guest_alias:
            QuizParticipacion.objects.create(
                cliente=None, guest_alias=guest_alias, fecha=today,
                puntaje=score, correctas=1 if was_correct else 0,
                usadas_ayuda=used_help, duracion=int(time_taken),
            )
        count = request.session.get(f'quiz_count_{today}', 0)
        request.session[f'quiz_count_{today}'] = count + 1

    nuevas = jugadas_hoy + 1
    return JsonResponse({
        'success'      : True,
        'score'        : score,
        'correct'      : was_correct,
        'jugadas_hoy'  : nuevas,
        'limite'       : limite,
        'limit_reached': nuevas >= limite,
        'es_premium'   : es_premium,
    })


def intro_quiz_view(request):
    return redirect('daily_quiz')

def quiz_skip_login_view(request):
    request.session['quiz_guest_skipped'] = True
    return redirect('daily_quiz')


# â”€â”€ Ranking SOLO del dÃ­a actual â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def ranking_quiz_view(request):
    from django.db.models import Sum

    today = timezone.now().date()

    # Usuarios registrados â€” solo hoy
    user_scores = (
        QuizParticipacion.objects
        .filter(cliente__isnull=False, fecha=today)
        .values('cliente__alias', 'cliente__user__username')
        .annotate(total=Sum('puntaje'))
        .order_by('-total')
    )
    entries = []
    for s in user_scores:
        entries.append({
            'alias': s['cliente__alias'] or s['cliente__user__username'] or 'AnÃ³nimo',
            'score': s['total'] or 0,
        })

    # Invitados â€” solo hoy
    guest_scores = (
        QuizParticipacion.objects
        .filter(cliente__isnull=True, fecha=today)
        .exclude(guest_alias='')
        .values('guest_alias')
        .annotate(total=Sum('puntaje'))
    )
    for g in guest_scores:
        entries.append({'alias': g['guest_alias'], 'score': g['total'] or 0})

    entries = sorted(entries, key=lambda x: x['score'], reverse=True)

    paginator  = Paginator(entries, 10)
    page_obj   = paginator.get_page(request.GET.get('page'))

    mi_alias = None
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'clienteperfil', None)
        if perfil:
            mi_alias = perfil.alias or request.user.username
    else:
        mi_alias = request.session.get('quiz_guest_alias') or None

    # Puntaje del usuario en el dÃ­a para el mensaje de compartir
    mi_score = 0
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'clienteperfil', None)
        if perfil:
            mi_score = QuizParticipacion.objects.filter(
                cliente=perfil, fecha=today
            ).aggregate(total=Sum('puntaje'))['total'] or 0
    else:
        guest_alias = request.session.get('quiz_guest_alias')
        if guest_alias:
            mi_score = QuizParticipacion.objects.filter(
                cliente__isnull=True, guest_alias=guest_alias, fecha=today
            ).aggregate(total=Sum('puntaje'))['total'] or 0

    return render(request, 'calculadora/rankingquiz.html', {
        'page_obj': page_obj,
        'mi_alias': mi_alias,
        'mi_score': mi_score,
        'fecha'   : today,
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ClientePerfil


@login_required
def elegir_alias_view(request):
    perfil = getattr(request.user, 'clienteperfil', None)
    if not perfil:
        return redirect('daily_quiz')

    if perfil.alias:
        return redirect('daily_quiz')

    error_message = None

    if request.method == 'POST':
        alias = request.POST.get('alias', '').strip()
        if not alias:
            error_message = "El alias no puede estar vacÃ­o."
        elif ClientePerfil.objects.filter(alias__iexact=alias).exists():
            error_message = "Este alias ya estÃ¡ en uso. ElegÃ­ otro."
        else:
            perfil.alias = alias
            perfil.save(update_fields=['alias'])
            return redirect('daily_quiz')

    return render(request, 'calculadora/elegir_alias.html', {'error_message': error_message})


@login_required
def verificar_alias_redireccion_view(request):
    user_profile, created = ClientePerfil.objects.get_or_create(user=request.user)
    if user_profile.alias and user_profile.alias_confirmado:
        return redirect('daily_quiz')
    else:
        return redirect('elegir_alias')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ClientePerfil, DiagnosticoFinanciero
from .forms import ClientePerfilForm
from decimal import Decimal, InvalidOperation

from decimal import Decimal

def to_decimal(v):
    try:
        if v in (None, "", "null"):
            return Decimal("0")
        return Decimal(str(v))
    except:
        return Decimal("0")


def to_int(v, default=0):
    try:
        if v in (None, "", "null"):
            return default
        return int(v)
    except (TypeError, ValueError):
        return default


def get_ordered_values(post_data, prefix, fallback_name=None):
    ordered = []
    index = 1
    while True:
        key = f"{prefix}_{index}"
        if key not in post_data:
            break
        value = (post_data.get(key) or "").strip()
        if value:
            ordered.append(value)
        index += 1

    if ordered:
        return ordered

    if fallback_name:
        return [value for value in post_data.getlist(fallback_name) if value]

    return []


def merge_guest_diagnostic_profile(request, perfil):
    guest_profile_id = request.session.get("guest_diagnostico_perfil_id")
    if not guest_profile_id or not request.user.is_authenticated:
        return

    guest_profile = ClientePerfil.objects.filter(
        id=guest_profile_id,
        user__isnull=True,
    ).first()
    if not guest_profile:
        request.session.pop("guest_diagnostico_perfil_id", None)
        return

    DiagnosticoFinanciero.objects.filter(cliente=guest_profile).update(cliente=perfil)

    if not perfil.edad and guest_profile.edad:
        perfil.edad = guest_profile.edad
    if not perfil.hijos_a_cargo and guest_profile.hijos_a_cargo:
        perfil.hijos_a_cargo = guest_profile.hijos_a_cargo
    if not perfil.situacion_habitacional and guest_profile.situacion_habitacional:
        perfil.situacion_habitacional = guest_profile.situacion_habitacional
    if not perfil.objetivos and guest_profile.objetivos:
        perfil.objetivos = guest_profile.objetivos
    perfil.diagnosticos_realizados = DiagnosticoFinanciero.objects.filter(cliente=perfil).count()
    perfil.save(update_fields=[
        "edad",
        "hijos_a_cargo",
        "situacion_habitacional",
        "objetivos",
        "diagnosticos_realizados",
    ])

    guest_profile.delete()
    request.session.pop("guest_diagnostico_perfil_id", None)
    request.session.modified = True


def formulario_view(request):
    perfil = None
    if request.user.is_authenticated:
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
        merge_guest_diagnostic_profile(request, perfil)

    if request.method == "POST":
        if perfil is None:
            guest_profile_id = request.session.get("guest_diagnostico_perfil_id")
            perfil = ClientePerfil.objects.filter(id=guest_profile_id, user__isnull=True).first()
            if perfil is None:
                perfil = ClientePerfil.objects.create(alias="Invitado")
                request.session["guest_diagnostico_perfil_id"] = perfil.id

        objetivos_ordenados = get_ordered_values(request.POST, "objetivo", "objetivos")
        valores_ordenados = get_ordered_values(request.POST, "valor", "importancia_dinero")
        limitantes_crecimiento = request.POST.getlist("limitantes_crecimiento")
        causas_estancamiento = request.POST.getlist("causas_estancamiento")
        resolucion_deficit = request.POST.getlist("resolucion_deficit")
        resultados_emprendimientos = request.POST.getlist("resultados_emprendimientos")
        sesgos_sistema = request.POST.getlist("sesgos_sistema")

        # -------- PERFIL --------
        edad = to_int(request.POST.get("edad"))
        if edad and (edad < 15 or edad > 115):
            edad = None
        perfil.edad = edad or None
        perfil.hijos_a_cargo = to_int(request.POST.get("hijos_a_cargo"))
        perfil.situacion_habitacional = request.POST.get("situacion_habitacional") or None
        perfil.objetivos = objetivos_ordenados
        perfil.diagnosticos_realizados = (perfil.diagnosticos_realizados or 0) + 1
        perfil.save()

        # -------- DIAGNÃ“STICO --------
        horas = to_decimal(request.POST.get("horas_trabajadas"))
        if horas > 20:
            horas = Decimal("20")

        patrimonio_comp = {
            "inmuebles": float(to_decimal(request.POST.get("pat_inmuebles"))),
            "vehiculos": float(to_decimal(request.POST.get("pat_vehiculos"))),
            "empresa": float(to_decimal(request.POST.get("pat_empresa"))),
            "inversiones": float(to_decimal(request.POST.get("pat_inversiones"))),
            "cash": float(to_decimal(request.POST.get("pat_cash"))),
            "creditos_a_favor": float(to_decimal(request.POST.get("pat_creditos_a_favor"))),
        }

        deuda_comp = {
            "tarjetas": float(to_decimal(request.POST.get("deu_tarjetas"))),
            "prestamos": float(to_decimal(request.POST.get("deu_prestamos"))),
            "hipoteca": float(to_decimal(request.POST.get("deu_hipoteca"))),
            "prenda": float(to_decimal(request.POST.get("deu_prenda"))),
            "terceros": float(to_decimal(request.POST.get("deu_terceros"))),
            "impuestos": float(to_decimal(request.POST.get("deu_impuestos"))),
        }

        patrimonio_total = sum(Decimal(str(value)) for value in patrimonio_comp.values())
        deuda_total = sum(Decimal(str(value)) for value in deuda_comp.values())

        respuestas_raw = {
            "estado_financiero": request.POST.get("estado_financiero"),
            "objetivos": request.POST.getlist("objetivos"),
            "objetivos_ordenados": objetivos_ordenados,
            "importancia_dinero": request.POST.getlist("importancia_dinero"),
            "valores_ordenados": valores_ordenados,
            "limitantes_crecimiento": limitantes_crecimiento,
            "causas_estancamiento": causas_estancamiento,
            "resolucion_deficit": resolucion_deficit,
            "resultados_emprendimientos": resultados_emprendimientos,
            "sesgos_sistema": sesgos_sistema,
            "estabilidad_laboral": request.POST.get("estabilidad_laboral"),
            "percepcion_estabilidad": request.POST.get("percepcion_estabilidad"),
            "conocimiento_financiero": request.POST.get("conocimiento_financiero"),
            "confianza_sistema": request.POST.get("confianza_sistema"),
        }
        payload_codificado = base64.urlsafe_b64encode(
            json.dumps(respuestas_raw, ensure_ascii=False).encode("utf-8")
        ).decode("utf-8")

        diagnostico = DiagnosticoFinanciero.objects.create(
            cliente=perfil,
            horas_trabajadas=horas,

            ingreso_trabajo=to_decimal(request.POST.get("ingreso_trabajo")),
            ingreso_negocio=to_decimal(request.POST.get("ingreso_negocio")),
            ingreso_rentas=to_decimal(request.POST.get("ingreso_rentas")),
            ingreso_inversiones=to_decimal(request.POST.get("ingreso_inversiones")),
            ingreso_otros=to_decimal(request.POST.get("ingreso_otros")),

            gasto_necesarios=to_decimal(request.POST.get("gasto_necesarios")),
            gasto_innecesarios=to_decimal(request.POST.get("gasto_innecesarios")),
            gasto_financieros=to_decimal(request.POST.get("gasto_financieros")),
            gasto_inversiones=to_decimal(request.POST.get("gasto_inversiones")),

            
            reaccion_perdida=request.POST.get("reaccion_perdida"),
        )

        # -------- COMPOSICIÃ“N (JSON) --------
        diagnostico.patrimonio_comp = {
            "inmuebles": float(to_decimal(request.POST.get("pat_inmuebles"))),
            "vehiculos": float(to_decimal(request.POST.get("pat_vehiculos"))),
            "empresa": float(to_decimal(request.POST.get("pat_empresa"))),
            "inversiones": float(to_decimal(request.POST.get("pat_inversiones"))),
            "cash": float(to_decimal(request.POST.get("pat_cash"))),
            "creditos_a_favor": float(to_decimal(request.POST.get("pat_creditos_a_favor"))),
        }

        diagnostico.deuda_comp = {
            "tarjetas": float(to_decimal(request.POST.get("deu_tarjetas"))),
            "prestamos": float(to_decimal(request.POST.get("deu_prestamos"))),
            "hipoteca": float(to_decimal(request.POST.get("deu_hipoteca"))),
            "prenda": float(to_decimal(request.POST.get("deu_prenda"))),
            "terceros": float(to_decimal(request.POST.get("deu_terceros"))),
            "impuestos": float(to_decimal(request.POST.get("deu_impuestos"))),
        }

        diagnostico.ingreso_emprendimiento = to_decimal(request.POST.get("ingreso_emprendimiento"))
        diagnostico.patrimonio_total = patrimonio_total
        diagnostico.deuda_total = deuda_total
        diagnostico.estado_financiero = request.POST.get("estado_financiero") or None
        diagnostico.estabilidad_laboral = request.POST.get("estabilidad_laboral") or None
        diagnostico.percepcion_estabilidad = to_int(request.POST.get("percepcion_estabilidad"))
        diagnostico.conocimiento_financiero = to_int(request.POST.get("conocimiento_financiero"))
        diagnostico.confianza_sistema = to_int(request.POST.get("confianza_sistema"))
        diagnostico.objetivos_ordenados = objetivos_ordenados
        diagnostico.importancia_dinero = valores_ordenados
        diagnostico.resultados_emprendimientos = resultados_emprendimientos
        diagnostico.limitantes_crecimiento = limitantes_crecimiento
        diagnostico.causas_estancamiento = causas_estancamiento
        diagnostico.resolucion_deficit = resolucion_deficit
        diagnostico.sesgos_sistema = sesgos_sistema
        diagnostico.respuestas_raw = respuestas_raw
        diagnostico.payload_codificado = payload_codificado
        diagnostico.save(update_fields=[
            "ingreso_emprendimiento",
            "patrimonio_comp",
            "deuda_comp",
            "patrimonio_total",
            "deuda_total",
            "estado_financiero",
            "estabilidad_laboral",
            "percepcion_estabilidad",
            "conocimiento_financiero",
            "confianza_sistema",
            "objetivos_ordenados",
            "importancia_dinero",
            "resultados_emprendimientos",
            "limitantes_crecimiento",
            "causas_estancamiento",
            "resolucion_deficit",
            "sesgos_sistema",
            "respuestas_raw",
            "payload_codificado",
        ])

        request.session["ultimo_diagnostico_id"] = diagnostico.id
        return redirect("resultado")

    return render(request, "formulario.html", {})


import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from calculadora.models import ClientePerfil, DiagnosticoFinanciero, ResultadoIA
from calculadora.services.resultado import construir_resultado, METAS_MAP
from calculadora.services.motor_calculos import calcular_motor_financiero
from calculadora.services.proyecciones import calcular_proyecciones


def construir_portfolio_sugerido(snapshot, diagnostico):
    conocimiento = int(snapshot.get("conocimiento_financiero") or 0)
    confianza = int(snapshot.get("confianza_sistema") or 0)
    estado = snapshot.get("estado_general") or "constructor"
    meses_supervivencia = float(snapshot.get("meses_supervivencia") or 0)
    reaccion = getattr(diagnostico, "reaccion_perdida", "") or ""

    score = 0
    if estado in ("fragil", "presionado"):
        score -= 2
    elif estado == "constructor":
        score += 0
    elif estado == "acumulador":
        score += 1
    elif estado == "despegando":
        score += 2

    if conocimiento <= 2:
        score -= 1
    elif conocimiento >= 4:
        score += 1

    if confianza <= 2:
        score -= 1
    elif confianza >= 4:
        score += 1

    if reaccion in ("locura", "vender", "nose"):
        score -= 2
    elif reaccion in ("estrategia", "oportunidades"):
        score += 1

    if meses_supervivencia < 3:
        score -= 1

    if score <= -3:
        perfil = "Defensivo"
        tesis = "Prioriza liquidez, baja volatilidad y aprendizaje antes de aumentar riesgo."
        alloc = [
            ("SGOV", "Treasuries 0-3 meses", 45, "liquidez defensiva"),
            ("AGG", "Bonos investment grade EE.UU.", 30, "estabilidad de renta fija"),
            ("ACWI", "Acciones globales", 15, "crecimiento diversificado"),
            ("GLD", "Oro fÃ­sico vÃ­a ETF", 10, "cobertura ante estrÃ©s"),
        ]
    elif score <= 1:
        perfil = "Balanceado"
        tesis = "Combina estabilidad con exposiciÃ³n global gradual, sin concentrar la cartera en una sola apuesta."
        alloc = [
            ("SGOV", "Treasuries 0-3 meses", 20, "reserva tÃ¡ctica"),
            ("AGG", "Bonos investment grade EE.UU.", 25, "base defensiva"),
            ("ACWI", "Acciones globales", 35, "nÃºcleo diversificado"),
            ("IVV", "S&P 500", 10, "calidad large cap EE.UU."),
            ("GLD", "Oro fÃ­sico vÃ­a ETF", 10, "diversificador"),
        ]
    elif score <= 3:
        perfil = "Crecimiento"
        tesis = "Acepta mÃ¡s fluctuaciÃ³n para buscar crecimiento, manteniendo una reserva y diversificaciÃ³n global."
        alloc = [
            ("SGOV", "Treasuries 0-3 meses", 10, "liquidez"),
            ("AGG", "Bonos investment grade EE.UU.", 15, "amortiguador"),
            ("ACWI", "Acciones globales", 40, "nÃºcleo global"),
            ("IVV", "S&P 500", 20, "motor EE.UU."),
            ("EEM", "Mercados emergentes", 10, "crecimiento satÃ©lite"),
            ("GLD", "Oro fÃ­sico vÃ­a ETF", 5, "cobertura"),
        ]
    else:
        perfil = "Agresivo diversificado"
        tesis = "Tiene tolerancia para renta variable, pero conserva caja mÃ­nima y activos no correlacionados."
        alloc = [
            ("SGOV", "Treasuries 0-3 meses", 5, "liquidez mÃ­nima"),
            ("AGG", "Bonos investment grade EE.UU.", 10, "control de volatilidad"),
            ("ACWI", "Acciones globales", 35, "nÃºcleo global"),
            ("IVV", "S&P 500", 30, "crecimiento EE.UU."),
            ("EEM", "Mercados emergentes", 15, "riesgo satÃ©lite"),
            ("GLD", "Oro fÃ­sico vÃ­a ETF", 5, "cobertura"),
        ]

    instrumentos = []
    for ticker, nombre, porcentaje, rol in alloc:
        instrumentos.append({
            "ticker": ticker,
            "nombre": nombre,
            "porcentaje": porcentaje,
            "rol": rol,
        })

    alertas = []
    if meses_supervivencia < 3:
        alertas.append("Antes de ejecutar una cartera de riesgo, construir 3 a 6 meses de gastos en instrumentos lÃ­quidos.")
    if conocimiento <= 2:
        alertas.append("Empezar con pocos instrumentos y rebalanceo simple; evitar derivados, apalancamiento y trading frecuente.")
    if confianza <= 2:
        alertas.append("Usar instrumentos transparentes, lÃ­quidos y con bajo costo para reducir fricciÃ³n psicolÃ³gica.")

    return {
        "perfil": perfil,
        "tesis": tesis,
        "instrumentos": instrumentos,
        "alertas": alertas,
        "rebalanceo": "Revisar cada 90 dÃ­as o cuando una clase se desvÃ­e mÃ¡s de 5 puntos porcentuales.",
    }
 
def resultado_view(request):
    """
    Genera y muestra el resultado financiero personalizado.
    Incluye: RadiografÃ­a, MÃ©tricas, Metas con feedback, Proyecciones, Plan de Guerra.
    """
    # ========================
    # 1. OBTENER DATOS DEL USUARIO
    # ========================
    diagnostico = None
    perfil = None
    ultimo_diagnostico_id = request.session.get("ultimo_diagnostico_id")

    if request.user.is_authenticated:
        perfil = ClientePerfil.objects.filter(user=request.user).first()
        if perfil:
            merge_guest_diagnostic_profile(request, perfil)
        if perfil and ultimo_diagnostico_id:
            diagnostico = DiagnosticoFinanciero.objects.filter(
                id=ultimo_diagnostico_id,
                cliente=perfil,
            ).first()
        if perfil and diagnostico is None:
            diagnostico = DiagnosticoFinanciero.objects.filter(cliente=perfil).last()
    elif ultimo_diagnostico_id:
        guest_profile_id = request.session.get("guest_diagnostico_perfil_id")
        diagnostico = DiagnosticoFinanciero.objects.filter(
            id=ultimo_diagnostico_id,
            cliente_id=guest_profile_id,
            cliente__user__isnull=True,
        ).select_related("cliente").first()
        perfil = diagnostico.cliente if diagnostico else None

    if not diagnostico:
        return redirect("formulario_view")
    
    # ========================
    # 2. CALCULAR SNAPSHOT Y RESULTADO IA
    # ========================
    snapshot = calcular_motor_financiero(diagnostico)
    resultado_ia = construir_resultado(perfil, diagnostico, permitir_ver=True)
    portfolio_sugerido = construir_portfolio_sugerido(snapshot, diagnostico)
    
    # ========================
    # 3. PARSEAR METAS CON FEEDBACK
    # ========================
    metas_info = None
    try:
        if resultado_ia.bloque_sesgo:
            metas_info = json.loads(resultado_ia.bloque_sesgo)
            # Sobreescribir imagen con el valor actual del METAS_MAP (ignora paths viejos en BD)
            meta_key = metas_info.get('meta_key')
            if not meta_key:
                # fallback para registros viejos: buscar por label
                label = metas_info.get('label', '')
                meta_key = next((k for k, v in METAS_MAP.items() if v['label'] == label), None)
            if meta_key and meta_key in METAS_MAP:
                metas_info['imagen'] = METAS_MAP[meta_key]['imagen']
    except (json.JSONDecodeError, TypeError):
        metas_info = None
    
    # ========================
    # 4. PARSEAR ACCIONES (Plan de Guerra)
    # ========================
    acciones = {"corto_plazo": [], "mediano_plazo": [], "largo_plazo": []}
    try:
        if resultado_ia.bloque_accion:
            acciones = json.loads(resultado_ia.bloque_accion)
    except (json.JSONDecodeError, TypeError):
        acciones = {"corto_plazo": [], "mediano_plazo": [], "largo_plazo": []}

    estructura = {}
    try:
        if resultado_ia.bloque_estructura:
            estructura = json.loads(resultado_ia.bloque_estructura)
    except (json.JSONDecodeError, TypeError):
        estructura = {}

    if not estructura:
        estructura = {
            "estado_general": snapshot.get("estado_general"),
            "perfil_financiero": snapshot.get("perfil_financiero"),
            "palanca_principal": snapshot.get("palanca_principal"),
            "riesgo_principal": snapshot.get("riesgo_principal"),
            "nivel_prejuicio": snapshot.get("nivel_prejuicio"),
            "conocimiento_financiero": snapshot.get("conocimiento_financiero"),
            "confianza_sistema": snapshot.get("confianza_sistema"),
        }

    if metas_info:
        metas_info.setdefault("perfil_financiero", estructura.get("perfil_financiero"))
        metas_info.setdefault("palanca_principal", estructura.get("palanca_principal"))
        metas_info.setdefault("riesgo_principal", estructura.get("riesgo_principal"))
        metas_info.setdefault("bloqueos_detectados", snapshot.get("bloqueos_detectados", []))

    estado_label_map = {
        "fragil": "Fragil",
        "presionado": "Presionado",
        "constructor": "Constructor",
        "acumulador": "Acumulador",
        "despegando": "Despegando",
    }
    estado_desc_map = {
        "fragil": "Hoy el sistema esta defendiendo caja y necesita recuperar aire antes de escalar.",
        "presionado": "Existe movimiento, pero cualquier desorden o imprevisto todavia te aprieta.",
        "constructor": "Ya hay margen y disciplina para empezar a convertir esfuerzo en sistema.",
        "acumulador": "Tu estructura ya acumula y ahora necesita mas criterio y diversificacion.",
        "despegando": "Hay potencial visible, pero aun falta orden para que el crecimiento sea consistente.",
    }
    palanca_desc_map = {
        "recuperar flujo de caja y bajar fragilidad": "Es la accion que mas rapido puede devolverte control operativo.",
        "crear margen y caja defensiva": "Primero necesitas espacio financiero para que tus decisiones no salgan desde la urgencia.",
        "convertir disciplina en sistema": "Ya no alcanza con voluntad: toca automatizar, medir y sostener.",
        "ordenar patrimonio y diversificar": "El siguiente salto no es trabajar mas, sino distribuir mejor el capital.",
        "escalar con foco y estructura": "Tu reto no es arrancar, sino crecer sin perder control ni liquidez.",
    }
    riesgo_desc_map = {
        "quedarte sin margen operativo": "Si no corriges esto primero, cualquier otra decision queda construida sobre fragilidad.",
        "invertir por encima de la caja que hoy puedes sostener": "Invertir esta bien, pero si ahoga tu liquidez te deja sin defensa.",
        "que la deuda cara te siga frenando": "La deuda toxica puede anular gran parte del esfuerzo que haces para avanzar.",
        "tener patrimonio pero sin caja real": "Puedes verte solvente en papeles y aun asi quedar vulnerable ante un imprevisto.",
        "quedarte inmovilizado por desconfianza": "No es falta de potencial, sino ruido mental frenando la ejecucion.",
        "crecer sin sistema claro": "Crecer sin reglas te expone a improvisar justo cuando mas dinero pasa por tus manos.",
    }

    estado_actual = snapshot.get("estado_general")
    palanca_actual = estructura.get("palanca_principal") or snapshot.get("palanca_principal")
    riesgo_actual = estructura.get("riesgo_principal") or snapshot.get("riesgo_principal")
    diagnostico_claves = [
        {
            "titulo": "Tu posicion actual",
            "valor": estado_label_map.get(estado_actual, "Sin definir"),
            "detalle": estado_desc_map.get(estado_actual, "Resume la etapa financiera en la que estas hoy."),
            "nota": f"Perfil interno detectado: {estructura.get('perfil_financiero') or snapshot.get('perfil_financiero') or 'sin definir'}",
        },
        {
            "titulo": "Tu palanca principal",
            "valor": (palanca_actual or "Sin definir").capitalize(),
            "detalle": palanca_desc_map.get(palanca_actual, "Es el movimiento con mayor retorno estrategico en tu caso actual."),
            "nota": "Si haces bien esto, el resto del plan empieza a rendir mucho mas.",
        },
        {
            "titulo": "Tu riesgo prioritario",
            "valor": (riesgo_actual or "Sin definir").capitalize(),
            "detalle": riesgo_desc_map.get(riesgo_actual, "Es el punto que mas conviene resolver antes de escalar."),
            "nota": "Atacarlo primero reduce errores caros y mejora tus decisiones siguientes.",
        },
    ]
    
    # ========================
    # 5. CALCULAR MÃ‰TRICAS
    # ========================
    margen_libertad = float(snapshot.get('ratio_libertad', 0)) * 100
    patrimonio_total = float(snapshot.get('patrimonio', 0))
    deuda_total = float(snapshot.get('deuda', 0))
    patrimonio_neto = patrimonio_total - deuda_total
    ingreso_por_hora = float(snapshot.get('ingreso_por_hora', 0))
    
    # ========================
    # 6. PARSEAR PROYECCIONES
    # ========================
    proy_pos = list(resultado_ia.proy_pos) if resultado_ia.proy_pos else []
    proy_med = list(resultado_ia.proy_med) if resultado_ia.proy_med else []
    proy_neg = list(resultado_ia.proy_neg) if resultado_ia.proy_neg else []
    if not proy_pos or not proy_med or not proy_neg:
        proyecciones = calcular_proyecciones(perfil, snapshot)
        proy_pos = list(proyecciones.get("positiva", []))
        proy_med = list(proyecciones.get("media", []))
        proy_neg = list(proyecciones.get("negativa", []))

    proy_pos_json = json.dumps(proy_pos)
    proy_med_json = json.dumps(proy_med)
    proy_neg_json = json.dumps(proy_neg)
    
    # ========================
    # 7. CONTEXTO PARA TEMPLATE
    # ========================
    contexto = {
        # Resultado IA
        "resultado": resultado_ia,
        
        # MÃ©tricas principales
        "margen_libertad": round(margen_libertad, 1),
        "patrimonio_total": patrimonio_total,
        "patrimonio_neto": patrimonio_neto,
        "ingreso_por_hora": ingreso_por_hora,
        
        # Metas con feedback personalizado
        "metas_info": metas_info,
        "diagnostico_claves": diagnostico_claves,
        "estructura": estructura,
        "snapshot": snapshot,
        "codigo_anonimo": diagnostico.codigo_anonimo,
        "portfolio_sugerido": portfolio_sugerido,
        
        # Proyecciones (JSON safe)
        "proy_pos_json": proy_pos_json,
        "proy_med_json": proy_med_json,
        "proy_neg_json": proy_neg_json,
        
        # Plan de Guerra
        "acciones": acciones,
    }
    
    return render(request, "calculadora/resultadotest.html", contexto)


def sugerencia_view(request):
    diagnostico = None
    perfil = None
    ultimo_diagnostico_id = request.session.get("ultimo_diagnostico_id")

    if request.user.is_authenticated:
        perfil = ClientePerfil.objects.filter(user=request.user).first()
        if perfil:
            merge_guest_diagnostic_profile(request, perfil)
        if perfil and ultimo_diagnostico_id:
            diagnostico = DiagnosticoFinanciero.objects.filter(
                id=ultimo_diagnostico_id,
                cliente=perfil,
            ).first()
        if perfil and diagnostico is None:
            diagnostico = DiagnosticoFinanciero.objects.filter(cliente=perfil).last()
    elif ultimo_diagnostico_id:
        guest_profile_id = request.session.get("guest_diagnostico_perfil_id")
        diagnostico = DiagnosticoFinanciero.objects.filter(
            id=ultimo_diagnostico_id,
            cliente_id=guest_profile_id,
            cliente__user__isnull=True,
        ).select_related("cliente").first()
        perfil = diagnostico.cliente if diagnostico else None

    if not diagnostico:
        return redirect("formulario_view")

    snapshot = calcular_motor_financiero(diagnostico)
    portfolio_sugerido = construir_portfolio_sugerido(snapshot, diagnostico)
    ingresos = float(snapshot.get("ingresos") or 0)
    gastos = float(snapshot.get("gastos") or 0)
    ahorro = float(snapshot.get("ahorro") or 0)
    inversion_mercado = max(ahorro * 0.8, 0)
    meses_supervivencia = float(snapshot.get("meses_supervivencia") or 0)

    profile_display_name = "Invitado"
    if perfil and perfil.user:
        profile_display_name = perfil.alias or perfil.user.first_name or perfil.user.username
    elif perfil and perfil.alias:
        profile_display_name = perfil.alias

    return render(request, "calculadora/sugerencia.html", {
        "perfil": perfil,
        "diagnostico": diagnostico,
        "snapshot": snapshot,
        "portfolio_sugerido": portfolio_sugerido,
        "ingresos": ingresos,
        "gastos": gastos,
        "ahorro": ahorro,
        "inversion_mercado": inversion_mercado,
        "meses_supervivencia": meses_supervivencia,
        "profile_display_name": profile_display_name,
    })
 

def rodriguez_wallet(request):
    from django.contrib import messages
    from django.core.paginator import Paginator
    from django.db.models import Sum
    from django.shortcuts import get_object_or_404
    from django.utils.dateparse import parse_date
    from .models import (
        BlueDollarRate,
        RodriguezCost,
        RodriguezSale,
        PersonalBudget,
        PersonalExpenseCategory,
        PersonalWalletMovement,
        PersonalWalletSettings,
    )

    _ensure_rodriguez_user()
    if not _rodriguez_required(request):
        return redirect("distribuidora_rodriguez")

    wallet_settings = _ensure_wallet_defaults()
    selected_year, selected_month, period_range, period_start, period_end = _wallet_period_bounds(request)

    def wallet_redirect(tab="panel"):
        return redirect(f"{request.path}?tab={tab}&anio={selected_year}&mes={selected_month}&rango={period_range}")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "currency":
            currency = request.POST.get("display_currency")
            if currency in {"ARS", "USD"}:
                wallet_settings.display_currency = currency
                wallet_settings.save(update_fields=["display_currency", "updated_at"])
            return wallet_redirect(request.POST.get("return_tab") or "panel")
        if action == "category":
            name = request.POST.get("category_name", "").strip()
            if name:
                PersonalExpenseCategory.objects.get_or_create(
                    name=name,
                    defaults={"active": True, "color": request.POST.get("color", "").strip() or "#776b5e"},
                )
                messages.success(request, "Categoria agregada.")
            return wallet_redirect("config")
        if action == "category_toggle":
            category = get_object_or_404(PersonalExpenseCategory, pk=request.POST.get("category_id"))
            category.active = not category.active
            category.save(update_fields=["active"])
            return wallet_redirect("config")
        if action in {"expense", "income"}:
            category = None
            category_id = request.POST.get("category_id")
            if category_id:
                category = get_object_or_404(PersonalExpenseCategory, pk=category_id)
            PersonalWalletMovement.objects.create(
                created_by=request.user,
                date=_naif_date(request.POST.get("date")),
                kind=PersonalWalletMovement.EXPENSE if action == "expense" else PersonalWalletMovement.INCOME,
                category=category,
                description=request.POST.get("description", "").strip(),
                amount=_money_from_post(request.POST.get("amount")),
                payment_method=request.POST.get("payment_method", "").strip(),
                notes=request.POST.get("notes", "").strip(),
            )
            messages.success(request, "Movimiento guardado.")
            return wallet_redirect("panel")
        if action == "movement_update":
            movement = get_object_or_404(PersonalWalletMovement, pk=request.POST.get("movement_id"))
            category_id = request.POST.get("category_id")
            movement.date = _naif_date(request.POST.get("date"))
            movement.kind = request.POST.get("kind") if request.POST.get("kind") in {"expense", "income"} else movement.kind
            movement.category = get_object_or_404(PersonalExpenseCategory, pk=category_id) if category_id else None
            movement.description = request.POST.get("description", "").strip()
            movement.amount = _money_from_post(request.POST.get("amount"))
            movement.payment_method = request.POST.get("payment_method", "").strip()
            movement.notes = request.POST.get("notes", "").strip()
            movement.save()
            messages.success(request, "Movimiento actualizado.")
            return wallet_redirect("historial")
        if action == "movement_delete":
            movement = get_object_or_404(PersonalWalletMovement, pk=request.POST.get("movement_id"))
            movement.delete()
            messages.success(request, "Movimiento eliminado.")
            return wallet_redirect("historial")
        if action == "budget":
            category = get_object_or_404(PersonalExpenseCategory, pk=request.POST.get("category_id"))
            PersonalBudget.objects.update_or_create(
                category=category,
                year=selected_year,
                month=selected_month,
                defaults={"amount": _money_from_post(request.POST.get("amount"))},
            )
            return wallet_redirect("config")

    categories = list(PersonalExpenseCategory.objects.all())
    active_categories = [category for category in categories if category.active]
    movements_qs = PersonalWalletMovement.objects.filter(date__gte=period_start, date__lte=period_end)
    expenses_qs = movements_qs.filter(kind=PersonalWalletMovement.EXPENSE)
    incomes_qs = movements_qs.filter(kind=PersonalWalletMovement.INCOME)
    naif_sales = RodriguezSale.objects.filter(date__gte=period_start, date__lte=period_end).aggregate(total=Sum("total"))["total"] or Decimal("0")
    naif_costs = RodriguezCost.objects.filter(date__gte=period_start, date__lte=period_end).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    naif_profit = naif_sales - naif_costs
    expenses_total = expenses_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    incomes_total = incomes_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    available_total = incomes_total + naif_profit
    balance = available_total - expenses_total
    investment_suggestion = max(available_total, Decimal("0")) * wallet_settings.investment_suggestion_percent / Decimal("100")

    rate_cache = {
        rate.date: rate.sell
        for rate in BlueDollarRate.objects.filter(date__lte=period_end).order_by("date")
    }
    currency = wallet_settings.display_currency
    today = timezone.localdate()
    currency_warning = currency == "USD" and not rate_cache
    def show(value, day=None):
        return _display_money(value, day or period_end, currency, rate_cache)

    expense_bars = []
    category_totals = expenses_qs.values("category__name", "category__color").annotate(total=Sum("amount")).order_by("-total")
    max_category = max([row["total"] for row in category_totals] + [Decimal("1")])
    for row in category_totals:
        expense_bars.append({
            "name": row["category__name"] or "Sin categoria",
            "color": row["category__color"] or "#f31313",
            "total": show(row["total"]),
            "percent": int((row["total"] / max_category) * Decimal("100")),
        })

    daily_map = {}
    for movement in movements_qs:
        row = daily_map.setdefault(movement.date, {"date": movement.date, "expenses": Decimal("0"), "incomes": Decimal("0")})
        row["expenses" if movement.kind == PersonalWalletMovement.EXPENSE else "incomes"] += movement.amount
    daily_rows = []
    for day, row in sorted(daily_map.items()):
        daily_rows.append({
            "label": day.strftime("%d/%m"),
            "expenses": show(row["expenses"], day),
            "incomes": show(row["incomes"], day),
            "net": show(row["incomes"] - row["expenses"], day),
        })

    history_date = parse_date(request.GET.get("hist_fecha") or "")
    history_qs = PersonalWalletMovement.objects.all()
    if history_date:
        history_qs = history_qs.filter(date=history_date)
    history_paginator = Paginator(history_qs, 10)
    history_page = history_paginator.get_page(request.GET.get("page") or 1)
    movement_rows = list(history_page.object_list)
    for movement in movement_rows:
        movement.display_amount = show(movement.amount, movement.date)

    budget_rows = []
    budget_map = {budget.category_id: budget for budget in PersonalBudget.objects.filter(year=selected_year, month=selected_month)}
    spent_map = {
        row["category_id"]: row["total"] or Decimal("0")
        for row in expenses_qs.values("category_id").annotate(total=Sum("amount"))
    }
    for category in active_categories:
        budget = budget_map.get(category.id)
        amount = budget.amount if budget else Decimal("0")
        spent = spent_map.get(category.id, Decimal("0"))
        percent = int((spent / amount) * Decimal("100")) if amount else 0
        budget_rows.append({
            "category": category,
            "amount": show(amount),
            "spent": show(spent),
            "percent": min(percent, 140),
        })

    years = sorted(
        {year_date.year for year_date in PersonalWalletMovement.objects.dates("date", "year")}
        | {year_date.year for year_date in RodriguezSale.objects.dates("date", "year")}
        | {today.year},
        reverse=True,
    )
    months = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"), (5, "Mayo"), (6, "Junio"),
        (7, "Julio"), (8, "Agosto"), (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
    ]

    context = {
        "today": today,
        "settings": wallet_settings,
        "currency": currency,
        "currency_symbol": "US$" if currency == "USD" else "$",
        "currency_warning": currency_warning,
        "selected_year": selected_year,
        "selected_month": selected_month,
        "period_range": period_range,
        "period_start": period_start,
        "period_end": period_end,
        "history_date": history_date,
        "history_page": history_page,
        "history_query_base": (
            f"tab=historial&anio={selected_year}&mes={selected_month}&rango={period_range}"
            + (f"&hist_fecha={history_date.isoformat()}" if history_date else "")
        ),
        "years": years,
        "months": months,
        "categories": categories,
        "active_categories": active_categories,
        "movements": movement_rows,
        "expenses_total": show(expenses_total),
        "incomes_total": show(incomes_total),
        "naif_profit": show(naif_profit),
        "available_total": show(available_total),
        "balance": show(balance),
        "investment_suggestion": show(investment_suggestion),
        "expense_bars": expense_bars,
        "daily_rows": daily_rows[-18:],
        "budget_rows": budget_rows,
    }
    return render(request, "calculadora/rodriguez_wallet.html", context)


def andex_landing(request):
    return render(request, 'calculadora/andex_landing.html')


def distribuidora_asistente_247(request):
    if not request.session.get("erp_demo_auth"):
        return JsonResponse({"ok": False, "reply": "Necesitas iniciar sesion para usar Asistente 247."}, status=403)
    if request.method != "POST":
        return JsonResponse({"ok": False, "reply": "Metodo no permitido."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "reply": "No pude leer el mensaje. Probemos de nuevo."}, status=400)

    message = str(payload.get("message", "")).strip()
    snapshot = payload.get("state") or {}
    text = message.lower()

    products = snapshot.get("products") or []
    clients = snapshot.get("clients") or []
    orders = snapshot.get("orders") or []
    cashflow = snapshot.get("cashflow") or []
    totals = snapshot.get("totals") or {}

    def money(value):
        try:
            return "$" + f"{int(round(float(value or 0))):,}".replace(",", ".")
        except (TypeError, ValueError):
            return "$0"

    def find_by_name(items, field="name"):
        clean_text = text.replace(",", " ")
        best = None
        for item in items:
            name = str(item.get(field, "")).lower()
            if name and name in clean_text:
                return item
            tokens = [token for token in name.split() if len(token) > 3]
            score = sum(1 for token in tokens if token in clean_text)
            if score and (not best or score > best[0]):
                best = (score, item)
        return best[1] if best else None

    def first_number(default=None):
        import re
        match = re.search(r"(\d+(?:[.,]\d+)?)", text)
        if not match:
            return default
        return float(match.group(1).replace(",", "."))

    try:
        import os
        from openai import OpenAI

        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            compact_state = {
                "products": products[:90],
                "clients": clients,
                "orders": orders,
                "cashflow": cashflow,
                "totals": totals,
            }
            system_prompt = (
                "Sos Asistente 247, una IA real dentro de un ERP demo para una distribuidora de alimentos. "
                "Tu tono es calido, simple, inteligente y operativo. Ayudas a trabajar, no haces humo.\n"
                "LeÃ© el estado actual del portal que recibis en JSON y respondÃ© con datos concretos.\n"
                "PodÃ©s guiar al usuario por estos mÃ³dulos: dashboard, tienda-publica, marketplace, ventas, "
                "armado, facturacion, logistica, stock, compras, clientes, finanzas y rrhh.\n"
                "Si el usuario pide ver stock o flujo de caja, respondÃ© con anÃ¡lisis breve y accion de navegar.\n"
                "Si pide cargar venta o registrar compra, preparÃ¡ una acciÃ³n, pero siempre needs_confirmation=true. "
                "No digas que ya ejecutaste una venta o compra si todavÃ­a no fue confirmada.\n"
                "Para preparar una venta necesitÃ¡s client_code, product_code y qty. Para preparar una compra necesitÃ¡s "
                "provider, product_code, qty y cost. Si faltan datos, pedilos y navegÃ¡ al mÃ³dulo correcto.\n"
                "DevolvÃ© SOLO JSON vÃ¡lido con esta forma exacta: "
                "{\"ok\":true,\"reply\":\"texto\",\"action\":null|{\"type\":\"navigate\",\"view\":\"stock\"}|"
                "{\"type\":\"prepare_sale\",\"client_code\":44,\"product_code\":101,\"qty\":20,\"amount\":123,\"feasible\":true}|"
                "{\"type\":\"prepare_purchase\",\"provider\":\"Campo Sur\",\"product_code\":104,\"qty\":50,\"cost\":1800},"
                "\"needs_confirmation\":false,\"confirm_label\":\"Confirmar\"}."
            )
            user_prompt = (
                "Mensaje del usuario:\n"
                f"{message}\n\n"
                "Estado actual del ERP demo:\n"
                f"{json.dumps(compact_state, ensure_ascii=False)}"
            )
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=360,
                temperature=0.35,
            )
            ai_payload = json.loads(response.choices[0].message.content or "{}")
            action = ai_payload.get("action")
            allowed_views = {
                "dashboard", "tienda-publica", "marketplace", "ventas", "armado",
                "facturacion", "logistica", "stock", "compras", "clientes", "finanzas", "rrhh"
            }
            allowed_actions = {"navigate", "prepare_sale", "prepare_purchase"}
            if isinstance(action, dict):
                if action.get("type") not in allowed_actions:
                    action = None
                if action and action.get("type") == "navigate" and action.get("view") not in allowed_views:
                    action = None
            else:
                action = None
            return JsonResponse({
                "ok": bool(ai_payload.get("ok", True)),
                "reply": str(ai_payload.get("reply") or "Estoy mirando el portal. Decime que queres hacer y te guio."),
                "action": action,
                "needs_confirmation": bool(ai_payload.get("needs_confirmation", False)),
                "confirm_label": ai_payload.get("confirm_label") or "Confirmar",
                "engine": "openai",
            })
    except Exception as e:
        print(f"[Asistente 247] OpenAI fallback local: {e}")

    if any(word in text for word in ["stock", "inventario", "faltante", "critico", "crÃ­tico"]):
        critical = [p for p in products if float(p.get("stock") or 0) <= float(p.get("min") or 0)]
        low = sorted(products, key=lambda p: float(p.get("stock") or 0))[:5]
        critical_names = ", ".join(p.get("name", "") for p in critical[:4]) or "sin productos criticos"
        low_names = ", ".join(f"{p.get('name')} ({p.get('stock')})" for p in low[:4])
        return JsonResponse({
            "ok": True,
            "reply": (
                f"Te llevo a Stock. Hoy veo {len(critical)} productos por debajo del minimo: {critical_names}. "
                f"Los niveles mas bajos son {low_names}. Conviene revisar reposicion antes de vender fuerte esos articulos."
            ),
            "action": {"type": "navigate", "view": "stock"},
            "needs_confirmation": False,
        })

    if any(word in text for word in ["caja", "flujo", "finanza", "finanzas", "mes", "vencimiento", "cobro"]):
        month_net = sum((1 if m.get("type") == "cobro" else -1) * float(m.get("amount") or 0) for m in cashflow)
        incoming = sum(float(m.get("amount") or 0) for m in cashflow if m.get("type") == "cobro")
        outgoing = sum(float(m.get("amount") or 0) for m in cashflow if m.get("type") != "cobro")
        next_items = sorted(cashflow, key=lambda m: str(m.get("date", "")))[:3]
        next_text = "; ".join(f"{m.get('date')} {m.get('concept')} {money(m.get('amount'))}" for m in next_items) or "sin movimientos agendados"
        return JsonResponse({
            "ok": True,
            "reply": (
                f"Te abro Finanzas. El flujo mensual agendado da {money(month_net)}: "
                f"cobros por {money(incoming)} y pagos por {money(outgoing)}. Proximos movimientos: {next_text}."
            ),
            "action": {"type": "navigate", "view": "finanzas"},
            "needs_confirmation": False,
        })

    if any(word in text for word in ["compra", "comprÃ©", "compre", "proveedor", "insumo", "gasto"]):
        product = find_by_name(products)
        qty = first_number(50)
        cost = None
        if " a " in text:
            numbers = []
            import re
            for match in re.findall(r"(\d+(?:[.,]\d+)?)", text):
                numbers.append(float(match.replace(",", ".")))
            if len(numbers) > 1:
                cost = numbers[-1]
        cost = cost or float((product or {}).get("cost") or 1)
        provider = "Campo Sur" if "campo" in text else "Distribuidora Centro" if "centro" in text else "Servicios generales" if "servicio" in text else "Frigorifico Norte"
        if not product:
            return JsonResponse({
                "ok": True,
                "reply": "Vamos a cargar una compra. Decime producto, cantidad y costo unitario. Ejemplo: compre 50 kg de papa lavada a 1800.",
                "action": {"type": "navigate", "view": "compras"},
                "needs_confirmation": False,
            })
        total = qty * cost
        return JsonResponse({
            "ok": True,
            "reply": f"Entendi una compra a {provider}: {qty:g} {product.get('mode')} de {product.get('name')} a {money(cost)}. Total estimado {money(total)}. Confirmame y la dejo cargada en compras.",
            "action": {
                "type": "prepare_purchase",
                "provider": provider,
                "product_code": product.get("code"),
                "qty": qty,
                "cost": cost,
            },
            "needs_confirmation": True,
            "confirm_label": "Confirmar compra",
        })

    if any(word in text for word in ["venta", "pedido", "vender", "cliente"]):
        product = find_by_name(products)
        client = find_by_name(clients)
        qty = first_number(1)
        if not product or not client:
            return JsonResponse({
                "ok": True,
                "reply": "Vamos con una venta. Decime cliente, producto y cantidad. Ejemplo: cargar venta a Mercado Centro de 20 kg de tomate redondo.",
                "action": {"type": "navigate", "view": "ventas"},
                "needs_confirmation": False,
            })
        amount = qty * float(product.get("price") or 0)
        feasible = qty <= float(product.get("stock") or 0)
        return JsonResponse({
            "ok": True,
            "reply": f"PreparÃ© el pedido para {client.get('name')}: {qty:g} {product.get('mode')} de {product.get('name')} por {money(amount)}. Stock actual {product.get('stock')}. {'Es factible.' if feasible else 'Ojo: supera el stock disponible.'} Confirmame antes de cargarlo.",
            "action": {
                "type": "prepare_sale",
                "client_code": client.get("code"),
                "product_code": product.get("code"),
                "qty": qty,
                "amount": amount,
                "feasible": feasible,
            },
            "needs_confirmation": True,
            "confirm_label": "Confirmar venta",
        })

    modules = "Ventas, Cargar compra, Stock, Finanzas, Logistica, Clientes, Facturacion, Armado pedidos, Marketplace y RRHH"
    return JsonResponse({
        "ok": True,
        "reply": f"Estoy para guiarte por el portal. Puedo ayudarte con {modules}. Decime algo como: cargar venta, registrar compra, controlar stock o ver flujo de caja del mes.",
        "action": None,
        "needs_confirmation": False,
    })




from django.shortcuts import render
from .models import Player  # o lo que corresponda

def ranking(request):
    jugadores = Player.objects.all().order_by('-score')[:10]  # o tu lÃ³gica
    usuario_actual = None  # buscÃ¡s el usuario actual si querÃ©s
    promedio = 80  # por ejemplo

    context = {
        'jugadores': jugadores,
        'usuario_actual': usuario_actual,
        'promedio': promedio,
        # lo que quieras pasar
    }
    return render(request, 'ranking.html', context)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Player, PlayerResult

from django.utils import timezone
from .models import QuizQuestion, QuizParticipacion

from django.shortcuts import render, get_object_or_404



@csrf_exempt
def guardar_perfil(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            perfil_nombre = data.get("perfil_generado")
            resultados = data.get("resultados")
            player_id = data.get("player_id") or request.session.get("player_id")  # âœ… Esta es la lÃ­nea clave

            if not (perfil_nombre and resultados and player_id):
                return JsonResponse({"error": "Faltan datos"}, status=400)

            jugador = Player.objects.get(id=player_id)

            PlayerResult.objects.create(
                player=jugador,
                vehicle_percentage=resultados.get("vehicle", 0),
                property_percentage=resultados.get("property", 0),
                education_percentage=resultados.get("education", 0),
                investment_percentage=resultados.get("investment", 0),
                leisure_percentage=resultados.get("leisure", 0),
                business_percentage=resultados.get("business", 0),
                score=0,  # PodÃ©s calcularlo y guardar si querÃ©s
                perfil_generado=perfil_nombre
            )

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "MÃ©todo no permitido"}, status=405)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

def require_login_action(request, redirect_to):
    """ Guarda la acciÃ³n solicitada para despuÃ©s del login """
    request.session["next_url"] = redirect_to
    return redirect("login_google")


# Mostrar la pregunta del dÃ­a
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.mail import send_mail
from .models import ClientePerfil, QuizParticipacion

from django.contrib.auth.models import User

@login_required
def alias_modal_view(request):
    profile, _ = ClientePerfil.objects.get_or_create(user=request.user)
    if profile.alias and profile.alias != f"usuario_{request.user.id}":
        return redirect('daily_quiz')

    if request.method == 'POST':
        alias = request.POST.get('alias').strip()
        if alias and not ClientePerfil.objects.filter(alias=alias).exists():
            profile.alias = alias
            profile.save()
            send_mail(
                'Â¡Bienvenido a InvertiresFÃ¡cil!',
                'Gracias por unirte a InvertiresFÃ¡cil, tu alias ya estÃ¡ activo y puedes empezar a jugar. Â¡Mucha suerte!',
                'no-reply@invertiresfacil.com',
                [request.user.email],
                fail_silently=True,
            )
            return redirect('daily_quiz')
        else:
            return render(request, 'alias_modal.html', {'error': 'Alias no disponible o invÃ¡lido.'})
    
    return render(request, 'alias_modal.html')

from django.utils import timezone

def ranking_view(request):
    filtro = request.GET.get('filtro', 'historico')
    if filtro == 'mes':
        desde = timezone.now() - timezone.timedelta(days=30)
        scores = UserScore.objects.filter(created_at__gte=desde)
    elif filtro == 'semana':
        desde = timezone.now() - timezone.timedelta(days=7)
        scores = UserScore.objects.filter(created_at__gte=desde)
    else:
        scores = UserScore.objects.all()

    scores = scores.order_by('-score', 'time_taken')
    paginator = Paginator(scores, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rankingquiz.html', {'page_obj': page_obj, 'filtro': filtro})





# Mostrar la pregunta del dÃ­a
import os as _os

_QUIZ_OFFSET_FILE = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), 'quiz_offset.json')

def _get_quiz_offset():
    try:
        import json as _json
        with open(_QUIZ_OFFSET_FILE) as f:
            return _json.load(f).get('offset', 0)
    except Exception:
        return 0

def _set_quiz_offset(offset):
    import json as _json
    with open(_QUIZ_OFFSET_FILE, 'w') as f:
        _json.dump({'offset': offset}, f)


# ============================================================
# REEMPLAZÃ las vistas del quiz en tu views.py con este bloque.
# BuscÃ¡ desde "_quiz_limite" hasta el final de "ranking_quiz_view"
# y reemplazalo completo.
# ============================================================

import os as _os
import json
import random as _random

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import (
    ClientePerfil, QuizQuestion, QuizOption,
    QuizParticipacion,
)

# â”€â”€ Archivo de offset (rotaciÃ³n diaria de preguntas) â”€â”€â”€â”€â”€â”€â”€â”€
_QUIZ_OFFSET_FILE = _os.path.join(
    _os.path.dirname(_os.path.dirname(__file__)), 'quiz_offset.json'
)

def _get_quiz_offset():
    try:
        with open(_QUIZ_OFFSET_FILE) as f:
            return json.load(f).get('offset', 0)
    except Exception:
        return 0

def _set_quiz_offset(offset):
    with open(_QUIZ_OFFSET_FILE, 'w') as f:
        json.dump({'offset': offset}, f)


# â”€â”€ CategorÃ­as de la ruleta â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CATEGORIAS = [
    ('acciones',              'ðŸ“ˆ Acciones'),
    ('matematica_financiera', 'ðŸ§® MatemÃ¡tica Financiera'),
    ('fci_etf',               'ðŸ“Š FCI o ETF'),
    ('internacional',         'ðŸŒ Internacional'),
    ('argentina',             'ðŸ‡¦ðŸ‡· Argentina'),
    ('fintech',               'ðŸ’¡ Fintech'),
]
CATEGORIAS_KEYS = [c[0] for c in CATEGORIAS]


# â”€â”€ LÃ­mite diario unificado: 3 para TODOS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _quiz_limite(request):
    """Retorna (jugadas_hoy, limite_diario, es_premium)."""
    today = timezone.now().date()
    LIMITE = 3  # igual para todos

    if request.user.is_authenticated:
        perfil = getattr(request.user, 'clienteperfil', None)
        plan   = getattr(perfil, 'plan_activo', 1) or 1
        es_premium = plan == 3
        jugadas = (
            QuizParticipacion.objects.filter(cliente=perfil, fecha=today).count()
            if perfil else 0
        )
    else:
        es_premium = False
        jugadas    = request.session.get(f'quiz_count_{today}', 0)

    return jugadas, LIMITE, es_premium


# â”€â”€ Vista principal del quiz â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def daily_question_view(request):
    today         = timezone.now().date()
    guest_skipped = request.session.get('quiz_guest_skipped', False)

    # POST = invitado eligiendo alias
    if request.method == 'POST' and not request.user.is_authenticated:
        alias = request.POST.get('alias', '').strip()
        if alias:
            if ClientePerfil.objects.filter(alias__iexact=alias).exists():
                return render(request, 'calculadora/daily_question.html', {
                    'pedir_alias': True,
                    'alias_error': 'Ese alias ya estÃ¡ en uso. ElegÃ­ otro.',
                })
            request.session['quiz_guest_alias']   = alias
            request.session['quiz_guest_skipped'] = True
        return redirect('daily_quiz')

    # Primer acceso sin cuenta â†’ modal login
    if not request.user.is_authenticated and not guest_skipped:
        return render(request, 'calculadora/daily_question.html', {
            'mostrar_login_modal': True,
        })

    # Invitado sin alias
    if not request.user.is_authenticated and not request.session.get('quiz_guest_alias'):
        return render(request, 'calculadora/daily_question.html', {'pedir_alias': True})

    # LÃ­mite diario alcanzado
    jugadas_hoy, limite, es_premium = _quiz_limite(request)
    if jugadas_hoy >= limite:
        return render(request, 'calculadora/daily_question.html', {
            'ya_jugo'        : True,
            'limite_alcanzado': True,
            'es_premium'     : es_premium,
            'jugadas_hoy'    : jugadas_hoy,
            'limite'         : limite,
        })

    # â”€â”€ CategorÃ­a elegida por la ruleta â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    categoria_key = request.GET.get('cat', '').strip()
    auto_spin     = request.GET.get('auto_spin', '0') == '1'

    # Si no hay categorÃ­a vÃ¡lida â†’ mostrar ruleta
    if categoria_key not in CATEGORIAS_KEYS:
        return render(request, 'calculadora/daily_question.html', {
            'mostrar_ruleta' : True,
            'categorias'     : CATEGORIAS,
            'jugadas_hoy'    : jugadas_hoy,
            'limite'         : limite,
            'es_premium'     : es_premium,
            'auto_spin'      : auto_spin,
        })

    # Buscar pregunta vÃ¡lida en esa categorÃ­a (debe tener opciÃ³n correcta)
    qs = QuizQuestion.objects.filter(
        categoria=categoria_key,
        options__is_correct=True,
    ).distinct()

    if not qs.exists():
        # Sin preguntas vÃ¡lidas en esta categorÃ­a â†’ fallback server-side a cualquier categorÃ­a
        # (sin redirect al cliente, evita el doble giro y el loop infinito)
        qs = QuizQuestion.objects.filter(options__is_correct=True).distinct()
        if not qs.exists():
            return render(request, 'calculadora/daily_question.html', {
                'question'    : None,
                'mostrar_ruleta': False,
                'jugadas_hoy' : jugadas_hoy,
                'limite'      : limite,
                'es_premium'  : es_premium,
            })

    # Elegir pregunta del dÃ­a
    total     = qs.count()
    base_idx  = (today.toordinal() + _get_quiz_offset() + jugadas_hoy) % total
    question  = qs.order_by('id')[base_idx]

    correct_option = question.options.filter(is_correct=True).first()
    options        = list(question.options.all())

    # Guardia adicional: pregunta sin opciones en DB (dato corrupto)
    if not correct_option or not options:
        return render(request, 'calculadora/daily_question.html', {
            'question'    : None,
            'mostrar_ruleta': False,
            'jugadas_hoy' : jugadas_hoy,
            'limite'      : limite,
            'es_premium'  : es_premium,
        })

    _random.Random(question.id * 1000 + today.toordinal()).shuffle(options)

    # Usar la categorÃ­a real de la pregunta (puede diferir si hubo fallback)
    categoria_key   = question.categoria
    categoria_label = dict(CATEGORIAS).get(categoria_key, categoria_key)

    return render(request, 'calculadora/daily_question.html', {
        'question'           : question,
        'shuffled_options'   : options,
        'correct_option_text': correct_option.text,
        'ya_jugo'            : False,
        'jugadas_hoy'        : jugadas_hoy,
        'limite'             : limite,
        'es_premium'         : es_premium,
        'categoria_key'      : categoria_key,
        'categoria_label'    : categoria_label,
        'mostrar_ruleta'     : True,
        'mostrar_popup'      : True,
        'auto_spin'          : False,
    })


# â”€â”€ Endpoint: registrar respuesta â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def submit_answer_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    data          = json.loads(request.body)
    question_id   = data.get('question_id')
    selected      = data.get('selected_option')
    used_help     = data.get('used_help', False)
    time_taken    = data.get('time_taken', 60)
    today         = timezone.now().date()

    question       = get_object_or_404(QuizQuestion, id=question_id)
    correct_option = question.options.filter(is_correct=True).first()

    jugadas_hoy, limite, es_premium = _quiz_limite(request)
    if jugadas_hoy >= limite:
        return JsonResponse({'success': False, 'limit_reached': True, 'es_premium': es_premium})

    # Puntaje
    was_correct = bool(correct_option and selected == correct_option.text)
    if was_correct:
        base_score = max(10, 100 - int(time_taken * 1.5))
        score      = int(base_score * 0.7) if used_help else base_score
    else:
        score = 0

    # Guardar
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'clienteperfil', None)
        if perfil:
            QuizParticipacion.objects.create(
                cliente=perfil, fecha=today, puntaje=score,
                correctas=1 if was_correct else 0,
                usadas_ayuda=used_help, duracion=int(time_taken),
            )
            perfil.quiz_score_total = (perfil.quiz_score_total or 0) + score
            perfil.save(update_fields=['quiz_score_total'])
    else:
        guest_alias = request.session.get('quiz_guest_alias', '')
        if guest_alias:
            QuizParticipacion.objects.create(
                cliente=None, guest_alias=guest_alias, fecha=today,
                puntaje=score, correctas=1 if was_correct else 0,
                usadas_ayuda=used_help, duracion=int(time_taken),
            )
        count = request.session.get(f'quiz_count_{today}', 0)
        request.session[f'quiz_count_{today}'] = count + 1

    nuevas = jugadas_hoy + 1
    return JsonResponse({
        'success'      : True,
        'score'        : score,
        'correct'      : was_correct,
        'jugadas_hoy'  : nuevas,
        'limite'       : limite,
        'limit_reached': nuevas >= limite,
        'es_premium'   : es_premium,
    })


def intro_quiz_view(request):
    return redirect('daily_quiz')

def quiz_skip_login_view(request):
    request.session['quiz_guest_skipped'] = True
    return redirect('daily_quiz')


# â”€â”€ Ranking SOLO del dÃ­a actual â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def ranking_quiz_view(request):
    from django.db.models import Sum

    today = timezone.now().date()

    # Usuarios registrados â€” solo hoy
    user_scores = (
        QuizParticipacion.objects
        .filter(cliente__isnull=False, fecha=today)
        .values('cliente__alias', 'cliente__user__username')
        .annotate(total=Sum('puntaje'))
        .order_by('-total')
    )
    entries = []
    for s in user_scores:
        entries.append({
            'alias': s['cliente__alias'] or s['cliente__user__username'] or 'AnÃ³nimo',
            'score': s['total'] or 0,
        })

    # Invitados â€” solo hoy
    guest_scores = (
        QuizParticipacion.objects
        .filter(cliente__isnull=True, fecha=today)
        .exclude(guest_alias='')
        .values('guest_alias')
        .annotate(total=Sum('puntaje'))
    )
    for g in guest_scores:
        entries.append({'alias': g['guest_alias'], 'score': g['total'] or 0})

    entries = sorted(entries, key=lambda x: x['score'], reverse=True)

    paginator  = Paginator(entries, 10)
    page_obj   = paginator.get_page(request.GET.get('page'))

    mi_alias = None
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'clienteperfil', None)
        if perfil:
            mi_alias = perfil.alias or request.user.username
    else:
        mi_alias = request.session.get('quiz_guest_alias') or None

    # Puntaje del usuario en el dÃ­a para el mensaje de compartir
    mi_score = 0
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'clienteperfil', None)
        if perfil:
            mi_score = QuizParticipacion.objects.filter(
                cliente=perfil, fecha=today
            ).aggregate(total=Sum('puntaje'))['total'] or 0
    else:
        guest_alias = request.session.get('quiz_guest_alias')
        if guest_alias:
            mi_score = QuizParticipacion.objects.filter(
                cliente__isnull=True, guest_alias=guest_alias, fecha=today
            ).aggregate(total=Sum('puntaje'))['total'] or 0

    return render(request, 'calculadora/rankingquiz.html', {
        'page_obj': page_obj,
        'mi_alias': mi_alias,
        'mi_score': mi_score,
        'fecha'   : today,
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ClientePerfil


@login_required
def elegir_alias_view(request):
    perfil = getattr(request.user, 'clienteperfil', None)
    if not perfil:
        return redirect('daily_quiz')

    if perfil.alias:
        return redirect('daily_quiz')

    error_message = None

    if request.method == 'POST':
        alias = request.POST.get('alias', '').strip()
        if not alias:
            error_message = "El alias no puede estar vacÃ­o."
        elif ClientePerfil.objects.filter(alias__iexact=alias).exists():
            error_message = "Este alias ya estÃ¡ en uso. ElegÃ­ otro."
        else:
            perfil.alias = alias
            perfil.save(update_fields=['alias'])
            return redirect('daily_quiz')

    return render(request, 'calculadora/elegir_alias.html', {'error_message': error_message})


@login_required
def verificar_alias_redireccion_view(request):
    user_profile, created = ClientePerfil.objects.get_or_create(user=request.user)
    if user_profile.alias and user_profile.alias_confirmado:
        return redirect('daily_quiz')
    else:
        return redirect('elegir_alias')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ClientePerfil, DiagnosticoFinanciero
from .forms import ClientePerfilForm
from decimal import Decimal, InvalidOperation

from decimal import Decimal

def to_decimal(v):
    try:
        if v in (None, "", "null"):
            return Decimal("0")
        return Decimal(str(v))
    except:
        return Decimal("0")


def to_int(v, default=0):
    try:
        if v in (None, "", "null"):
            return default
        return int(v)
    except (TypeError, ValueError):
        return default


def get_ordered_values(post_data, prefix, fallback_name=None):
    ordered = []
    index = 1
    while True:
        key = f"{prefix}_{index}"
        if key not in post_data:
            break
        value = (post_data.get(key) or "").strip()
        if value:
            ordered.append(value)
        index += 1

    if ordered:
        return ordered

    if fallback_name:
        return [value for value in post_data.getlist(fallback_name) if value]

    return []


def merge_guest_diagnostic_profile(request, perfil):
    guest_profile_id = request.session.get("guest_diagnostico_perfil_id")
    if not guest_profile_id or not request.user.is_authenticated:
        return

    guest_profile = ClientePerfil.objects.filter(
        id=guest_profile_id,
        user__isnull=True,
    ).first()
    if not guest_profile:
        request.session.pop("guest_diagnostico_perfil_id", None)
        return

    DiagnosticoFinanciero.objects.filter(cliente=guest_profile).update(cliente=perfil)

    if not perfil.edad and guest_profile.edad:
        perfil.edad = guest_profile.edad
    if not perfil.hijos_a_cargo and guest_profile.hijos_a_cargo:
        perfil.hijos_a_cargo = guest_profile.hijos_a_cargo
    if not perfil.situacion_habitacional and guest_profile.situacion_habitacional:
        perfil.situacion_habitacional = guest_profile.situacion_habitacional
    if not perfil.objetivos and guest_profile.objetivos:
        perfil.objetivos = guest_profile.objetivos
    perfil.diagnosticos_realizados = DiagnosticoFinanciero.objects.filter(cliente=perfil).count()
    perfil.save(update_fields=[
        "edad",
        "hijos_a_cargo",
        "situacion_habitacional",
        "objetivos",
        "diagnosticos_realizados",
    ])

    guest_profile.delete()
    request.session.pop("guest_diagnostico_perfil_id", None)
    request.session.modified = True


def formulario_view(request):
    perfil = None
    if request.user.is_authenticated:
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
        merge_guest_diagnostic_profile(request, perfil)

    if request.method == "POST":
        if perfil is None:
            guest_profile_id = request.session.get("guest_diagnostico_perfil_id")
            perfil = ClientePerfil.objects.filter(id=guest_profile_id, user__isnull=True).first()
            if perfil is None:
                perfil = ClientePerfil.objects.create(alias="Invitado")
                request.session["guest_diagnostico_perfil_id"] = perfil.id

        objetivos_ordenados = get_ordered_values(request.POST, "objetivo", "objetivos")
        valores_ordenados = get_ordered_values(request.POST, "valor", "importancia_dinero")
        limitantes_crecimiento = request.POST.getlist("limitantes_crecimiento")
        causas_estancamiento = request.POST.getlist("causas_estancamiento")
        resolucion_deficit = request.POST.getlist("resolucion_deficit")
        resultados_emprendimientos = request.POST.getlist("resultados_emprendimientos")
        sesgos_sistema = request.POST.getlist("sesgos_sistema")

        # -------- PERFIL --------
        edad = to_int(request.POST.get("edad"))
        if edad and (edad < 15 or edad > 115):
            edad = None
        perfil.edad = edad or None
        perfil.hijos_a_cargo = to_int(request.POST.get("hijos_a_cargo"))
        perfil.situacion_habitacional = request.POST.get("situacion_habitacional") or None
        perfil.objetivos = objetivos_ordenados
        perfil.diagnosticos_realizados = (perfil.diagnosticos_realizados or 0) + 1
        perfil.save()

        # -------- DIAGNÃ“STICO --------
        horas = to_decimal(request.POST.get("horas_trabajadas"))
        if horas > 20:
            horas = Decimal("20")

        patrimonio_comp = {
            "inmuebles": float(to_decimal(request.POST.get("pat_inmuebles"))),
            "vehiculos": float(to_decimal(request.POST.get("pat_vehiculos"))),
            "empresa": float(to_decimal(request.POST.get("pat_empresa"))),
            "inversiones": float(to_decimal(request.POST.get("pat_inversiones"))),
            "cash": float(to_decimal(request.POST.get("pat_cash"))),
            "creditos_a_favor": float(to_decimal(request.POST.get("pat_creditos_a_favor"))),
        }

        deuda_comp = {
            "tarjetas": float(to_decimal(request.POST.get("deu_tarjetas"))),
            "prestamos": float(to_decimal(request.POST.get("deu_prestamos"))),
            "hipoteca": float(to_decimal(request.POST.get("deu_hipoteca"))),
            "prenda": float(to_decimal(request.POST.get("deu_prenda"))),
            "terceros": float(to_decimal(request.POST.get("deu_terceros"))),
            "impuestos": float(to_decimal(request.POST.get("deu_impuestos"))),
        }

        patrimonio_total = sum(Decimal(str(value)) for value in patrimonio_comp.values())
        deuda_total = sum(Decimal(str(value)) for value in deuda_comp.values())

        respuestas_raw = {
            "estado_financiero": request.POST.get("estado_financiero"),
            "objetivos": request.POST.getlist("objetivos"),
            "objetivos_ordenados": objetivos_ordenados,
            "importancia_dinero": request.POST.getlist("importancia_dinero"),
            "valores_ordenados": valores_ordenados,
            "limitantes_crecimiento": limitantes_crecimiento,
            "causas_estancamiento": causas_estancamiento,
            "resolucion_deficit": resolucion_deficit,
            "resultados_emprendimientos": resultados_emprendimientos,
            "sesgos_sistema": sesgos_sistema,
            "estabilidad_laboral": request.POST.get("estabilidad_laboral"),
            "percepcion_estabilidad": request.POST.get("percepcion_estabilidad"),
            "conocimiento_financiero": request.POST.get("conocimiento_financiero"),
            "confianza_sistema": request.POST.get("confianza_sistema"),
        }
        payload_codificado = base64.urlsafe_b64encode(
            json.dumps(respuestas_raw, ensure_ascii=False).encode("utf-8")
        ).decode("utf-8")

        diagnostico = DiagnosticoFinanciero.objects.create(
            cliente=perfil,
            horas_trabajadas=horas,

            ingreso_trabajo=to_decimal(request.POST.get("ingreso_trabajo")),
            ingreso_negocio=to_decimal(request.POST.get("ingreso_negocio")),
            ingreso_rentas=to_decimal(request.POST.get("ingreso_rentas")),
            ingreso_inversiones=to_decimal(request.POST.get("ingreso_inversiones")),
            ingreso_otros=to_decimal(request.POST.get("ingreso_otros")),

            gasto_necesarios=to_decimal(request.POST.get("gasto_necesarios")),
            gasto_innecesarios=to_decimal(request.POST.get("gasto_innecesarios")),
            gasto_financieros=to_decimal(request.POST.get("gasto_financieros")),
            gasto_inversiones=to_decimal(request.POST.get("gasto_inversiones")),

            
            reaccion_perdida=request.POST.get("reaccion_perdida"),
        )

        # -------- COMPOSICIÃ“N (JSON) --------
        diagnostico.patrimonio_comp = {
            "inmuebles": float(to_decimal(request.POST.get("pat_inmuebles"))),
            "vehiculos": float(to_decimal(request.POST.get("pat_vehiculos"))),
            "empresa": float(to_decimal(request.POST.get("pat_empresa"))),
            "inversiones": float(to_decimal(request.POST.get("pat_inversiones"))),
            "cash": float(to_decimal(request.POST.get("pat_cash"))),
            "creditos_a_favor": float(to_decimal(request.POST.get("pat_creditos_a_favor"))),
        }

        diagnostico.deuda_comp = {
            "tarjetas": float(to_decimal(request.POST.get("deu_tarjetas"))),
            "prestamos": float(to_decimal(request.POST.get("deu_prestamos"))),
            "hipoteca": float(to_decimal(request.POST.get("deu_hipoteca"))),
            "prenda": float(to_decimal(request.POST.get("deu_prenda"))),
            "terceros": float(to_decimal(request.POST.get("deu_terceros"))),
            "impuestos": float(to_decimal(request.POST.get("deu_impuestos"))),
        }

        diagnostico.ingreso_emprendimiento = to_decimal(request.POST.get("ingreso_emprendimiento"))
        diagnostico.patrimonio_total = patrimonio_total
        diagnostico.deuda_total = deuda_total
        diagnostico.estado_financiero = request.POST.get("estado_financiero") or None
        diagnostico.estabilidad_laboral = request.POST.get("estabilidad_laboral") or None
        diagnostico.percepcion_estabilidad = to_int(request.POST.get("percepcion_estabilidad"))
        diagnostico.conocimiento_financiero = to_int(request.POST.get("conocimiento_financiero"))
        diagnostico.confianza_sistema = to_int(request.POST.get("confianza_sistema"))
        diagnostico.objetivos_ordenados = objetivos_ordenados
        diagnostico.importancia_dinero = valores_ordenados
        diagnostico.resultados_emprendimientos = resultados_emprendimientos
        diagnostico.limitantes_crecimiento = limitantes_crecimiento
        diagnostico.causas_estancamiento = causas_estancamiento
        diagnostico.resolucion_deficit = resolucion_deficit
        diagnostico.sesgos_sistema = sesgos_sistema
        diagnostico.respuestas_raw = respuestas_raw
        diagnostico.payload_codificado = payload_codificado
        diagnostico.save(update_fields=[
            "ingreso_emprendimiento",
            "patrimonio_comp",
            "deuda_comp",
            "patrimonio_total",
            "deuda_total",
            "estado_financiero",
            "estabilidad_laboral",
            "percepcion_estabilidad",
            "conocimiento_financiero",
            "confianza_sistema",
            "objetivos_ordenados",
            "importancia_dinero",
            "resultados_emprendimientos",
            "limitantes_crecimiento",
            "causas_estancamiento",
            "resolucion_deficit",
            "sesgos_sistema",
            "respuestas_raw",
            "payload_codificado",
        ])

        request.session["ultimo_diagnostico_id"] = diagnostico.id
        return redirect("resultado")

    return render(request, "formulario.html", {})


import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from calculadora.models import ClientePerfil, DiagnosticoFinanciero, ResultadoIA
from calculadora.services.resultado import construir_resultado, METAS_MAP
from calculadora.services.motor_calculos import calcular_motor_financiero
from calculadora.services.proyecciones import calcular_proyecciones


def construir_portfolio_sugerido(snapshot, diagnostico):
    conocimiento = int(snapshot.get("conocimiento_financiero") or 0)
    confianza = int(snapshot.get("confianza_sistema") or 0)
    estado = snapshot.get("estado_general") or "constructor"
    meses_supervivencia = float(snapshot.get("meses_supervivencia") or 0)
    reaccion = getattr(diagnostico, "reaccion_perdida", "") or ""

    score = 0
    if estado in ("fragil", "presionado"):
        score -= 2
    elif estado == "constructor":
        score += 0
    elif estado == "acumulador":
        score += 1
    elif estado == "despegando":
        score += 2

    if conocimiento <= 2:
        score -= 1
    elif conocimiento >= 4:
        score += 1

    if confianza <= 2:
        score -= 1
    elif confianza >= 4:
        score += 1

    if reaccion in ("locura", "vender", "nose"):
        score -= 2
    elif reaccion in ("estrategia", "oportunidades"):
        score += 1

    if meses_supervivencia < 3:
        score -= 1

    if score <= -3:
        perfil = "Defensivo"
        tesis = "Prioriza liquidez, baja volatilidad y aprendizaje antes de aumentar riesgo."
        alloc = [
            ("SGOV", "Treasuries 0-3 meses", 45, "liquidez defensiva"),
            ("AGG", "Bonos investment grade EE.UU.", 30, "estabilidad de renta fija"),
            ("ACWI", "Acciones globales", 15, "crecimiento diversificado"),
            ("GLD", "Oro fÃ­sico vÃ­a ETF", 10, "cobertura ante estrÃ©s"),
        ]
    elif score <= 1:
        perfil = "Balanceado"
        tesis = "Combina estabilidad con exposiciÃ³n global gradual, sin concentrar la cartera en una sola apuesta."
        alloc = [
            ("SGOV", "Treasuries 0-3 meses", 20, "reserva tÃ¡ctica"),
            ("AGG", "Bonos investment grade EE.UU.", 25, "base defensiva"),
            ("ACWI", "Acciones globales", 35, "nÃºcleo diversificado"),
            ("IVV", "S&P 500", 10, "calidad large cap EE.UU."),
            ("GLD", "Oro fÃ­sico vÃ­a ETF", 10, "diversificador"),
        ]
    elif score <= 3:
        perfil = "Crecimiento"
        tesis = "Acepta mÃ¡s fluctuaciÃ³n para buscar crecimiento, manteniendo una reserva y diversificaciÃ³n global."
        alloc = [
            ("SGOV", "Treasuries 0-3 meses", 10, "liquidez"),
            ("AGG", "Bonos investment grade EE.UU.", 15, "amortiguador"),
            ("ACWI", "Acciones globales", 40, "nÃºcleo global"),
            ("IVV", "S&P 500", 20, "motor EE.UU."),
            ("EEM", "Mercados emergentes", 10, "crecimiento satÃ©lite"),
            ("GLD", "Oro fÃ­sico vÃ­a ETF", 5, "cobertura"),
        ]
    else:
        perfil = "Agresivo diversificado"
        tesis = "Tiene tolerancia para renta variable, pero conserva caja mÃ­nima y activos no correlacionados."
        alloc = [
            ("SGOV", "Treasuries 0-3 meses", 5, "liquidez mÃ­nima"),
            ("AGG", "Bonos investment grade EE.UU.", 10, "control de volatilidad"),
            ("ACWI", "Acciones globales", 35, "nÃºcleo global"),
            ("IVV", "S&P 500", 30, "crecimiento EE.UU."),
            ("EEM", "Mercados emergentes", 15, "riesgo satÃ©lite"),
            ("GLD", "Oro fÃ­sico vÃ­a ETF", 5, "cobertura"),
        ]

    instrumentos = []
    for ticker, nombre, porcentaje, rol in alloc:
        instrumentos.append({
            "ticker": ticker,
            "nombre": nombre,
            "porcentaje": porcentaje,
            "rol": rol,
        })

    alertas = []
    if meses_supervivencia < 3:
        alertas.append("Antes de ejecutar una cartera de riesgo, construir 3 a 6 meses de gastos en instrumentos lÃ­quidos.")
    if conocimiento <= 2:
        alertas.append("Empezar con pocos instrumentos y rebalanceo simple; evitar derivados, apalancamiento y trading frecuente.")
    if confianza <= 2:
        alertas.append("Usar instrumentos transparentes, lÃ­quidos y con bajo costo para reducir fricciÃ³n psicolÃ³gica.")

    return {
        "perfil": perfil,
        "tesis": tesis,
        "instrumentos": instrumentos,
        "alertas": alertas,
        "rebalanceo": "Revisar cada 90 dÃ­as o cuando una clase se desvÃ­e mÃ¡s de 5 puntos porcentuales.",
    }
 
def resultado_view(request):
    """
    Genera y muestra el resultado financiero personalizado.
    Incluye: RadiografÃ­a, MÃ©tricas, Metas con feedback, Proyecciones, Plan de Guerra.
    """
    # ========================
    # 1. OBTENER DATOS DEL USUARIO
    # ========================
    diagnostico = None
    perfil = None
    ultimo_diagnostico_id = request.session.get("ultimo_diagnostico_id")

    if request.user.is_authenticated:
        perfil = ClientePerfil.objects.filter(user=request.user).first()
        if perfil:
            merge_guest_diagnostic_profile(request, perfil)
        if perfil and ultimo_diagnostico_id:
            diagnostico = DiagnosticoFinanciero.objects.filter(
                id=ultimo_diagnostico_id,
                cliente=perfil,
            ).first()
        if perfil and diagnostico is None:
            diagnostico = DiagnosticoFinanciero.objects.filter(cliente=perfil).last()
    elif ultimo_diagnostico_id:
        guest_profile_id = request.session.get("guest_diagnostico_perfil_id")
        diagnostico = DiagnosticoFinanciero.objects.filter(
            id=ultimo_diagnostico_id,
            cliente_id=guest_profile_id,
            cliente__user__isnull=True,
        ).select_related("cliente").first()
        perfil = diagnostico.cliente if diagnostico else None

    if not diagnostico:
        return redirect("formulario_view")
    
    # ========================
    # 2. CALCULAR SNAPSHOT Y RESULTADO IA
    # ========================
    snapshot = calcular_motor_financiero(diagnostico)
    resultado_ia = construir_resultado(perfil, diagnostico, permitir_ver=True)
    portfolio_sugerido = construir_portfolio_sugerido(snapshot, diagnostico)
    
    # ========================
    # 3. PARSEAR METAS CON FEEDBACK
    # ========================
    metas_info = None
    try:
        if resultado_ia.bloque_sesgo:
            metas_info = json.loads(resultado_ia.bloque_sesgo)
            # Sobreescribir imagen con el valor actual del METAS_MAP (ignora paths viejos en BD)
            meta_key = metas_info.get('meta_key')
            if not meta_key:
                # fallback para registros viejos: buscar por label
                label = metas_info.get('label', '')
                meta_key = next((k for k, v in METAS_MAP.items() if v['label'] == label), None)
            if meta_key and meta_key in METAS_MAP:
                metas_info['imagen'] = METAS_MAP[meta_key]['imagen']
    except (json.JSONDecodeError, TypeError):
        metas_info = None
    
    # ========================
    # 4. PARSEAR ACCIONES (Plan de Guerra)
    # ========================
    acciones = {"corto_plazo": [], "mediano_plazo": [], "largo_plazo": []}
    try:
        if resultado_ia.bloque_accion:
            acciones = json.loads(resultado_ia.bloque_accion)
    except (json.JSONDecodeError, TypeError):
        acciones = {"corto_plazo": [], "mediano_plazo": [], "largo_plazo": []}

    estructura = {}
    try:
        if resultado_ia.bloque_estructura:
            estructura = json.loads(resultado_ia.bloque_estructura)
    except (json.JSONDecodeError, TypeError):
        estructura = {}

    if not estructura:
        estructura = {
            "estado_general": snapshot.get("estado_general"),
            "perfil_financiero": snapshot.get("perfil_financiero"),
            "palanca_principal": snapshot.get("palanca_principal"),
            "riesgo_principal": snapshot.get("riesgo_principal"),
            "nivel_prejuicio": snapshot.get("nivel_prejuicio"),
            "conocimiento_financiero": snapshot.get("conocimiento_financiero"),
            "confianza_sistema": snapshot.get("confianza_sistema"),
        }

    if metas_info:
        metas_info.setdefault("perfil_financiero", estructura.get("perfil_financiero"))
        metas_info.setdefault("palanca_principal", estructura.get("palanca_principal"))
        metas_info.setdefault("riesgo_principal", estructura.get("riesgo_principal"))
        metas_info.setdefault("bloqueos_detectados", snapshot.get("bloqueos_detectados", []))

    estado_label_map = {
        "fragil": "Fragil",
        "presionado": "Presionado",
        "constructor": "Constructor",
        "acumulador": "Acumulador",
        "despegando": "Despegando",
    }
    estado_desc_map = {
        "fragil": "Hoy el sistema esta defendiendo caja y necesita recuperar aire antes de escalar.",
        "presionado": "Existe movimiento, pero cualquier desorden o imprevisto todavia te aprieta.",
        "constructor": "Ya hay margen y disciplina para empezar a convertir esfuerzo en sistema.",
        "acumulador": "Tu estructura ya acumula y ahora necesita mas criterio y diversificacion.",
        "despegando": "Hay potencial visible, pero aun falta orden para que el crecimiento sea consistente.",
    }
    palanca_desc_map = {
        "recuperar flujo de caja y bajar fragilidad": "Es la accion que mas rapido puede devolverte control operativo.",
        "crear margen y caja defensiva": "Primero necesitas espacio financiero para que tus decisiones no salgan desde la urgencia.",
        "convertir disciplina en sistema": "Ya no alcanza con voluntad: toca automatizar, medir y sostener.",
        "ordenar patrimonio y diversificar": "El siguiente salto no es trabajar mas, sino distribuir mejor el capital.",
        "escalar con foco y estructura": "Tu reto no es arrancar, sino crecer sin perder control ni liquidez.",
    }
    riesgo_desc_map = {
        "quedarte sin margen operativo": "Si no corriges esto primero, cualquier otra decision queda construida sobre fragilidad.",
        "invertir por encima de la caja que hoy puedes sostener": "Invertir esta bien, pero si ahoga tu liquidez te deja sin defensa.",
        "que la deuda cara te siga frenando": "La deuda toxica puede anular gran parte del esfuerzo que haces para avanzar.",
        "tener patrimonio pero sin caja real": "Puedes verte solvente en papeles y aun asi quedar vulnerable ante un imprevisto.",
        "quedarte inmovilizado por desconfianza": "No es falta de potencial, sino ruido mental frenando la ejecucion.",
        "crecer sin sistema claro": "Crecer sin reglas te expone a improvisar justo cuando mas dinero pasa por tus manos.",
    }

    estado_actual = snapshot.get("estado_general")
    palanca_actual = estructura.get("palanca_principal") or snapshot.get("palanca_principal")
    riesgo_actual = estructura.get("riesgo_principal") or snapshot.get("riesgo_principal")
    diagnostico_claves = [
        {
            "titulo": "Tu posicion actual",
            "valor": estado_label_map.get(estado_actual, "Sin definir"),
            "detalle": estado_desc_map.get(estado_actual, "Resume la etapa financiera en la que estas hoy."),
            "nota": f"Perfil interno detectado: {estructura.get('perfil_financiero') or snapshot.get('perfil_financiero') or 'sin definir'}",
        },
        {
            "titulo": "Tu palanca principal",
            "valor": (palanca_actual or "Sin definir").capitalize(),
            "detalle": palanca_desc_map.get(palanca_actual, "Es el movimiento con mayor retorno estrategico en tu caso actual."),
            "nota": "Si haces bien esto, el resto del plan empieza a rendir mucho mas.",
        },
        {
            "titulo": "Tu riesgo prioritario",
            "valor": (riesgo_actual or "Sin definir").capitalize(),
            "detalle": riesgo_desc_map.get(riesgo_actual, "Es el punto que mas conviene resolver antes de escalar."),
            "nota": "Atacarlo primero reduce errores caros y mejora tus decisiones siguientes.",
        },
    ]
    
    # ========================
    # 5. CALCULAR MÃ‰TRICAS
    # ========================
    margen_libertad = float(snapshot.get('ratio_libertad', 0)) * 100
    patrimonio_total = float(snapshot.get('patrimonio', 0))
    deuda_total = float(snapshot.get('deuda', 0))
    patrimonio_neto = patrimonio_total - deuda_total
    ingreso_por_hora = float(snapshot.get('ingreso_por_hora', 0))
    
    # ========================
    # 6. PARSEAR PROYECCIONES
    # ========================
    proy_pos = list(resultado_ia.proy_pos) if resultado_ia.proy_pos else []
    proy_med = list(resultado_ia.proy_med) if resultado_ia.proy_med else []
    proy_neg = list(resultado_ia.proy_neg) if resultado_ia.proy_neg else []
    if not proy_pos or not proy_med or not proy_neg:
        proyecciones = calcular_proyecciones(perfil, snapshot)
        proy_pos = list(proyecciones.get("positiva", []))
        proy_med = list(proyecciones.get("media", []))
        proy_neg = list(proyecciones.get("negativa", []))

    proy_pos_json = json.dumps(proy_pos)
    proy_med_json = json.dumps(proy_med)
    proy_neg_json = json.dumps(proy_neg)
    
    # ========================
    # 7. CONTEXTO PARA TEMPLATE
    # ========================
    contexto = {
        # Resultado IA
        "resultado": resultado_ia,
        
        # MÃ©tricas principales
        "margen_libertad": round(margen_libertad, 1),
        "patrimonio_total": patrimonio_total,
        "patrimonio_neto": patrimonio_neto,
        "ingreso_por_hora": ingreso_por_hora,
        
        # Metas con feedback personalizado
        "metas_info": metas_info,
        "diagnostico_claves": diagnostico_claves,
        "estructura": estructura,
        "snapshot": snapshot,
        "codigo_anonimo": diagnostico.codigo_anonimo,
        "portfolio_sugerido": portfolio_sugerido,
        
        # Proyecciones (JSON safe)
        "proy_pos_json": proy_pos_json,
        "proy_med_json": proy_med_json,
        "proy_neg_json": proy_neg_json,
        
        # Plan de Guerra
        "acciones": acciones,
    }
    
    return render(request, "calculadora/resultadotest.html", contexto)


def sugerencia_view(request):
    diagnostico = None
    perfil = None
    ultimo_diagnostico_id = request.session.get("ultimo_diagnostico_id")

    if request.user.is_authenticated:
        perfil = ClientePerfil.objects.filter(user=request.user).first()
        if perfil:
            merge_guest_diagnostic_profile(request, perfil)
        if perfil and ultimo_diagnostico_id:
            diagnostico = DiagnosticoFinanciero.objects.filter(
                id=ultimo_diagnostico_id,
                cliente=perfil,
            ).first()
        if perfil and diagnostico is None:
            diagnostico = DiagnosticoFinanciero.objects.filter(cliente=perfil).last()
    elif ultimo_diagnostico_id:
        guest_profile_id = request.session.get("guest_diagnostico_perfil_id")
        diagnostico = DiagnosticoFinanciero.objects.filter(
            id=ultimo_diagnostico_id,
            cliente_id=guest_profile_id,
            cliente__user__isnull=True,
        ).select_related("cliente").first()
        perfil = diagnostico.cliente if diagnostico else None

    if not diagnostico:
        return redirect("formulario_view")

    snapshot = calcular_motor_financiero(diagnostico)
    portfolio_sugerido = construir_portfolio_sugerido(snapshot, diagnostico)
    ingresos = float(snapshot.get("ingresos") or 0)
    gastos = float(snapshot.get("gastos") or 0)
    ahorro = float(snapshot.get("ahorro") or 0)
    inversion_mercado = max(ahorro * 0.8, 0)
    meses_supervivencia = float(snapshot.get("meses_supervivencia") or 0)

    profile_display_name = "Invitado"
    if perfil and perfil.user:
        profile_display_name = perfil.alias or perfil.user.first_name or perfil.user.username
    elif perfil and perfil.alias:
        profile_display_name = perfil.alias

    return render(request, "calculadora/sugerencia.html", {
        "perfil": perfil,
        "diagnostico": diagnostico,
        "snapshot": snapshot,
        "portfolio_sugerido": portfolio_sugerido,
        "ingresos": ingresos,
        "gastos": gastos,
        "ahorro": ahorro,
        "inversion_mercado": inversion_mercado,
        "meses_supervivencia": meses_supervivencia,
        "profile_display_name": profile_display_name,
    })
 
@login_required
def redirect_post_login(request):
    """ Decide quÃ© hacer despuÃ©s del login, segÃºn el flujo del usuario. """
    from django.utils.http import url_has_allowed_host_and_scheme

    next_url = request.GET.get("next") or request.POST.get("next") or request.session.pop("next_url", None)

    # ðŸ”¥ Si venÃ­a con una acciÃ³n concreta â†’ volver ahÃ­
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)

    # ðŸ”¥ Si usuario tiene perfil+plan â†’ enviar a perfil
    perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
    merge_guest_diagnostic_profile(request, perfil)
    _merge_guest_companies_into_user(request)

    if perfil and perfil.plan_activo:
        return redirect("perfil_usuario")

    # ðŸ”¥ Si no tiene plan â†’ llevarlo a planes
    return redirect("planes")



from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlencode
import logging
import os
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import oauth2_login

logger = logging.getLogger(__name__)


def login_google_direct(request):
    """
    RedirecciÃ³n estable al login de Google de allauth.
    Evita depender del nombre interno de URL del provider y preserva `next`.
    """
    if settings.DEBUG:
        return dev_login(request)

    next_url = request.GET.get("next")
    login_path = "/accounts/google/login/"
    if next_url:
        return redirect(f"{login_path}?{urlencode({'next': next_url})}")
    return redirect(login_path)


def _get_google_creds():
    client_id = (
        os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
        or os.getenv("GOOGLE_CLIENT_ID")
        or os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        or ""
    )
    secret = (
        os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
        or os.getenv("GOOGLE_CLIENT_SECRET")
        or os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
        or ""
    )
    return client_id.strip(), secret.strip()


def _ensure_google_socialapp():
    """
    Asegura que allauth tenga un SocialApp Google asociado al SITE_ID actual.
    Evita 500 por SocialApp faltante o site no enlazado.
    """
    client_id, secret = _get_google_creds()
    if not client_id or not secret:
        return False

    site, _ = Site.objects.get_or_create(
        id=settings.SITE_ID,
        defaults={"domain": "www.invertiresfacil.com", "name": "invertiresfacil.com"},
    )

    apps = list(SocialApp.objects.filter(provider="google").order_by("id"))

    # Preferimos una app ya asociada al SITE_ID y con client_id correcto.
    app = None
    for candidate in apps:
        if candidate.sites.filter(id=site.id).exists() and candidate.client_id == client_id:
            app = candidate
            break

    if app is None:
        for candidate in apps:
            if candidate.sites.filter(id=site.id).exists():
                app = candidate
                break

    if app is None and apps:
        app = apps[0]

    if app is None:
        app = SocialApp(provider="google", name="Google")

    changed = False
    if app.client_id != client_id:
        app.client_id = client_id
        changed = True
    if app.secret != secret:
        app.secret = secret
        changed = True
    if app.key != "":
        app.key = ""
        changed = True
    if not app.pk or changed:
        app.save()

    if not app.sites.filter(id=site.id).exists():
        app.sites.add(site)

    # Evita MultipleObjectsReturned en allauth:
    # solo una SocialApp de Google debe quedar asociada al SITE_ID actual.
    duplicated_ids = []
    for other in SocialApp.objects.filter(provider="google").exclude(id=app.id):
        if other.sites.filter(id=site.id).exists():
            other.sites.remove(site)
            duplicated_ids.append(other.id)
    if duplicated_ids:
        logger.warning(
            "Se desasociaron SocialApp duplicadas de Google del site %s: %s",
            site.id,
            duplicated_ids,
        )

    return True


def google_login_entry(request):
    if settings.DEBUG:
        return dev_login(request)
    """
    Entry-point robusto para Google OAuth en producciÃ³n.
    """
    try:
        configured = _ensure_google_socialapp()
        if not configured:
            logger.error("Google OAuth no configurado: faltan credenciales en variables de entorno.")
            return JsonResponse(
                {"error": "Google login no configurado en el servidor"},
                status=503,
            )
        return oauth2_login(request)
    except Exception:
        logger.exception("Fallo en /accounts/google/login/")
        raise




# views.py
from django.http import JsonResponse
import mercadopago
from django.conf import settings

def crear_preferencia(request):
    print("ðŸš€ Entrando a crear_preferencia")

    access_token = settings.MERCADOPAGO_ACCESS_TOKEN
    print("ðŸ” ACCESS TOKEN:", access_token)

    if not access_token:
        return JsonResponse({"error": "Access token no configurado"}, status=500)

    sdk = mercadopago.SDK(access_token)

    preference_data = {
        "items": [{
            "title": "Feedback Financiero Personalizado",
            "quantity": 1,
            "unit_price": 100.0
        }],
        "back_urls": {
            "success": "https://www.invertiresfacil.com/ranking/",
            "failure": "https://www.invertiresfacil.com/ranking/",
            "pending": "https://www.invertiresfacil.com/ranking/"
        },
        "auto_return": "approved"
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        print("âœ… Preferencia creada:", preference_response)
        return JsonResponse({ "preference_id": preference_response["response"]["id"] })
    except Exception as e:
        print("âŒ Error al crear preferencia:", e)
        return JsonResponse({ "error": str(e) }, status=500)

from decimal import Decimal

import os
import mercadopago

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from calculadora.models import (
    Plan,
    PromoCode,
    RegaloPendiente,
    MercadoPagoPayment,
    Subscripcion,
    ClientePerfil,
)
from calculadora.services.planes import activate_plan
from openai import OpenAI


User = get_user_model()

ORACULO_DEMO_SESSION_KEY = "oraculo_demo_usos"
ORACULO_DEMO_LIMIT = 6


def _build_oraculo_demo_prompt():
    return (
        "Sos el Oraculo Demo de InvertirEsFacil. Tu mision es ayudar a una persona "
        "que esta entrando al sitio a entender finanzas, mercado argentino o decidir si el servicio le sirve.\n"
        "No tenes datos personales, diagnostico ni historial del usuario. No finjas tenerlos.\n"
        "Tono: ingenioso, inteligente, argentino, claro y comercial sin sonar vendedor barato.\n"
        "Responde con criterio, honestidad y precision. Si el servicio no parece encajar, decilo.\n"
        "Maximo 95 palabras. Parrafos cortos. Evita listas largas.\n"
        "Podes explicar en criollo dolar oficial, blue, MEP, CCL, inflacion, tasas, bonos, ADRs, "
        "riesgo argentino y como leer noticias economicas sin dar recomendaciones concretas.\n"
        "Podes explicar: Plan Esencial ($25 mil), Plan Premium ($100 mil), diagnostico IA, "
        "PDF financiero, cuenta comitente, simulador, Oraculo, reuniones 1 a 1, seguimiento "
        "mensual y referidos 50%.\n"
        "Objetivo: ayudar a decidir. No des asesoramiento financiero personalizado ni "
        "recomendaciones de inversion concretas. Para eso, invita a usar el diagnostico "
        "y el Oraculo completo dentro del plan.\n"
        "Cuando corresponda, orienta asi: Esencial si quiere guia y herramientas para empezar; "
        "Premium si quiere seguimiento, reuniones y una estrategia revisada con mas cercania.\n"
        "No prometas rentabilidad, resultados garantizados ni magia financiera."
    )


def oraculo_demo_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usados = request.session.get(ORACULO_DEMO_SESSION_KEY, 0)
    if usados >= ORACULO_DEMO_LIMIT:
        return JsonResponse({
            "reply": (
                "Ya usaste las 6 consultas gratis de esta muestra. Buena senal: si llegaste "
                "hasta aca, habia dudas reales. Para seguir con respuestas mas utiles, elegi "
                "un plan y usa el Oraculo completo con tu diagnostico."
            ),
            "limit_reached": True,
            "remaining": 0,
        })

    try:
        if request.content_type and "application/json" in request.content_type:
            data = json.loads(request.body or "{}")
            mensaje_usuario = data.get("message", "")
        else:
            mensaje_usuario = request.POST.get("message", "")

        mensaje_usuario = (mensaje_usuario or "").strip()
        if not mensaje_usuario:
            return JsonResponse({"reply": "Preguntame algo concreto y te ayudo a decidir sin humo."}, status=400)

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": _build_oraculo_demo_prompt()},
                {"role": "user", "content": mensaje_usuario},
            ],
            max_tokens=170,
            temperature=0.72,
        )

        request.session[ORACULO_DEMO_SESSION_KEY] = usados + 1
        request.session.modified = True

        return JsonResponse({
            "reply": response.choices[0].message.content,
            "limit_reached": False,
            "remaining": max(ORACULO_DEMO_LIMIT - usados - 1, 0),
        })

    except Exception as e:
        print(f"[Oraculo Demo] Error: {e}")
        return JsonResponse({
            "reply": "Se trabo la muestra del Oraculo. Probalo de nuevo en un momento.",
        }, status=500)


@login_required(login_url="/accounts/google/login/")
def iniciar_compra(request, plan_id):
    if not request.user.is_authenticated:
        return require_login_action(request, f"/iniciar-compra/{plan_id}/")
    plan = get_object_or_404(Plan, id=plan_id)
    aplicar_referido(request, request.user)

    try:
        precio = Decimal(plan.precio)
    except Exception:
        return HttpResponse("Precio invÃ¡lido", status=400)

    if precio <= 0:
        return HttpResponse("Precio del plan debe ser mayor a 0", status=400)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": plan.nombre,
            "quantity": 1,
            "unit_price": float(precio),
            "currency_id": "ARS",
        }],
        "external_reference": f"self:{request.user.id}:{plan.id}",
        "back_urls": {
            "success": "https://www.invertiresfacil.com/pago-exitoso/",
            "failure": "https://www.invertiresfacil.com/pago-cancelado/",
        },

        "auto_return": "approved",
        "notification_url": "https://www.invertiresfacil.com/mercadopago/webhook/",
    }

    preference = sdk.preference().create(preference_data)

    if preference.get("status") != 201:
        return HttpResponse(f"MercadoPago error: {preference}", status=500)

    return redirect(preference["response"]["init_point"])


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from decimal import Decimal
from django.contrib import messages
from calculadora.models import PromoCode, Subscripcion, ClientePerfil
from calculadora.utils import aplicar_referido, pagar_comision


@login_required(login_url="/accounts/google/login/")

def redeem_code(request):
    if request.method == "GET":
        request.session["open_redeem"] = True
        return redirect("planes")

    code_input = request.POST.get("code", "").strip().upper()

    try:
        promo = PromoCode.objects.select_related("plan").get(code=code_input)
    except PromoCode.DoesNotExist:
        messages.error(request, "Codigo invalido.")
        return redirect("planes")

    if not promo.can_use():
        messages.error(request, "Codigo ya utilizado o vencido.")
        return redirect("planes")

    promo.used_count += 1
    promo.save(update_fields=["used_count"])

    aplicar_referido(request, request.user)
    activate_plan(
        user=request.user,
        plan=promo.plan,
        source="promo",
        reference=promo.code,
    )

    messages.success(request, f"Codigo validado. Activaste {promo.plan.nombre}.")
    return redirect("perfil_usuario")
def _extract_payment_id(request):
    try:
        data = json.loads(request.body)
        return data.get("data", {}).get("id")
    except Exception:
        return None


@csrf_exempt
def mercadopago_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    payment_id = _extract_payment_id(request) or request.GET.get("id") or request.GET.get("data.id")

    if not payment_id:
        return JsonResponse({"ok": True}, status=200)

    if MercadoPagoPayment.objects.filter(payment_id=payment_id).exists():
        return JsonResponse({"ok": True, "duplicate": True}, status=200)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    mp_payment = sdk.payment().get(payment_id)

    if mp_payment.get("status") != 200:
        MercadoPagoPayment.objects.create(
            payment_id=payment_id,
            status="fetch_error",
            raw=mp_payment,
        )
        return JsonResponse({"ok": True}, status=200)

    response = mp_payment["response"]
    status = response.get("status")
    external_reference = response.get("external_reference") or ""
    user = None
    plan = None
    kind = None
    ref_a = None
    ref_b = None

    try:
        kind, ref_a, ref_b = external_reference.split(":")
        if kind == "self":
            user = User.objects.get(id=int(ref_a))
            plan = Plan.objects.get(id=int(ref_b))
    except Exception:
        pass

    record = MercadoPagoPayment.objects.create(
        payment_id=payment_id,
        status=status,
        external_reference=external_reference,
        raw=response,
        user=user,
        plan_id=plan.id if plan else None,
    )

    if status != "approved":
        return JsonResponse({"ok": True, "status": status}, status=200)

    try:
        if kind == "self":
            if not user or not plan:
                raise ValueError("Referencia de pago invalida")

            activate_plan(
                user=user,
                plan=plan,
                source="mercadopago",
                reference=payment_id,
            )

        elif kind == "gift":
            regalo = RegaloPendiente.objects.get(id=int(ref_a))

            activate_plan(
                user=regalo.destinatario,
                plan=regalo.plan,
                source="gift",
                reference=payment_id,
                regalo=regalo,
            )

        return JsonResponse({"ok": True, "activated": True}, status=200)

    except Exception as e:
        record.status = "activation_error"
        record.raw = {"error": str(e)}
        record.save(update_fields=["status", "raw"])
        return JsonResponse({"ok": True}, status=200)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from calculadora.models import ClientePerfil, DiagnosticoFinanciero
from calculadora.services.world_dashboard import build_world_dashboard_context, get_or_create_ceo_brief


def perfil_usuario(request):
    perfil = None
    cliente = None
    profile_display_name = "Invitado"
    profile_email = ""
    
    if request.user.is_authenticated:
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
        profile_display_name = perfil.alias or request.user.first_name or request.user.username
        profile_email = request.user.email
    
        # Si el usuario mandÃ³ el formulario para cambiar el alias:
        if request.method == "POST":
            nuevo_alias = request.POST.get("nuevo_alias")
            if nuevo_alias:
                perfil.alias = nuevo_alias.strip()
                perfil.save(update_fields=["alias"])
                return redirect("perfil_usuario")

        cliente = DiagnosticoFinanciero.objects.filter(cliente=perfil).last()
    elif request.method == "POST":
        return redirect(f"/accounts/google/login/?next={request.path}")

    return render(request, "perfil_usuario.html", {
        "perfil": perfil,
        "cliente": cliente,
        "is_guest": not request.user.is_authenticated,
        "login_profile_url": f"/login/?next={request.path}",
        "profile_display_name": profile_display_name,
        "profile_email": profile_email,
    })


@login_required(login_url="/accounts/google/login/")
def world_dashboard(request):
    perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
    context = build_world_dashboard_context()
    is_intelligence_pro = perfil.plan_activo == 4
    if is_intelligence_pro:
        ceo_brief = get_or_create_ceo_brief(
            context["stress_index"],
            context["world_metrics"],
            context["conflict_zones"],
            context["global_assets"],
        )
    else:
        ceo_brief = {
            "content": "- Stress global y alertas ejecutivas.\n- Comparador VIP de paises.\n- Reglas visuales personalizadas.\n- Brief diario generado por IA.\n- Mesa global para decisiones.",
            "model": "preview",
            "date": context["stress_index"].get("snapshot_date"),
        }
    context.update({
        "perfil": perfil,
        "profile_display_name": perfil.alias or request.user.first_name or request.user.username,
        "is_intelligence_pro": is_intelligence_pro,
        "intelligence_pro_plan_id": 4,
        "ceo_brief": ceo_brief,
        "world_alerts": list(request.user.world_alerts.filter(activa=True)[:4]) if is_intelligence_pro else [],
    })
    return render(request, "world_dashboard.html", context)


def _build_world_dashboard_prompt():
    return (
        "Sos el Oraculo del World Intelligence Dashboard de InvertirEsFacil. "
        "Ayudas a publico general interesado en finanzas y tecnologia a leer paises, "
        "continentes, indicadores demograficos, desigualdad, inflacion, clima, activos "
        "globales y datos espaciales. No des recomendaciones de inversion personalizadas. "
        "Responde en espanol claro, con tono ejecutivo, maximo 110 palabras. "
        "Si el usuario pregunta por un dato, explica que significa y que lectura macro permite."
    )


@login_required(login_url="/accounts/google/login/")
def world_dashboard_oracle(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except Exception:
        data = {}

    question = (data.get("message") or "").strip()
    selected = (data.get("selected") or "").strip()
    if not question:
        return JsonResponse({"reply": "Dame una pregunta concreta sobre un pais, indicador o activo global."}, status=400)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return JsonResponse({
            "reply": (
                f"Estoy sin llave de IA ahora. Lectura rapida: mira {selected or 'el pais seleccionado'} "
                "comparando poblacion, natalidad, inflacion, PBI per capita y Gini. Esa combinacion cuenta "
                "si el crecimiento es demografico, economico o desigual."
            )
        })

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _build_world_dashboard_prompt()},
                {"role": "user", "content": f"Seleccion actual: {selected or 'Mundo'}\nPregunta: {question}"},
            ],
            max_tokens=190,
            temperature=0.55,
        )
        return JsonResponse({"reply": response.choices[0].message.content})
    except Exception as e:
        print(f"[World Dashboard Oracle] Error: {e}")
        return JsonResponse({"reply": "No pude conectar la IA ahora. Proba de nuevo en un momento."}, status=500)


from calculadora.models import ClientePerfil

def planes_view(request):
    _capture_referral_code(request)
    tiene_plan_activo = False

    if request.user.is_authenticated:
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)

        if perfil and perfil.plan_activo:
            tiene_plan_activo = True

    return render(request, "planes.html", {
        "tiene_plan_activo": tiene_plan_activo
    })


def planeserp(request):
    return render(request, "planeserp.html")
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from .models import Plan, Subscripcion, ClientePerfil
from .utils import aplicar_referido, pagar_comision


@login_required(login_url="/accounts/google/login/")
def pago_exitoso(request):
    messages.success(
        request,
        "Pago recibido. MercadoPago esta confirmando la operacion; tu plan se activa automaticamente al aprobarse."
    )
    return redirect("perfil_usuario")

@login_required(login_url="/accounts/google/login/")
def pago_cancelado(request):
    return redirect("planes")


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from calculadora.models import Plan, GiftRequest


@login_required(login_url="/accounts/google/login/")
@require_POST
def regalar_plan(request, plan_id):
    if not request.user.is_authenticated:
        return require_login_action(request, f"/regalar/{plan_id}/")
    plan = get_object_or_404(Plan, id=plan_id)

    nombre = request.POST.get("nombre")
    telefono = request.POST.get("telefono")

    if not nombre or not telefono:
        messages.error(request, "CompletÃ¡ todos los datos")
        return redirect("planes")

    GiftRequest.objects.create(
        comprador=request.user,
        plan=plan,
        nombre_destinatario=nombre,
        telefono_destinatario=telefono,
    )

    messages.success(
        request,
        "ðŸŽ Regalo registrado. Te contactaremos para coordinar la entrega."
    )

    return redirect("planes")



from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from calculadora.models import PromoCode, Plan

@staff_member_required
def crear_codigos_view(request):
    if request.method == "POST":
        plan_id = request.POST.get("plan")
        cantidad = int(request.POST.get("cantidad", 0))
        prefijo = request.POST.get("prefijo", "").strip().upper()
        max_uses = int(request.POST.get("max_uses", 1))

        if not plan_id or cantidad <= 0 or not prefijo:
            messages.error(request, "Datos invÃ¡lidos")
            return redirect("crear_codigos")

        plan = Plan.objects.get(id=plan_id)

        creados = []

        # buscamos el Ãºltimo nÃºmero usado con ese prefijo
        existentes = PromoCode.objects.filter(code__startswith=prefijo).count()

        for i in range(1, cantidad + 1):
            numero = existentes + i
            code = f"{prefijo}{str(numero).zfill(3)}"

            PromoCode.objects.create(
                code=code,
                plan=plan,
                max_uses=max_uses
            )
            creados.append(code)

        messages.success(
            request,
            f"âœ… {len(creados)} cÃ³digos creados: {', '.join(creados)}"
        )

        return redirect("crear_codigos")

    planes = Plan.objects.all()
    return render(request, "calculadora/crear_codigos.html", {
        "planes": planes
    })


from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect

def dev_login(request):
    user, _ = User.objects.get_or_create(
        email="miotti322@gmail.com",
        defaults={
            "username": "emi",
            "first_name": "Emi",
            "is_staff": True,
            "is_superuser": True,
        }
    )
    update_fields = []
    if user.username != "emi":
        user.username = "emi"
        update_fields.append("username")
    if user.first_name != "Emi":
        user.first_name = "Emi"
        update_fields.append("first_name")
    if not user.is_staff:
        user.is_staff = True
        update_fields.append("is_staff")
    if not user.is_superuser:
        user.is_superuser = True
        update_fields.append("is_superuser")
    if update_fields:
        user.save(update_fields=update_fields)
    perfil, _ = ClientePerfil.objects.get_or_create(user=user)
    perfil.alias = "Emi"
    if perfil.plan_activo != 4:
        perfil.plan_activo = 4
    perfil.save(update_fields=["alias", "plan_activo"])
    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)
    return redirect(request.GET.get("next") or "/perfil/world-dashboard/")


# ============================================================
# ReemplazÃ¡ chatbot_view y chatbot_vip_view en tu views.py
# por este bloque completo.
#
# TAMBIÃ‰N en urls.py dejÃ¡ UNA sola ruta:
#   path("chatbot/", chatbot_view, name="chatbot"),
# y eliminÃ¡ la ruta chatbot_vip si la tenÃ­as.
# ============================================================

import os
import json
import tempfile

from django.http       import JsonResponse
from django.shortcuts  import render
from django.contrib.auth.decorators import login_required
from openai            import OpenAI

from calculadora.models import ClientePerfil, DiagnosticoFinanciero, ChatMensaje


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CONSTANTES DE PLANES
# Plan 1 = Sin plan (visita o usuario nuevo)
# Plan 2 = BÃ¡sico
# Plan 3 = Premium
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PLAN_SIN_PLAN = 1
PLAN_BASICO   = 2
PLAN_PREMIUM  = 3

LIMITE_SIN_PLAN = 3    # mensajes gratis totales (sesiÃ³n)
LIMITE_BASICO   = 20   # mensajes por sesiÃ³n en plan bÃ¡sico
MAX_HISTORY_BD  = 12   # cuÃ¡ntos mensajes previos mandamos a la IA como contexto


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# HELPERS INTERNOS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _get_perfil_y_diagnostico(user):
    """Devuelve (perfil, diagnostico). Cualquiera puede ser None."""
    if not (user and user.is_authenticated):
        return None, None
    perfil = getattr(user, "clienteperfil", None)
    if not perfil:
        return None, None
    diagnostico = DiagnosticoFinanciero.objects.filter(cliente=perfil).last()
    return perfil, diagnostico


def _get_plan(perfil):
    """Devuelve el id del plan activo. Default: PLAN_SIN_PLAN."""
    if not perfil:
        return PLAN_SIN_PLAN
    return perfil.plan_activo or PLAN_SIN_PLAN


def _get_resultado_context(perfil):
    """
    Extrae el ResultadoIA mÃ¡s reciente del usuario y arma un bloque de texto
    con radiografÃ­a, meta, feedback y plan de guerra para el system prompt.
    """
    if not perfil:
        return ""
    try:
        from calculadora.models import ResultadoIA
        from calculadora.services.resultado import METAS_MAP
        resultado = ResultadoIA.objects.filter(
            usuario=perfil.user, estado='completado'
        ).order_by('-id').first()
        if not resultado:
            return ""

        lines = ["\nANÃLISIS IA PREVIO DEL USUARIO (generado por el sistema):"]

        # RadiografÃ­a
        if resultado.bloque_diagnostico:
            lines.append(f"\nRADIOGRAFÃA EJECUTIVA:\n{resultado.bloque_diagnostico}")

        # Meta + feedback
        if resultado.bloque_sesgo:
            try:
                meta_info = json.loads(resultado.bloque_sesgo)
                meta_key = meta_info.get('meta_key')
                label = meta_info.get('label', '')
                feedback = meta_info.get('feedback', '')
                # Imagen siempre fresca desde METAS_MAP
                if meta_key and meta_key in METAS_MAP:
                    label = METAS_MAP[meta_key]['label']
                if label:
                    lines.append(f"\nMETA DEL USUARIO: {label}")
                if feedback:
                    lines.append(f"FEEDBACK DE META:\n{feedback}")
            except Exception:
                pass

        # Plan de guerra
        if resultado.bloque_accion:
            try:
                acciones = json.loads(resultado.bloque_accion)
                lines.append("\nPLAN DE GUERRA GENERADO:")
                for accion in acciones.get('corto_plazo', []):
                    lines.append(f"  [CORTO] {accion}")
                for accion in acciones.get('mediano_plazo', []):
                    lines.append(f"  [MEDIANO] {accion}")
                for accion in acciones.get('largo_plazo', []):
                    lines.append(f"  [LARGO] {accion}")
            except Exception:
                pass

        if len(lines) <= 1:
            return ""

        lines.append(
            "\nUSO: PodÃ©s referenciar este anÃ¡lisis directamente en tus respuestas. "
            "Si el usuario pregunta sobre su plan, su meta o su situaciÃ³n, usÃ¡ estos datos. "
            "No los repitas todos de una, usÃ¡ lo relevante segÃºn la pregunta."
        )
        return "\n".join(lines)
    except Exception:
        return ""


def _build_user_context(perfil, diagnostico):
    """
    Arma el bloque de texto con los datos disponibles del usuario.
    Si faltan datos, lo indica de forma que la IA lo aproveche.
    """
    if not perfil:
        return "Usuario sin autenticar. No tenemos ningÃºn dato financiero."

    lines = []

    # Datos bÃ¡sicos
    nombre = (
        perfil.alias
        or (perfil.user.first_name if perfil.user else None)
        or "el usuario"
    )
    lines.append(f"- Nombre/Alias: {nombre}")

    if perfil.edad:
        lines.append(f"- Edad: {perfil.edad} aÃ±os")

    if perfil.hijos_a_cargo is not None:
        lines.append(f"- Personas a cargo: {perfil.hijos_a_cargo}")

    if perfil.situacion_habitacional:
        hab = "propietario" if perfil.situacion_habitacional == "propietario" else "alquila"
        lines.append(f"- Vivienda: {hab}")

    if perfil.perfil_asignado:
        lines.append(f"- Perfil inversor (IA): {perfil.perfil_asignado}")

    if perfil.quiz_score_total:
        lines.append(f"- Puntaje Quiz Financiero: {perfil.quiz_score_total} pts")

    # Datos del diagnÃ³stico
    if diagnostico:
        try:
            ing = (
                diagnostico.ingreso_trabajo
                + diagnostico.ingreso_negocio
                + diagnostico.ingreso_rentas
                + diagnostico.ingreso_inversiones
                + diagnostico.ingreso_otros
            )
            gas = (
                diagnostico.gasto_necesarios
                + diagnostico.gasto_innecesarios
                + diagnostico.gasto_financieros
                + diagnostico.gasto_inversiones
            )
            lines.append(f"- Ingreso mensual total: ${ing:,.0f}")
            lines.append(f"- Gasto mensual total:   ${gas:,.0f}")
            lines.append(f"- Ahorro mensual:         ${ing - gas:,.0f}")

            if diagnostico.patrimonio_total and diagnostico.patrimonio_total > 0:
                lines.append(f"- Patrimonio total: ${diagnostico.patrimonio_total:,.0f}")
            if diagnostico.deuda_total and diagnostico.deuda_total > 0:
                lines.append(f"- Deuda total: ${diagnostico.deuda_total:,.0f}")
            if diagnostico.reaccion_perdida:
                lines.append(f"- ReacciÃ³n ante pÃ©rdidas: {diagnostico.reaccion_perdida}")
            if diagnostico.perfil_asignado:
                lines.append(f"- Perfil del diagnÃ³stico: {diagnostico.perfil_asignado}")
        except Exception:
            pass

    if len(lines) <= 1:
        return (
            f"- Nombre/Alias: {nombre}\n"
            "- Sin datos financieros cargados todavÃ­a."
        )

    return "\n".join(lines)


def _build_system_prompt(plan, perfil, diagnostico):
    """
    Construye el system prompt completo adaptado al plan del usuario.
    Personalidad base compartida + secciÃ³n de datos + instrucciones por plan.
    """
    user_ctx       = _build_user_context(perfil, diagnostico)
    resultado_ctx  = _get_resultado_context(perfil)
    tiene_diag     = diagnostico is not None
    tiene_perfil   = bool(perfil and (perfil.edad or perfil.situacion_habitacional))

    # â”€â”€ PERSONALIDAD BASE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    base = (
        "Sos 'El OrÃ¡culo', la mente financiera y sarcÃ¡stica de Emiliano Miotti.\n"
        "HablÃ¡s en argentino: filoso, directo, con humor negro y jerga local "
        "(\"pichÃ³n\", \"alto clavo\", \"timba\", \"garrÃ³n\", \"no te hagas el vivo\").\n"
        "Cero bullets. Cero estructura. PÃ¡rrafos cortos. MÃ¡ximo 80 palabras por respuesta.\n"
        "No das consejos genÃ©ricos: usÃ¡s los datos del usuario para ser especÃ­fico y cortante.\n"
        "Opiniones fijas: los plazos fijos son una trampa, los planes de auto son un lujo caro, "
        "Bitcoin es el mejor seguro del siglo, y la casa propia es un gusto que sale caro.\n"
    )

    # â”€â”€ DATOS DEL USUARIO â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    user_section = f"\nDATOS DEL USUARIO (usÃ¡ estos para personalizar las respuestas):\n{user_ctx}\n"
    if resultado_ctx:
        user_section += resultado_ctx + "\n"

    # InstrucciÃ³n de diagnÃ³stico si faltan datos
    if not tiene_diag and not tiene_perfil:
        user_section += (
            "\nIMPORTANTE: Este usuario no completÃ³ ningÃºn dato todavÃ­a. "
            "Si la pregunta lo amerita, sugerile de forma sarcÃ¡stica que haga el DiagnÃ³stico IA: "
            "\"Â¿CÃ³mo te ayudo sin saber ni cuÃ¡nto ganÃ¡s? AndÃ¡ al panel y hacÃ© el DiagnÃ³stico IA, "
            "tardÃ¡s 3 minutos y al menos sabemos de quÃ© hablar.\"\n"
        )
    elif not tiene_diag:
        user_section += (
            "\nNOTA: Tiene datos de perfil bÃ¡sicos pero no hizo el DiagnÃ³stico IA completo. "
            "Si el tema lo pide, sugerile completarlo para darte consejos mÃ¡s precisos.\n"
        )

    # â”€â”€ INSTRUCCIONES POR PLAN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if plan == PLAN_SIN_PLAN:
        plan_section = (
            "\nMODO: USUARIO SIN PLAN\n"
            "- PodÃ©s dar 1 o 2 consejos de valor real, pero al final de la conversaciÃ³n "
            "mencionÃ¡ de forma natural (no insistente) que con el Plan BÃ¡sico pueden seguir.\n"
            "- CTA: \"Si querÃ©s profundizar esto, revisÃ¡ los planes en /planes/ â€” "
            "el BÃ¡sico no rompe el bolsillo.\"\n"
            "- Si estÃ¡ muy perdido, derivalo al DiagnÃ³stico IA antes que nada.\n"
        )

    elif plan == PLAN_BASICO:
        plan_section = (
            "\nMODO: PLAN BÃSICO\n"
            "- Este usuario ya pagÃ³ algo: tratalo bien, dale consejos de calidad real.\n"
            "- UNA sola vez por conversaciÃ³n, cuando el tema lo pida naturalmente (estrategia "
            "a largo plazo, anÃ¡lisis de portafolio, situaciÃ³n compleja), mencionÃ¡ que con "
            "Premium tiene reuniones 1 a 1 y seguimiento personalizado con Emiliano.\n"
            "- CTA: \"Para armar un plan de verdad con seguimiento mensual, "
            "el Premium incluye una call directa.\"\n"
            "- No menciones upgrades en cada respuesta. Solo cuando tenga sentido.\n"
        )

    else:  # PLAN_PREMIUM
        plan_section = (
            "\nMODO: PLAN PREMIUM â€” CLIENTE VIP\n"
            "- Este usuario tiene acceso ilimitado, reuniones 1 a 1 y seguimiento personalizado.\n"
            "- Tratalo como a un cliente al que le cobrÃ¡s en dÃ³lares la hora. "
            "Sin CTAs de venta, sin mencionar upgrades, ya estÃ¡ en el tope.\n"
            "- PodÃ©s profundizar mÃ¡s: estrategias, anÃ¡lisis de su situaciÃ³n, proyecciones.\n"
            "- Si el tema requiere anÃ¡lisis muy profundo de su situaciÃ³n completa, sugerile: "
            "\"Esto lo resolvemos mejor en una call, agendÃ¡ en tu panel.\"\n"
        )

    return base + user_section + plan_section


def _check_limit(request, plan, perfil):
    """
    Verifica si el usuario superÃ³ el lÃ­mite de mensajes.
    Para usuarios autenticados con plan bÃ¡sico/premium: cuenta mensajes en BD.
    Para no autenticados: usa sesiÃ³n.
    Retorna (bloqueado: bool, mensaje: str | None)
    """
    if plan == PLAN_PREMIUM:
        return False, None

    if plan == PLAN_SIN_PLAN:
        usados = request.session.get("oraculo_usos_anonimo", 0)
        if usados >= LIMITE_SIN_PLAN:
            return True, (
                "Ya te di mis 3 consejos gratis, pichÃ³n. El resto tiene precio. "
                "Si querÃ©s seguir charlando, "
                "<a href='/planes/' style='color:#22c55e;font-weight:bold;"
                "text-decoration:underline;'>revisÃ¡ los planes acÃ¡</a> "
                "â€” el BÃ¡sico no te va a fundir."
            )
        return False, None

    # Plan BÃ¡sico: contamos mensajes del usuario en esta sesiÃ³n (Django session)
    usados = request.session.get("oraculo_usos_sesion", 0)
    if usados >= LIMITE_BASICO:
        return True, (
            "Llegaste al lÃ­mite de mensajes de esta sesiÃ³n. "
            "Para sesiones sin lÃ­mite y con seguimiento personalizado, "
            "<a href='/planes/' style='color:#22c55e;font-weight:bold;"
            "text-decoration:underline;'>el Plan Premium</a> "
            "incluye una call directa con Emiliano."
        )
    return False, None


def _increment_usage(request, plan):
    """Incrementa el contador de mensajes segÃºn el plan."""
    if plan == PLAN_SIN_PLAN:
        key = "oraculo_usos_anonimo"
    elif plan == PLAN_BASICO:
        key = "oraculo_usos_sesion"
    else:
        return  # Premium: sin lÃ­mite, no contamos
    request.session[key] = request.session.get(key, 0) + 1


def _get_history_from_db(perfil):
    """
    Recupera los Ãºltimos MAX_HISTORY_BD mensajes del cliente desde la BD
    y los devuelve en el formato que espera la API de OpenAI.
    """
    if not perfil:
        return []
    mensajes = (
        ChatMensaje.objects
        .filter(cliente=perfil)
        .order_by("-creado_en")[:MAX_HISTORY_BD]
    )
    # Invertimos para orden cronolÃ³gico (mÃ¡s viejos primero)
    return [
        {"role": m.role, "content": m.content}
        for m in reversed(list(mensajes))
    ]


def _save_message_to_db(perfil, role, content):
    """Guarda un mensaje en la BD. Solo para usuarios autenticados."""
    if not perfil:
        return
    ChatMensaje.objects.create(
        cliente=perfil,
        role=role,
        content=content,
    )


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# VISTA PRINCIPAL
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@login_required(login_url="/accounts/google/login/")
def chatbot_view(request):
    """
    Vista unificada del OrÃ¡culo. Maneja:
    âœ“ Plan Sin Plan  â†’ 3 mensajes gratis (sesiÃ³n) + paywall suave
    âœ“ Plan BÃ¡sico    â†’ 20 mensajes/sesiÃ³n, upsell sutil 1 vez
    âœ“ Plan Premium   â†’ sin lÃ­mites, tono VIP, sugerencia de call
    âœ“ Historial persistente en BD (solo autenticados)
    âœ“ Contexto financiero personalizado (perfil + diagnÃ³stico)
    âœ“ Soporte de audio vÃ­a Whisper
    âœ“ Fix XSS: el input del usuario se trata como texto plano en el frontend
    """
    if request.method != "POST":
        return render(request, "chatbot.html")

    try:
        # 1. Datos del usuario
        perfil, diagnostico = _get_perfil_y_diagnostico(request.user)
        plan = _get_plan(perfil)

        # 2. Verificar lÃ­mite
        bloqueado, msg_bloqueo = _check_limit(request, plan, perfil)
        if bloqueado:
            return JsonResponse({"reply": msg_bloqueo})

        # 3. Extraer mensaje (texto o audio)
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        mensaje_usuario = ""

        if "audio" in request.FILES:
            audio_file = request.FILES["audio"]
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                for chunk in audio_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", file=f
                )
            os.remove(tmp_path)
            mensaje_usuario = transcript.text

        elif request.content_type and "application/json" in request.content_type:
            data = json.loads(request.body)
            mensaje_usuario = data.get("message", "")

        elif "message" in request.POST:
            mensaje_usuario = request.POST.get("message", "")

        mensaje_usuario = mensaje_usuario.strip()
        if not mensaje_usuario:
            return JsonResponse({
                "reply": "Â¿Te comieron la lengua los ratones? HablÃ¡ que el tiempo es oro."
            })

        # 4. Historial desde BD + system prompt
        history   = _get_history_from_db(perfil)
        system_prompt = _build_system_prompt(plan, perfil, diagnostico)

        messages_to_send = (
            [{"role": "system", "content": system_prompt}]
            + history
            + [{"role": "user", "content": mensaje_usuario}]
        )

        # 5. Llamar a OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages_to_send,
            max_tokens=160,
            temperature=0.85,
        )
        respuesta_ia = response.choices[0].message.content

        # 6. Guardar en BD (solo usuarios autenticados)
        _save_message_to_db(perfil, "user",      mensaje_usuario)
        _save_message_to_db(perfil, "assistant", respuesta_ia)

        # 7. Incrementar contador de sesiÃ³n y responder
        _increment_usage(request, plan)

        return JsonResponse({"reply": respuesta_ia})

    except Exception as e:
        print(f"[OrÃ¡culo] Error: {e}")
        return JsonResponse(
            {"reply": "Se me pinchÃ³ una rueda de la Ferrari. Escribime en 5 minutos."},
            status=500,
        )
    

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from calculadora.models import ClientePerfil, ChatMensaje
 
@login_required
def chatbot_historial_view(request):
    """
    Devuelve los Ãºltimos mensajes del usuario para cargar en el modal.
    Solo GET. Usado por el frontend al abrir el chat.
    """
    if request.method != "GET":
        return JsonResponse({"error": "MÃ©todo no permitido"}, status=405)
 
    try:
        perfil = getattr(request.user, "clienteperfil", None)
        if not perfil:
            return JsonResponse({"mensajes": []})
 
        # Ãšltimos 20 mensajes en orden cronolÃ³gico
        mensajes = (
            ChatMensaje.objects
            .filter(cliente=perfil)
            .order_by("-creado_en")[:20]
        )
 
        return JsonResponse({
            "mensajes": [
                {"role": m.role, "content": m.content}
                for m in reversed(list(mensajes))
            ]
        })
 
    except Exception as e:
        print(f"[Historial] Error: {e}")
        return JsonResponse({"mensajes": []})

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from calculadora.models import SolicitudAsesoria
@login_required(login_url="/accounts/google/login/")
@require_http_methods(["POST"])
def solicitar_asesoria(request):
    """
    Retorna JSON para AJAX (no redirect).
    """
    try:
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)

        if perfil.plan_activo not in (3, 4):
            return JsonResponse({
                "success": False,
                "error": "Solo Premium puede agendar asesorÃ­a"
            }, status=403)
        
        horario = request.POST.get("horario_preferido", "").strip()
        
        if not horario:
            return JsonResponse({
                "success": False,
                "error": "IndicÃ¡ un horario preferido"
            }, status=400)
        
        # Crear solicitud
        SolicitudAsesoria.objects.create(
            cliente=perfil,
            nombre=perfil.alias or request.user.first_name or request.user.username,
            email=request.user.email,
            horario_preferido=horario,
        )
        
        return JsonResponse({
            "success": True,
            "message": "âœ… Solicitud registrada. Emiliano te contacta en < 24hs."
        }, status=201)
        
    except Exception as e:
        print(f"[ERROR solicitar_asesoria] {str(e)}")
        return JsonResponse({
            "success": False,
            "error": "Error interno"
        }, status=500)

from calculadora.models import InscripcionCursoFintech

@login_required(login_url="/accounts/google/login/")
@require_http_methods(["POST"])
def inscribir_curso_fintech(request):
    try:
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)

        if perfil.plan_activo not in (3, 4):
            return JsonResponse({
                "success": False,
                "error": "Solo usuarios Premium pueden inscribirse al curso"
            }, status=403)

        nombre = request.POST.get("nombre", "").strip()
        edad_raw = request.POST.get("edad", "").strip()
        mes = request.POST.get("mes_elegido", "").strip()

        meses_validos = {"mayo", "junio", "julio", "agosto", "septiembre"}

        if not nombre:
            return JsonResponse({"success": False, "error": "El nombre es requerido"}, status=400)
        if not edad_raw or not edad_raw.isdigit():
            return JsonResponse({"success": False, "error": "La edad debe ser un nÃºmero vÃ¡lido"}, status=400)
        if mes not in meses_validos:
            return JsonResponse({"success": False, "error": "Mes invÃ¡lido"}, status=400)

        InscripcionCursoFintech.objects.create(
            cliente=perfil,
            nombre=nombre,
            email=request.user.email,
            edad=int(edad_raw),
            mes_elegido=mes,
        )

        return JsonResponse({
            "success": True,
            "message": f"Â¡InscripciÃ³n confirmada para {mes.capitalize()}! Emiliano te contacta pronto."
        }, status=201)

    except Exception as e:
        print(f"[ERROR inscribir_curso_fintech] {str(e)}")
        return JsonResponse({"success": False, "error": "Error interno"}, status=500)

# ============================================================
# WALL STREET CORDOBES
# ============================================================

SESSION_MARKET_KEY = "mercado_pyme"
INITIAL_MARKET_CASH = Decimal("10000000.00")


def _ensure_guest_market_session(request):
    data = request.session.get(SESSION_MARKET_KEY)
    if not data:
        data = {"cash_balance": str(INITIAL_MARKET_CASH), "holdings": {}}
        request.session[SESSION_MARKET_KEY] = data
    return data


def _normalize_guest_holding(raw):
    if isinstance(raw, dict):
        return {
            "quantity": int(raw.get("quantity", 0)),
            "avg_cost": Decimal(str(raw.get("avg_cost", "0"))),
        }
    return {"quantity": int(raw or 0), "avg_cost": Decimal("0")}


def _calculate_average_cost(user, company):
    from calculadora.models import Transaction

    quantity = 0
    invested = Decimal("0")
    for tx in Transaction.objects.filter(user=user, company=company).order_by("timestamp"):
        if tx.type == Transaction.BUY:
            invested += tx.price_at_transaction * tx.quantity
            quantity += tx.quantity
        elif quantity:
            avg_cost = invested / quantity
            sold = min(quantity, tx.quantity)
            invested -= avg_cost * sold
            quantity -= sold
    if quantity <= 0:
        return Decimal("0")
    return invested / quantity


def _merge_guest_session_into_user(request):
    from calculadora.models import Company, Portfolio, Transaction

    data = request.session.get(SESSION_MARKET_KEY)
    if not data or not request.user.is_authenticated:
        return

    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    if portfolio.cash_balance == INITIAL_MARKET_CASH and not Transaction.objects.filter(user=request.user).exists():
        portfolio.cash_balance = Decimal(str(data.get("cash_balance", INITIAL_MARKET_CASH)))
        portfolio.save(update_fields=["cash_balance", "updated_at"])

        for company_id, raw in data.get("holdings", {}).items():
            holding = _normalize_guest_holding(raw)
            if holding["quantity"] <= 0:
                continue
            company = Company.objects.filter(id=company_id).first()
            if not company:
                continue
            Transaction.objects.create(
                user=request.user,
                company=company,
                type=Transaction.BUY,
                quantity=holding["quantity"],
                price_at_transaction=holding["avg_cost"] or company.current_price,
            )

    request.session.pop(SESSION_MARKET_KEY, None)
    request.session.modified = True


def _get_user_holding(user, company):
    from calculadora.models import Transaction

    quantity = 0
    for tx in Transaction.objects.filter(user=user, company=company).only("type", "quantity"):
        quantity += tx.quantity if tx.type == Transaction.BUY else -tx.quantity
    return quantity


def _get_market_account(request):
    from calculadora.models import Company, Portfolio, Transaction

    if request.user.is_authenticated:
        _merge_guest_session_into_user(request)
        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
        holdings = {}
        account_companies = Company.objects.filter(
            market_visibility__in=[Company.VISIBILITY_PUBLIC_NAMED, Company.VISIBILITY_OPEN_INVESTORS],
        ) | Company.objects.filter(created_by=request.user)
        for company in account_companies.distinct():
            owned = _get_user_holding(request.user, company)
            if owned:
                holdings[str(company.id)] = {
                    "quantity": owned,
                    "avg_cost": _calculate_average_cost(request.user, company),
                }
        transactions = Transaction.objects.filter(user=request.user).select_related("company")[:10]
        return portfolio.cash_balance, holdings, transactions

    data = _ensure_guest_market_session(request)
    normalized = {
        company_id: _normalize_guest_holding(raw)
        for company_id, raw in data.get("holdings", {}).items()
    }
    return Decimal(data["cash_balance"]), normalized, []


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key or ""


def _user_company_queryset(request):
    from calculadora.models import Company

    if request.user.is_authenticated:
        return Company.objects.filter(created_by=request.user)
    return Company.objects.filter(guest_session_key=_ensure_session_key(request))


def _merge_guest_companies_into_user(request):
    from calculadora.models import Company

    if not request.user.is_authenticated or not request.session.session_key:
        return
    Company.objects.filter(
        created_by__isnull=True,
        guest_session_key=request.session.session_key,
    ).update(created_by=request.user, guest_session_key="")


def _get_market_nickname(request):
    from calculadora.models import ClientePerfil

    if request.user.is_authenticated:
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
        return perfil.alias or ""
    return request.session.get("market_nickname", "")


def _set_market_nickname(request, nickname):
    from calculadora.models import ClientePerfil

    nickname = nickname.strip()[:50]
    if not nickname:
        return "Elegi un nick para operar en el mercado."
    if request.user.is_authenticated:
        if ClientePerfil.objects.filter(alias__iexact=nickname).exclude(user=request.user).exists():
            return "Ese nick ya esta en uso."
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
        perfil.alias = nickname
        perfil.save(update_fields=["alias"])
    else:
        request.session["market_nickname"] = nickname
        request.session.modified = True
    return ""




def market_home(request):
    from calculadora.models import CapitalOffering, Company

    open_offerings = CapitalOffering.objects.filter(
        status=CapitalOffering.OPEN,
        company__market_visibility=Company.VISIBILITY_OPEN_INVESTORS,
    ).select_related("company")[:3]
    return render(request, "calculadora/market_home.html", {"open_offerings": open_offerings})


@login_required(login_url="/accounts/google/login/")
def market_ceo_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "El Centro de Comando es interno de la plataforma.")
        return redirect("market_dashboard")
    from calculadora.services.cordoba_street_agents import build_ceo_agent_report

    report = build_ceo_agent_report()
    return render(request, "calculadora/market_ceo_dashboard.html", {"report": report})


@login_required(login_url="/accounts/google/login/")
def market_dashboard(request):
    from calculadora.logic import generate_market_noise
    from calculadora.models import Company, CompanyFollow
    from django.utils import timezone
    from zoneinfo import ZoneInfo

    generate_market_noise()
    if request.method == "POST" and request.POST.get("action") == "market_nickname":
        error = _set_market_nickname(request, request.POST.get("nickname", ""))
        if error:
            messages.error(request, error)
            return redirect("market_dashboard")
        messages.success(request, "Nick de mercado activado.")
        return redirect("market_dashboard")
    if request.method == "POST" and request.POST.get("action") == "follow_company":
        company = Company.objects.filter(id=request.POST.get("company_id")).first()
        if not company:
            messages.error(request, "Empresa no encontrada.")
            return redirect("market_dashboard")
        if not _get_market_nickname(request):
            messages.error(request, "Elegi un nick para seguir empresas.")
            return redirect("market_dashboard")
        if request.user.is_authenticated:
            follow, created = CompanyFollow.objects.get_or_create(company=company, user=request.user)
        else:
            follow, created = CompanyFollow.objects.get_or_create(
                company=company,
                guest_session_key=_ensure_session_key(request),
            )
        if not created:
            follow.delete()
        return redirect("market_dashboard")

    cash_balance, holdings, transactions = _get_market_account(request)
    companies_qs = Company.objects.select_related("capital_offering").filter(
        market_visibility__in=[Company.VISIBILITY_PUBLIC_NAMED, Company.VISIBILITY_OPEN_INVESTORS],
    )
    if request.user.is_authenticated:
        companies_qs = companies_qs | Company.objects.select_related("capital_offering").filter(created_by=request.user)
    companies = sorted(companies_qs.distinct(), key=lambda item: item.market_cap, reverse=True)
    positions = []
    sectors = []

    for company in companies:
        if company.sector not in sectors:
            sectors.append(company.sector)
        holding = holdings.get(str(company.id), {"quantity": 0, "avg_cost": Decimal("0")})
        quantity = int(holding["quantity"])
        if quantity:
            avg_cost = holding["avg_cost"]
            gain_percent = Decimal("0")
            if avg_cost:
                gain_percent = ((company.current_price - avg_cost) / avg_cost) * Decimal("100")
            market_value = company.current_price * quantity
            cost_basis = avg_cost * quantity
            daily_gain = (company.current_price - company.previous_price) * quantity
            positions.append({
                "company": company,
                "quantity": quantity,
                "avg_cost": avg_cost,
                "gain_percent": gain_percent,
                "market_value": market_value,
                "cost_basis": cost_basis,
                "daily_gain": daily_gain,
            })

    invested_total = sum(position["market_value"] for position in positions)
    cash_total = cash_balance + invested_total
    cost_total = sum(position["cost_basis"] for position in positions)
    daily_gain_total = sum(position["daily_gain"] for position in positions)
    historical_gain_total = invested_total - cost_total
    daily_gain_percent = Decimal("0")
    if cash_total - daily_gain_total:
        daily_gain_percent = (daily_gain_total / (cash_total - daily_gain_total)) * Decimal("100")
    historical_gain_percent = Decimal("0")
    if cost_total:
        historical_gain_percent = (historical_gain_total / cost_total) * Decimal("100")
    for position in positions:
        position["portfolio_percent"] = Decimal("0")
        if cash_total:
            position["portfolio_percent"] = (position["market_value"] / cash_total) * Decimal("100")
    now = timezone.localtime(timezone.now(), ZoneInfo("America/Argentina/Buenos_Aires"))
    market_is_open = 10 <= now.hour < 17
    market_nickname = _get_market_nickname(request)
    followed_company_ids = set()
    followed_companies = []
    if market_nickname:
        if request.user.is_authenticated:
            followed_company_ids = set(CompanyFollow.objects.filter(user=request.user).values_list("company_id", flat=True))
        else:
            followed_company_ids = set(CompanyFollow.objects.filter(guest_session_key=_ensure_session_key(request)).values_list("company_id", flat=True))
        followed_companies = [company for company in companies if company.id in followed_company_ids]

    return render(request, "calculadora/market_dashboard.html", {
        "cash_balance": cash_balance,
        "cash_total": cash_total,
        "daily_gain_total": daily_gain_total,
        "daily_gain_percent": daily_gain_percent,
        "historical_gain_total": historical_gain_total,
        "historical_gain_percent": historical_gain_percent,
        "companies": companies,
        "sectors": sectors,
        "positions": positions,
        "transactions": transactions,
        "market_is_open": market_is_open,
        "market_time": now,
        "market_nickname": market_nickname,
        "show_nickname_modal": not bool(market_nickname),
        "followed_company_ids": followed_company_ids,
        "followed_companies": followed_companies,
    })


@login_required(login_url="/accounts/google/login/")
def company_valuation_view(request):
    from calculadora.forms import CompanyValuationForm
    from calculadora.logic import price_company

    if request.method == "POST":
        form = CompanyValuationForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            if request.user.is_authenticated:
                company.created_by = request.user
            else:
                company.guest_session_key = _ensure_session_key(request)
            price_company(company)
            company.save()
            request.session["ipo_just_listed_id"] = company.id
            request.session.modified = True
            return redirect("ipo_admin_detail", company_id=company.id)
    else:
        form = CompanyValuationForm()

    return render(request, "calculadora/company_valuation_form.html", {"form": form})


@login_required(login_url="/accounts/google/login/")
def ipo_admin_list(request):
    companies = _user_company_queryset(request).order_by("-created_at")
    return render(request, "calculadora/ipo_admin_list.html", {"companies": companies})


@login_required(login_url="/accounts/google/login/")
def capital_offering_edit(request, company_id):
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from calculadora.forms import CapitalOfferingForm, OfferingAnswerForm, OfferingEvidenceForm
    from calculadora.models import CapitalOffering, OfferingQuestion

    company = get_object_or_404(_user_company_queryset(request), id=company_id)
    offering = CapitalOffering.objects.filter(company=company).first()
    action = request.POST.get("action", "save")
    offering_data = request.POST if request.method == "POST" and action in ("save", "publish", "close") else None
    evidence_data = request.POST if request.method == "POST" and action == "evidence" else None
    evidence_files = request.FILES if request.method == "POST" and action == "evidence" else None
    answer_data = request.POST if request.method == "POST" and action == "answer" else None
    form = CapitalOfferingForm(offering_data, instance=offering)
    evidence_form = OfferingEvidenceForm(evidence_data, evidence_files)
    answer_form = OfferingAnswerForm(answer_data)

    if request.method == "POST" and action == "evidence":
        if not offering:
            messages.error(request, "Guarda la apertura antes de cargar evidencias.")
            return redirect("capital_offering_edit", company_id=company.id)
        if evidence_form.is_valid():
            evidence = evidence_form.save(commit=False)
            evidence.offering = offering
            evidence.save()
            messages.success(request, "Evidencia publicada en la ficha.")
            return redirect("capital_offering_edit", company_id=company.id)

    if request.method == "POST" and action == "answer":
        if not offering:
            messages.error(request, "Todavia no hay apertura para responder preguntas.")
            return redirect("capital_offering_edit", company_id=company.id)
        question = get_object_or_404(OfferingQuestion, offering=offering, id=request.POST.get("question_id"))
        if answer_form.is_valid():
            question.answer = answer_form.cleaned_data["answer"]
            question.answered_by = request.user if request.user.is_authenticated else None
            question.answered_at = timezone.now()
            question.save(update_fields=["answer", "answered_by", "answered_at"])
            messages.success(request, "Respuesta publicada.")
            return redirect("capital_offering_edit", company_id=company.id)

    if request.method == "POST" and action in ("save", "publish", "close") and form.is_valid():
        previous_contract = offering.contract_terms if offering else ""
        offering = form.save(commit=False)
        offering.company = company

        if offering.pk and previous_contract != offering.contract_terms:
            offering.contract_version += 1

        if action == "publish":
            if not request.user.is_authenticated:
                messages.error(request, "Inicia sesion para publicar una apertura de capital.")
                return redirect("google_login_entry")
            offering.status = CapitalOffering.OPEN
            offering.published_at = offering.published_at or timezone.now()
            company.public_float_percent = offering.offered_percent
            company.market_visibility = company.VISIBILITY_OPEN_INVESTORS
            company.save(update_fields=["public_float_percent", "market_visibility", "updated_at"])
            messages.success(request, "Apertura publicada. El mercado ya puede verla y enviar solicitudes de contacto.")
        elif action == "close":
            offering.status = CapitalOffering.CLOSED
            messages.success(request, "Apertura cerrada.")
        else:
            messages.success(request, "Borrador guardado.")

        offering.save()
        return redirect("capital_offering_edit", company_id=company.id)

    return render(request, "calculadora/capital_offering_edit.html", {
        "company": company,
        "offering": offering,
        "form": form,
        "evidence_form": evidence_form,
        "answer_form": answer_form,
        "reservations": offering.reservations.select_related("user").all() if offering else [],
        "evidences": offering.evidences.all() if offering else [],
        "questions": offering.questions.select_related("user").all() if offering else [],
    })


@login_required(login_url="/accounts/google/login/")
def capital_offering_detail(request, offering_id):
    from django.contrib.auth.views import redirect_to_login
    from django.db import transaction as db_transaction
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from calculadora.forms import CapitalReservationForm, InvestorProfileForm, OfferingQuestionForm
    from calculadora.models import CapitalOffering, CapitalReservation, InvestorProfile, OfferingQuestion

    offering = get_object_or_404(
        CapitalOffering.objects.select_related("company"),
        id=offering_id,
        status=CapitalOffering.OPEN,
    )
    existing = None
    investor_profile = None
    if request.user.is_authenticated:
        existing = CapitalReservation.objects.filter(offering=offering, user=request.user).first()
        investor_profile = InvestorProfile.objects.filter(user=request.user).first()

    form = CapitalReservationForm(
        request.POST if request.POST.get("action", "reserve") == "reserve" else None,
        initial={"amount": existing.amount if existing else offering.minimum_reservation},
    )
    profile_form = InvestorProfileForm(
        request.POST if request.POST.get("action", "reserve") == "reserve" else None,
        instance=investor_profile,
    )
    question_form = OfferingQuestionForm(request.POST if request.POST.get("action") == "question" else None)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if request.POST.get("action") == "cancel":
            CapitalReservation.objects.filter(offering=offering, user=request.user).update(status=CapitalReservation.CANCELLED)
            messages.success(request, "Solicitud retirada. No queda ninguna intencion activa a tu nombre.")
            return redirect("capital_offering_detail", offering_id=offering.id)
        if request.POST.get("action") == "question":
            if question_form.is_valid():
                OfferingQuestion.objects.create(
                    offering=offering,
                    user=request.user,
                    question=question_form.cleaned_data["question"],
                )
                messages.success(request, "Pregunta publicada para el fundador.")
                return redirect("capital_offering_detail", offering_id=offering.id)
        if offering.company.created_by_id == request.user.id:
            messages.error(request, "El dueÃ±o de la empresa no puede reservar su propia apertura.")
            return redirect("capital_offering_detail", offering_id=offering.id)
        if request.POST.get("action", "reserve") == "reserve" and form.is_valid() and profile_form.is_valid():
            investor_profile = profile_form.save(commit=False)
            investor_profile.user = request.user
            investor_profile.save()
            amount = form.cleaned_data["amount"]
            if amount < offering.minimum_reservation:
                form.add_error("amount", f"La reserva minima es ${offering.minimum_reservation:,.0f}.")
            else:
                with db_transaction.atomic():
                    locked = CapitalOffering.objects.select_for_update().get(id=offering.id)
                    current = CapitalReservation.objects.filter(offering=locked, user=request.user).first()
                    reserved_without_user = locked.reserved_total - (current.amount if current and current.status == CapitalReservation.ACTIVE else Decimal("0"))
                    available = locked.capital_target - reserved_without_user
                    if amount > available:
                        form.add_error("amount", f"Solo quedan ${max(available, Decimal('0')):,.0f} disponibles para reservar.")
                    else:
                        CapitalReservation.objects.update_or_create(
                            offering=locked,
                            user=request.user,
                            defaults={
                                "amount": amount,
                                "status": CapitalReservation.ACTIVE,
                                "accepted_contract_version": locked.contract_version,
                                "accepted_at": timezone.now(),
                            },
                        )
                        messages.success(request, "Solicitud de compra registrada. No se realizo ningun cobro.")
                        return redirect("capital_offering_detail", offering_id=offering.id)

    return render(request, "calculadora/capital_offering_detail.html", {
        "offering": offering,
        "company": offering.company,
        "form": form,
        "profile_form": profile_form,
        "question_form": question_form,
        "existing_reservation": existing,
        "investor_profile": investor_profile,
        "evidences": offering.evidences.all(),
        "questions": offering.questions.select_related("user", "answered_by").filter(is_public=True),
    })


@login_required(login_url="/accounts/google/login/")
def ipo_admin_detail(request, company_id):
    from django.shortcuts import get_object_or_404
    from decimal import Decimal
    from calculadora.forms import CompanyIpoUpdateForm, CompanyShareStructureForm, CompanyValuationReviewForm
    from calculadora.models import ClientePerfil, CompanyIpoComment, CompanyIpoLike, CompanyIpoUpdate

    company = get_object_or_404(_user_company_queryset(request), id=company_id)
    if request.method == "POST":
        action = request.POST.get("action")
        form = CompanyIpoUpdateForm(request.POST if action == "update" else None)
        share_form = CompanyShareStructureForm(request.POST if action == "ipo_setup" else None)
        review_form = CompanyValuationReviewForm(request.POST if action == "valuation_review" else None)

        if action == "ipo_setup" and share_form.is_valid():
            market_cap = company.market_cap
            total_shares = share_form.cleaned_data["total_shares"]
            public_float_percent = share_form.cleaned_data["public_float_percent"]
            next_price = (market_cap / Decimal(str(total_shares))).quantize(Decimal("0.01"))
            company.total_shares = total_shares
            company.public_float_percent = public_float_percent
            company.current_price = max(next_price, Decimal("0.01"))
            company.previous_price = company.current_price
            company.save(update_fields=["total_shares", "public_float_percent", "current_price", "previous_price", "updated_at"])
            request.session.pop("ipo_just_listed_id", None)
            request.session.modified = True
            messages.success(request, "IPO configurada. Ya podes gestionar comunicados oficiales.")
            return redirect("ipo_admin_detail", company_id=company.id)

        if action == "update" and form.is_valid():
            CompanyIpoUpdate.objects.create(company=company, **form.cleaned_data)
            messages.success(request, "Novedad cargada en el tablero de IPO.")
            return redirect("ipo_admin_detail", company_id=company.id)

        if action == "valuation_review" and review_form.is_valid():
            review = review_form.save(commit=False)
            review.company = company
            review.requested_by = request.user
            review.save()
            messages.success(request, "Revision solicitada. Queda pendiente en el Centro de Comando.")
            return redirect("ipo_admin_detail", company_id=company.id)

        if action == "like":
            update = get_object_or_404(CompanyIpoUpdate, company=company, id=request.POST.get("update_id"))
            if request.user.is_authenticated:
                like, created = CompanyIpoLike.objects.get_or_create(update=update, user=request.user)
            else:
                like, created = CompanyIpoLike.objects.get_or_create(
                    update=update,
                    guest_session_key=_ensure_session_key(request),
                )
            if not created:
                like.delete()
            return redirect("ipo_admin_detail", company_id=company.id)

        if action == "comment":
            update = get_object_or_404(CompanyIpoUpdate, company=company, id=request.POST.get("update_id"))
            body = request.POST.get("comment", "").strip()
            alias = _get_market_nickname(request)
            if not alias:
                messages.error(request, "Elegi un nick en cotizaciones para comentar.")
                return redirect("ipo_admin_detail", company_id=company.id)
            if not body:
                messages.error(request, "Escribi un comentario.")
                return redirect("ipo_admin_detail", company_id=company.id)
            CompanyIpoComment.objects.create(
                update=update,
                user=request.user if request.user.is_authenticated else None,
                guest_session_key="" if request.user.is_authenticated else _ensure_session_key(request),
                alias=alias,
                body=body,
            )
            messages.success(request, "Comentario publicado.")
            return redirect("ipo_admin_detail", company_id=company.id)

    else:
        form = CompanyIpoUpdateForm()
        share_form = CompanyShareStructureForm(initial={
            "total_shares": company.total_shares,
            "public_float_percent": company.public_float_percent or Decimal("20"),
        })
        review_form = CompanyValuationReviewForm(initial={
            "perceived_value": company.perceived_valuation or company.market_cap,
            "reason": company.perceived_valuation_reason,
        })

    daily = company.variation_percent
    seed = Decimal(str((company.id % 9) + 2))
    simulated_metrics = [
        {"label": "Variacion diaria", "value": daily, "kind": "percent"},
        {"label": "Variacion mensual", "value": (daily * Decimal("5.5")) + seed, "kind": "percent"},
        {"label": "YTD", "value": (daily * Decimal("14")) + (seed * Decimal("1.7")), "kind": "percent"},
        {"label": "1 ano", "value": (daily * Decimal("28")) + (seed * Decimal("3.2")), "kind": "percent"},
    ]
    ipo_just_listed = request.session.get("ipo_just_listed_id") == company.id
    market_nickname = _get_market_nickname(request)
    perfil = None
    if request.user.is_authenticated:
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)

    return render(request, "calculadora/ipo_admin_detail.html", {
        "company": company,
        "form": form,
        "share_form": share_form,
        "updates": company.ipo_updates.prefetch_related("comments__user", "likes__user").all(),
        "simulated_metrics": simulated_metrics,
        "ipo_just_listed": ipo_just_listed,
        "comment_alias": market_nickname,
        "review_form": review_form,
        "valuation_reviews": company.valuation_reviews.all()[:5],
    })


@login_required(login_url="/accounts/google/login/")
def trade_company(request, company_id):
    from django.db import transaction as db_transaction
    from django.shortcuts import get_object_or_404
    from calculadora.models import Company, CompanyIpoComment, CompanyIpoLike, CompanyIpoUpdate, Portfolio, Transaction

    company = get_object_or_404(Company, id=company_id)
    cash_balance, holdings, transactions = _get_market_account(request)
    current_holding = holdings.get(str(company.id), {"quantity": 0, "avg_cost": Decimal("0")})
    owned_quantity = int(current_holding["quantity"])

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "like":
            update = get_object_or_404(CompanyIpoUpdate, company=company, id=request.POST.get("update_id"))
            if request.user.is_authenticated:
                like, created = CompanyIpoLike.objects.get_or_create(update=update, user=request.user)
            else:
                like, created = CompanyIpoLike.objects.get_or_create(
                    update=update,
                    guest_session_key=_ensure_session_key(request),
                )
            if not created:
                like.delete()
            return redirect("trade_company", company_id=company.id)

        if action == "comment":
            update = get_object_or_404(CompanyIpoUpdate, company=company, id=request.POST.get("update_id"))
            body = request.POST.get("comment", "").strip()
            alias = _get_market_nickname(request)
            if not alias:
                messages.error(request, "Elegi un nick en cotizaciones para comentar.")
                return redirect("market_dashboard")
            if not body:
                messages.error(request, "Escribi un comentario.")
                return redirect("trade_company", company_id=company.id)
            CompanyIpoComment.objects.create(
                update=update,
                user=request.user if request.user.is_authenticated else None,
                guest_session_key="" if request.user.is_authenticated else _ensure_session_key(request),
                alias=alias,
                body=body,
            )
            messages.success(request, "Comentario publicado.")
            return redirect("trade_company", company_id=company.id)

        try:
            quantity = int(request.POST.get("quantity", "0"))
        except ValueError:
            quantity = 0

        if quantity <= 0 or action not in ("buy", "sell"):
            messages.error(request, "Ingresa una cantidad valida.")
            return redirect("trade_company", company_id=company.id)

        total = company.current_price * quantity

        if request.user.is_authenticated:
            with db_transaction.atomic():
                portfolio, _ = Portfolio.objects.select_for_update().get_or_create(user=request.user)
                owned_quantity = _get_user_holding(request.user, company)

                if action == "buy":
                    if portfolio.cash_balance < total:
                        messages.error(request, "Saldo insuficiente para comprar.")
                    else:
                        portfolio.cash_balance -= total
                        portfolio.save(update_fields=["cash_balance", "updated_at"])
                        Transaction.objects.create(
                            user=request.user,
                            company=company,
                            type=Transaction.BUY,
                            quantity=quantity,
                            price_at_transaction=company.current_price,
                        )
                        company.traded_volume += quantity
                        company.save(update_fields=["traded_volume", "updated_at"])
                        messages.success(request, "Compra registrada.")

                if action == "sell":
                    if owned_quantity < quantity:
                        messages.error(request, "No tenes suficientes acciones para vender.")
                    else:
                        portfolio.cash_balance += total
                        portfolio.save(update_fields=["cash_balance", "updated_at"])
                        Transaction.objects.create(
                            user=request.user,
                            company=company,
                            type=Transaction.SELL,
                            quantity=quantity,
                            price_at_transaction=company.current_price,
                        )
                        company.traded_volume += quantity
                        company.save(update_fields=["traded_volume", "updated_at"])
                        messages.success(request, "Venta registrada.")
        else:
            data = _ensure_guest_market_session(request)
            guest_cash = Decimal(data["cash_balance"])
            guest_holdings = data.get("holdings", {})
            guest_holding = _normalize_guest_holding(guest_holdings.get(str(company.id), 0))
            owned_quantity = int(guest_holding["quantity"])

            if action == "buy":
                if guest_cash < total:
                    messages.error(request, "Saldo insuficiente para comprar.")
                else:
                    guest_cash -= total
                    previous_cost = guest_holding["avg_cost"] * owned_quantity
                    next_quantity = owned_quantity + quantity
                    avg_cost = (previous_cost + total) / next_quantity
                    guest_holdings[str(company.id)] = {
                        "quantity": next_quantity,
                        "avg_cost": str(avg_cost),
                    }
                    company.traded_volume += quantity
                    company.save(update_fields=["traded_volume", "updated_at"])
                    messages.success(request, "Compra simulada en tu sesion.")

            if action == "sell":
                if owned_quantity < quantity:
                    messages.error(request, "No tenes suficientes acciones para vender.")
                else:
                    guest_cash += total
                    next_quantity = owned_quantity - quantity
                    if next_quantity:
                        guest_holdings[str(company.id)] = {
                            "quantity": next_quantity,
                            "avg_cost": str(guest_holding["avg_cost"]),
                        }
                    else:
                        guest_holdings.pop(str(company.id), None)
                    company.traded_volume += quantity
                    company.save(update_fields=["traded_volume", "updated_at"])
                    messages.success(request, "Venta simulada en tu sesion.")

            data["cash_balance"] = str(guest_cash)
            data["holdings"] = guest_holdings
            request.session[SESSION_MARKET_KEY] = data
            request.session.modified = True

        return redirect("market_dashboard")

    market_nickname = _get_market_nickname(request)

    return render(request, "calculadora/trade_company.html", {
        "company": company,
        "cash_balance": cash_balance,
        "owned_quantity": owned_quantity,
        "max_affordable": int(cash_balance // company.current_price) if company.current_price else 0,
        "sell_all_value": company.current_price * owned_quantity,
        "transactions": transactions,
        "updates": company.ipo_updates.prefetch_related("comments__user", "likes__user").all(),
        "comment_alias": market_nickname,
    })



