import uuid

from django.conf import settings
from django.db import models


def generar_token():
    return uuid.uuid4().hex


class Pregunta(models.Model):
    FACIL, MEDIA, DIFICIL = "facil", "media", "dificil"
    DIFICULTAD_CHOICES = [(FACIL, "Fácil"), (MEDIA, "Media"), (DIFICIL, "Difícil")]

    AHORRO, DEUDA_INTERES, INVERSION_RIESGO, PRESUPUESTO, OTROS = (
        "ahorro", "deuda_interes", "inversion_riesgo", "presupuesto", "otros",
    )
    CATEGORIA_CHOICES = [
        (AHORRO, "Ahorro"),
        (DEUDA_INTERES, "Deuda e interés"),
        (INVERSION_RIESGO, "Inversión y riesgo"),
        (PRESUPUESTO, "Presupuesto"),
        (OTROS, "Otros"),
    ]

    texto = models.CharField(max_length=280)
    opciones = models.JSONField()  # lista de 4 strings
    respuesta_correcta = models.PositiveSmallIntegerField()  # índice 0-3
    explicacion = models.TextField(blank=True)
    dificultad = models.CharField(max_length=10, choices=DIFICULTAD_CHOICES)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default=OTROS)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"

    def __str__(self):
        return self.texto[:60]


class Partida(models.Model):
    LOBBY, EN_CURSO, FINALIZADA = "lobby", "en_curso", "finalizada"
    ESTADO_CHOICES = [(LOBBY, "Lobby"), (EN_CURSO, "En curso"), (FINALIZADA, "Finalizada")]

    PREGUNTA_INACTIVA, PREGUNTA_ACTIVA, PREGUNTA_REVELADA = "inactiva", "activa", "revelada"
    PREGUNTA_ESTADO_CHOICES = [
        (PREGUNTA_INACTIVA, "Inactiva"),
        (PREGUNTA_ACTIVA, "Activa"),
        (PREGUNTA_REVELADA, "Revelada"),
    ]

    codigo = models.CharField(max_length=6, unique=True, db_index=True)
    nombre = models.CharField(max_length=120, blank=True)
    colegio = models.CharField(max_length=120, blank=True)
    curso = models.CharField(max_length=60, blank=True)
    host_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trivias_creadas"
    )
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default=LOBBY)
    pregunta_actual_index = models.PositiveSmallIntegerField(default=0)
    pregunta_estado = models.CharField(
        max_length=12, choices=PREGUNTA_ESTADO_CHOICES, default=PREGUNTA_INACTIVA
    )
    pregunta_iniciada_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"

    def __str__(self):
        return f"Trivia {self.codigo} ({self.estado})"


class PartidaPregunta(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name="preguntas")
    pregunta = models.ForeignKey(Pregunta, on_delete=models.PROTECT, related_name="+")
    orden = models.PositiveSmallIntegerField()  # 0-based

    class Meta:
        verbose_name = "Pregunta de partida"
        verbose_name_plural = "Preguntas de partida"
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(fields=["partida", "orden"], name="tf_orden_unico_por_partida"),
        ]

    def __str__(self):
        return f"{self.partida.codigo} · #{self.orden}: {self.pregunta.texto[:40]}"


class Jugador(models.Model):
    INDIVIDUAL, EQUIPO = "individual", "equipo"
    TIPO_CHOICES = [(INDIVIDUAL, "Individual"), (EQUIPO, "Equipo")]

    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name="jugadores")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=60)
    codigo_equipo = models.CharField(max_length=6, blank=True, default="")
    puntaje_total = models.IntegerField(default=0)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Jugador"
        verbose_name_plural = "Jugadores"
        constraints = [
            models.UniqueConstraint(fields=["partida", "nombre"], name="tf_nombre_unico_por_partida"),
            models.UniqueConstraint(
                fields=["partida", "codigo_equipo"],
                name="tf_codigo_equipo_unico_por_partida",
                condition=models.Q(tipo="equipo"),
            ),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Miembro(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name="miembros")
    token = models.CharField(max_length=32, unique=True, db_index=True, default=generar_token)
    nombre = models.CharField(max_length=60)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Miembro"
        verbose_name_plural = "Miembros"

    def __str__(self):
        return f"{self.nombre} @ {self.jugador.nombre}"


class VotoMiembro(models.Model):
    miembro = models.ForeignKey(Miembro, on_delete=models.CASCADE, related_name="votos")
    partida_pregunta = models.ForeignKey(PartidaPregunta, on_delete=models.CASCADE, related_name="votos")
    opcion_elegida = models.PositiveSmallIntegerField(null=True, blank=True)
    tiempo_ms = models.PositiveIntegerField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Voto"
        verbose_name_plural = "Votos"
        constraints = [
            models.UniqueConstraint(
                fields=["miembro", "partida_pregunta"], name="tf_un_voto_por_miembro_y_pregunta"
            ),
        ]

    def __str__(self):
        return f"{self.miembro.nombre} · {self.partida_pregunta}: {self.opcion_elegida}"


class Respuesta(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name="respuestas")
    partida_pregunta = models.ForeignKey(PartidaPregunta, on_delete=models.CASCADE, related_name="respuestas")
    opcion_elegida = models.PositiveSmallIntegerField(null=True, blank=True)
    es_correcta = models.BooleanField(default=False)
    puntos_obtenidos = models.IntegerField(default=0)
    tiempo_ms = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"
        constraints = [
            models.UniqueConstraint(
                fields=["jugador", "partida_pregunta"], name="tf_respuesta_unica_por_jugador_y_pregunta"
            ),
        ]

    def __str__(self):
        return f"{self.jugador.nombre} · {self.partida_pregunta}: {self.puntos_obtenidos}pts"
