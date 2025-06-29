from django.contrib import admin
from .models import CarreraRata

# Register your models here.
admin.site.register(CarreraRata)


from django.contrib import admin
from .models import Player, PlayerResult, Scenario, Question, Option  # importa tus modelos

admin.site.register(Player)
admin.site.register(PlayerResult)
admin.site.register(Scenario)

admin.site.register(Question)
admin.site.register(Option)
