from django.core.management.base import BaseCommand

from charla_votacion.contenido import crear_sesion


class Command(BaseCommand):
    help = "Crea una nueva sesión de votación para la charla, con las etapas predefinidas."

    def add_arguments(self, parser):
        parser.add_argument("--nombre", default="Charla en vivo")

    def handle(self, *args, **options):
        sesion = crear_sesion(nombre=options["nombre"])

        self.stdout.write(self.style.SUCCESS(f"Sesión creada. Código: {sesion.codigo}"))
        self.stdout.write(f"Presentador: /votacion/presentador/{sesion.codigo}/")
        self.stdout.write(f"Alumnos: /votacion/  (código: {sesion.codigo})")
