"""
Fuerza qué pregunta aparece hoy ajustando un offset global.

Uso:
    python manage.py quiz_set_today <question_id>

Ejemplo:
    python manage.py quiz_set_today 5   # la pregunta con ID 5 sale hoy
"""
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from calculadora.models import QuizQuestion
from calculadora.views import _set_quiz_offset, _get_quiz_offset


class Command(BaseCommand):
    help = 'Fuerza qué pregunta aparece hoy en el quiz'

    def add_arguments(self, parser):
        parser.add_argument('question_id', type=int)

    def handle(self, *args, **options):
        qid = options['question_id']
        preguntas = list(QuizQuestion.objects.order_by('id'))
        total = len(preguntas)
        if total == 0:
            raise CommandError('No hay preguntas cargadas.')

        ids = [q.id for q in preguntas]
        if qid not in ids:
            raise CommandError(f'No existe pregunta con ID {qid}. IDs disponibles: {ids}')

        target_index = ids.index(qid)
        today_ordinal = date.today().toordinal()
        # offset = target_index - today_ordinal  (mod total)
        new_offset = (target_index - today_ordinal) % total
        _set_quiz_offset(new_offset)

        q = preguntas[target_index]
        self.stdout.write(self.style.SUCCESS(
            f'\n  Offset actualizado a {new_offset}.'
            f'\n  Hoy aparece: [{q.id}] {q.text}\n'
        ))
        self.stdout.write('  Para verificar el calendario completo:')
        self.stdout.write(self.style.WARNING('  python manage.py quiz_schedule\n'))
