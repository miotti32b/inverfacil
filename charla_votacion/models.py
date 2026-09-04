import random
import string

from django.db import models


def generar_codigo():
    alfabeto = string.ascii_uppercase.replace("O", "").replace("I", "")
    return "".join(random.choices(alfabeto + "23456789", k=4))


class Sesion(models.Model):
    codigo = models.CharField(max_length=8, unique=True, default=generar_codigo)
    nombre = models.CharField(max_length=120, default="Charla")
    activa = models.BooleanField(default=True)
    posicion_actual = models.PositiveIntegerField(default=1)
    creada = models.DateTimeField(auto_now_add=True)
    prompt_final = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    @property
    def etapa_actual(self):
        return self.etapas.filter(orden=self.posicion_actual).first()

    @property
    def terminada(self):
        return self.etapa_actual is None

    def avanzar(self):
        self.posicion_actual += 1
        self.save(update_fields=["posicion_actual"])
        if self.terminada and not self.prompt_final:
            self.generar_prompt()

    def generar_prompt(self):
        decisiones = "\n".join(
            f"- {etapa.titulo}: {etapa.ganadora.texto}"
            + (f" ({etapa.ganadora.descripcion})" if etapa.ganadora.descripcion else "")
            for etapa in self.etapas.order_by("orden")
            if etapa.ganadora
        )
        prompt = (
            "Quiero que construyas un MVP web serio y capitalizable -no un juego ni una "
            "demo infantil- basado en las siguientes decisiones de negocio, tomadas por "
            "votación en vivo para el modelo de negocio de una startup real que podría "
            "llevarse adelante de verdad:\n\n"
            f"{decisiones}\n\n"
            "Instrucciones:\n"
            "1. Combiná todas las decisiones en un solo producto coherente, aplicando el "
            "problema elegido específicamente al contexto de la industria elegida (ej. si "
            "la industria es agro y el problema es 'ineficiencia', pensá en una "
            "ineficiencia real y concreta del campo o de una empresa agropecuaria).\n"
            "2. Tratalo como el MVP de una startup real con potencial de convertirse en un "
            "proyecto genuino, no como un juguete de clase: diseño prolijo y profesional, "
            "copy serio (sin infantilizar), y una estructura de producto que un inversor "
            "-o la propia escuela- podría tomarse en serio.\n"
            "3. Incluí elementos de negocio visibles aunque sean simulados: una sección "
            "de precios o planes acorde al modelo de monetización elegido, y algún "
            "indicador de tracción (ej. usuarios activos, facturación, testimonios) que "
            "haga sentir que el producto ya está capitalizando.\n"
            "4. Mantené el alcance chico: tiene que poder construirse y mostrarse "
            "funcionando en pocos minutos, en vivo frente a la clase.\n"
            "5. Al terminar, publicalo como un Claude Artifact para verlo funcionando "
            "al instante frente a la clase.\n"
        )
        self.prompt_final = prompt
        self.save(update_fields=["prompt_final"])
        return prompt


class Etapa(models.Model):
    sesion = models.ForeignKey(Sesion, related_name="etapas", on_delete=models.CASCADE)
    orden = models.PositiveIntegerField()
    titulo = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=240, blank=True)
    cerrada = models.BooleanField(default=False)
    ganadora = models.ForeignKey(
        "Opcion", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        ordering = ["orden"]
        unique_together = ("sesion", "orden")

    def __str__(self):
        return f"{self.sesion.codigo} · Etapa {self.orden}: {self.titulo}"

    def resultados(self):
        return [
            {
                "id": opcion.id,
                "texto": opcion.texto,
                "votos": opcion.votos.count(),
            }
            for opcion in self.opciones.all()
        ]

    def cerrar_y_elegir_ganadora(self):
        ganadora = max(self.opciones.all(), key=lambda o: o.votos.count(), default=None)
        self.ganadora = ganadora
        self.cerrada = True
        self.save(update_fields=["ganadora", "cerrada"])
        return ganadora


class Opcion(models.Model):
    etapa = models.ForeignKey(Etapa, related_name="opciones", on_delete=models.CASCADE)
    texto = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.texto


class Voto(models.Model):
    etapa = models.ForeignKey(Etapa, related_name="votos_etapa", on_delete=models.CASCADE)
    opcion = models.ForeignKey(Opcion, related_name="votos", on_delete=models.CASCADE)
    dispositivo_id = models.CharField(max_length=64)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("etapa", "dispositivo_id")


class Participante(models.Model):
    sesion = models.ForeignKey(Sesion, related_name="participantes", on_delete=models.CASCADE)
    dispositivo_id = models.CharField(max_length=64)
    primera_vez = models.DateTimeField(auto_now_add=True)
    ultima_vez = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("sesion", "dispositivo_id")


class Interesado(models.Model):
    sesion = models.ForeignKey(Sesion, related_name="interesados", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=120, blank=True)
    contacto = models.CharField(max_length=200)
    comentario = models.CharField(max_length=300, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre or 'Sin nombre'} ({self.contacto})"
