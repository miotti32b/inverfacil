from django.conf import settings
from django.db import models
from django.utils import timezone


RANGOS = [
    {
        "slug": "basico",
        "nombre": "Basico",
        "icono": "🌱",
        "color": "#22c55e",
        "descripcion": "Ordena las bases: como funciona el dinero y tus finanzas personales.",
        "min": 1,
        "max": 2,
    },
    {
        "slug": "intermedio",
        "nombre": "Intermedio",
        "icono": "📈",
        "color": "#0ea5e9",
        "descripcion": "Metete en el mundo de las inversiones y la tecnologia cotidiana.",
        "min": 3,
        "max": 4,
    },
    {
        "slug": "avanzado",
        "nombre": "Avanzado",
        "icono": "⚙️",
        "color": "#8b5cf6",
        "descripcion": "Programacion e inteligencia artificial aplicadas a la vida real.",
        "min": 5,
        "max": 6,
    },
    {
        "slug": "experto",
        "nombre": "Experto",
        "icono": "🚀",
        "color": "#f97316",
        "descripcion": "Emprendimiento, marketing y ventas con criterio.",
        "min": 7,
        "max": 8,
    },
    {
        "slug": "legendario",
        "nombre": "Legendario",
        "icono": "👑",
        "color": "#eab308",
        "descripcion": "Automatizacion, sistemas y la integracion final de todo lo aprendido.",
        "min": 9,
        "max": 10,
    },
]


def rango_para_numero(numero):
    for rango in RANGOS:
        if rango["min"] <= numero <= rango["max"]:
            return rango
    return RANGOS[-1]


class Curso(models.Model):
    titulo = models.CharField(max_length=180)
    slug = models.SlugField(max_length=190, unique=True)
    descripcion = models.TextField()
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return self.titulo


class Modulo(models.Model):
    ESTADO_BLOQUEADO = "bloqueado"
    ESTADO_DISPONIBLE = "disponible"
    ESTADO_COMPLETADO = "completado"
    ESTADO_CHOICES = (
        (ESTADO_BLOQUEADO, "Bloqueado"),
        (ESTADO_DISPONIBLE, "Disponible"),
        (ESTADO_COMPLETADO, "Completado"),
    )

    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="modulos")
    numero = models.PositiveSmallIntegerField()
    titulo = models.CharField(max_length=180)
    objetivo = models.TextField(blank=True)
    descripcion = models.TextField()
    contenido_teorico = models.TextField()
    puntos_clave = models.TextField(
        blank=True,
        help_text="Un punto clave por linea. Se muestra como lista de repaso rapido.",
    )
    imagen_url = models.URLField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["numero"]
        unique_together = ("curso", "numero")
        verbose_name = "Modulo"
        verbose_name_plural = "Modulos"

    def __str__(self):
        return f"{self.numero}. {self.titulo}"

    @property
    def rango(self):
        return rango_para_numero(self.numero)

    @property
    def puntos_clave_lista(self):
        return [linea.strip() for linea in self.puntos_clave.splitlines() if linea.strip()]


class ImagenModulo(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="imagenes")
    titulo = models.CharField(max_length=120, blank=True)
    imagen = models.ImageField(upload_to="curso_acelerado/infografias/", blank=True, null=True)
    imagen_url = models.URLField(blank=True)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Imagen de modulo"
        verbose_name_plural = "Imagenes de modulo"

    def __str__(self):
        return self.titulo or f"Imagen modulo {self.modulo.numero}"


class PreguntaDiagnostico(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="preguntas_diagnostico")
    texto = models.TextField()
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Pregunta de diagnostico"
        verbose_name_plural = "Preguntas de diagnostico"

    def __str__(self):
        return self.texto[:80]


class OpcionDiagnostico(models.Model):
    pregunta = models.ForeignKey(PreguntaDiagnostico, on_delete=models.CASCADE, related_name="opciones")
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Opcion de diagnostico"
        verbose_name_plural = "Opciones de diagnostico"

    def __str__(self):
        return self.texto


class Quiz(models.Model):
    modulo = models.OneToOneField(Modulo, on_delete=models.CASCADE, related_name="quiz")
    titulo = models.CharField(max_length=160)
    porcentaje_aprobacion = models.PositiveSmallIntegerField(default=70)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.titulo


class Pregunta(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="preguntas")
    texto = models.TextField()
    explicacion = models.TextField(blank=True)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"

    def __str__(self):
        return self.texto[:80]


class OpcionRespuesta(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name="opciones")
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Opcion de respuesta"
        verbose_name_plural = "Opciones de respuesta"

    def __str__(self):
        return self.texto


class IntentoQuiz(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="intentos_curso")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="intentos")
    puntaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    aprobado = models.BooleanField(default=False)
    correctas = models.PositiveSmallIntegerField(default=0)
    total_preguntas = models.PositiveSmallIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Intento de quiz"
        verbose_name_plural = "Intentos de quiz"

    def __str__(self):
        estado = "aprobado" if self.aprobado else "no aprobado"
        return f"{self.usuario} - {self.quiz} - {self.puntaje}% ({estado})"


class RespuestaAlumno(models.Model):
    intento = models.ForeignKey(IntentoQuiz, on_delete=models.CASCADE, related_name="respuestas")
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion = models.ForeignKey(OpcionRespuesta, on_delete=models.CASCADE)
    es_correcta = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Respuesta de alumno"
        verbose_name_plural = "Respuestas de alumno"

    def __str__(self):
        return f"{self.intento.usuario} - {self.pregunta_id}"


class ProgresoModulo(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progresos_modulo")
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="progresos")
    estado = models.CharField(max_length=20, choices=Modulo.ESTADO_CHOICES, default=Modulo.ESTADO_BLOQUEADO)
    mejor_puntaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    intentos = models.PositiveIntegerField(default=0)
    aprobado_en = models.DateTimeField(null=True, blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("usuario", "modulo")
        verbose_name = "Progreso de modulo"
        verbose_name_plural = "Progresos de modulo"

    def marcar_completado(self, puntaje):
        self.estado = Modulo.ESTADO_COMPLETADO
        self.mejor_puntaje = max(self.mejor_puntaje, puntaje)
        self.aprobado_en = self.aprobado_en or timezone.now()
        self.save(update_fields=["estado", "mejor_puntaje", "aprobado_en", "actualizado_en"])

    def __str__(self):
        return f"{self.usuario} - {self.modulo} - {self.estado}"


class ProgresoCurso(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progresos_curso")
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="progresos")
    modulos_completados = models.PositiveSmallIntegerField(default=0)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    iniciado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("usuario", "curso")
        verbose_name = "Progreso de curso"
        verbose_name_plural = "Progresos de curso"

    def recalcular(self):
        total = self.curso.modulos.filter(activo=True).count()
        completados = ProgresoModulo.objects.filter(
            usuario=self.usuario,
            modulo__curso=self.curso,
            estado=Modulo.ESTADO_COMPLETADO,
        ).count()
        self.modulos_completados = completados
        self.porcentaje = round((completados / total) * 100, 2) if total else 0
        self.save(update_fields=["modulos_completados", "porcentaje", "actualizado_en"])

    def __str__(self):
        return f"{self.usuario} - {self.curso} - {self.porcentaje}%"

# Create your models here.
