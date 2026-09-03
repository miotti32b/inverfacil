from django.urls import path

from . import views

app_name = "charla_votacion"

urlpatterns = [
    path("", views.unirse, name="unirse"),
    path("sesion/<str:codigo>/", views.sesion_alumno, name="sesion"),
    path("api/estado/<str:codigo>/", views.api_estado, name="api_estado"),
    path("api/votar/<str:codigo>/", views.api_votar, name="api_votar"),
    path("presentador/<str:codigo>/", views.presentador, name="presentador"),
    path(
        "presentador/<str:codigo>/siguiente/",
        views.presentador_siguiente_etapa,
        name="siguiente_etapa",
    ),
]
