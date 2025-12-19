import plotly.graph_objs as go
from django.shortcuts import render

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



import json

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

import json
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
import json
from django.db import models  # 🔥 Agrega esto

from django.http import JsonResponse
from .models import Player
import json

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
import json
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
import json

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




# calculadora/views.py
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import ClientePerfilForm
from .models import ClientePerfil
from .utils import generar_feedback_ia  # tu función que llama a OpenAI

def _to_decimal(v):
    if v is None or v == "":
        return Decimal(0)
    try:
        # permitir "10.000,50" o "10000.50"
        s = str(v).replace(".", "").replace(",", ".")
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return Decimal(0)

def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ClientePerfil
from .forms import ClientePerfilForm
from .utils import calcular_proyecciones, generar_feedback_ia


# ============================================================
# 📋 FORMULARIO – Diagnóstico financiero automatizado
# ============================================================

@login_required
def formulario_view(request):
    """
    Formulario principal del diagnóstico financiero.
    Genera el feedback con IA y redirige al resultado visual (resultadotest.html).
    """
    if request.method == "POST":
        perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
        form = ClientePerfilForm(request.POST, instance=perfil)

        # Inicializamos por si el form falla
        cliente = perfil

        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.user = request.user
            cliente.save()
        else:
            # Solo logueamos los errores, pero no detenemos el flujo
            print("⚠️ ClientePerfilForm.errors:", form.errors.as_json())
            # Guardamos lo que se pueda
            for campo, valor in request.POST.items():
                if hasattr(perfil, campo):
                    setattr(perfil, campo, valor)
            perfil.save()

        # Guardamos diagnóstico complementario
        horas_trabajadas = request.POST.get("horas_trabajadas", 0)
        reaccion_perdida = request.POST.get("reaccion_perdida", "")

        DiagnosticoFinanciero.objects.create(
            cliente=cliente,
            horas_trabajadas=horas_trabajadas,
            reaccion_perdida=reaccion_perdida,
        )

        # Generamos feedback
        try:
            proyecciones = calcular_proyecciones(cliente)
            feedback_texto = generar_feedback_ia(cliente, proyecciones)
            cliente.ultimo_feedback = feedback_texto
            cliente.save()
        except Exception as e:
            print(f"⚠️ Error llamando a OpenAI: {e}")
            cliente.ultimo_feedback = "No pudimos generar el feedback en este momento. Intentalo más tarde."
            cliente.save()

        # ✅ Guardar ID en sesión y redirigir siempre al resultado
        request.session["ultimo_cliente_id"] = cliente.id
        return redirect("resultadotest")

    # GET
    form = ClientePerfilForm()
    return render(request, "formulario.html", {"form": form})



# ============================================================
# 💬 RESULTADO – Feedback generado por IA
# ============================================================

@login_required
def resultado_view(request):
    """
    Muestra el resultado del diagnóstico financiero: feedback IA y proyecciones.
    """
    cliente = None
    feedback_ia = None
    proyecciones = None

    cid = request.session.get("ultimo_cliente_id")
    if cid:
        try:
            cliente = ClientePerfil.objects.get(id=cid)
            feedback_ia = cliente.feedback
            proyecciones = calcular_proyecciones(cliente)
        except ClientePerfil.DoesNotExist:
            pass

    return render(request, "resultadotest.html", {
        "cliente": cliente,
        "feedback_ia": feedback_ia,
        "proyecciones": proyecciones,
    })

from decimal import Decimal
import mercadopago
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from calculadora.models import Plan


