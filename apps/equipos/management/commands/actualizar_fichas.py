from django.core.management.base import BaseCommand
from apps.equipos.models import Equipo

class Command(BaseCommand):
    help = 'Actualiza el estado de todas las fichas técnicas'

    def handle(self, *args, **options):
        equipos = Equipo.objects.all()
        actualizados = 0
        
        for equipo in equipos:
            # Esto forzará la recalculación del estado
            equipo.save()
            actualizados += 1
            
        self.stdout.write(
            self.style.SUCCESS(f'Se actualizaron {actualizados} equipos exitosamente.')
        )