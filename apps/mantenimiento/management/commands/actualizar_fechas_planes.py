from django.core.management.base import BaseCommand
from apps.mantenimiento.models import PlanMantenimiento
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Actualiza las fechas de próxima ejecución para los planes existentes'

    def handle(self, *args, **options):
        planes = PlanMantenimiento.objects.all()
        
        for plan in planes:
            # Si no tiene próxima ejecución, calcularla
            if not plan.proxima_ejecucion:
                if plan.fecha_inicio:
                    # Para planes existentes, generar fechas distribuidas en los próximos 30 días
                    dias_random = random.randint(1, 30)
                    plan.proxima_ejecucion = date.today() + timedelta(days=dias_random)
                else:
                    # Si no tiene fecha de inicio, asignar una
                    plan.fecha_inicio = date.today()
                    plan.proxima_ejecucion = date.today() + timedelta(days=random.randint(7, 30))
                
                plan.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {plan.codigo_plan}: próximo mantenimiento el {plan.proxima_ejecucion}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎯 Actualizados {planes.count()} planes de mantenimiento'
            )
        )