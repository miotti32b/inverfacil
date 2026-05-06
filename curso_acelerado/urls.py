from django.urls import path

from . import views


app_name = "curso_acelerado"

urlpatterns = [
    path("", views.curso_landing, name="landing"),
    path("bloqueado/", views.curso_bloqueado, name="bloqueado"),
    path("panel/", views.curso_panel, name="panel"),
    path("progreso/", views.progreso_general, name="progreso"),
    path("modulo/<int:modulo_id>/", views.modulo_detalle, name="modulo_detalle"),
    path("modulo/<int:modulo_id>/quiz/", views.quiz_view, name="quiz"),
    path("modulo/<int:modulo_id>/quiz/enviar/", views.quiz_submit, name="quiz_submit"),
    path("quiz/resultado/<int:intento_id>/", views.resultado_quiz, name="resultado_quiz"),
]
