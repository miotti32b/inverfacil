import plotly.graph_objs as go
from django.shortcuts import render
from calculadora.services.resultado import construir_resultado
import json

from django.db import models  # 🔥 Agrega esto
from .forms import CarreraRataForm


def carrera_rata_view(request):
    if request.method == "POST":
        form = CarreraRataForm(request.POST)
        if form.is_valid():
            carrera_rata = form.save()
            return render(request, 'calculadora/resultado.html', {'carrera_rata': carrera_rata})
    else:
        form = CarreraRataForm()
    return render(request, 'calculadora/carrerarata.html', {'form': form})


def inversiones_view(request):
    return render(request, 'calculadora/inversiones.html')



from django.shortcuts import render
from django.conf import settings
from django.contrib.sites.models import Site

def home(request):
    if settings.DEBUG:
        current_site = Site.objects.get(id=settings.SITE_ID)
        sites_list = list(Site.objects.values_list('id', 'domain'))
        print("DEBUG SITE INFO")
        print("SITE_ID usado:", settings.SITE_ID)
        print("Dominio del SITE_ID:", current_site.domain)
        print("Todos los sites:", sites_list)

    return render(request, "home.html")





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

        # Determinar el número total de períodos
        if time_period == 'daily':
            total_periods = int(time)
        elif time_period == 'weekly':
            total_periods = int(time * 7)
        elif time_period == 'monthly':
            total_periods = int(time * 365 / 12)
        else:  # yearly
            total_periods = int(time * 365)

        # Inicializar el monto total con la inversión inicial
        total_amount = principal
        total_contributions = principal

        # Ajustar la tasa de interés según su frecuencia
        if rate_period == 'daily':
            rate_per_period = rate
        elif rate_period == 'weekly':
            rate_per_period = rate / 7
        elif rate_period == 'monthly':
            rate_per_period = rate / 30
        else:  # yearly
            rate_per_period = rate / 365

        # Resultados para el gráfico
        periods = []
        contributions = []
        interests = []

        # Iterar sobre cada período total
        for period in range(1, total_periods + 1):
            # Aplicar los aportes adicionales según la frecuencia seleccionada
            if (investment_period == 'daily' and period % 1 == 0) or \
               (investment_period == 'weekly' and period % 7 == 0) or \
               (investment_period == 'monthly' and period % 30 == 0) or \
               (investment_period == 'yearly' and period % 365 == 0):
                total_amount += additional_investment
                total_contributions += additional_investment

            # Aplicar el interés compuesto
            total_amount *= (1 + rate_per_period)

            # Guardar resultados significativos (mensuales o anuales) para el gráfico
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

    # Si no es POST, renderizar formulario vacío
    return render(request, 'calculadora/calculadora.html')


import random
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
            request.session["username"] = username  # 🔥 Guarda el usuario en la sesión
            return JsonResponse({"success": True, "player_id": player.id})  

    return render(request, "calculadora/start.html")


def game_view(request):
    return render(request, "calculadora/game.html")

from django.http import JsonResponse
from .models import Player

from django.db import models  # 🔥 Agrega esto





def guardar_puntaje(request):
    if request.method == "POST":  # ✅ SOLO PERMITIMOS POST
        try:
            data = json.loads(request.body)  # 📌 Leer JSON correctamente

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
        return JsonResponse({"success": False, "error": "Método no permitido."}, status=405)  # ❌ Bloqueamos GET



from django.db.models import Count, Avg, Max



from django.shortcuts import render
from .models import Player

def ranking_view(request):
    jugadores = Player.objects.order_by('-score')[:10]  # 🔥 Top 10 jugadores
    usuario_actual = Player.objects.filter(username=request.session.get("username")).first()
    ids_top10 = {jugador.id for jugador in jugadores}  # 🔥 IDs de los top 10

    posicion_real = None
    promedio = 0

    if usuario_actual:
        # 🔥 Contar cuántos jugadores tienen un puntaje mayor
        posicion_real = Player.objects.filter(score__gt=usuario_actual.score).count() + 1
        
        # 🔥 Calcular porcentaje de jugadores superados
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
        jugador = Player.objects.latest('id')  # Obtiene el último jugador registrado
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




