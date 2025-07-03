import plotly.graph_objs as go
from django.shortcuts import render
import numpy as np
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


# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'calculadora/home.html')

from django.shortcuts import render

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
from .models import Question, UserScore


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
def submit_answer_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')
        used_help = data.get('used_help')
        time_taken = data.get('time_taken')

        question = get_object_or_404(Question, id=question_id)
        correct_option = question.options.filter(is_correct=True).first()

        score = max(0, 100 - int(time_taken * (100 / 60)))
        if used_help:
            score = int(score * 0.7)

        name = request.user.username if request.user.is_authenticated else data.get('name', 'Invitado')

        UserScore.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            score=score,
            date=timezone.now().date(),
            used_help=used_help,
            time_taken=time_taken
        )

        return JsonResponse({'success': True, 'score': score, 'correct': selected_option == correct_option.text})
    return JsonResponse({'success': False})


from django.shortcuts import render

def intro_quiz_view(request):
    return render(request, 'intro_quiz.html')
