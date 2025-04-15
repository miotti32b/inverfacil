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
from calculadora import views  # Importa las vistas desde la app calculadora
from calculadora.views import api_endpoint  # Asegúrate de importar la vista
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),  # Página principal de la web
    path("calculadora/", views.calculadora_interes_compuesto, name="calculadora"),
    path("carrera-rata/", views.carrera_rata_view, name="carrera_rata"),
    path("inversiones/", views.inversiones_view, name="inversiones"),

    # ✅ Ajustamos las rutas del juego correctamente
    path("juego/", views.start_game, name="start"),  # Página de inicio del juego (corregido)
    path("juego/game/", views.game_view, name="game"),  # Página del juego
    path("juego/guardar_puntaje/", views.guardar_puntaje, name="guardar_puntaje"),  # 🔥 CORREGIDO
    path("juego/ranking/", views.ranking_view, name="ranking"),
    path("obtener_id_jugador/", views.obtener_id_jugador, name="obtener_id_jugador"),
    path('api/tu-endpoint/', api_endpoint, name='api-endpoint'),
    path("juego/instrucciones/", views.instrucciones_view, name="instrucciones"),
    path('landing/', views.landing, name='landing'),
]

from django.urls import path
from calculadora import views

urlpatterns = [
    path('', views.ranking, name='home'),  # Redirecciona la raíz al ranking
    path('ranking/', views.ranking, name='ranking'),
    path('crear_preferencia/', views.crear_preferencia, name='crear_preferencia'),
]