from django.shortcuts import render
from .models import Player  # o lo que corresponda

def ranking(request):
    jugadores = Player.objects.all().order_by('-score')[:10]  # o tu lógica
    usuario_actual = None  # buscás el usuario actual si querés
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
            player_id = data.get("player_id") or request.session.get("player_id")  # ✅ Esta es la línea clave

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
                score=0,  # Podés calcularlo y guardar si querés
                perfil_generado=perfil_nombre
            )

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

def require_login_action(request, redirect_to):
    """ Guarda la acción solicitada para después del login """
    request.session["next_url"] = redirect_to
    return redirect("login_google")


# Mostrar la pregunta del día
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.mail import send_mail
from .models import ClientePerfil, QuizParticipacion

from django.contrib.auth.models import User

@login_required
def alias_modal_view(request):
    profile = request.user.profile
    if profile.alias and profile.alias != f"usuario_{request.user.id}":
        return redirect('daily_quiz')
    
    if request.method == 'POST':
        alias = request.POST.get('alias').strip()
        if alias and not UserProfile.objects.filter(alias=alias).exists():
            profile.alias = alias
            profile.save()
            send_mail(
                '¡Bienvenido a InvertiresFácil!',
                'Gracias por unirte a InvertiresFácil, tu alias ya está activo y puedes empezar a jugar. ¡Mucha suerte!',
                'no-reply@invertiresfacil.com',
                [request.user.email],
                fail_silently=True,
            )
            return redirect('daily_quiz')
        else:
            return render(request, 'alias_modal.html', {'error': 'Alias no disponible o inválido.'})
    
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





# Mostrar la pregunta del día
def daily_question_view(request):
    today = timezone.now().date()
    question = Question.objects.filter(created_at__date=today).first()
    if not question:
        question = Question.objects.order_by('-created_at').first()
    correct_option = question.options.filter(is_correct=True).first() if question else None
    return render(request, 'daily_question.html', {
        'question': question,
        'correct_option_text': correct_option.text if correct_option else ''
    })


# Procesar la respuesta enviada por el usuario
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import QuizQuestion, QuizOption, QuizParticipacion, ClientePerfil

from django.utils import timezone


def submit_answer_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')
        used_help = data.get('used_help')
        time_taken = data.get('time_taken')
        today = timezone.now().date()

        question = get_object_or_404(Question, id=question_id)
        correct_option = question.options.filter(is_correct=True).first()

        # ✅ Restricción: Solo una participación por día
        if request.user.is_authenticated:
            if UserScore.objects.filter(user=request.user, date=today).exists():
                return JsonResponse({'success': False, 'message': 'Ya jugaste hoy, vuelve mañana 🕒'})
        else:
            guest_counter, created = GuestCounter.objects.get_or_create(id=1)
            guest_identifier = f"Invitado #{guest_counter.count}"
            if UserScore.objects.filter(alias=guest_identifier, date=today).exists():
                return JsonResponse({'success': False, 'message': 'Ya jugaste hoy como invitado, vuelve mañana 🕒'})

        # ✅ Calcular puntaje
        if selected_option == correct_option.text:
            base_score = max(10, 100 - int(time_taken * 1.5))
            if used_help:
                base_score = int(base_score * 0.7)
            score = base_score
            was_correct = True
        else:
            score = 0
            was_correct = False

        # ✅ Guardar puntaje
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            alias = user_profile.alias
            user_instance = request.user

            user_profile.games_played += 1
            if was_correct:
                user_profile.correct_answers += 1
            else:
                user_profile.incorrect_answers += 1
            user_profile.save()
        else:
            guest_counter.count += 1
            guest_counter.save()
            alias = f"Invitado #{guest_counter.count}"
            user_instance = None

        UserScore.objects.create(
            user=user_instance,
            alias=alias,
            score=score,
            date=today,
            used_help=used_help,
            time_taken=time_taken
        )

        return JsonResponse({
            'success': True,
            'score': score,
            'correct': was_correct
        })

    return JsonResponse({'success': False})


