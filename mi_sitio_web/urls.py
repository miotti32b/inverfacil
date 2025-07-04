"""
URL configuration for mi_sitio_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from calculadora import views as calculadora_views
from django.http import HttpResponse
from django.contrib.auth.models import User


def create_superuser(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='miotti322@gmail.com',
            password='TuClaveSegura123'
        )
        return HttpResponse('✅ Superusuario creado correctamente.')
    else:
        return HttpResponse('ℹ️ El usuario admin ya existe.')



from django.contrib import admin

from calculadora import views
from calculadora.views import api_endpoint
from django.urls import path, include
from calculadora.views import intro_quiz_view
from calculadora.views import elegir_alias_view
from calculadora.views import verificar_alias_redireccion_view
urlpatterns = [
    path('admin/', admin.site.urls),

    # Página principal (Home)
    path("", views.home, name="home"),

    # Calculadora y otras herramientas
    path("calculadora/", views.calculadora_interes_compuesto, name="calculadora"),
    path("carrera-rata/", views.carrera_rata_view, name="carrera_rata"),
    path("inversiones/", views.inversiones_view, name="inversiones"),

    # Juego
    path("juego/", views.start_game, name="start"),
    path("juego/game/", views.game_view, name="game"),
    path("juego/ranking/", views.ranking_view, name="ranking"),
    path("juego/guardar_puntaje/", views.guardar_puntaje, name="guardar_puntaje"),
    path("juego/instrucciones/", views.instrucciones_view, name="instrucciones"),
    path("obtener_id_jugador/", views.obtener_id_jugador, name="obtener_id_jugador"),
    path('juego/guardar_perfil/', views.guardar_perfil, name='guardar_perfil'),

    # API
    path('api/tu-endpoint/', api_endpoint, name='api-endpoint'),

    # Landing
    path('landing/', views.landing, name='landing'),
    path("juego/crear_preferencia/", views.crear_preferencia, name="crear_preferencia"),
    #quiz
    path('intro-quiz/', intro_quiz_view, name='intro_quiz'),
    path('quiz/ranking/', calculadora_views.ranking_quiz_view, name='quiz_ranking'),
    path('quiz/alias/', calculadora_views.alias_modal_view, name='alias_modal'),
    path('quiz/ranking/', calculadora_views.ranking_view, name='ranking_quiz'),
    path('accounts/', include('allauth.urls')),
    path('quiz/', calculadora_views.daily_question_view, name='daily_quiz'),
    path('create-superuser/', create_superuser),
    path('quiz/submit/', calculadora_views.submit_answer_view, name='submit_answer'),
    

    path('elegir-alias/', elegir_alias_view, name='elegir_alias'),
    

    path('verificar-alias/', verificar_alias_redireccion_view, name='verificar_alias'),


]


