from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import uuid
from django.utils import timezone
from django.conf import settings
# ============================================================
# 🐀 CARRERA DE LA RATA
# ============================================================

class CarreraRata(models.Model):
    patrimonio_neto = models.DecimalField(max_digits=12, decimal_places=2)
    ingreso_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    gasto_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    fuentes_ingreso = models.IntegerField()
    horas_trabajadas = models.DecimalField(max_digits=4, decimal_places=2)
    puntaje_final = models.DecimalField(max_digits=5, decimal_places=2, blank=True)

    def calcular_puntaje(self):
        rangos_pn = [500, 1500, 3000, 6500, 15000, 35000, 80000]
        rangos_im = [50, 150, 300, 500, 1000, 2000, 5000]
        rangos_gm = [50, 150, 300, 500, 1000, 2000, 5000]
        rangos_fi = [1, 2, 3, 4, 5, 6, 7]
        rangos_hl = [1, 2, 3, 4, 5, 6, 7]

        def calcular_porcentaje(valor, max_val):
            return min(float(valor) / max_val * 100, 100)

        porcentaje_pn = calcular_porcentaje(self.patrimonio_neto, max(rangos_pn))
        porcentaje_im = calcular_porcentaje(self.ingreso_mensual, max(rangos_im))
        porcentaje_gm = calcular_porcentaje(self.gasto_mensual, max(rangos_gm))
        porcentaje_fi = calcular_porcentaje(self.fuentes_ingreso, max(rangos_fi))
        porcentaje_hl = calcular_porcentaje(self.horas_trabajadas, max(rangos_hl))

        self.puntaje_final = round(
            (porcentaje_pn + porcentaje_im + porcentaje_gm + porcentaje_fi + (100 - porcentaje_hl)) / 5
        )

    def save(self, *args, **kwargs):
        self.calcular_puntaje()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Puntaje {self.puntaje_final} - PN: {self.patrimonio_neto}"


# ============================================================
# 💼 CLIENTE PERFIL – Núcleo del ecosistema
# ============================================================

class ClientePerfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    # 🔹 Datos personales
    edad = models.PositiveIntegerField(null=True, blank=True)
    # 💼 Experiencia
    experiencia_emprendimientos = models.PositiveSmallIntegerField(
        default=0,
        help_text="Nivel de experiencia en emprendimientos (0 a 10)"
)

    hijos_a_cargo = models.PositiveIntegerField(default=0)

    # 💰 Plan y accesos
    plan_activo = models.PositiveSmallIntegerField(null=True, blank=True)  # 1=Inicio,2=Medio,3=Premium
    tiene_curso = models.BooleanField(default=False)
    acceso_chatbot = models.BooleanField(default=False)
    acceso_quiz = models.BooleanField(default=True)

    # 📊 Estado general
    diagnosticos_realizados = models.PositiveIntegerField(default=0)
    quiz_score_total = models.IntegerField(default=0)
    quiz_rank = models.IntegerField(null=True, blank=True)
    total_referred = models.PositiveIntegerField(default=0)
    referral_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # 🔗 Referidos
    referral_code = models.CharField(max_length=12, unique=True, null=True, blank=True)
    referido_por = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="referidos")

    # 🧠 Feedback IA
    ultimo_feedback = models.TextField(blank=True, null=True)
    perfil_asignado = models.CharField(max_length=100, blank=True, null=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username if self.user else 'Invitado'} (Plan {self.plan_activo or '-'})"


# ============================================================
# 📋 DIAGNÓSTICO FINANCIERO (Histórico)
# ============================================================

class DiagnosticoFinanciero(models.Model):
    cliente = models.ForeignKey(ClientePerfil, on_delete=models.CASCADE, related_name="diagnosticos")
    fecha = models.DateTimeField(auto_now_add=True)
    horas_trabajadas = models.DecimalField(max_digits=4, decimal_places=1, default=0)  # ⏱️ Nuevo campo
    ingreso_trabajo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_negocio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_rentas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_inversiones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_otros = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    gasto_necesarios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_innecesarios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_financieros = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_inversiones = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    patrimonio_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    deuda_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    reaccion_perdida = models.CharField(max_length=100, blank=True, null=True)

    perfil_asignado = models.CharField(max_length=100, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def ahorro_mensual(self):
        return (
            self.ingreso_trabajo + self.ingreso_negocio + self.ingreso_rentas +
            self.ingreso_inversiones + self.ingreso_otros
        ) - (
            self.gasto_necesarios + self.gasto_innecesarios +
            self.gasto_financieros + self.gasto_inversiones
        )

    def __str__(self):
        return f"Diagnóstico {self.fecha.date()} – {self.cliente.user.username}"


# ============================================================
# PLANES PAGOS
# ============================================================
class Plan(models.Model):
    nombre = models.CharField(max_length=200)
    precio = models.IntegerField()

    def __str__(self):
        return self.nombre


class Pago(models.Model):
    ESTADOS = (
        ("pending", "Pendiente"),
        ("approved", "Aprobado"),
        ("rejected", "Rechazado"),
    )

    mp_payment_id = models.CharField(max_length=100, unique=True)
    mp_preference_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=ESTADOS)
    amount = models.IntegerField()

    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    pagador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pagos_realizados"
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pagador} - {self.plan} - {self.status}"


