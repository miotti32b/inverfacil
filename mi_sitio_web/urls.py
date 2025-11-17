from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth.models import User

from calculadora import views as calc_views
from calculadora import views as calculadora_views
from calculadora import views  # 👈 importa tus vistas
from calculadora.views import (
    api_endpoint,
    intro_quiz_view,
    elegir_alias_view,
    verificar_alias_redireccion_view,
)

# Endpoint rápido para crear superusuario
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

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path("", views.home, name="home"),             # tu portada actual
    
    path('planeserp/', views.planeserp, name='planeserp'),

    path("iniciar-compra/<int:plan_id>/", planes_views.iniciar_compra, name="iniciar_compra"),
    path("pago-exitoso/", planes_views.pago_exitoso, name="pago_exitoso"),
    path("pago-cancelado/", planes_views.pago_cancelado, name="pago_cancelado"),
    path("perfil/", planes_views.perfil_usuario, name="perfil_usuario"),
    path("planes/", planes_views.planes_list, name="planes")

    # Home
    path("", calculadora_views.home, name="home"),

    
    path("formulario/", calc_views.formulario_view, name="formulario_view"),

    
    path("checkout/<int:plan_id>/", calc_views.checkout, name="checkout"),
    
    
    
    
    # Calculadora y herramientas
    path("calculadora/", calculadora_views.calculadora_interes_compuesto, name="calculadora"),
    path("carrera-rata/", calculadora_views.carrera_rata_view, name="carrera_rata"),
    path("inversiones/", calculadora_views.inversiones_view, name="inversiones"),

    # Juego general
    path("juego/", calculadora_views.start_game, name="start"),
    path("juego/game/", calculadora_views.game_view, name="game"),
    path("juego/ranking/", calculadora_views.ranking_view, name="ranking"),
    path("juego/guardar_puntaje/", calculadora_views.guardar_puntaje, name="guardar_puntaje"),
    path("juego/instrucciones/", calculadora_views.instrucciones_view, name="instrucciones"),
    path("obtener_id_jugador/", calculadora_views.obtener_id_jugador, name="obtener_id_jugador"),
    path('juego/guardar_perfil/', calculadora_views.guardar_perfil, name='guardar_perfil'),

    # API
    path('api/tu-endpoint/', api_endpoint, name='api-endpoint'),

    # Landing
    path('landing/', calculadora_views.landing, name='landing'),
    path("juego/crear_preferencia/", calculadora_views.crear_preferencia, name="crear_preferencia"),

    # Quiz financiero
    path('intro-quiz/', intro_quiz_view, name='intro_quiz'),
    path('quiz/ranking/', calculadora_views.ranking_quiz_view, name='quiz_ranking'),
    path('quiz/alias/', calculadora_views.alias_modal_view, name='alias_modal'),
    path('quiz/', calculadora_views.daily_question_view, name='daily_quiz'),
    path('quiz/submit/', calculadora_views.submit_answer_view, name='submit_answer'),

    # Alias post login
    path('elegir-alias/', elegir_alias_view, name='elegir_alias'),
    path('verificar-alias/', verificar_alias_redireccion_view, name='verificar_alias'),

    # Auth
    path('accounts/', include('allauth.urls')),
    

    # Superusuario rápido
    path('create-superuser/', create_superuser),
]


