
""" carrera rata antiguo
from django.db import models

class CarreraRata(models.Model):
    patrimonio_neto = models.DecimalField(max_digits=12, decimal_places=2)
    ingreso_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    gasto_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    fuentes_ingreso = models.IntegerField()
    horas_trabajadas = models.DecimalField(max_digits=4, decimal_places=2)
    categoria_final = models.CharField(max_length=50, blank=True)

    def calcular_categoria(self):
        def asignar_categoria(valor, rangos):
            for i, rango in enumerate(rangos, start=1):
                if valor < rango:
                    return i
            return len(rangos) + 1

        # Definir los rangos para cada parámetro
        rangos_pn = [5000, 15000, 30000, 65000, 150000, 350000, 800000]
        rangos_im = [500, 1500, 3000, 5000, 10000, 20000, 50000]
        rangos_gm = [500, 1500, 3000, 5000, 10000, 20000, 50000]
        rangos_fi = [2, 3, 4, 5, 6, 7, 8]
        rangos_hl = [2, 3, 4, 5, 6, 7, 8]

        # Calcular las categorías
        categoria_pn = asignar_categoria(self.patrimonio_neto, rangos_pn)
        categoria_im = asignar_categoria(self.ingreso_mensual, rangos_im)
        categoria_gm = asignar_categoria(self.gasto_mensual, rangos_gm)
        categoria_fi = asignar_categoria(self.fuentes_ingreso, rangos_fi)
        categoria_hl = 9 - asignar_categoria(self.horas_trabajadas, rangos_hl)  # Invertir la categoría de horas trabajadas

        # Sumar todos los puntajes
        puntaje_total = categoria_pn + categoria_im + categoria_gm + categoria_fi + categoria_hl

        # Asignar una categoría final basada en el puntaje total
        if puntaje_total <= 10:
            self.categoria_final = "Rata de por vida"
        elif 11 <= puntaje_total <= 15:
            self.categoria_final = "Rata Clásica"
        elif 16 <= puntaje_total <= 20:
            self.categoria_final = "Rata Consciente"
        elif 21 <= puntaje_total <= 25:
            self.categoria_final = "Rata Inteligente"
        else:
            self.categoria_final = "Rata Dorada"

    def __str__(self):
        return f"Categoría {self.categoria_final} - PN: {self.patrimonio_neto}"

    def save(self, *args, **kwargs):
        self.calcular_categoria()
        super(CarreraRata, self).save(*args, **kwargs)
"""

from django.db import models
from decimal import Decimal

class CarreraRata(models.Model):
    patrimonio_neto = models.DecimalField(max_digits=12, decimal_places=2)
    ingreso_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    gasto_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    fuentes_ingreso = models.IntegerField()
    horas_trabajadas = models.DecimalField(max_digits=4, decimal_places=2)
    puntaje_final = models.DecimalField(max_digits=5, decimal_places=2, blank=True)

    def calcular_puntaje(self):
        # Definir los rangos para cada parámetro
        rangos_pn = [500, 1500, 3000, 6500, 15000, 35000, 80000]
        rangos_im = [50, 150, 300, 500, 1000, 2000, 5000]
        rangos_gm = [50, 150, 300, 500, 1000, 2000, 5000]
        rangos_fi = [1, 2, 3, 4, 5, 6, 7]
        rangos_hl = [1, 2, 3, 4, 5, 6, 7]

        # Función para convertir valores a un porcentaje relativo
        def calcular_porcentaje(valor, max_val):
            return min(float(valor) / max_val * 100, 100)

        # Calcular los porcentajes para cada parámetro
        porcentaje_pn = calcular_porcentaje(self.patrimonio_neto, max(rangos_pn))
        porcentaje_im = calcular_porcentaje(self.ingreso_mensual, max(rangos_im))
        porcentaje_gm = calcular_porcentaje(self.gasto_mensual, max(rangos_gm))
        porcentaje_fi = calcular_porcentaje(self.fuentes_ingreso, max(rangos_fi))
        porcentaje_hl = calcular_porcentaje(self.horas_trabajadas, max(rangos_hl))

        # Calcular el puntaje final como promedio ponderado de los porcentajes
        puntaje_total = (porcentaje_pn + porcentaje_im + porcentaje_gm + porcentaje_fi + (100 - porcentaje_hl)) / 5

        self.puntaje_final = round(puntaje_total)

    def __str__(self):
        return f"Puntaje {self.puntaje_final} - PN: {self.patrimonio_neto}"

    def save(self, *args, **kwargs):
        self.calcular_puntaje()
        super(CarreraRata, self).save(*args, **kwargs)

