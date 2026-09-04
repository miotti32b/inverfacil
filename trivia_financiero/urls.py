from django.urls import path

from . import views

app_name = "trivia_financiero"

urlpatterns = [
    path("panel/", views.panel, name="panel"),
    path("panel/crear/", views.panel_crear, name="panel_crear"),
    path("panel/estadisticas/", views.panel_estadisticas, name="panel_estadisticas"),
    path("panel/<str:codigo>/resultado/", views.panel_resultado, name="panel_resultado"),

    path("panel/preguntas/", views.panel_preguntas, name="panel_preguntas"),
    path("panel/preguntas/nueva/", views.panel_pregunta_form, name="panel_pregunta_nueva"),
    path("panel/preguntas/<int:pregunta_id>/editar/", views.panel_pregunta_form, name="panel_pregunta_editar"),
    path("panel/preguntas/<int:pregunta_id>/toggle/", views.panel_pregunta_toggle, name="panel_pregunta_toggle"),

    path("host/<str:codigo>/lobby/", views.host_lobby, name="host_lobby"),
    path("host/<str:codigo>/estado/", views.host_estado, name="host_estado"),
    path("host/<str:codigo>/iniciar/", views.host_iniciar_partida, name="host_iniciar_partida"),
    path("host/<str:codigo>/pregunta/iniciar/", views.host_iniciar_pregunta, name="host_iniciar_pregunta"),
    path("host/<str:codigo>/pregunta/revelar/", views.host_revelar_pregunta, name="host_revelar_pregunta"),
    path("host/<str:codigo>/pregunta/siguiente/", views.host_siguiente_pregunta, name="host_siguiente_pregunta"),

    path("j/<str:codigo>/", views.jugador_unirse, name="jugador_unirse"),
    path("j/<str:codigo>/jugar/", views.jugador_jugar, name="jugador_jugar"),
    path("j/<str:codigo>/estado/", views.jugador_estado, name="jugador_estado"),
    path("j/<str:codigo>/votar/", views.jugador_votar, name="jugador_votar"),
]
