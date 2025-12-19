from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth.models import User

# Importa UNA SOLA VEZ las vistas
from calculadora import views

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

    # Home
    path("", views.home, name="home"),

    # Planes (ERP + Finanzas)
    path("planeserp/", views.planeserp, name="planeserp"),
    path("planes/", views.planes_view, name="planes"),

    # Pago y suscripción
    path("iniciar-compra/<int:plan_id>/", views.iniciar_compra, name="iniciar_compra"),
    path("pago-exitoso/", views.pago_exitoso, name="pago_exitoso"),
    path("pago-cancelado/", views.pago_cancelado, name="pago_cancelado"),

    # Formulario de diagnóstico
    path("formulario/", views.formulario_view, name="formulario_view"),

    # Calculadora y herramientas
    path("calculadora/", views.calculadora_interes_compuesto, name="calculadora"),
    path("carrera-rata/", views.carrera_rata_view, name="carrera_rata"),
    path("inversiones/", views.inversiones_view, name="inversiones"),

    # Juego principal
    path("juego/", views.start_game, name="start"),
    path("juego/game/", views.game_view, name="game"),
    path("juego/ranking/", views.ranking_view, name="ranking"),
    path("juego/guardar_puntaje/", views.guardar_puntaje, name="guardar_puntaje"),
    path("juego/instrucciones/", views.instrucciones_view, name="instrucciones"),
    path("obtener_id_jugador/", views.obtener_id_jugador, name="obtener_id_jugador"),
    path("juego/guardar_perfil/", views.guardar_perfil, name="guardar_perfil"),

    # Quiz diario
    path("intro-quiz/", views.intro_quiz_view, name="intro_quiz"),
    path("quiz/", views.daily_question_view, name="daily_quiz"),
    path("quiz/submit/", views.submit_answer_view, name="submit_answer"),
    path("quiz/ranking/", views.ranking_quiz_view, name="quiz_ranking"),
    path("quiz/alias/", views.alias_modal_view, name="alias_modal"),

    # Alias post login
    path("elegir-alias/", views.elegir_alias_view, name="elegir_alias"),
    path("verificar-alias/", views.verificar_alias_redireccion_view, name="verificar_alias"),

    # Landing
    path("landing/", views.landing, name="landing"),
    path("juego/crear_preferencia/", views.crear_preferencia, name="crear_preferencia"),

    # Auth (Google Login)
    path("accounts/", include('allauth.urls')),

    # Crear superusuario rápido
    path("create-superuser/", create_superuser),

    
    path("mercadopago/webhook/", views.mercadopago_webhook, name="mercadopago_webhook"),
    
    path("mercadopago/webhook/", views.mercadopago_webhook, name="mp_webhook"),
    path("regalar/<int:plan_id>/", views.regalar_plan, name="regalar_plan"),


]
