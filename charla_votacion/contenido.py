ETAPAS = [
    {
        "titulo": "¿En qué industria vas a emprender?",
        "descripcion": "La industria define el mercado real en el que vas a competir.",
        "opciones": [
            ("Agro y ganadería", "Producción, campo, insumos y todo lo que mueve al sector agropecuario."),
            ("Finanzas y consumo", "Plata, ahorro, pagos o consumo de las personas y las empresas."),
            ("Entretenimiento y ocio", "Juegos, contenido, eventos o todo lo que la gente hace en su tiempo libre."),
            ("Salud y bienestar", "Cuidado físico, mental o de calidad de vida de las personas."),
        ],
    },
    {
        "titulo": "¿Qué tipo de problema van a resolver en esa industria?",
        "descripcion": "Todo negocio arranca de un problema real dentro de su industria.",
        "opciones": [
            ("Ineficiencia y pérdida de tiempo", "Un proceso que hoy se hace lento o a mano, y se podría optimizar."),
            ("Falta de información o datos", "Se decide 'a ojo' por falta de información clara y a tiempo."),
            ("Costos altos o desperdicio", "Se gasta de más o se pierde recurso que se podría evitar."),
            ("Acceso limitado", "Un grupo no tiene acceso fácil a algo que necesita."),
        ],
    },
    {
        "titulo": "¿Quién es tu cliente?",
        "descripcion": "No es lo mismo vender a un adolescente que a un colegio. Elegí a quién le vendés.",
        "opciones": [
            ("Adolescentes (15 a 18)", "Mismo perfil que ustedes, mismos códigos y necesidades."),
            ("Padres y familias", "Ellos deciden y pagan; buscan tranquilidad y practicidad."),
            ("Empresas e instituciones", "Le vendés a una organización, no a la persona individual."),
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


def crear_sesion(nombre="Charla en vivo"):
    from .models import Etapa, Opcion, Sesion

    Sesion.objects.filter(activa=True).update(activa=False)
    sesion = Sesion.objects.create(nombre=nombre)

    for orden, etapa_data in enumerate(ETAPAS, start=1):
        etapa = Etapa.objects.create(
            sesion=sesion,
            orden=orden,
            titulo=etapa_data["titulo"],
            descripcion=etapa_data["descripcion"],
        )
        for texto, descripcion in etapa_data["opciones"]:
            Opcion.objects.create(etapa=etapa, texto=texto, descripcion=descripcion)

    return sesion
