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


import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from calculadora.services.motor_calculos import calcular_motor_financiero
from calculadora.services.resultado import construir_resultado
from calculadora.models import ClientePerfil, DiagnosticoFinanciero

@login_required(login_url="/accounts/google/login/")
def resultado_view(request):
    # Buscamos el perfil y diagnóstico del usuario logueado
    perfil = ClientePerfil.objects.filter(user=request.user).first()
    diagnostico = DiagnosticoFinanciero.objects.filter(cliente=perfil).last()
    
    # Si no tiene diagnóstico, lo mandamos a llenar el formulario
    if not perfil or not diagnostico:
        return redirect("formulario_view")

    # Calculamos el snapshot real para mandarlo a las tarjetas (KPIs) del HTML
    snapshot = calcular_motor_financiero(diagnostico)

    # Lógica de planes
    modo = "completo" 

    # Llamamos a la IA (o recuperamos el resultado guardado)
    diagnostico_financiero = perfil.diagnosticos.latest('fecha')
    resultado_ia = construir_resultado(perfil, diagnostico_financiero, permitir_ver=True)

    # ========================
    # AGREGAR ESTOS DATOS NUEVOS
    # ========================
    
    # Parsear metas y acciones de forma segura
    bloque_metas = {}
    try:
        if resultado_ia.bloque_sesgo:
            bloque_metas = json.loads(resultado_ia.bloque_sesgo)
    except (json.JSONDecodeError, TypeError):
        bloque_metas = {}
    
    acciones = {"corto_plazo": [], "mediano_plazo": [], "largo_plazo": []}
    try:
        if resultado_ia.bloque_accion:
            acciones = json.loads(resultado_ia.bloque_accion)
    except (json.JSONDecodeError, TypeError):
        acciones = {"corto_plazo": [], "mediano_plazo": [], "largo_plazo": []}
    
    # Calcular métricas principales
    margen_libertad = float(snapshot.get('ratio_libertad', 0)) * 100
    patrimonio_total = float(snapshot.get('patrimonio', 0))
    deuda_total = float(snapshot.get('deuda', 0))
    patrimonio_neto = patrimonio_total - deuda_total
    
    # Preparar proyecciones en JSON válido para JavaScript
    proy_pos_json = json.dumps(list(resultado_ia.proy_pos) if resultado_ia.proy_pos else [])
    proy_med_json = json.dumps(list(resultado_ia.proy_med) if resultado_ia.proy_med else [])
    proy_neg_json = json.dumps(list(resultado_ia.proy_neg) if resultado_ia.proy_neg else [])
    
    # ========================
    # CONTEXTO (ACTUALIZADO)
    # ========================
    contexto = {
        "modo": modo,
        "resultado": resultado_ia,
        
        # Datos originales
        "ahorro": snapshot.get("ahorro", 0),
        "tasa_ahorro": float(snapshot.get("tasa_ahorro", 0)) * 100,
        "ratio_deuda_patrimonio": snapshot.get("ratio_deuda_patrimonio", 0),
        "ingreso_por_hora": snapshot.get("ingreso_por_hora", 0),
        
        # ✨ DATOS NUEVOS PARA EL TEMPLATE MEJORADO
        "margen_libertad": round(margen_libertad, 1),
        "patrimonio_total": patrimonio_total,
        "deuda_total": deuda_total,
        "patrimonio_neto": patrimonio_neto,
        
        # Proyecciones (JSON strings para JavaScript)
        "proy_pos_json": proy_pos_json,
        "proy_med_json": proy_med_json,
        "proy_neg_json": proy_neg_json,
        
        # Metas e acciones
        "metas_info": bloque_metas if bloque_metas else None,
        "acciones": acciones,
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
    
    # Si el usuario mandó el formulario para cambiar el alias:
    if request.method == "POST":
        nuevo_alias = request.POST.get("nuevo_alias")
        if nuevo_alias:
            perfil.alias = nuevo_alias.strip()
            perfil.save(update_fields=["alias"])
            return redirect("perfil_usuario")

    cliente = DiagnosticoFinanciero.objects.filter(cliente=perfil).last()

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


# ============================================================
# Reemplazá chatbot_view y chatbot_vip_view en tu views.py
# por este bloque completo.
#
# TAMBIÉN en urls.py dejá UNA sola ruta:
#   path("chatbot/", chatbot_view, name="chatbot"),
# y eliminá la ruta chatbot_vip si la tenías.
# ============================================================

import os
import json
import tempfile

from django.http       import JsonResponse
from django.shortcuts  import render
from django.contrib.auth.decorators import login_required
from openai            import OpenAI

from calculadora.models import ClientePerfil, DiagnosticoFinanciero, ChatMensaje


# ──────────────────────────────────────────────────────────────
# CONSTANTES DE PLANES
# Plan 1 = Sin plan (visita o usuario nuevo)
# Plan 2 = Básico
# Plan 3 = Premium
# ──────────────────────────────────────────────────────────────
PLAN_SIN_PLAN = 1
PLAN_BASICO   = 2
PLAN_PREMIUM  = 3

LIMITE_SIN_PLAN = 3    # mensajes gratis totales (sesión)
LIMITE_BASICO   = 20   # mensajes por sesión en plan básico
MAX_HISTORY_BD  = 12   # cuántos mensajes previos mandamos a la IA como contexto


# ──────────────────────────────────────────────────────────────
# HELPERS INTERNOS
# ──────────────────────────────────────────────────────────────

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


def _build_user_context(perfil, diagnostico):
    """
    Arma el bloque de texto con los datos disponibles del usuario.
    Si faltan datos, lo indica de forma que la IA lo aproveche.
    """
    if not perfil:
        return "Usuario sin autenticar. No tenemos ningún dato financiero."

    lines = []

    # Datos básicos
    nombre = (
        perfil.alias
        or (perfil.user.first_name if perfil.user else None)
        or "el usuario"
    )
    lines.append(f"- Nombre/Alias: {nombre}")

    if perfil.edad:
        lines.append(f"- Edad: {perfil.edad} años")

    if perfil.hijos_a_cargo is not None:
        lines.append(f"- Personas a cargo: {perfil.hijos_a_cargo}")

    if perfil.situacion_habitacional:
        hab = "propietario" if perfil.situacion_habitacional == "propietario" else "alquila"
        lines.append(f"- Vivienda: {hab}")

    if perfil.perfil_asignado:
        lines.append(f"- Perfil inversor (IA): {perfil.perfil_asignado}")

    if perfil.quiz_score_total:
        lines.append(f"- Puntaje Quiz Financiero: {perfil.quiz_score_total} pts")

    # Datos del diagnóstico
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
                lines.append(f"- Reacción ante pérdidas: {diagnostico.reaccion_perdida}")
            if diagnostico.perfil_asignado:
                lines.append(f"- Perfil del diagnóstico: {diagnostico.perfil_asignado}")
        except Exception:
            pass

    if len(lines) <= 1:
        return (
            f"- Nombre/Alias: {nombre}\n"
            "- Sin datos financieros cargados todavía."
        )

    return "\n".join(lines)


def _build_system_prompt(plan, perfil, diagnostico):
    """
    Construye el system prompt completo adaptado al plan del usuario.
    Personalidad base compartida + sección de datos + instrucciones por plan.
    """
    user_ctx       = _build_user_context(perfil, diagnostico)
    tiene_diag     = diagnostico is not None
    tiene_perfil   = bool(perfil and (perfil.edad or perfil.situacion_habitacional))

    # ── PERSONALIDAD BASE ──────────────────────────────────────
    base = (
        "Sos 'El Oráculo', la mente financiera y sarcástica de Emiliano Miotti.\n"
        "Hablás en argentino: filoso, directo, con humor negro y jerga local "
        "(\"pichón\", \"alto clavo\", \"timba\", \"garrón\", \"no te hagas el vivo\").\n"
        "Cero bullets. Cero estructura. Párrafos cortos. Máximo 80 palabras por respuesta.\n"
        "No das consejos genéricos: usás los datos del usuario para ser específico y cortante.\n"
        "Opiniones fijas: los plazos fijos son una trampa, los planes de auto son un lujo caro, "
        "Bitcoin es el mejor seguro del siglo, y la casa propia es un gusto que sale caro.\n"
    )

    # ── DATOS DEL USUARIO ────────────────────────────────────────
    user_section = f"\nDATOS DEL USUARIO (usá estos para personalizar las respuestas):\n{user_ctx}\n"

    # Instrucción de diagnóstico si faltan datos
    if not tiene_diag and not tiene_perfil:
        user_section += (
            "\nIMPORTANTE: Este usuario no completó ningún dato todavía. "
            "Si la pregunta lo amerita, sugerile de forma sarcástica que haga el Diagnóstico IA: "
            "\"¿Cómo te ayudo sin saber ni cuánto ganás? Andá al panel y hacé el Diagnóstico IA, "
            "tardás 3 minutos y al menos sabemos de qué hablar.\"\n"
        )
    elif not tiene_diag:
        user_section += (
            "\nNOTA: Tiene datos de perfil básicos pero no hizo el Diagnóstico IA completo. "
            "Si el tema lo pide, sugerile completarlo para darte consejos más precisos.\n"
        )

    # ── INSTRUCCIONES POR PLAN ────────────────────────────────────
    if plan == PLAN_SIN_PLAN:
        plan_section = (
            "\nMODO: USUARIO SIN PLAN\n"
            "- Podés dar 1 o 2 consejos de valor real, pero al final de la conversación "
            "mencioná de forma natural (no insistente) que con el Plan Básico pueden seguir.\n"
            "- CTA: \"Si querés profundizar esto, revisá los planes en /planes/ — "
            "el Básico no rompe el bolsillo.\"\n"
            "- Si está muy perdido, derivalo al Diagnóstico IA antes que nada.\n"
        )

    elif plan == PLAN_BASICO:
        plan_section = (
            "\nMODO: PLAN BÁSICO\n"
            "- Este usuario ya pagó algo: tratalo bien, dale consejos de calidad real.\n"
            "- UNA sola vez por conversación, cuando el tema lo pida naturalmente (estrategia "
            "a largo plazo, análisis de portafolio, situación compleja), mencioná que con "
            "Premium tiene reuniones 1 a 1 y seguimiento personalizado con Emiliano.\n"
            "- CTA: \"Para armar un plan de verdad con seguimiento mensual, "
            "el Premium incluye una call directa.\"\n"
            "- No menciones upgrades en cada respuesta. Solo cuando tenga sentido.\n"
        )

    else:  # PLAN_PREMIUM
        plan_section = (
            "\nMODO: PLAN PREMIUM — CLIENTE VIP\n"
            "- Este usuario tiene acceso ilimitado, reuniones 1 a 1 y seguimiento personalizado.\n"
            "- Tratalo como a un cliente al que le cobrás en dólares la hora. "
            "Sin CTAs de venta, sin mencionar upgrades, ya está en el tope.\n"
            "- Podés profundizar más: estrategias, análisis de su situación, proyecciones.\n"
            "- Si el tema requiere análisis muy profundo de su situación completa, sugerile: "
            "\"Esto lo resolvemos mejor en una call, agendá en tu panel.\"\n"
        )

    return base + user_section + plan_section


def _check_limit(request, plan, perfil):
    """
    Verifica si el usuario superó el límite de mensajes.
    Para usuarios autenticados con plan básico/premium: cuenta mensajes en BD.
    Para no autenticados: usa sesión.
    Retorna (bloqueado: bool, mensaje: str | None)
    """
    if plan == PLAN_PREMIUM:
        return False, None

    if plan == PLAN_SIN_PLAN:
        usados = request.session.get("oraculo_usos_anonimo", 0)
        if usados >= LIMITE_SIN_PLAN:
            return True, (
                "Ya te di mis 3 consejos gratis, pichón. El resto tiene precio. "
                "Si querés seguir charlando, "
                "<a href='/planes/' style='color:#22c55e;font-weight:bold;"
                "text-decoration:underline;'>revisá los planes acá</a> "
                "— el Básico no te va a fundir."
            )
        return False, None

    # Plan Básico: contamos mensajes del usuario en esta sesión (Django session)
    usados = request.session.get("oraculo_usos_sesion", 0)
    if usados >= LIMITE_BASICO:
        return True, (
            "Llegaste al límite de mensajes de esta sesión. "
            "Para sesiones sin límite y con seguimiento personalizado, "
            "<a href='/planes/' style='color:#22c55e;font-weight:bold;"
            "text-decoration:underline;'>el Plan Premium</a> "
            "incluye una call directa con Emiliano."
        )
    return False, None


def _increment_usage(request, plan):
    """Incrementa el contador de mensajes según el plan."""
    if plan == PLAN_SIN_PLAN:
        key = "oraculo_usos_anonimo"
    elif plan == PLAN_BASICO:
        key = "oraculo_usos_sesion"
    else:
        return  # Premium: sin límite, no contamos
    request.session[key] = request.session.get(key, 0) + 1


def _get_history_from_db(perfil):
    """
    Recupera los últimos MAX_HISTORY_BD mensajes del cliente desde la BD
    y los devuelve en el formato que espera la API de OpenAI.
    """
    if not perfil:
        return []
    mensajes = (
        ChatMensaje.objects
        .filter(cliente=perfil)
        .order_by("-creado_en")[:MAX_HISTORY_BD]
    )
    # Invertimos para orden cronológico (más viejos primero)
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


# ──────────────────────────────────────────────────────────────
# VISTA PRINCIPAL
# ──────────────────────────────────────────────────────────────

def chatbot_view(request):
    """
    Vista unificada del Oráculo. Maneja:
    ✓ Plan Sin Plan  → 3 mensajes gratis (sesión) + paywall suave
    ✓ Plan Básico    → 20 mensajes/sesión, upsell sutil 1 vez
    ✓ Plan Premium   → sin límites, tono VIP, sugerencia de call
    ✓ Historial persistente en BD (solo autenticados)
    ✓ Contexto financiero personalizado (perfil + diagnóstico)
    ✓ Soporte de audio vía Whisper
    ✓ Fix XSS: el input del usuario se trata como texto plano en el frontend
    """
    if request.method != "POST":
        return render(request, "chatbot.html")

    try:
        # 1. Datos del usuario
        perfil, diagnostico = _get_perfil_y_diagnostico(request.user)
        plan = _get_plan(perfil)

        # 2. Verificar límite
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
                "reply": "¿Te comieron la lengua los ratones? Hablá que el tiempo es oro."
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

        # 7. Incrementar contador de sesión y responder
        _increment_usage(request, plan)

        return JsonResponse({"reply": respuesta_ia})

    except Exception as e:
        print(f"[Oráculo] Error: {e}")
        return JsonResponse(
            {"reply": "Se me pinchó una rueda de la Ferrari. Escribime en 5 minutos."},
            status=500,
        )
    

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from calculadora.models import ClientePerfil, ChatMensaje
 
@login_required
def chatbot_historial_view(request):
    """
    Devuelve los últimos mensajes del usuario para cargar en el modal.
    Solo GET. Usado por el frontend al abrir el chat.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)
 
    try:
        perfil = getattr(request.user, "clienteperfil", None)
        if not perfil:
            return JsonResponse({"mensajes": []})
 
        # Últimos 20 mensajes en orden cronológico
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

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

@login_required(login_url="/accounts/google/login/")
@require_http_methods(["POST"])
def solicitar_asesoria(request):
    """
    Retorna JSON para AJAX (no redirect).
    """
    try:
        perfil = request.user.clienteperfil
        
        if perfil.plan_activo != 3:
            return JsonResponse({
                "success": False,
                "error": "Solo Premium puede agendar asesoría"
            }, status=403)
        
        horario = request.POST.get("horario_preferido", "").strip()
        
        if not horario:
            return JsonResponse({
                "success": False,
                "error": "Indicá un horario preferido"
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
            "message": "✅ Solicitud registrada. Emiliano te contacta en < 24hs."
        }, status=201)
        
    except Exception as e:
        print(f"[ERROR solicitar_asesoria] {str(e)}")
        return JsonResponse({
            "success": False,
            "error": "Error interno"
        }, status=500)

# Agregar esto al final de calculadora/views.py

