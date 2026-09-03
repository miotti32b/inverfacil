from django.core.management.base import BaseCommand

from charla_votacion.models import Etapa, Opcion, Sesion

ETAPAS = [
    {
        "titulo": "¿Qué problema real van a resolver?",
        "descripcion": "Toda empresa arranca acá: a quién le duele algo, y por qué le importa.",
        "opciones": [
            ("Plata y consumo joven", "Cómo los adolescentes ahorran, gastan o manejan la plata que tienen."),
            ("Estudio y productividad", "Organizarse, aprender más rápido o rendir mejor en el cole."),
            ("Salud mental y bienestar", "Manejar estrés, ansiedad, sueño o ejercicio."),
            ("Conexión y comunidad", "Encontrar gente con intereses parecidos y armar cosas juntos."),
        ],
    },
    {
        "titulo": "¿Quién es tu cliente?",
        "descripcion": "No es lo mismo vender a un adolescente que a un colegio. Elegí a quién le vendés.",
        "opciones": [
            ("Adolescentes (15 a 18)", "Mismo perfil que ustedes, mismos códigos y necesidades."),
            ("Padres y familias", "Ellos deciden y pagan; buscan tranquilidad y practicidad."),
            ("Colegios e instituciones", "Le vendés a la institución, no a la persona individual."),
            ("Jóvenes en general (18 a 30)", "Mercado más amplio: universitarios y primeros trabajos."),
        ],
    },
    {
        "titulo": "¿Por qué te eligen a vos y no a otro?",
        "descripcion": "Esa es tu propuesta de valor: la razón concreta por la que alguien usaría esto.",
        "opciones": [
            ("Es gratis y accesible", "El precio bajo o nulo es la ventaja principal."),
            ("Es mucho más rápido y simple", "Resuelve en minutos algo que hoy lleva horas."),
            ("Usa IA para personalizar todo", "La tecnología se adapta a cada usuario particular."),
            ("Genera comunidad y pertenencia", "La gente vuelve por el grupo, no solo por la función."),
        ],
    },
    {
        "titulo": "¿Cómo gana plata la empresa?",
        "descripcion": "Un producto sin modelo de ingresos es un hobby, no una empresa.",
        "opciones": [
            ("Freemium", "Gratis con funciones básicas; se paga por las funciones premium."),
            ("Suscripción mensual", "Todos los usuarios pagan una cuota fija para usarlo."),
            ("Publicidad", "Es gratis para el usuario; se financia con anunciantes."),
            ("Comisión por transacción", "Cobra un porcentaje cada vez que se usa para vender o intercambiar algo."),
        ],
    },
    {
        "titulo": "¿Qué tipo de producto van a construir?",
        "descripcion": "El formato define cómo la gente lo va a usar todos los días.",
        "opciones": [
            ("App o herramienta web", "Algo que el usuario mismo usa para resolver su problema."),
            ("Marketplace", "Conecta a quienes ofrecen algo con quienes lo necesitan."),
            ("Red o comunidad", "Un espacio para publicar, compartir y conectar entre usuarios."),
            ("Asistente con IA", "Un 'copiloto' que ayuda a resolver algo específico paso a paso."),
        ],
    },
    {
        "titulo": "¿Cuál es tu ventaja competitiva?",
        "descripcion": "La función estrella: lo que hace que este producto gane contra los que ya existen.",
        "opciones": [
            ("Personalización con IA", "El producto se adapta a cada usuario en particular."),
            ("Gamificación y ranking", "Puntos, niveles y competencia sana entre usuarios."),
            ("Colaboración en tiempo real", "Varias personas usándolo juntas, al mismo tiempo."),
            ("Automatización", "Hace de forma automática algo que hoy es tedioso y manual."),
        ],
    },
    {
        "titulo": "¿Cuál es la identidad de marca?",
        "descripcion": "Cómo se ve y se siente la marca frente al cliente y frente a un inversor.",
        "opciones": [
            ("Colorida y joven", "Directo a nuestra generación, con onda y cercanía."),
            ("Minimalista y premium", "Prolija y seria, como una marca grande y consolidada."),
            ("Oscura y tech", "Estética gamer/tech, pensada para usuarios avanzados."),
            ("Cálida y confiable", "Transmite seguridad y cercanía, apta para toda la familia."),
        ],
    },
]


class Command(BaseCommand):
    help = "Crea una nueva sesión de votación para la charla, con las 7 etapas predefinidas."

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
