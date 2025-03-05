import plotly.graph_objs as go
from django.shortcuts import render
import numpy as np
from django.db import models  # 🔥 Agrega esto

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

from django.shortcuts import render
from django.db import models  # ✅ Agregamos models
from .models import Player

def ranking_view(request):
    jugadores = Player.objects.order_by("-score", "created_at")  # Ordenamos por puntaje y fecha
    promedio = Player.objects.aggregate(models.Avg("score"))["score__avg"] or 0  # ✅ Ahora models está definido correctamente

    return render(request, "calculadora/ranking.html", {"jugadores": jugadores, "promedio": promedio})


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
