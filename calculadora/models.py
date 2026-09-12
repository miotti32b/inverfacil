from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import uuid
import hashlib
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
    referral_commission_paid = models.BooleanField(default=False)

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
    codigo_anonimo = models.CharField(max_length=24, unique=True, blank=True, null=True)

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
    ingreso_emprendimiento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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
    estado_financiero = models.CharField(max_length=50, blank=True, null=True)
    estabilidad_laboral = models.CharField(max_length=50, blank=True, null=True)
    percepcion_estabilidad = models.PositiveSmallIntegerField(default=0)
    conocimiento_financiero = models.PositiveSmallIntegerField(default=0)
    confianza_sistema = models.PositiveSmallIntegerField(default=0)
    reaccion_perdida = models.CharField(max_length=100, blank=True, null=True)
    objetivos_ordenados = models.JSONField(default=list, blank=True)
    importancia_dinero = models.JSONField(default=list, blank=True)
    resultados_emprendimientos = models.JSONField(default=list, blank=True)
    limitantes_crecimiento = models.JSONField(default=list, blank=True)
    causas_estancamiento = models.JSONField(default=list, blank=True)
    resolucion_deficit = models.JSONField(default=list, blank=True)
    sesgos_sistema = models.JSONField(default=list, blank=True)
    respuestas_raw = models.JSONField(default=dict, blank=True)
    payload_codificado = models.TextField(blank=True, null=True)
    perfil_asignado = models.CharField(max_length=100, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    # =========================
    # MÉTODOS
    # =========================
    def ahorro_mensual(self):
        ingresos = (
            self.ingreso_trabajo +
            self.ingreso_negocio +
            self.ingreso_emprendimiento +
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

    def save(self, *args, **kwargs):
        if not self.codigo_anonimo:
            base = f"{self.cliente_id or 'anon'}-{uuid.uuid4().hex}"
            digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12].upper()
            self.codigo_anonimo = f"IEF-{digest}"
        super().save(*args, **kwargs)

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


class WorldDashboardSnapshot(models.Model):
    fecha = models.DateField(unique=True)
    stress_score = models.PositiveSmallIntegerField(default=50)
    stress_label = models.CharField(max_length=40, default="Vigilancia")
    category_scores = models.JSONField(default=dict, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"World snapshot {self.fecha} - {self.stress_score}"


class WorldCeoBrief(models.Model):
    fecha = models.DateField(unique=True)
    contenido = models.TextField(blank=True, default="")
    modelo = models.CharField(max_length=80, blank=True, default="")
    generado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"CEO brief {self.fecha}"


class WorldDashboardAlert(models.Model):
    OPERATORS = (
        ("gt", "Mayor que"),
        ("lt", "Menor que"),
        ("eq", "Igual a"),
        ("contains", "Contiene"),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="world_alerts")
    nombre = models.CharField(max_length=120)
    metric_key = models.CharField(max_length=80)
    operator = models.CharField(max_length=20, choices=OPERATORS, default="gt")
    threshold = models.CharField(max_length=80, blank=True, default="")
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-actualizado_en"]

    def __str__(self):
        return f"{self.usuario} - {self.nombre}"

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


# ============================================================
# WALL STREET CORDOBES - Simulador bursatil educativo
# ============================================================

class Company(models.Model):
    TECH = "TECH"
    AGRO = "AGRO"
    RETAIL = "RETAIL"
    SERVICIOS = "SERVICIOS"
    INDUSTRIA = "INDUSTRIA"
    GASTRONOMIA = "GASTRONOMIA"
    FINANZAS = "FINANZAS"
    ENTRETENIMIENTO = "ENTRETENIMIENTO"
    INMOBILIARIO = "INMOBILIARIO"

    SECTOR_CHOICES = [
        (TECH, "Tecnologia"),
        (AGRO, "Agro"),
        (RETAIL, "Retail / Consumo"),
        (SERVICIOS, "Servicios"),
        (INDUSTRIA, "Industria"),
        (GASTRONOMIA, "Gastronomia"),
        (FINANZAS, "Finanzas"),
        (ENTRETENIMIENTO, "Entretenimiento"),
        (INMOBILIARIO, "Inmobiliario"),
    ]

    QUOTE_REASON_CHOICES = [
        ("inversores", "Busco inversores"),
        ("curiosidad", "Solo curiosidad"),
        ("venta", "Quiero vender mi empresa"),
        ("competencia", "Comparacion con competencia"),
        ("expansion", "Quiero abrir nuevas unidades"),
        ("socios", "Busco socios estrategicos"),
        ("ordenar", "Quiero ordenar mis numeros"),
        ("marca", "Quiero medir mi marca"),
        ("sucesion", "Estoy pensando sucesion"),
    ]
    VISIBILITY_PRIVATE = "private"
    VISIBILITY_PUBLIC_NAMED = "public_named"
    VISIBILITY_OPEN_INVESTORS = "open_investors"
    VISIBILITY_CHOICES = [
        (VISIBILITY_PRIVATE, "Privada"),
        (VISIBILITY_PUBLIC_NAMED, "Publica con nombre"),
        (VISIBILITY_OPEN_INVESTORS, "Publica abierta a inversores"),
    ]
    MARKET_SCOPE_CHOICES = [
        ("barrial", "Barrial"),
        ("zona_norte", "Zona norte"),
        ("zona_sur", "Zona sur"),
        ("cordoba_capital", "Cordoba capital"),
        ("interior", "Interior provincial"),
        ("provincia", "Toda Cordoba"),
        ("regional", "Region centro"),
        ("nacional", "Nacional"),
        ("exportable", "Exportable"),
    ]

    name = models.CharField(max_length=120)
    ticker = models.CharField(max_length=8, blank=True, default="")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="listed_companies")
    guest_session_key = models.CharField(max_length=80, blank=True, default="")
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES)
    market_visibility = models.CharField(
        max_length=24,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PRIVATE,
    )
    is_anonymous = models.BooleanField(default=False)
    quote_reason = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )
    legal_structure = models.CharField(max_length=40, blank=True, default="")
    competitive_advantage = models.CharField(max_length=120, blank=True, default="")

    revenue = models.DecimalField(max_digits=16, decimal_places=2)
    employees = models.PositiveIntegerField(default=1)
    years_active = models.PositiveIntegerField(default=0)
    growth_rate = models.DecimalField(max_digits=6, decimal_places=4, default=Decimal("0"))
    ebitda_margin = models.DecimalField(max_digits=6, decimal_places=4, default=Decimal("0"))
    gross_margin = models.DecimalField(max_digits=6, decimal_places=4, default=Decimal("0"))
    debt_level = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    total_assets = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0"))
    active_customers = models.PositiveIntegerField(default=0)
    revenue_next_24m = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0"))
    employees_next_24m = models.PositiveIntegerField(default=0)
    active_customers_next_24m = models.PositiveIntegerField(default=0)
    market_scope_current = models.CharField(max_length=32, choices=MARKET_SCOPE_CHOICES, blank=True, default="")
    market_scope_future = models.CharField(max_length=32, choices=MARKET_SCOPE_CHOICES, blank=True, default="")
    perceived_valuation = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0"))
    perceived_valuation_reason = models.TextField(blank=True, default="")

    valuation_initial = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0"))
    valuation_low = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0"))
    valuation_high = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0"))
    previous_price = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0"))
    current_price = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0"))
    last_noise_percent = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal("0"))
    traded_volume = models.PositiveIntegerField(default=0)
    total_shares = models.PositiveIntegerField(default=10000)
    public_float_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Empresa cotizante"
        verbose_name_plural = "Empresas cotizantes"

    @property
    def display_name(self):
        if self.market_visibility == self.VISIBILITY_PRIVATE:
            return self.name
        if self.is_anonymous:
            return f"Empresa {self.get_sector_display()} Anonima #{self.id}"
        return self.name

    @property
    def is_market_public(self):
        return self.market_visibility in {
            self.VISIBILITY_PUBLIC_NAMED,
            self.VISIBILITY_OPEN_INVESTORS,
        }

    @property
    def is_open_to_investors(self):
        return self.market_visibility == self.VISIBILITY_OPEN_INVESTORS

    @property
    def variation_percent(self):
        if not self.previous_price:
            return Decimal("0")
        return ((self.current_price - self.previous_price) / self.previous_price) * Decimal("100")

    @property
    def market_cap(self):
        shares = Decimal(str(self.total_shares or 10000))
        return self.current_price * shares

    @property
    def public_shares(self):
        return int((Decimal(str(self.total_shares or 0)) * self.public_float_percent / Decimal("100")).quantize(Decimal("1")))

    @property
    def retained_shares(self):
        return max(int(self.total_shares or 0) - self.public_shares, 0)

    def save(self, *args, **kwargs):
        if not self.ticker:
            words = "".join(part[0] for part in self.name.upper().split() if part)
            self.ticker = (words or self.name[:4].upper())[:6]
        self.ticker = self.ticker.upper()[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name


class Portfolio(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="market_portfolio")
    cash_balance = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("10000000.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Portfolio {self.user} - ${self.cash_balance}"


class Transaction(models.Model):
    BUY = "BUY"
    SELL = "SELL"
    TYPE_CHOICES = [
        (BUY, "Compra"),
        (SELL, "Venta"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="market_transactions")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    price_at_transaction = models.DecimalField(max_digits=16, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    @property
    def total_amount(self):
        return self.price_at_transaction * self.quantity

    def __str__(self):
        return f"{self.get_type_display()} {self.quantity} {self.company}"


class CompanyIpoUpdate(models.Model):
    UPDATE_TYPES = [
        ("info", "Informacion relevante"),
        ("problema", "Problema detectado"),
        ("solucion", "Nueva solucion"),
        ("hito", "Hito comercial"),
        ("finanzas", "Dato financiero"),
    ]
    IMPACT_CHOICES = [
        ("positivo", "Impacto positivo"),
        ("neutral", "Impacto neutral"),
        ("negativo", "Impacto negativo"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="ipo_updates")
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES)
    impact = models.CharField(max_length=20, choices=IMPACT_CHOICES, default="neutral")
    title = models.CharField(max_length=120)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company.ticker} - {self.title}"


class CompanyIpoComment(models.Model):
    update = models.ForeignKey(CompanyIpoUpdate, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="ipo_comments")
    guest_session_key = models.CharField(max_length=80, blank=True, default="")
    alias = models.CharField(max_length=50)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.alias} en {self.update}"


class CompanyIpoLike(models.Model):
    update = models.ForeignKey(CompanyIpoUpdate, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="ipo_likes")
    guest_session_key = models.CharField(max_length=80, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.user.username if self.user else self.guest_session_key or "invitado"
        return f"MG {who} en {self.update}"


class CompanyFollow(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="followers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="followed_companies")
    guest_session_key = models.CharField(max_length=80, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.user.username if self.user else self.guest_session_key or "invitado"
        return f"{who} sigue {self.company.ticker}"


class CompanyValuationReview(models.Model):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    ANSWERED = "answered"
    SERVICE_OFFERED = "service_offered"
    CLOSED = "closed"
    STATUS_CHOICES = [
        (PENDING, "Pendiente"),
        (IN_REVIEW, "En analisis"),
        (ANSWERED, "Respondida"),
        (SERVICE_OFFERED, "Servicio ofrecido"),
        (CLOSED, "Cerrada"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="valuation_reviews")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="valuation_reviews")
    perceived_value = models.DecimalField(max_digits=16, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    internal_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Solicitud de revision de valuacion"
        verbose_name_plural = "Solicitudes de revision de valuacion"

    def __str__(self):
        return f"{self.company.ticker} - {self.get_status_display()}"


class CapitalOffering(models.Model):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    STATUS_CHOICES = [
        (DRAFT, "Borrador"),
        (OPEN, "Solicitudes abiertas"),
        (CLOSED, "Cerrada"),
    ]
    DOC_SELF_DECLARED = "self_declared"
    DOC_IN_CONVERSATION = "in_conversation"
    DOC_PENDING = "pending"
    DOC_DOCUMENTED = "documented"
    DOC_PLATFORM_VALIDATED = "platform_validated"
    DOC_THIRD_PARTY_VALIDATED = "third_party_validated"
    DOCUMENTATION_STATUS_CHOICES = [
        (DOC_SELF_DECLARED, "Autodeclarado"),
        (DOC_IN_CONVERSATION, "En conversacion"),
        (DOC_PENDING, "Documentacion pendiente"),
        (DOC_DOCUMENTED, "Documentado"),
        (DOC_PLATFORM_VALIDATED, "Validado por Cordoba Street"),
        (DOC_THIRD_PARTY_VALIDATED, "Validado por tercero"),
    ]
    INSTRUMENT_PRIVATE_CONTACT = "private_contact"
    INSTRUMENT_LEGAL_AGREEMENT = "legal_agreement"
    INSTRUMENT_SMART_CONTRACT = "smart_contract"
    INSTRUMENT_TOKENIZATION = "tokenization"
    INSTRUMENT_MILESTONE_FUNDS = "milestone_funds"
    INSTRUMENT_STAGE_CHOICES = [
        (INSTRUMENT_PRIVATE_CONTACT, "Contacto privado entre partes"),
        (INSTRUMENT_LEGAL_AGREEMENT, "Acuerdo legal"),
        (INSTRUMENT_SMART_CONTRACT, "Smart contract"),
        (INSTRUMENT_TOKENIZATION, "Tokenizacion"),
        (INSTRUMENT_MILESTONE_FUNDS, "Fondos por hitos"),
    ]

    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="capital_offering")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=DRAFT)
    documentation_status = models.CharField(
        max_length=32,
        choices=DOCUMENTATION_STATUS_CHOICES,
        default=DOC_SELF_DECLARED,
    )
    instrument_stage = models.CharField(
        max_length=32,
        choices=INSTRUMENT_STAGE_CHOICES,
        default=INSTRUMENT_PRIVATE_CONTACT,
    )
    summary = models.TextField()
    location = models.CharField(max_length=120)
    founder_name = models.CharField(max_length=120)
    public_contact = models.CharField(max_length=160)
    capital_target = models.DecimalField(max_digits=16, decimal_places=2)
    minimum_reservation = models.DecimalField(max_digits=16, decimal_places=2)
    offered_percent = models.DecimalField(max_digits=5, decimal_places=2)
    expansion_plan = models.TextField()
    use_of_funds = models.TextField()
    milestone_1 = models.CharField(max_length=240)
    milestone_2 = models.CharField(max_length=240)
    milestone_3 = models.CharField(max_length=240)
    reporting_frequency = models.CharField(max_length=120)
    information_commitment = models.TextField()
    shareholder_decisions = models.TextField()
    capital_release_terms = models.TextField()
    risks = models.TextField()
    contract_terms = models.TextField()
    contract_version = models.PositiveIntegerField(default=1)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Apertura de capital"
        verbose_name_plural = "Aperturas de capital"

    @property
    def reserved_total(self):
        return self.reservations.filter(status=CapitalReservation.ACTIVE).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0")

    @property
    def reservation_progress(self):
        if not self.capital_target:
            return Decimal("0")
        return min((self.reserved_total / self.capital_target) * Decimal("100"), Decimal("100"))

    def __str__(self):
        return f"{self.company.ticker} - {self.get_status_display()}"


class InvestorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="investor_profile")
    full_name = models.CharField(max_length=140)
    document_id = models.CharField(max_length=32)
    tax_id = models.CharField(max_length=32, blank=True, default="")
    phone = models.CharField(max_length=40)
    city = models.CharField(max_length=120)
    risk_acknowledged = models.BooleanField(default=False)
    data_consent = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Perfil inversor"
        verbose_name_plural = "Perfiles inversores"

    @property
    def is_complete(self):
        return bool(
            self.full_name
            and self.document_id
            and self.phone
            and self.city
            and self.risk_acknowledged
            and self.data_consent
        )

    def __str__(self):
        return f"{self.full_name} ({self.user})"


class CapitalReservation(models.Model):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (ACTIVE, "Activa"),
        (CANCELLED, "Cancelada"),
    ]

    offering = models.ForeignKey(CapitalOffering, on_delete=models.CASCADE, related_name="reservations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="capital_reservations")
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=ACTIVE)
    accepted_contract_version = models.PositiveIntegerField()
    accepted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-accepted_at"]
        constraints = [
            models.UniqueConstraint(fields=["offering", "user"], name="unique_user_capital_reservation"),
        ]
        verbose_name = "Solicitud de compra de acciones"
        verbose_name_plural = "Solicitudes de compra de acciones"

    def __str__(self):
        return f"{self.user} solicita comprar ${self.amount} en {self.offering.company.ticker}"


class OfferingEvidence(models.Model):
    DECLARED = "declared"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    STATUS_CHOICES = [
        (DECLARED, "Declarado"),
        (PENDING, "Pendiente de verificar"),
        (VERIFIED, "Verificado"),
        (REJECTED, "Rechazado"),
    ]
    TYPE_CHOICES = [
        ("financial", "Finanzas"),
        ("stock", "Stock"),
        ("legal", "Legal"),
        ("asset", "Activo"),
        ("contract", "Contrato"),
        ("photo", "Foto"),
        ("other", "Otro"),
    ]

    offering = models.ForeignKey(CapitalOffering, on_delete=models.CASCADE, related_name="evidences")
    evidence_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="other")
    title = models.CharField(max_length=140)
    description = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=PENDING)
    file = models.FileField(upload_to="capital_offerings/evidence/", blank=True)
    external_url = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Evidencia de apertura"
        verbose_name_plural = "Evidencias de apertura"

    def __str__(self):
        return f"{self.offering.company.ticker} - {self.title}"


