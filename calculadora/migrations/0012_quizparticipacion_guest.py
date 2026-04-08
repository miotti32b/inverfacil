from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calculadora', '0011_quiz_reset_30_preguntas'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizparticipacion',
            name='guest_alias',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='quizparticipacion',
            name='cliente',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='participaciones_quiz',
                to='calculadora.clienteperfil',
            ),
        ),
    ]
