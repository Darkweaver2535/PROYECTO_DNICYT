from django.core.management.base import BaseCommand
from apps.materiales.models import CategoriaMaterial

class Command(BaseCommand):
    help = 'Crear categorías de materiales iniciales'

    def handle(self, *args, **options):
        categorias = [
            {
                'codigo': 'MAT-CONS',
                'nombre': 'Materiales de Construcción',
                'descripcion': 'Cemento, arena, grava, ladrillos, blocks, etc.',
                'tipo_categoria': 'materiales_construccion'
            },
            {
                'codigo': 'MAT-SOLD',
                'nombre': 'Materiales de Soldadura',
                'descripcion': 'Electrodos, alambre de soldadura, fundentes, gases, etc.',
                'tipo_categoria': 'materiales_soldadura'
            },
            {
                'codigo': 'CONS-LAB',
                'nombre': 'Consumibles de Laboratorio',
                'descripcion': 'Guantes, mascarillas, papel, jeringas, etc.',
                'tipo_categoria': 'consumibles_laboratorio'
            },
            {
                'codigo': 'QUIM-REA',
                'nombre': 'Químicos y Reactivos',
                'descripcion': 'Ácidos, bases, solventes, reactivos analíticos, etc.',
                'tipo_categoria': 'quimicos_reactivos'
            },
            {
                'codigo': 'LUB-FLU',
                'nombre': 'Lubricantes y Fluidos',
                'descripcion': 'Aceites, grasas, fluidos hidráulicos, refrigerantes, etc.',
                'tipo_categoria': 'lubricantes_fluidos'
            },
            {
                'codigo': 'MAT-ELEC',
                'nombre': 'Materiales Eléctricos',
                'descripcion': 'Cables, conectores, fusibles, interruptores, etc.',
                'tipo_categoria': 'materiales_electricos'
            },
            {
                'codigo': 'MAT-MET',
                'nombre': 'Materiales Metálicos',
                'descripcion': 'Chapas, barras, tubos, perfiles metálicos, etc.',
                'tipo_categoria': 'materiales_metalicos'
            },
            {
                'codigo': 'COMB-GAS',
                'nombre': 'Combustibles y Gases',
                'descripcion': 'Gasolina, diesel, acetileno, oxígeno, argón, etc.',
                'tipo_categoria': 'combustibles_gases'
            },
            {
                'codigo': 'PINT-REC',
                'nombre': 'Pinturas y Recubrimientos',
                'descripcion': 'Pinturas, barnices, primers, anticorrosivos, etc.',
                'tipo_categoria': 'pinturas_recubrimientos'
            },
            {
                'codigo': 'ADH-SELL',
                'nombre': 'Adhesivos y Sellantes',
                'descripcion': 'Pegamentos, silicones, masillas, cintas adhesivas, etc.',
                'tipo_categoria': 'adhesivos_sellantes'
            },
            {
                'codigo': 'ABR-PUL',
                'nombre': 'Abrasivos y Pulimentos',
                'descripcion': 'Lijas, discos de corte, muelas, pasta para pulir, etc.',
                'tipo_categoria': 'abrasivos_pulimentos'
            },
            {
                'codigo': 'MAT-PROT',
                'nombre': 'Materiales de Protección',
                'descripcion': 'Lonas, plásticos protectores, fundas, empaques, etc.',
                'tipo_categoria': 'materiales_proteccion'
            },
        ]

        for categoria_data in categorias:
            categoria, created = CategoriaMaterial.objects.get_or_create(
                codigo=categoria_data['codigo'],
                defaults=categoria_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Categoría creada: {categoria.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Categoría ya existe: {categoria.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS('Todas las categorías han sido procesadas')
        )