from django.core.management.base import BaseCommand

from charla_votacion.models import Etapa, Opcion, Sesion

ETAPAS = [
    {
        "titulo": "¿Sobre qué tema va el proyecto?",
        "descripcion": "Elegí el problema o tema que va a resolver lo que construyamos.",
        "opciones": [
            ("Educación y estudio", "Algo que ayude a organizarse, aprender o repasar para el cole."),
            ("Vida social y amigos", "Algo para conectar gente, organizar planes o compartir cosas."),
            ("Diversión y juegos", "Algo pensado pura y exclusivamente para pasarla bien."),
            ("Comunidad y medio ambiente", "Algo que ayude al barrio, al cole o al planeta."),
        ],
    },
    {
        "titulo": "¿Qué tipo de producto va a ser?",
        "descripcion": "El formato general de lo que vamos a construir.",
        "opciones": [
            ("Juego interactivo", "Con puntos, desafíos o niveles."),
            ("Herramienta útil", "Tipo calculadora, planificador o generador de ideas."),
            ("Red o muro social", "Un lugar para publicar, comentar o votar cosas entre todos."),
            ("Generador con IA", "Que crea texto, imágenes o historias a partir de lo que pide el usuario."),
        ],
    },
    {
        "titulo": "¿Cuál va a ser la función estrella?",
        "descripcion": "La feature principal que va a tener el proyecto.",
        "opciones": [
            ("Ranking y competencia", "Los usuarios compiten y ven quién va ganando."),
            ("Personalización con IA", "La app responde distinto según cada usuario."),
            ("Modo grupal en vivo", "Varias personas usándolo al mismo tiempo."),
            ("Diseño espectacular", "Animaciones y efectos que la hacen ver increíble."),
        ],
    },
    {
        "titulo": "¿Para quién es y qué onda visual tiene?",
        "descripcion": "El público y el estilo con el que se va a ver.",
        "opciones": [
            ("Colorido y divertido", "Pensado para gente de nuestra edad, con mucho color."),
            ("Oscuro y gamer", "Estilo minimalista, oscuro, tipo videojuego."),
            ("Cálido y amigable", "Para toda la familia, cercano y simple."),
            ("Profesional y elegante", "Serio, prolijo, como una app 'de grandes'."),
        ],
    },
]


class Command(BaseCommand):
    help = "Crea una nueva sesión de votación para la charla, con las 4 etapas predefinidas."

    def add_arguments(self, parser):
        parser.add_argument("--nombre", default="Charla en vivo")

    def handle(self, *args, **options):
        sesion = Sesion.objects.create(nombre=options["nombre"])

        for orden, etapa_data in enumerate(ETAPAS, start=1):
            etapa = Etapa.objects.create(
                sesion=sesion,
                orden=orden,
                titulo=etapa_data["titulo"],
                descripcion=etapa_data["descripcion"],
            )
            for texto, descripcion in etapa_data["opciones"]:
                Opcion.objects.create(etapa=etapa, texto=texto, descripcion=descripcion)

        self.stdout.write(self.style.SUCCESS(f"Sesión creada. Código: {sesion.codigo}"))
        self.stdout.write(f"Presentador: /votacion/presentador/{sesion.codigo}/")
        self.stdout.write(f"Alumnos: /votacion/  (código: {sesion.codigo})")
