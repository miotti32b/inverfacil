from django.core.management.base import BaseCommand

from trivia_financiero.contenido import PREGUNTAS
from trivia_financiero.models import Pregunta


class Command(BaseCommand):
    help = "Carga (o actualiza) el banco de preguntas de trivia_financiero. Idempotente."

    def handle(self, *args, **options):
        creadas = 0
        actualizadas = 0
        for datos in PREGUNTAS:
            _, creado = Pregunta.objects.update_or_create(
                texto=datos["texto"],
                defaults={
                    "opciones": datos["opciones"],
                    "respuesta_correcta": datos["respuesta_correcta"],
                    "explicacion": datos["explicacion"],
                    "dificultad": datos["dificultad"],
                    "categoria": datos["categoria"],
                    "activa": True,
                },
            )
            if creado:
                creadas += 1
            else:
                actualizadas += 1
        self.stdout.write(self.style.SUCCESS(f"Preguntas creadas: {creadas} · actualizadas: {actualizadas}"))
