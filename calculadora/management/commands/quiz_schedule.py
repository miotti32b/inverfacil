"""
Muestra el calendario de preguntas del quiz para los próximos N días.

Uso:
    python manage.py quiz_schedule          # próximos 30 días
    python manage.py quiz_schedule --dias 7 # próximos 7 días
"""
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from calculadora.models import QuizQuestion
from calculadora.views import _get_quiz_offset


class Command(BaseCommand):
    help = 'Muestra el calendario de preguntas del quiz'

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=30)

    def handle(self, *args, **options):
        preguntas = list(QuizQuestion.objects.order_by('id'))
        total = len(preguntas)
        if total == 0:
            self.stdout.write(self.style.ERROR('No hay preguntas cargadas.'))
            return

        offset = _get_quiz_offset()
        dias = options['dias']
        today = date.today()

        self.stdout.write(self.style.SUCCESS(f'\n{"─"*60}'))
        self.stdout.write(self.style.SUCCESS(f'  CALENDARIO QUIZ — próximos {dias} días  (offset={offset})'))
        self.stdout.write(self.style.SUCCESS(f'{"─"*60}'))

        for i in range(dias):
            d = today + timedelta(days=i)
            idx = (d.toordinal() + offset) % total
            q = preguntas[idx]
            marker = ' ◀ HOY' if i == 0 else (' ◀ MAÑANA' if i == 1 else '')
            label = 'HOY  ' if i == 0 else ('MAÑANA' if i == 1 else d.strftime('%d/%m'))
            texto = q.text[:55] + ('…' if len(q.text) > 55 else '')
            self.stdout.write(f'  {label}  [ID:{q.id:>3}]  {texto}{marker}')

        self.stdout.write(self.style.SUCCESS(f'{"─"*60}\n'))
        self.stdout.write(f'Para cambiar la pregunta de hoy:')
        self.stdout.write(self.style.WARNING('  python manage.py quiz_set_today <question_id>\n'))
