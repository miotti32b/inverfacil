import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculadora', '0012_quizparticipacion_guest'),
    ]

    operations = [
        migrations.CreateModel(
            name='InscripcionCursoFintech',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('edad', models.PositiveSmallIntegerField()),
                ('mes_elegido', models.CharField(
                    max_length=20,
                    choices=[
                        ('mayo', 'Mayo 2025'),
                        ('junio', 'Junio 2025'),
                        ('julio', 'Julio 2025'),
                        ('agosto', 'Agosto 2025'),
                        ('septiembre', 'Septiembre 2025'),
                    ]
                )),
                ('atendida', models.BooleanField(default=False)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='inscripciones_curso_fintech',
                    to='calculadora.clienteperfil'
                )),
            ],
            options={
                'ordering': ['-creado_en'],
            },
        ),
    ]