def intro_quiz_view(request):
    return render(request, 'intro_quiz.html')


from .models import QuizParticipacion

from django.shortcuts import render
from django.utils import timezone

from django.core.paginator import Paginator

def ranking_quiz_view(request):
    scores = UserScore.objects.all().order_by('-score', 'time_taken')
    paginator = Paginator(scores, 20)  # 20 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    mi_alias = None
    if request.user.is_authenticated:
        try:
            mi_alias = request.user.userprofile.alias
        except:
            mi_alias = None

    return render(request, 'rankingquiz.html', {
        'page_obj': page_obj,
        'mi_alias': mi_alias,
    })



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ClientePerfil


@login_required
def elegir_alias_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if user_profile.alias and user_profile.alias_confirmado:
        # Si ya tiene alias confirmado, no necesita elegir, lo enviamos al quiz
        return redirect('daily_quiz')

    error_message = None

    if request.method == 'POST':
        alias = request.POST.get('alias', '').strip()

        if not alias:
            error_message = "El alias no puede estar vacío."
        elif UserProfile.objects.filter(alias__iexact=alias).exists():
            error_message = "Este alias ya está en uso. Por favor, elige otro."
        else:
            user_profile.alias = alias
            user_profile.alias_confirmado = True  # 🆕 marcar como confirmado
            user_profile.save()
            return redirect('daily_quiz')

    return render(request, 'elegir_alias.html', {'error_message': error_message})


@login_required
def verificar_alias_redireccion_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
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

@login_required(login_url="/accounts/google/login/")
def formulario_view(request):
    perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # -------- PERFIL (solo lo que existe en el form) --------
        perfil.edad = int(request.POST.get("edad") or 0) or None
        perfil.hijos_a_cargo = int(request.POST.get("hijos_a_cargo") or 0)
        perfil.situacion_habitacional = request.POST.get("situacion_habitacional") or None
        perfil.save()

        # -------- DIAGNÓSTICO --------
        horas = to_decimal(request.POST.get("horas_trabajadas"))
        if horas > 20:
            horas = Decimal("20")

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

        # -------- COMPOSICIÓN (JSON) --------
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

        diagnostico.save(update_fields=["patrimonio_comp", "deuda_comp"])

        request.session["ultimo_diagnostico_id"] = diagnostico.id
        return redirect("resultado")

    return render(request, "formulario.html", {})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from calculadora.services.motor_calculos import calcular_motor_financiero
from calculadora.services.resultado import construir_resultado
from calculadora.models import ClientePerfil, DiagnosticoFinanciero

@login_required(login_url="/accounts/google/login/") # O la URL de login que uses
def resultado_view(request):
    # Buscamos el perfil y diagnóstico del usuario logueado
    perfil = ClientePerfil.objects.filter(user=request.user).first()
    diagnostico = DiagnosticoFinanciero.objects.filter(cliente=perfil).last() # <-- ESTO TE SALVA LA VIDA
    
    # Si no tiene diagnóstico, lo mandamos a llenar el formulario
    if not perfil or not diagnostico:
        return redirect("formulario_view")

    # Calculamos el snapshot real para mandarlo a las tarjetas (KPIs) del HTML
    snapshot = calcular_motor_financiero(diagnostico)

    # Lógica de planes (esto lo ajustás según tu modelo de negocio)
    modo = "completo" 

    # Llamamos a la IA (o recuperamos el resultado guardado)
    resultado_ia = construir_resultado(perfil, diagnostico, permitir_ver=True)

    # Inyectamos los datos REALES del motor al HTML
    contexto = {
        "modo": modo,
        "resultado": resultado_ia,
        # Pasamos los datos del snapshot a la vista
        "ahorro": snapshot.get("ahorro", 0),
        # Multiplicamos por 100 si la tasa viene como decimal (ej: 0.15 -> 15%)
        "tasa_ahorro": float(snapshot.get("tasa_ahorro", 0)) * 100, 
        "ratio_deuda_patrimonio": snapshot.get("ratio_deuda_patrimonio", 0),
        "ingreso_por_hora": snapshot.get("ingreso_por_hora", 0),
    }

    return render(request, "calculadora/resultadotest.html", contexto)

