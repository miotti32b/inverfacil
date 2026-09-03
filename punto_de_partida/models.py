import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


def generar_token():
    return uuid.uuid4().hex


class Partida(models.Model):
    LOBBY, EN_CURSO, FINALIZADA = "lobby", "en_curso", "finalizada"
    ESTADO_CHOICES = [(LOBBY, "Lobby"), (EN_CURSO, "En curso"), (FINALIZADA, "Finalizada")]

    RONDA_INACTIVA, RONDA_ACTIVA, RONDA_REVELADA = "inactiva", "activa", "revelada"
    RONDA_ESTADO_CHOICES = [
        (RONDA_INACTIVA, "Inactiva"),
        (RONDA_ACTIVA, "Activa"),
        (RONDA_REVELADA, "Revelada"),
    ]

    codigo = models.CharField(max_length=6, unique=True, db_index=True)
    nombre = models.CharField(max_length=120, blank=True)
    host_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="partidas_creadas"
    )
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default=LOBBY)
    ronda_actual = models.PositiveSmallIntegerField(default=0)  # 0 = lobby, 1..6 en curso
    ronda_estado = models.CharField(
        max_length=12, choices=RONDA_ESTADO_CHOICES, default=RONDA_INACTIVA
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"

    def __str__(self):
        return f"Partida {self.codigo} ({self.estado})"


class Participante(models.Model):
    INDIVIDUAL, EQUIPO = "individual", "equipo"
    TIPO_CHOICES = [(INDIVIDUAL, "Individual"), (EQUIPO, "Equipo")]

    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name="participantes")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=60)
    codigo_equipo = models.CharField(max_length=6, blank=True, default="")

    capital_inicial = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    capital_actual = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    deuda = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))

    colchon_disponible = models.BooleanField(default=False)
    colchon_usado = models.BooleanField(default=False)
    penalizacion_ronda2 = models.BooleanField(default=False)  # activada por Ronda 1 "ignorar"

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        constraints = [
            models.UniqueConstraint(fields=["partida", "nombre"], name="pdp_nombre_unico_por_partida"),
            models.UniqueConstraint(
                fields=["partida", "codigo_equipo"],
                name="pdp_codigo_equipo_unico_por_partida",
                condition=models.Q(tipo="equipo"),
            ),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    def habilidades(self):
        return list(self.miembros.exclude(habilidad="").values_list("habilidad", flat=True))


class Miembro(models.Model):
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name="miembros")
    token = models.CharField(max_length=32, unique=True, db_index=True, default=generar_token)
    nombre = models.CharField(max_length=60)

    peso_tier = models.CharField(max_length=20, blank=True, default="")
    peso_valor = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("0"))
    monto_asignado = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    habilidad = models.CharField(max_length=30, blank=True, default="")

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Miembro"
        verbose_name_plural = "Miembros"

    def __str__(self):
        return f"{self.nombre} @ {self.participante.nombre}"


class Voto(models.Model):
    miembro = models.ForeignKey(Miembro, on_delete=models.CASCADE, related_name="votos")
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name="votos")
    ronda = models.PositiveSmallIntegerField()
    opcion = models.CharField(max_length=40)
    extra = models.JSONField(default=dict, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Voto"
        verbose_name_plural = "Votos"
        constraints = [
            models.UniqueConstraint(fields=["miembro", "ronda"], name="pdp_un_voto_por_miembro_y_ronda"),
        ]

    def __str__(self):
        return f"{self.miembro.nombre} R{self.ronda}: {self.opcion}"


class HistorialCapital(models.Model):
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name="historial")
    ronda = models.PositiveSmallIntegerField()  # 0 = capital inicial
    capital = models.DecimalField(max_digits=14, decimal_places=2)
    deuda = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    detalle = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Historial de capital"
        verbose_name_plural = "Historial de capital"
        ordering = ["participante_id", "ronda"]
        constraints = [
            models.UniqueConstraint(fields=["participante", "ronda"], name="pdp_historial_unico"),
        ]

    def __str__(self):
        return f"{self.participante.nombre} R{self.ronda}: {self.capital}"
