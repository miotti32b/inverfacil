from django.urls import path

from . import views

app_name = "punto_de_partida"

urlpatterns = [
    path("host/crear/", views.host_crear_partida, name="host_crear"),
    path("host/<str:codigo>/lobby/", views.host_lobby, name="host_lobby"),
    path("host/<str:codigo>/estado/", views.host_estado, name="host_estado"),
    path("host/<str:codigo>/iniciar/", views.host_iniciar_partida, name="host_iniciar_partida"),
    path("host/<str:codigo>/ronda/iniciar/", views.host_iniciar_ronda, name="host_iniciar_ronda"),
    path("host/<str:codigo>/ronda/revelar/", views.host_revelar_ronda, name="host_revelar_ronda"),
    path("host/<str:codigo>/ronda/siguiente/", views.host_siguiente_ronda, name="host_siguiente_ronda"),
    path("host/<str:codigo>/final/", views.host_final, name="host_final"),

    path("j/<str:codigo>/", views.jugador_unirse, name="jugador_unirse"),
    path("j/<str:codigo>/jugar/", views.jugador_jugar, name="jugador_jugar"),
    path("j/<str:codigo>/estado/", views.jugador_estado, name="jugador_estado"),
    path("j/<str:codigo>/votar/", views.jugador_votar, name="jugador_votar"),
]