@login_required
def redirect_post_login(request):
    """ Decide qué hacer después del login, según el flujo del usuario. """

    next_url = request.session.pop("next_url", None)  # recuperar acción pendiente

    # 🔥 Si venía con una acción concreta → volver ahí
    if next_url:
        return redirect(next_url)

    # 🔥 Si usuario tiene perfil+plan → enviar a perfil
    perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)

    if perfil and perfil.plan_activo:
        return redirect("perfil_usuario")

    # 🔥 Si no tiene plan → llevarlo a planes
    return redirect("planes")



from django.shortcuts import redirect
from allauth.socialaccount.providers.google.views import oauth2_login

from django.conf import settings


from django.shortcuts import redirect
from django.urls import reverse

def login_google_direct(request):
    return redirect(reverse("google_login"))




# views.py
from django.http import JsonResponse
import mercadopago
from django.conf import settings

def crear_preferencia(request):
    print("🚀 Entrando a crear_preferencia")

    access_token = settings.MERCADOPAGO_ACCESS_TOKEN
    print("🔐 ACCESS TOKEN:", access_token)

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
        print("✅ Preferencia creada:", preference_response)
        return JsonResponse({ "preference_id": preference_response["response"]["id"] })
    except Exception as e:
        print("❌ Error al crear preferencia:", e)
        return JsonResponse({ "error": str(e) }, status=500)

from decimal import Decimal

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


User = get_user_model()

@login_required(login_url="/accounts/google/login/")
def iniciar_compra(request, plan_id):
    if not request.user.is_authenticated:
        return require_login_action(request, f"/iniciar-compra/{plan_id}/")
    plan = get_object_or_404(Plan, id=plan_id)

    try:
        precio = Decimal(plan.precio)
    except Exception:
        return HttpResponse("Precio inválido", status=400)

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
            "success": f"https://www.invertiresfacil.com/pago-exitoso/?plan_id={plan.id}",
            "failure": f"https://www.invertiresfacil.com/pago-cancelado/?plan_id={plan.id}",
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

    # 🔥 Si GET → abrir modal automático
    if request.method == "GET":
        request.session["open_redeem"] = True
        return redirect("planes")

    # --- POST ---
    code_input = request.POST.get("code","").strip().upper()

    try:
        promo = PromoCode.objects.select_related("plan").get(code=code_input)
    except PromoCode.DoesNotExist:
        messages.error(request,"❌ Código inválido.")
        return redirect("planes")

    if not promo.can_use():
        messages.error(request,"⚠️ Código ya utilizado o vencido.")
        return redirect("planes")

    # Crear/actualizar suscripción
    Subscripcion.objects.update_or_create(
        usuario=request.user,
        defaults={
            "plan": promo.plan,
            "estado": "active",
            "preapproval_id": promo.code,
        }
    )

    # Marcar uso del código
    promo.used_count += 1
    promo.save(update_fields=["used_count"])

    # Perfil activo
    perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
    perfil.plan_activo = promo.plan.id
    perfil.save(update_fields=["plan_activo"])

    aplicar_referido(request, request.user)

    pagar_comision(
        perfil_referido=perfil,
        monto_plan=Decimal(promo.plan.precio)
    )

    messages.success(request,f"🎉 ¡Código validado! Activaste {promo.plan.nombre}.")

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
    external_reference = response.get("external_reference")

    record = MercadoPagoPayment.objects.create(
        payment_id=payment_id,
        status=status,
        external_reference=external_reference,
        raw=response,
    )

    if status != "approved":
        return JsonResponse({"ok": True, "status": status}, status=200)

    try:
        kind, a, b = external_reference.split(":")

        if kind == "self":
            user = User.objects.get(id=int(a))
            plan = Plan.objects.get(id=int(b))

            activate_plan(
                user=user,
                plan=plan,
                source="mercadopago",
                reference=payment_id,
            )

        elif kind == "gift":
            regalo = RegaloPendiente.objects.get(id=int(a))

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