from django.db import models

class ClientePerfil(models.Model):
    # Bloque 1 – Datos básicos
    edad = models.IntegerField()
    estado_civil = models.CharField(max_length=50)
    hijos_a_cargo = models.IntegerField(default=0)

    # Bloque 2 – Situación financiera
    ingreso_trabajo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_negocio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_rentas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_inversiones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_otros = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    gasto_necesarios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_innecesarios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_financieros = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_inversiones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    

    patrimonio_vivienda = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patrimonio_vehiculos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patrimonio_ahorros_local = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patrimonio_ahorros_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patrimonio_inversiones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patrimonio_negocio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patrimonio_otros = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    deuda_tarjeta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deuda_auto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deuda_casa = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deuda_financiera = models.DecimalField(max_digits=12, decimal_places=2, default=0)


    # Bloque 3 – Objetivos
    objetivos = models.JSONField()  # guardamos hasta 3 seleccionados
    plazo_inversion = models.CharField(max_length=20)

    # Bloque 4 – Perfil psicológico y conocimientos
    reaccion_perdida = models.CharField(max_length=50)
    importancia_dinero = models.JSONField()  # puede marcar 2
    uso_millon = models.JSONField()  # puede marcar 2
    conocimiento_acciones = models.CharField(max_length=100)
    conocimiento_seguridad = models.JSONField()  # puede marcar 2

    # Bloque 5 – Preferencias
    liquidez = models.CharField(max_length=20)

    # Resultado del análisis
    perfil_asignado = models.CharField(max_length=50, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil Cliente {self.id} - Edad {self.edad}"


class Player(models.Model):
    username = models.CharField(max_length=50)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Hombre', 'Hombre'), ('Mujer', 'Mujer'), ('Otro', 'Otro')])
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username






class Scenario(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    age = models.IntegerField()
    family_status = models.CharField(max_length=100)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    debts = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.title

# models.py
class PlayerResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    vehicle_percentage = models.IntegerField()
    property_percentage = models.IntegerField()
    education_percentage = models.IntegerField()
    investment_percentage = models.IntegerField()
    business_percentage = models.IntegerField()
    leisure_percentage = models.IntegerField()
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 🔥 Nuevos campos
    perfil_generado = models.CharField(max_length=100, blank=True, null=True)
    perfil_resumen = models.TextField(blank=True, null=True)  # para la descripción

    def __str__(self):
        return f"{self.player.username} - {self.score} - {self.perfil_generado}"




# QUIZ PREGUNTAS
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alias = models.CharField(max_length=50, unique=True)
    alias_confirmado = models.BooleanField(default=False)  # 🆕 nuevo campo
    games_played = models.IntegerField(default=0)  # 🆕 partidas jugadas
    correct_answers = models.IntegerField(default=0)  # 🆕 aciertos
    incorrect_answers = models.IntegerField(default=0)  # 🆕 errores
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alias} ({self.user.email})"

class UserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    alias = models.CharField(max_length=50, null=True, blank=True)  # 🆕 Para registrar alias o 'Invitado #N'
    score = models.IntegerField()
    date = models.DateField(default=timezone.now)
    used_help = models.BooleanField(default=False)
    time_taken = models.IntegerField(help_text="En segundos")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        alias = self.alias
        if alias:
            alias_to_use = alias
        elif self.user is not None and hasattr(self.user, 'username'):
            alias_to_use = self.user.username
        else:
            alias_to_use = 'Invitado'
        return f"{alias_to_use} - {self.score} puntos en {self.date}"






from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, alias=f"usuario_{instance.id}")


from django.db import models

class Question(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correcta' if self.is_correct else 'Incorrecta'})"

class GuestCounter(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"GuestCounter: {self.count}"