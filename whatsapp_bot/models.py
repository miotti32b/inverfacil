from django.db import models

from calculadora.models import ClientePerfil


class Contact(models.Model):
    ESTADO_NUEVO = "nuevo"
    ESTADO_INTERESADO = "interesado"
    ESTADO_CLIENTE = "cliente"
    ESTADO_DESCARTADO = "descartado"
    ESTADO_CHOICES = [
        (ESTADO_NUEVO, "Nuevo"),
        (ESTADO_INTERESADO, "Interesado"),
        (ESTADO_CLIENTE, "Cliente"),
        (ESTADO_DESCARTADO, "Descartado"),
    ]

    wa_id = models.CharField(
        max_length=32,
        unique=True,
        help_text="Número de teléfono en formato WhatsApp (sin '+', ej. 51987654321)",
    )
    nombre_perfil = models.CharField(
        max_length=150,
        blank=True,
        help_text="Nombre que reporta WhatsApp para este contacto",
    )
    cliente_perfil = models.ForeignKey(
        ClientePerfil,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contactos_whatsapp",
        help_text="Vínculo manual con el perfil de cliente del sitio (opcional)",
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_NUEVO)
    creado_en = models.DateTimeField(auto_now_add=True)
    ultimo_mensaje_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-ultimo_mensaje_en", "-creado_en"]

    def __str__(self):
        return self.nombre_perfil or self.wa_id

    @property
    def hizo_diagnostico(self):
        if not self.cliente_perfil_id:
            return False
        return self.cliente_perfil.diagnosticos.exists()


class Message(models.Model):
    DIRECCION_ENTRANTE = "in"
    DIRECCION_SALIENTE = "out"
    DIRECCION_CHOICES = [
        (DIRECCION_ENTRANTE, "Entrante"),
        (DIRECCION_SALIENTE, "Saliente"),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="mensajes")
    direccion = models.CharField(max_length=3, choices=DIRECCION_CHOICES)
    cuerpo = models.TextField(blank=True)
    wa_message_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    es_automatico = models.BooleanField(default=False)
    error_detalle = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado_en"]

    def __str__(self):
        return f"{self.get_direccion_display()} · {self.contact} · {self.creado_en:%Y-%m-%d %H:%M}"


class AutoReplyRule(models.Model):
    palabra_clave = models.CharField(
        max_length=100,
        blank=True,
        help_text="Se dispara si el mensaje entrante CONTIENE este texto (sin mayúsculas/minúsculas). Vacío si es la regla de respaldo.",
    )
    respuesta = models.TextField()
    activo = models.BooleanField(default=True)
    prioridad = models.PositiveIntegerField(
        default=0, help_text="Se evalúan de menor a mayor; la primera que matchee gana."
    )
    es_fallback = models.BooleanField(
        default=False,
        help_text="Se usa cuando ningún otro palabra clave matchea. Solo debería haber una activa.",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["prioridad", "id"]

    def __str__(self):
        return self.palabra_clave if self.palabra_clave else "(fallback)"


class BroadcastCampaign(models.Model):
    ESTADO_BORRADOR = "borrador"
    ESTADO_ENVIANDO = "enviando"
    ESTADO_ENVIADO = "enviado"
    ESTADO_ERROR = "error"
    ESTADO_CHOICES = [
        (ESTADO_BORRADOR, "Borrador"),
        (ESTADO_ENVIANDO, "Enviando"),
        (ESTADO_ENVIADO, "Enviado"),
        (ESTADO_ERROR, "Con errores"),
    ]

    nombre = models.CharField(max_length=150)
    template_name = models.CharField(
        max_length=150,
        help_text="Debe coincidir exactamente con una plantilla ya APROBADA en Meta",
    )
    template_language = models.CharField(max_length=10, default="es")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_BORRADOR)
    estado_objetivo = models.CharField(
        max_length=20,
        choices=Contact.ESTADO_CHOICES,
        blank=True,
        help_text="Filtra los contactos a los que se les envía por su estado. Vacío = todos.",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    enviado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return self.nombre

    def contactos_objetivo(self):
        qs = Contact.objects.all()
        if self.estado_objetivo:
            qs = qs.filter(estado=self.estado_objetivo)
        return qs


class CampaignRecipient(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_ENVIADO = "enviado"
    ESTADO_ERROR = "error"
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_ENVIADO, "Enviado"),
        (ESTADO_ERROR, "Error"),
    ]

    campaign = models.ForeignKey(BroadcastCampaign, on_delete=models.CASCADE, related_name="destinatarios")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="campanas_recibidas")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    wa_message_id = models.CharField(max_length=100, blank=True)
    error_detalle = models.TextField(blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("campaign", "contact")]

    def __str__(self):
        return f"{self.campaign} → {self.contact}"
