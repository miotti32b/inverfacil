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
from django.urls import path
from calculadora import views
from calculadora.views import api_endpoint

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
]