@login_required(login_url="/accounts/google/login/")
def perfil_usuario(request):
    perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
    cliente = DiagnosticoFinanciero.objects.filter(
        cliente=perfil
    ).last()

    return render(request, "perfil_usuario.html", {
        "perfil": perfil,
        "cliente": cliente,
    })



from calculadora.models import ClientePerfil

def planes_view(request):
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
    plan_id = request.GET.get("plan_id")

    if not plan_id:
        messages.error(request, "❌ No se pudo identificar el plan.")
        return redirect("planes")

    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        messages.error(request, "❌ Plan inexistente.")
        return redirect("planes")

    # Activar suscripción
    Subscripcion.objects.update_or_create(
        usuario=request.user,
        defaults={
            "plan": plan,
            "estado": "active",
        }
    )

    # Actualizar perfil
    perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
    perfil.plan_activo = plan.id
    perfil.save(update_fields=["plan_activo"])

    # 👉 Aplicar referido
    aplicar_referido(request, request.user)

    # 👉 Pagar comisión (NIVEL 1)
    pagar_comision(
        perfil_referido=perfil,
        monto_plan=Decimal(plan.precio)
    )

    messages.success(
        request,
        f"🎉 Pago exitoso. Bienvenido al {plan.nombre}."
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
        messages.error(request, "Completá todos los datos")
        return redirect("planes")

    GiftRequest.objects.create(
        comprador=request.user,
        plan=plan,
        nombre_destinatario=nombre,
        telefono_destinatario=telefono,
    )

    messages.success(
        request,
        "🎁 Regalo registrado. Te contactaremos para coordinar la entrega."
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
            messages.error(request, "Datos inválidos")
            return redirect("crear_codigos")

        plan = Plan.objects.get(id=plan_id)

        creados = []

        # buscamos el último número usado con ese prefijo
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
            f"✅ {len(creados)} códigos creados: {', '.join(creados)}"
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
        username="dev_user",
        defaults={
            "email": "dev@local.test",
            "is_staff": True,
            "is_superuser": True,
        }
    )
    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)
    return redirect("/formulario/")


import json
from django.http import JsonResponse
from django.shortcuts import render
from openai import OpenAI
import os

import os
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from openai import OpenAI

