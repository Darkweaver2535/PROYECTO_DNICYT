from django.core.management.base import BaseCommand
from apps.mantenimiento.models import RepuestoCritico

class Command(BaseCommand):
    help = 'Crear repuestos críticos de ejemplo'

    def handle(self, *args, **options):
        repuestos = [
            {
                'nombre': 'Rodamiento SKF 6208',
                'codigo_fabricante': 'SKF-6208-2RS1',
                'descripcion': 'Rodamiento rígido de bolas, sellado doble',
                'stock_minimo': 4,
                'tiempo_entrega': 15,
                'proveedor': 'SKF Bolivia',
                'costo_unitario': 150.00
            },
            {
                'nombre': 'Sello mecánico bomba centrífuga',
                'codigo_fabricante': 'SM-BC-001',
                'descripcion': 'Sello mecánico para bomba centrífuga, resistente a químicos',
                'stock_minimo': 2,
                'tiempo_entrega': 30,
                'proveedor': 'Mechanical Seals Inc.',
                'costo_unitario': 280.00
            },
            {
                'nombre': 'Filtro de aceite hidráulico',
                'codigo_fabricante': 'HF-6555',
                'descripcion': 'Filtro de aceite hidráulico 10 micrones',
                'stock_minimo': 6,
                'tiempo_entrega': 7,
                'proveedor': 'Hydraulic Filters SA',
                'costo_unitario': 75.00
            },
            {
                'nombre': 'Correa trapecial A42',
                'codigo_fabricante': 'CT-A42-STD',
                'descripcion': 'Correa trapecial estándar A42',
                'stock_minimo': 3,
                'tiempo_entrega': 5,
                'proveedor': 'Belts & More',
                'costo_unitario': 45.00
            },
        ]
        
        for repuesto_data in repuestos:
            repuesto, created = RepuestoCritico.objects.get_or_create(
                nombre=repuesto_data['nombre'],
                defaults=repuesto_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Repuesto creado: {repuesto.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Repuesto ya existe: {repuesto.nombre}')
                )