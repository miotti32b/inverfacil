from django.contrib import admin

from .models import Etapa, Opcion, Sesion, Voto


class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 1


class EtapaInline(admin.TabularInline):
    model = Etapa
    extra = 0
    show_change_link = True


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "activa", "creada")
    inlines = [EtapaInline]


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ("sesion", "orden", "titulo", "cerrada", "ganadora")
    inlines = [OpcionInline]


admin.site.register(Opcion)
admin.site.register(Voto)