class PlanActivo(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planes_activos"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE)

    activo = models.BooleanField(default=True)
    asignado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.plan}"


# calculadora/models.py

from django.db import models
from django.conf import settings

class RegaloPendiente(models.Model):
    comprador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="regalos_realizados"
    )

    telefono_destinatario = models.CharField(max_length=20)
    nombre_destinatario = models.CharField(max_length=100)

    plan = models.ForeignKey("Plan", on_delete=models.CASCADE)

    payment_id = models.CharField(max_length=120, blank=True, null=True)
    pagado = models.BooleanField(default=False)

    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="regalos_recibidos"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    activado = models.BooleanField(default=False)

    def __str__(self):
        return f"🎁 {self.plan.nombre} para {self.nombre_destinatario}"


import uuid
from django.db import models
from django.conf import settings

class GiftPurchase(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("paid", "Pagado"),
        ("cancelled", "Cancelado"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    comprador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="regalos_comprados"
    )

    plan = models.ForeignKey("Plan", on_delete=models.PROTECT)

    destinatario_nombre = models.CharField(max_length=120)
    destinatario_telefono = models.CharField(max_length=20)

    mp_preference_id = models.CharField(max_length=255, blank=True, null=True)
    mp_payment_id = models.CharField(max_length=255, blank=True, null=True)

    estado = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"🎁 {self.plan.nombre} → {self.destinatario_nombre} ({self.estado})"


# core/models.py (o donde guardes modelos del checkout)
from django.db import models
from django.conf import settings

class MercadoPagoPayment(models.Model):
    payment_id = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=32, blank=True, null=True)
    external_reference = models.CharField(max_length=255, blank=True, null=True)
    raw = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    plan_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"MP {self.payment_id} {self.status}"

from django.db import models
from django.utils import timezone

class PromoCode(models.Model):
    code = models.CharField(max_length=32, unique=True)
    plan = models.ForeignKey("Plan", on_delete=models.CASCADE)
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def can_use(self):
        if not self.active:
            return False
        if self.used_count >= self.max_uses:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

    def __str__(self):
        return f"{self.code} ({self.used_count}/{self.max_uses})"




class Subscripcion(models.Model):
    ESTADO_CHOICES = (
        ("active", "Activa"),
        ("paused", "Pausada"),
        ("cancelled", "Cancelada"),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    preapproval_id = models.CharField(max_length=120, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="active")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario} - {self.plan} ({self.estado})"






# ============================================================
# 🎮 GAME / ESCENARIOS – Separar luego a app 'alkimia'
# ============================================================

class Player(models.Model):
    username = models.CharField(max_length=50)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[
        ('Hombre', 'Hombre'), ('Mujer', 'Mujer'), ('Otro', 'Otro')
    ])
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
    perfil_generado = models.CharField(max_length=100, blank=True, null=True)
    perfil_resumen = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.player.username} - {self.score} - {self.perfil_generado}"


# ============================================================
# ❓ QUIZ FINANCIERO
# ============================================================

class QuizQuestion(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correcta' if self.is_correct else 'Incorrecta'})"


class QuizParticipacion(models.Model):
    cliente = models.ForeignKey(ClientePerfil, on_delete=models.CASCADE, related_name="participaciones_quiz")
    fecha = models.DateField(auto_now_add=True)
    puntaje = models.IntegerField(default=0)
    correctas = models.IntegerField(default=0)
    usadas_ayuda = models.BooleanField(default=False)
    duracion = models.IntegerField(default=0)  # segundos

    def __str__(self):
        return f"{self.cliente.user.username} - {self.fecha} ({self.puntaje} pts)"
