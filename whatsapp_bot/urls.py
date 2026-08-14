from django.urls import path

from . import views

app_name = "whatsapp_bot"

urlpatterns = [
    path("webhook/", views.webhook, name="webhook"),
    path("", views.bandeja, name="bandeja"),
    path("c/<int:contact_id>/", views.conversacion, name="conversacion"),
]