# Agregamos el login_required para asegurarnos de que sepamos qué plan tiene
@login_required
def chatbot_view(request):
    if request.method == "POST":
        try:
            # 1. LÓGICA DEL PAYWALL (LÍMITE DE MENSAJES PARA PLAN FREE)
            perfil = getattr(request.user, 'clienteperfil', None)
            # Asumimos que plan_activo == 1 es el Free/Inicial
            if perfil and perfil.plan_activo == 1:
                # Buscamos cuántos mensajes mandó hoy (se guarda en su sesión)
                mensajes_usados = request.session.get('oraculo_usos', 0)
                
                if mensajes_usados >= 3: # LÍMITE: A los 3 mensajes lo cortamos
                    mensaje_bloqueo = (
                        "Pichón, mi tiempo vale plata y ya te di demasiados consejos gratis. "
                        "Si querés seguir charlando y dejar de perder plata, "
                        "<a href='/planes/' style='color:#22c55e; font-weight:bold; text-decoration:underline;'>actualizá tu plan a Basic acá</a>. Nos vemos en las grandes ligas."
                    )
                    return JsonResponse({"reply": mensaje_bloqueo})
                
                # Si todavía le quedan, le sumamos 1 al contador invisible
                request.session['oraculo_usos'] = mensajes_usados + 1

            # 2. LÓGICA DEL MENSAJE (Si es Premium o si le quedan mensajes gratis)
            data = json.loads(request.body)
            mensaje_usuario = data.get("message", "")
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            # EL CEREBRO DEL ORÁCULO: Ahora sabe derivar tráfico
            system_prompt = """
            Sos el 'Oráculo', la mente financiera y sarcástica de Emiliano Miotti. Estás chateando por WhatsApp.
            
            REGLA DE ORO: TUS RESPUESTAS NUNCA DEBEN SUPERAR LAS 80 PALABRAS. SIN EXCEPCIONES.
            
            Cero estructura. Hablá natural, sarcástico, con humor negro y jerga argentina ("pichón", "alto clavo", "timba"). 

            CÓMO DERIVAR A LA GENTE (Ofrecé esto de forma natural y sarcástica según lo que te digan):
            1. Si están en CERO, perdidos o no saben por dónde arrancar: Mandalos a hacer el "Diagnóstico IA" que está en su panel. (Ej: "Estás más perdido que perro en cancha de bochas, andá a hacer el Diagnóstico IA primero").
            2. Si están aburridos, quieren jugar o se hacen los capos de Wall Street: Desafialos a ir al "Desafío Financiero" de la plataforma. (Ej: "Si te sobra tiempo y te creés el Lobo de Wall Street, andá a competir al Desafío Financiero").
            3. Si preguntan cosas extremadamente básicas (qué es un bono, inflación, etc): Mandalos a leer la "Guía del Dinero" que tienen disponible.

            Tu contexto: Odias los plazos fijos y los planes de auto. Preferís Bitcoin. Creés que la casa propia es un gusto caro.

            Desestructurate. Sé rápido, filoso, divertido y llevátelos a tu terreno.
            """

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": mensaje_usuario}
                ],
                max_tokens=120,
                temperature=0.85
            )

            respuesta_ia = response.choices[0].message.content
            return JsonResponse({"reply": respuesta_ia})

        except Exception as e:
            print(f"Error en el chatbot: {e}") 
            return JsonResponse({"reply": "Se me pinchó una rueda de la Ferrari, escribime en 5."}, status=500)

    return render(request, "chatbot.html")


@login_required
def chatbot_vip_view(request):
    # 1. LÓGICA DEL CHAT VIP (Sin límites de mensajes)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            mensaje_usuario = data.get("message", "")
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            # El cerebro VIP: Mantiene la personalidad, pero sabe que está en una sesión 1 a 1
            system_prompt = """
            Sos el 'Oráculo', la mente financiera y sarcástica de Emiliano Miotti. Estás en una sesión VIP 1 a 1.
            
            REGLA DE ORO: TUS RESPUESTAS NUNCA DEBEN SUPERAR LAS 80 PALABRAS. SIN EXCEPCIONES.
            
            Cero estructura. Hablá natural, sarcástico, con humor negro y jerga argentina ("pichón", "alto clavo", "timba"). 
            Al ser un usuario VIP, dale consejos un poco más profundos y directos sobre qué hacer con su plata, pero mantené tu estilo filoso.
            
            Tu contexto: Odias los plazos fijos y los planes de auto. Preferís Bitcoin. Creés que la casa propia es un gusto caro.

            Desestructurate y hacé de cuenta que le estás cobrando la hora en dólares por esta charla.
            """

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": mensaje_usuario}
                ],
                max_tokens=150,
                temperature=0.85
            )

            return JsonResponse({"reply": response.choices[0].message.content})

        except Exception as e:
            print(f"Error en el chatbot VIP: {e}") 
            return JsonResponse({"reply": "Se cortó la luz en la mansión, aguantame 5 minutos."}, status=500)

    # 2. GET: Mostrar el HTML a pantalla completa
    return render(request, "chatbot.html")