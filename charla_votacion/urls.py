from django.urls import path

from . import views

app_name = "charla_votacion"

urlpatterns = [
    path("", views.unirse, name="unirse"),
    path("sesion/<str:codigo>/", views.sesion_alumno, name="sesion"),
    path("api/estado/<str:codigo>/", views.api_estado, name="api_estado"),
    path("api/votar/<str:codigo>/", views.api_votar, name="api_votar"),
    path("api/presente/<str:codigo>/", views.api_presente, name="api_presente"),
    path("api/interesado/<str:codigo>/", views.api_interesado, name="api_interesado"),
    path("presentador/<str:codigo>/", views.presentador, name="presentador"),
    path(
        "presentador/<str:codigo>/cerrar/",
        views.presentador_cerrar_etapa,
        name="cerrar_etapa",
    ),
    path(
        "presentador/<str:codigo>/siguiente/",
        views.presentador_siguiente_etapa,
        name="siguiente_etapa",
    ),
    path("panel/", views.panel, name="panel"),
    path("panel/crear/", views.panel_crear_sesion, name="panel_crear_sesion"),
    path("panel/<str:codigo>/", views.panel_resultados, name="panel_resultados"),
]
