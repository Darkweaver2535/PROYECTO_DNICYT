from django.core.management.base import BaseCommand
from apps.mantenimiento.models import PlanMantenimiento
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Actualiza las fechas de mantenimiento para testing'

    def handle(self, *args, **options):
        planes = PlanMantenimiento.objects.all()
        
        for plan in planes:
            # Simular fechas para testing
            if not plan.proxima_ejecucion:
                # Generar fechas aleatorias para los próximos 60 días
                dias_random = random.randint(1, 60)
                plan.proxima_ejecucion = date.today() + timedelta(days=dias_random)
                plan.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Actualizado {plan.codigo_plan}: próximo mantenimiento el {plan.proxima_ejecucion}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Se actualizaron {planes.count()} planes de mantenimiento'
            )
        )