@login_required(login_url="/accounts/google/login/")
def iniciar_compra(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    # 1️⃣ Validación fuerte de precio
    try:
        precio = Decimal(plan.precio)
    except Exception:
        return HttpResponse("Precio del plan inválido", status=400)

    if precio <= 0:
        return HttpResponse("Precio del plan debe ser mayor a 0", status=400)

    unit_price = float(precio.quantize(Decimal("0.01")))

    print("🧪 PLAN:", plan.id, plan.nombre)
    print("🧪 PRECIO:", unit_price)

    try:
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        preference_data = {
            "items": [{
                "title": plan.nombre,
                "quantity": 1,
                "unit_price": unit_price,
                "currency_id": "ARS",
            }],
            "back_urls": {
                "success": "https://www.invertiresfacil.com/pago-exitoso/",
                "failure": "https://www.invertiresfacil.com/pago-cancelado/",
            },
            "auto_return": "approved",
            "external_reference": f"user_{request.user.id}_plan_{plan.id}",
        }

        preference = sdk.preference().create(preference_data)

        print("🧾 MP RESPONSE:", preference)

        if not preference or preference.get("status") != 201:
            return HttpResponse(
                f"MercadoPago error: {preference}",
                status=500
            )

        checkout_url = preference["response"].get("init_point")

        if not checkout_url:
            return HttpResponse(
                f"MercadoPago sin init_point: {preference}",
                status=500
            )

        request.session["plan_compra_id"] = plan.id
        return redirect(checkout_url)

    except Exception as e:
        print("❌ ERROR iniciar_compra:", str(e))
        return HttpResponse(
            "Error procesando el pago. Intentá nuevamente.",
            status=500
        )



# ============================================
# 🔴 3. COMPRA ace
# ============================================
@login_required
def pago_exitoso(request):
    return redirect("perfil_usuario")

# ============================================
# 🔴 3. COMPRA CANCELADA
# ============================================

@login_required(login_url="/accounts/google/login/")
def pago_cancelado(request):
    return redirect("planes")



@login_required(login_url="/accounts/google/login/")
def crear_regalo(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    if request.method == "POST":
        nombre = request.POST["nombre"]
        telefono = request.POST["telefono"]

        regalo = RegaloPendiente.objects.create(
            comprador=request.user,
            nombre_destinatario=nombre,
            telefono_destinatario=telefono,
            plan=plan
        )

        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        preference_data = {
            "items": [{
                "title": f"🎁 Regalo: {plan.nombre}",
                "quantity": 1,
                "unit_price": float(plan.precio),
                "currency_id": "ARS"
            }],
            "external_reference": f"gift_{regalo.id}",
            "notification_url": "https://www.invertiresfacil.com/mercadopago/webhook/",
            "back_urls": {
                "success": "https://www.invertiresfacil.com/planes/",
                "failure": "https://www.invertiresfacil.com/planes/"
            },
            "auto_return": "approved"
        }

        preference = sdk.preference().create(preference_data)

        return redirect(preference["response"]["init_point"])

    return redirect("planes")



import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from calculadora.models import GiftPurchase

@csrf_exempt
def mercadopago_webhook(request):
    payload = json.loads(request.body or "{}")

    payment_id = payload.get("data", {}).get("id")
    topic = payload.get("type")

    if topic != "payment":
        return HttpResponse(status=200)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    payment = sdk.payment().get(payment_id)["response"]

    if payment.get("status") != "approved":
        return HttpResponse(status=200)

    external_ref = payment.get("external_reference")

    try:
        regalo = GiftPurchase.objects.get(id=external_ref)
    except GiftPurchase.DoesNotExist:
        return HttpResponse(status=200)

    regalo.estado = "paid"
    regalo.mp_payment_id = payment_id
    regalo.save()

    # 🔜 acá va WhatsApp automático
    return HttpResponse(status=200)



@login_required(login_url="/accounts/google/login/")
def activar_regalo(request):
    regalo = RegaloPendiente.objects.filter(
        telefono_destinatario__icontains=request.user.username,
        pagado=True,
        activado=False
    ).first()

    if not regalo:
        return redirect("perfil_usuario")

    regalo.destinatario = request.user
    regalo.activado = True
    regalo.save()

    Subscripcion.objects.update_or_create(
        usuario=request.user,
        plan=regalo.plan,
        defaults={
            "preapproval_id": regalo.payment_id,
            "estado": "active"
        }
    )

    perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)
    perfil.plan_activo = regalo.plan.id
    perfil.save()

    return redirect("perfil_usuario")


import mercadopago
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from calculadora.models import Plan, GiftPurchase
from django.views.decorators.http import require_POST

@login_required(login_url="/accounts/google/login/")
@require_POST
def regalar_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    nombre = request.POST.get("nombre")
    telefono = request.POST.get("telefono")

    if not nombre or not telefono:
        return redirect("planes")

    regalo = GiftPurchase.objects.create(
        comprador=request.user,
        plan=plan,
        destinatario_nombre=nombre,
        destinatario_telefono=telefono,
    )

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": f"Regalo: {plan.nombre}",
            "quantity": 1,
            "unit_price": float(plan.precio),
            "currency_id": "ARS",
        }],
        "external_reference": str(regalo.id),
        "back_urls": {
            "success": "https://www.invertiresfacil.com/pago-exitoso/",
            "failure": "https://www.invertiresfacil.com/pago-cancelado/",
        },
        "auto_return": "approved",
        "notification_url": "https://www.invertiresfacil.com/mercadopago/webhook/",
    }

    preference = sdk.preference().create(preference_data)

    if preference.get("status") != 201:
        return HttpResponse("Error MercadoPago (regalo)", status=500)

    regalo.mp_preference_id = preference["response"]["id"]
    regalo.save()

    return redirect(preference["response"]["init_point"])




# ============================================
# 🧍‍♂️ PERFIL DEL USUARIO
# ============================================

@login_required(login_url="/accounts/google/login/")
def perfil_usuario(request):
    perfil, _ = ClientePerfil.objects.get_or_create(user=request.user)

    # Si el usuario no tiene un plan asignado → que vaya a planes
    if not perfil.plan_activo:
        return redirect("planes")

    contexto = {
        "perfil": perfil,
        "plan_id": perfil.plan_activo,

        # Finanzas
        "es_fin_incio": perfil.plan_activo == 1,
        "es_fin_intermedio": perfil.plan_activo == 2,
        "es_fin_personal": perfil.plan_activo == 3,

        # ERP
        "erp_basico": perfil.plan_activo == 4,
        "erp_intermedio": perfil.plan_activo == 5,
        "erp_avanzado": perfil.plan_activo == 6,
    }

    return render(request, "perfil_usuario.html", contexto)



# ============================================
# 🟡 5. AL CREAR PERFIL (referidos)
# ============================================

@login_required(login_url="/accounts/google/login/")
def crear_perfil_usuario(request):

    perfil, created = ClientePerfil.objects.get_or_create(user=request.user)

    if created and not perfil.referido_por:
        ref_code = request.session.get("referido_por")
        if ref_code:
            try:
                referidor = ClientePerfil.objects.get(referral_code=ref_code)
                perfil.referido_por = referidor
                referidor.total_referred += 1
                referidor.referral_earnings += Decimal("500.00")
                referidor.save()
                perfil.save()
            except ClientePerfil.DoesNotExist:
                pass

    return redirect("perfil_usuario")



# ============================================
# 🟣 6. PÁGINAS DE PLANES
# ============================================

def planeserp(request):
    return render(request, 'planeserp.html')

def planes_view(request):
    return render(request, "calculadora/planes.html")

