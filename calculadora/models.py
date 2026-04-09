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
SITUACION_HAB_CHOICES = [
    ("propietario", "Casa propia"),
    ("alquila", "Alquila"),
]

class ClientePerfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    alias = models.CharField(max_length=50, blank=True, null=True)
    edad = models.PositiveIntegerField(null=True, blank=True)

    experiencia_emprendimientos = models.PositiveSmallIntegerField(
        default=0,
        help_text="Nivel de experiencia en emprendimientos (0 a 10)"
    )

    hijos_a_cargo = models.PositiveIntegerField(default=0)

    situacion_habitacional = models.CharField(
        max_length=20,
        choices=SITUACION_HAB_CHOICES,
        null=True,
        blank=True,
    )
    objetivos = models.JSONField(default=list, blank=True)
    # 💰 Plan y accesos
    plan_activo = models.PositiveSmallIntegerField(default=1, null=True, blank=True)
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
    referido_por = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referidos"
    )

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
from django.db import models
# ajustá el import si tu estructura difiere


class DiagnosticoFinanciero(models.Model):
    # =========================
    # RELACIÓN
    # =========================
    cliente = models.ForeignKey(
        ClientePerfil,
        on_delete=models.CASCADE,
        related_name="diagnosticos"
    )

    fecha = models.DateTimeField(auto_now_add=True)

    # =========================
    # TIEMPO
    # =========================
    horas_trabajadas = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text="Horas trabajadas por día"
    )

    # =========================
    # INGRESOS
    # =========================
    ingreso_trabajo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_negocio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_rentas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_inversiones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_otros = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # =========================
    # GASTOS
    # =========================
    gasto_necesarios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_innecesarios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_financieros = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_inversiones = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # =========================
    # PATRIMONIO (AGREGADO)
    # =========================
    patrimonio_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    deuda_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    # =========================
    # PATRIMONIO (DETALLE)
    # =========================
    patrimonio_comp = models.JSONField(default=dict, blank=True)
    deuda_comp = models.JSONField(default=dict, blank=True)

    # =========================
    # COMPORTAMIENTO / PERFIL
    # =========================
    reaccion_perdida = models.CharField(max_length=100, blank=True, null=True)
    perfil_asignado = models.CharField(max_length=100, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    # =========================
    # MÉTODOS
    # =========================
    def ahorro_mensual(self):
        ingresos = (
            self.ingreso_trabajo +
            self.ingreso_negocio +
            self.ingreso_rentas +
            self.ingreso_inversiones +
            self.ingreso_otros
        )

        gastos = (
            self.gasto_necesarios +
            self.gasto_innecesarios +
            self.gasto_financieros +
            self.gasto_inversiones
        )

        return ingresos - gastos

    def __str__(self):
        return f"Diagnóstico {self.fecha.date()} – {self.cliente.user.username}"



from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class ResultadoIA(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(
        max_length=20,
        default="pending"
    )

    tokens_usados = models.IntegerField(
        default=0
    )

    costo_estimado_usd = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=0
    )

    error_msg = models.TextField(
        blank=True,
        default=""
    )



    input_hash = models.CharField(max_length=64)
    modelo_ia = models.CharField(max_length=50)
    contenido = models.TextField(default="", blank=True)
    bloque_diagnostico = models.TextField(default="", blank=True)
    bloque_estructura = models.TextField(default="")
    bloque_sesgo = models.TextField(default="")
    bloque_proyeccion = models.TextField(default="")
    bloque_accion = models.TextField(default="")
    bloque_cierre = models.TextField(default="")

    proy_pos = models.JSONField(default=list)
    proy_med = models.JSONField(default=list)
    proy_neg = models.JSONField(default=list)

    creado_en = models.DateTimeField(default=timezone.now)
    # Control asíncrono
    
    

    esta_bloqueado = models.BooleanField(default=True)

    class Meta:
        unique_together = ("usuario", "input_hash")


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

CATEGORIA_CHOICES = [
    ('acciones',              '📈 Acciones'),
    ('matematica_financiera', '🧮 Matemática Financiera'),
    ('fci_etf',               '📊 FCI o ETF'),
    ('internacional',         '🌍 Internacional'),
    ('argentina',             '🇦🇷 Argentina'),
    ('fintech',               '💡 Fintech'),
]
 
class QuizQuestion(models.Model):
    text      = models.CharField(max_length=500)
    categoria = models.CharField(
        max_length=30,
        choices=CATEGORIA_CHOICES,
        default='acciones',
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.text[:60]}"

class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correcta' if self.is_correct else 'Incorrecta'})"


class QuizParticipacion(models.Model):
    cliente = models.ForeignKey(ClientePerfil, on_delete=models.CASCADE, related_name="participaciones_quiz", null=True, blank=True)
    guest_alias = models.CharField(max_length=20, blank=True, default='')
    fecha = models.DateField(auto_now_add=True)
    puntaje = models.IntegerField(default=0)
    correctas = models.IntegerField(default=0)
    usadas_ayuda = models.BooleanField(default=False)
    duracion = models.IntegerField(default=0)  # segundos

    def __str__(self):
        who = self.cliente.user.username if self.cliente else self.guest_alias or 'invitado'
        return f"{who} - {self.fecha} ({self.puntaje} pts)"


class GiftRequest(models.Model):
    comprador = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey("Plan", on_delete=models.CASCADE)
    nombre_destinatario = models.CharField(max_length=100)
    telefono_destinatario = models.CharField(max_length=20)
    mensaje = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"🎁 {self.nombre_destinatario} ({self.plan.nombre})"


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist

@receiver(post_save, sender=User, dispatch_uid="crear_perfil_unico_uid")
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        # get_or_create evita que el servidor colapse si la señal se dispara dos veces
        ClientePerfil.objects.get_or_create(user=instance)

@receiver(post_save, sender=User, dispatch_uid="guardar_perfil_unico_uid")
def guardar_perfil_usuario(sender, instance, **kwargs):
    try:
        instance.clienteperfil.save()
    except ObjectDoesNotExist:
        pass



# ============================================================
# Agregá este bloque al final de tu calculadora/models.py
# ============================================================

class ChatMensaje(models.Model):
    """
    Historial persistente de conversaciones con el Oráculo.
    Cada fila es un mensaje (user o assistant).
    """
    ROLES = [
        ("user",      "Usuario"),
        ("assistant", "Oráculo"),
    ]

    cliente   = models.ForeignKey(
        ClientePerfil,
        on_delete=models.CASCADE,
        related_name="chat_mensajes"
    )
    role      = models.CharField(max_length=10, choices=ROLES)
    content   = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado_en"]   # orden cronológico siempre

    def __str__(self):
        return f"[{self.role}] {self.cliente} – {self.creado_en:%Y-%m-%d %H:%M}"


class SolicitudAsesoria(models.Model):
    """
    Registro de solicitudes de reunión 1 a 1.
    Solo para usuarios Premium (plan_activo == 3).
    """
    cliente           = models.ForeignKey(
        ClientePerfil,
        on_delete=models.CASCADE,
        related_name="solicitudes_asesoria"
    )
    # Datos tomados automáticamente del usuario — sin fricción
    nombre            = models.CharField(max_length=100)
    email             = models.EmailField()
    horario_preferido = models.CharField(max_length=100, blank=True)

    atendida          = models.BooleanField(default=False)
    creado_en         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        estado = "✅" if self.atendida else "⏳"
        return f"{estado} {self.nombre} — {self.creado_en:%d/%m/%Y %H:%M}"


# ============================================================
# 🎓 CURSO FINTECH – Inscripciones
# ============================================================

class InscripcionCursoFintech(models.Model):
    MESES_CHOICES = [
        ("mayo",       "Mayo 2025"),
        ("junio",      "Junio 2025"),
        ("julio",      "Julio 2025"),
        ("agosto",     "Agosto 2025"),
        ("septiembre", "Septiembre 2025"),
    ]

    cliente   = models.ForeignKey(
        ClientePerfil,
        on_delete=models.CASCADE,
        related_name="inscripciones_curso_fintech"
    )
    nombre    = models.CharField(max_length=100)
    email     = models.EmailField()
    edad      = models.PositiveSmallIntegerField()
    mes_elegido = models.CharField(max_length=20, choices=MESES_CHOICES)

    atendida  = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        estado = "✅" if self.atendida else "⏳"
        return f"{estado} {self.nombre} — {self.get_mes_elegido_display()} — {self.creado_en:%d/%m/%Y %H:%M}"
    