class OfferingQuestion(models.Model):
    offering = models.ForeignKey(CapitalOffering, on_delete=models.CASCADE, related_name="questions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="offering_questions")
    question = models.TextField()
    answer = models.TextField(blank=True, default="")
    answered_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="answered_offering_questions")
    answered_at = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pregunta de apertura"
        verbose_name_plural = "Preguntas de apertura"

    def __str__(self):
        return f"Pregunta en {self.offering.company.ticker}"


class NaifSale(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    import_key = models.CharField(max_length=180, unique=True, null=True, blank=True)
    source_file = models.CharField(max_length=120, blank=True, default="")
    date = models.DateField(default=timezone.localdate)
    client = models.CharField(max_length=120)
    product_code = models.CharField(max_length=24, blank=True, default="")
    product_name = models.CharField(max_length=120, blank=True, default="")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    paid = models.BooleanField(default=True)
    notes = models.CharField(max_length=240, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "NAIF venta"
        verbose_name_plural = "NAIF ventas"

    def save(self, *args, **kwargs):
        self.total = (self.quantity or Decimal("0")) * (self.unit_price or Decimal("0"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.client} - ${self.total}"


class NaifProduct(models.Model):
    code = models.CharField(max_length=24, unique=True)
    name = models.CharField(max_length=120)
    suggested_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "NAIF producto"
        verbose_name_plural = "NAIF productos"

    def __str__(self):
        return self.name


class NaifClient(models.Model):
    name = models.CharField(max_length=120, unique=True)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "NAIF cliente"
        verbose_name_plural = "NAIF clientes"

    def __str__(self):
        return self.name


class NaifCostCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    active = models.BooleanField(default=True)
    show_in_metrics = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "NAIF rubro de costo"
        verbose_name_plural = "NAIF rubros de costo"

    def __str__(self):
        return self.name


class NaifCostItem(models.Model):
    category = models.ForeignKey(NaifCostCategory, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__name", "name"]
        unique_together = ("category", "name")
        verbose_name = "NAIF item de costo"
        verbose_name_plural = "NAIF items de costo"

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class NaifCost(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    import_key = models.CharField(max_length=180, unique=True, null=True, blank=True)
    source_file = models.CharField(max_length=120, blank=True, default="")
    date = models.DateField(default=timezone.localdate)
    category = models.CharField(max_length=80, blank=True, default="")
    item = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    supplier = models.CharField(max_length=120, blank=True, default="")
    paid = models.BooleanField(default=True)
    notes = models.CharField(max_length=240, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "NAIF costo"
        verbose_name_plural = "NAIF costos"

    def __str__(self):
        return f"{self.date} - {self.item} - ${self.amount}"


class RodriguezSale(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.localdate)
    client = models.CharField(max_length=120)
    product_code = models.CharField(max_length=24, blank=True, default="")
    product_name = models.CharField(max_length=120, blank=True, default="")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    paid = models.BooleanField(default=True)
    notes = models.CharField(max_length=240, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Rodriguez venta"
        verbose_name_plural = "Rodriguez ventas"

    def save(self, *args, **kwargs):
        self.total = (self.quantity or Decimal("0")) * (self.unit_price or Decimal("0"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.client} - ${self.total}"


class RodriguezProduct(models.Model):
    code = models.CharField(max_length=24, unique=True)
    name = models.CharField(max_length=120)
    suggested_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Rodriguez producto"
        verbose_name_plural = "Rodriguez productos"

    def __str__(self):
        return self.name


class RodriguezClient(models.Model):
    name = models.CharField(max_length=120, unique=True)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Rodriguez cliente"
        verbose_name_plural = "Rodriguez clientes"

    def __str__(self):
        return self.name


class RodriguezCostCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    active = models.BooleanField(default=True)
    show_in_metrics = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Rodriguez rubro de costo"
        verbose_name_plural = "Rodriguez rubros de costo"

    def __str__(self):
        return self.name


class RodriguezCostItem(models.Model):
    category = models.ForeignKey(RodriguezCostCategory, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__name", "name"]
        unique_together = ("category", "name")
        verbose_name = "Rodriguez item de costo"
        verbose_name_plural = "Rodriguez items de costo"

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class RodriguezCost(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.localdate)
    category = models.CharField(max_length=80, blank=True, default="")
    item = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    supplier = models.CharField(max_length=120, blank=True, default="")
    paid = models.BooleanField(default=True)
    notes = models.CharField(max_length=240, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Rodriguez costo"
        verbose_name_plural = "Rodriguez costos"

    def __str__(self):
        return f"{self.date} - {self.item} - ${self.amount}"


class PersonalWalletSettings(models.Model):
    display_currency = models.CharField(
        max_length=3,
        choices=[("ARS", "Pesos"), ("USD", "USD blue")],
        default="ARS",
    )
    investment_suggestion_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("5.00"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "NAIF billetera configuracion"
        verbose_name_plural = "NAIF billetera configuracion"

    def __str__(self):
        return f"Billetera en {self.display_currency}"


class PersonalExpenseCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    active = models.BooleanField(default=True)
    color = models.CharField(max_length=20, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "NAIF categoria gasto personal"
        verbose_name_plural = "NAIF categorias gasto personal"

    def __str__(self):
        return self.name


class PersonalWalletMovement(models.Model):
    EXPENSE = "expense"
    INCOME = "income"
    KIND_CHOICES = [
        (EXPENSE, "Gasto"),
        (INCOME, "Ingreso"),
    ]
    SOURCE_MANUAL = "manual"
    SOURCE_CHOICES = [
        (SOURCE_MANUAL, "Manual"),
        ("naif_profit", "Ganancia NAIF"),
    ]

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.localdate)
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=EXPENSE)
    category = models.ForeignKey(PersonalExpenseCategory, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=180, blank=True, default="")
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=80, blank=True, default="")
    notes = models.CharField(max_length=240, blank=True, default="")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "NAIF movimiento billetera"
        verbose_name_plural = "NAIF movimientos billetera"

    def __str__(self):
        return f"{self.get_kind_display()} {self.date} - ${self.amount}"


class PersonalBudget(models.Model):
    category = models.ForeignKey(PersonalExpenseCategory, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-year", "-month", "category__name"]
        unique_together = ("category", "year", "month")
        verbose_name = "NAIF presupuesto personal"
        verbose_name_plural = "NAIF presupuestos personales"

    def __str__(self):
        return f"{self.category} {self.month}/{self.year} - ${self.amount}"


class BlueDollarRate(models.Model):
    date = models.DateField(unique=True)
    buy = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sell = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    source = models.CharField(max_length=80, blank=True, default="Bluelytics")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Dolar blue historico"
        verbose_name_plural = "Dolar blue historico"

    def __str__(self):
        return f"{self.date} - {self.sell}"


# ============================================================
# EL FLETE DE DIBU - ERP LOGISTICA / MUDANZAS / FLETES
# ============================================================


class DibuVehicle(models.Model):
    TRUCK = "truck"
    PICKUP = "pickup"
    KIND_CHOICES = [(TRUCK, "Camion / Chasis"), (PICKUP, "Pickup")]

    code = models.SlugField(max_length=24, unique=True)
    name = models.CharField(max_length=80)
    plate = models.CharField(max_length=16, blank=True, default="")
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=TRUCK)
    image = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Nombre del archivo en static/calculadora/img/",
    )
    capacity_kg = models.PositiveIntegerField(default=0)
    odometer_km = models.DecimalField(max_digits=12, decimal_places=1, default=0)
    active = models.BooleanField(default=True)

    tires_last_km = models.DecimalField(max_digits=12, decimal_places=1, default=0)
    tires_interval_km = models.PositiveIntegerField(default=40000)
    belt_last_km = models.DecimalField(max_digits=12, decimal_places=1, default=0)
    belt_interval_km = models.PositiveIntegerField(default=60000)

    notes = models.CharField(max_length=240, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Dibu vehiculo"
        verbose_name_plural = "Dibu vehiculos"

    def __str__(self):
        return self.name

    def _alert_for(self, last_km, interval_km):
        """Devuelve el estado de un mantenimiento por kilometraje."""
        if not interval_km:
            return {"remaining": None, "state": "off", "due_at": None}
        due_at = Decimal(str(last_km or 0)) + Decimal(str(interval_km))
        remaining = due_at - Decimal(str(self.odometer_km or 0))
        if remaining <= 0:
            state = "due"
        elif remaining <= Decimal(str(interval_km)) * Decimal("0.1"):
            state = "soon"
        else:
            state = "ok"
        return {"remaining": remaining, "state": state, "due_at": due_at}

    @property
    def tires_alert(self):
        return self._alert_for(self.tires_last_km, self.tires_interval_km)

    @property
    def belt_alert(self):
        return self._alert_for(self.belt_last_km, self.belt_interval_km)


class DibuServiceType(models.Model):
    code = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_per_km = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Dibu tipo de servicio"
        verbose_name_plural = "Dibu tipos de servicio"

    def __str__(self):
        return self.name

    def quote_for(self, km):
        return (self.base_price or Decimal("0")) + (self.price_per_km or Decimal("0")) * Decimal(str(km or 0))


class DibuClient(models.Model):
    name = models.CharField(max_length=120, unique=True)
    phone = models.CharField(max_length=40, blank=True, default="")
    address = models.CharField(max_length=180, blank=True, default="")
    notes = models.CharField(max_length=240, blank=True, default="")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Dibu cliente"
        verbose_name_plural = "Dibu clientes"

    def __str__(self):
        return self.name


class DibuHelper(models.Model):
    name = models.CharField(max_length=120, unique=True)
    phone = models.CharField(max_length=40, blank=True, default="")
    default_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Dibu ayudante"
        verbose_name_plural = "Dibu ayudantes"

    def __str__(self):
        return self.name


class DibuTrip(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.localdate)
    client = models.CharField(max_length=120)
    client_phone = models.CharField(max_length=40, blank=True, default="")
    vehicle = models.ForeignKey(
        DibuVehicle, null=True, blank=True, on_delete=models.SET_NULL, related_name="trips"
    )
    service_code = models.CharField(max_length=32, blank=True, default="")
    service_name = models.CharField(max_length=120, blank=True, default="")
    origin = models.CharField(max_length=180, blank=True, default="")
    destination = models.CharField(max_length=180, blank=True, default="")
    km = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_per_km = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    extra = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, help_text="Peajes, escalera, piso alto, etc."
    )
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    helpers_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid = models.BooleanField(default=True)
    notes = models.CharField(max_length=240, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Dibu viaje"
        verbose_name_plural = "Dibu viajes"

    def __str__(self):
        return f"{self.date} - {self.client} - ${self.price}"

    @property
    def net(self):
        """Lo que queda del viaje despues de pagar a los ayudantes."""
        return (self.price or Decimal("0")) - (self.helpers_cost or Decimal("0"))


class DibuTripHelper(models.Model):
    trip = models.ForeignKey(DibuTrip, on_delete=models.CASCADE, related_name="helper_rows")
    helper_name = models.CharField(max_length=120)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["helper_name"]
        verbose_name = "Dibu ayudante en viaje"
        verbose_name_plural = "Dibu ayudantes en viajes"

    def __str__(self):
        return f"{self.helper_name} - ${self.fee}"


class DibuFuelLoad(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.localdate)
    vehicle = models.ForeignKey(DibuVehicle, on_delete=models.CASCADE, related_name="fuel_loads")
    liters = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    odometer_km = models.DecimalField(max_digits=12, decimal_places=1, default=0)
    station = models.CharField(max_length=120, blank=True, default="")
    full_tank = models.BooleanField(default=True, help_text="Tanque lleno: permite calcular consumo real")
    notes = models.CharField(max_length=240, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-odometer_km", "-created_at"]
        verbose_name = "Dibu carga de combustible"
        verbose_name_plural = "Dibu cargas de combustible"

    def __str__(self):
        return f"{self.date} - {self.vehicle} - {self.liters}L"

    @property
    def price_per_liter(self):
        if not self.liters:
            return Decimal("0")
        return (self.amount or Decimal("0")) / self.liters


class DibuCostCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    active = models.BooleanField(default=True)
    show_in_metrics = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Dibu rubro de costo"
        verbose_name_plural = "Dibu rubros de costo"

    def __str__(self):
        return self.name


class DibuCostItem(models.Model):
    category = models.ForeignKey(DibuCostCategory, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__name", "name"]
        unique_together = ("category", "name")
        verbose_name = "Dibu item de costo"
        verbose_name_plural = "Dibu items de costo"

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class DibuCost(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.localdate)
    vehicle = models.ForeignKey(
        DibuVehicle, null=True, blank=True, on_delete=models.SET_NULL, related_name="costs"
    )
    category = models.CharField(max_length=80, blank=True, default="")
    item = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    supplier = models.CharField(max_length=120, blank=True, default="")
    paid = models.BooleanField(default=True)
    notes = models.CharField(max_length=240, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Dibu costo"
        verbose_name_plural = "Dibu costos"

    def __str__(self):
        return f"{self.date} - {self.item} - ${self.amount}"


class DibuQuote(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.localdate)
    client = models.CharField(max_length=120)
    phone = models.CharField(max_length=40, blank=True, default="")
    service_name = models.CharField(max_length=120, blank=True, default="")
    origin = models.CharField(max_length=180, blank=True, default="")
    destination = models.CharField(max_length=180, blank=True, default="")
    km = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.CharField(max_length=240, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Dibu presupuesto"
        verbose_name_plural = "Dibu presupuestos"

    def __str__(self):
        return f"{self.date} - {self.client} - ${self.price}"


# ---------- Billetera personal de Dibu (separada de Naif / Rodriguez) ----------


class DibuWalletSettings(models.Model):
    display_currency = models.CharField(
        max_length=3,
        choices=[("ARS", "Pesos"), ("USD", "USD blue")],
        default="ARS",
    )
    investment_suggestion_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("5.00"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dibu billetera configuracion"
        verbose_name_plural = "Dibu billetera configuracion"

    def __str__(self):
        return f"Billetera Dibu en {self.display_currency}"


class DibuExpenseCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    active = models.BooleanField(default=True)
    color = models.CharField(max_length=20, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Dibu categoria gasto personal"
        verbose_name_plural = "Dibu categorias gasto personal"

    def __str__(self):
        return self.name


class DibuWalletMovement(models.Model):
    EXPENSE = "expense"
    INCOME = "income"
    KIND_CHOICES = [(EXPENSE, "Gasto"), (INCOME, "Ingreso")]
    SOURCE_MANUAL = "manual"
    SOURCE_CHOICES = [
        (SOURCE_MANUAL, "Manual"),
        ("dibu_profit", "Ganancia El Flete de Dibu"),
    ]

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.localdate)
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=EXPENSE)
    category = models.ForeignKey(DibuExpenseCategory, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=180, blank=True, default="")
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=80, blank=True, default="")
    notes = models.CharField(max_length=240, blank=True, default="")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Dibu movimiento billetera"
        verbose_name_plural = "Dibu movimientos billetera"

    def __str__(self):
        return f"{self.get_kind_display()} {self.date} - ${self.amount}"


class DibuBudget(models.Model):
    category = models.ForeignKey(DibuExpenseCategory, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-year", "-month", "category__name"]
        unique_together = ("category", "year", "month")
        verbose_name = "Dibu presupuesto personal"
        verbose_name_plural = "Dibu presupuestos personales"

    def __str__(self):
        return f"{self.category} {self.month}/{self.year} - ${self.amount}"
