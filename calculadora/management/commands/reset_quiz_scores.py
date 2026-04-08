from django.core.management.base import BaseCommand
from calculadora.models import QuizParticipacion, ClientePerfil


class Command(BaseCommand):
    help = 'Elimina todas las participaciones del quiz y resetea quiz_score_total a 0'

    def handle(self, *args, **options):
        total = QuizParticipacion.objects.count()
        QuizParticipacion.objects.all().delete()
        ClientePerfil.objects.update(quiz_score_total=0)
        self.stdout.write(self.style.SUCCESS(
            f'✅ {total} participaciones eliminadas. Scores reseteados a 0.'
        ))
