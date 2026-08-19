from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth.models import User
from calculadora.views import login_google_direct
from calculadora.views import (
    # ... tus imports que ya tenés ...
    chatbot_view,
    chatbot_historial_view,
)

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

from django.conf import settings
from calculadora.views import dev_login
from calculadora.views import solicitar_asesoria
urlpatterns = [
    path('admin/', admin.site.urls),
    path("login/", login_google_direct, name="login_google"),
    path("redirect-post-login/", views.redirect_post_login, name="redirect_post_login"),

    # Home
    path("", views.home, name="home"),
    path("home-prototipo/", views.home_prototipo, name="home_prototipo"),
    path("asesor-financiero-cordoba/", views.asesor_financiero_cordoba, name="asesor_financiero_cordoba"),
    path("asesor-financiero-cnv-cordoba/", views.asesor_financiero_cordoba, name="asesor_financiero_cnv_cordoba"),
    path("agente-productor-cnv-2264/", views.asesor_financiero_cordoba, name="agente_productor_cnv_2264"),
    path("financiamiento-pyme-mercado-capitales/", views.asesor_financiero_cordoba, name="financiamiento_pyme_mercado_capitales"),
    path("voz-ia/", views.voice_clone_landing, name="voice_clone_landing"),
    path("voz-ia/generar/", views.generate_voice_clone_audio, name="generate_voice_clone_audio"),

    # Planes (ERP + Finanzas)
    path("planeserp/", views.planeserp, name="planeserp"),
    path("planes/", views.planes_view, name="planes"),
    path("curso-acelerado/", include("curso_acelerado.urls")),
    path("whatsapp/", include("whatsapp_bot.urls")),


    # Pago y suscripción
    path("iniciar-compra/<int:plan_id>/", views.iniciar_compra, name="iniciar_compra"),
    path("pago-exitoso/", views.pago_exitoso, name="pago_exitoso"),
    path("pago-cancelado/", views.pago_cancelado, name="pago_cancelado"),

    # Formulario de diagnóstico
    path("formulario/", views.formulario_view, name="formulario_view"),
    path("resultado/", views.resultado_view, name="resultado"),
    path("sugerencia/", views.sugerencia_view, name="sugerencia"),

    # Calculadora y herramientas
    path("calculadora/", views.calculadora_interes_compuesto, name="calculadora"),
    path("carrera-rata/", views.carrera_rata_view, name="carrera_rata"),
    path("carrera-rata/inmersiva/", views.carrera_rata_inmersiva_view, name="carrera_rata_inmersiva"),
    path("inversiones/", views.inversiones_view, name="inversiones"),
    path("mercado/", views.market_home, name="market_home"),
    path("mercado/cotizaciones/", views.market_dashboard, name="market_dashboard"),
    path("mercado/ceo/", views.market_ceo_dashboard, name="market_ceo_dashboard"),
    path("mercado/valuar/", views.company_valuation_view, name="company_valuation"),
    path("mercado/ipos/", views.ipo_admin_list, name="ipo_admin_list"),
    path("mercado/ipos/<int:company_id>/", views.ipo_admin_detail, name="ipo_admin_detail"),
    path("mercado/ipos/<int:company_id>/apertura/", views.capital_offering_edit, name="capital_offering_edit"),
    path("mercado/aperturas/<int:offering_id>/", views.capital_offering_detail, name="capital_offering_detail"),
    path("mercado/operar/<int:company_id>/", views.trade_company, name="trade_company"),
    path(
        "practica-importacion-lifecycle/",
        views.practica_importacion_lifecycle_view,
        name="practica_importacion_lifecycle",
    ),

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
    path("quiz/skip-login/", views.quiz_skip_login_view, name="quiz_skip_login"),

    # Alias post login
    path("elegir-alias/", views.elegir_alias_view, name="elegir_alias"),
    path("verificar-alias/", views.verificar_alias_redireccion_view, name="verificar_alias"),

    # Landing
    path("landing/", views.landing, name="landing"),
    path("andex/", views.andex_landing, name="andex_landing"),
    path("distribuidora/", views.distribuidora_portal, name="distribuidora_portal"),
    path("distribuidora/asistente-247/", views.distribuidora_asistente_247, name="distribuidora_asistente_247"),
    path("demo-erp/", views.demo_erp, name="demo_erp"),
    path("pymes/", views.pymes_naif, name="pymes_naif"),
    path("pymes/billetera/", views.naif_wallet, name="naif_wallet"),
    path("pymes/exportar/", views.pymes_naif_export, name="pymes_naif_export"),
    path("distribuidora-rodriguez/", views.distribuidora_rodriguez, name="distribuidora_rodriguez"),
    path("distribuidora-rodriguez/billetera/", views.rodriguez_wallet, name="rodriguez_wallet"),
    path("juego/crear_preferencia/", views.crear_preferencia, name="crear_preferencia"),

    # Auth (Google Login)
    path("accounts/google/login/", views.google_login_entry, name="google_login_entry"),
    path("accounts/", include('allauth.urls')),

    # Crear superusuario rápido
    path("create-superuser/", create_superuser),
    
    path("mercadopago/webhook/", views.mercadopago_webhook, name="mercadopago_webhook"),
        
    path("regalar/<int:plan_id>/", views.regalar_plan, name="regalar_plan"),
    
    path("admin/crear-codigos/", views.crear_codigos_view, name="crear_codigos"),
    
    path("canjear-codigo/", views.redeem_code, name="redeem_code"),
    path("perfil/", views.perfil_usuario, name="perfil_usuario"),
    path("perfil/world-dashboard/", views.world_dashboard, name="world_dashboard"),
    path("perfil/world-dashboard/oraculo/", views.world_dashboard_oracle, name="world_dashboard_oracle"),
    path("oraculo-demo/", views.oraculo_demo_view, name="oraculo_demo"),
    path("chatbot/", chatbot_view, name="chatbot"),
    path("chatbot/historial/", chatbot_historial_view, name="chatbot_historial"),
    # En calculadora/urls.py, agregar esta línea



    # aseso

    path('solicitar-asesoria/', solicitar_asesoria, name='solicitar_asesoria'),
    path('inscribir-curso-fintech/', views.inscribir_curso_fintech, name='inscribir_curso_fintech'),

]
if settings.DEBUG:
    urlpatterns += [
        path("dev-login/", dev_login, name="dev_login"),
    ]
