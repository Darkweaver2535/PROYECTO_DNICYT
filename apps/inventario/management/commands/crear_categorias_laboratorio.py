from django.core.management.base import BaseCommand
from apps.inventario.models import CategoriaRepuesto

class Command(BaseCommand):
    help = 'Crea categorías específicas para el laboratorio de Metal Mecánica'

    def handle(self, *args, **options):
        categorias = [
            # Equipos de Soldadura y Corte
            {
                'codigo': 'EQS',
                'nombre': 'Equipos de Soldadura y Corte',
                'tipo_categoria': 'equipos',
                'seccion_aplicable': 'S1 - Soldadura, Corte y Perforación',
                'descripcion': 'Equipos para procesos de soldadura y corte de metales'
            },
            
            # Equipos de Maquinado
            {
                'codigo': 'EQM',
                'nombre': 'Equipos de Maquinado CNC',
                'tipo_categoria': 'equipos',
                'seccion_aplicable': 'S2 - Maquinado y Mecanizado',
                'descripcion': 'Máquinas CNC y equipos de maquinado automatizado'
            },
            
            {
                'codigo': 'EMC',
                'nombre': 'Equipos de Maquinado Convencional',
                'tipo_categoria': 'equipos',
                'seccion_aplicable': 'S2 - Maquinado y Mecanizado',
                'descripcion': 'Tornos, fresadoras y taladros convencionales'
            },
            
            # Fundición y Tratamiento Térmico
            {
                'codigo': 'EFT',
                'nombre': 'Equipos de Fundición y Tratamiento Térmico',
                'tipo_categoria': 'equipos',
                'seccion_aplicable': 'S5 - Fundición',
                'descripcion': 'Hornos, equipos de fundición y tratamiento térmico'
            },
            
            # Conformado
            {
                'codigo': 'ECM',
                'nombre': 'Equipos de Conformado de Metales',
                'tipo_categoria': 'equipos',
                'seccion_aplicable': 'S6 - Sujeción y Doblado',
                'descripcion': 'Prensas, dobladoras y equipos de conformado'
            },
            
            {
                'codigo': 'ECP',
                'nombre': 'Equipos de Conformado de Plásticos',
                'tipo_categoria': 'equipos',
                'seccion_aplicable': 'S4 - Plásticos',
                'descripcion': 'Máquinas de inyección, extrusión y termoformado'
            },
            
            # Prototipado
            {
                'codigo': 'EP3',
                'nombre': 'Equipos de Prototipado e Impresión 3D',
                'tipo_categoria': 'equipos',
                'seccion_aplicable': 'S3 - Prototipado',
                'descripcion': 'Impresoras 3D y equipos de prototipado rápido'
            },
            
            # Transporte y Elevación
            {
                'codigo': 'ETE',
                'nombre': 'Equipos de Transporte y Elevación',
                'tipo_categoria': 'equipos',
                'seccion_aplicable': 'S7 - Transporte y Elevación',
                'descripcion': 'Grúas, tecles y equipos de manejo de materiales'
            },
            
            # Medición y Calibración
            {
                'codigo': 'HMC',
                'nombre': 'Herramientas de Medición y Calibración',
                'tipo_categoria': 'herramientas',
                'seccion_aplicable': 'CAL - Control de Calidad',
                'descripcion': 'Instrumentos de medición y calibración'
            },
            
            # Afilado y Rectificado
            {
                'codigo': 'EAR',
                'nombre': 'Equipos de Afilado y Rectificado',
                'tipo_categoria': 'equipos',
                'seccion_aplicable': 'S2 - Maquinado y Mecanizado',
                'descripcion': 'Rectificadoras y equipos de afilado'
            },
            
            # Repuestos por Categoría
            {
                'codigo': 'RPS',
                'nombre': 'Repuestos de Soldadura',
                'tipo_categoria': 'repuestos',
                'seccion_aplicable': 'S1 - Soldadura, Corte y Perforación',
                'descripcion': 'Repuestos específicos para equipos de soldadura'
            },
            
            {
                'codigo': 'RPM',
                'nombre': 'Repuestos de Maquinado',
                'tipo_categoria': 'repuestos',
                'seccion_aplicable': 'S2 - Maquinado y Mecanizado',
                'descripcion': 'Repuestos para máquinas herramientas'
            },
            
            {
                'codigo': 'REE',
                'nombre': 'Repuestos Eléctricos y Electrónicos',
                'tipo_categoria': 'repuestos',
                'seccion_aplicable': 'MAN - Mantenimiento',
                'descripcion': 'Componentes eléctricos y electrónicos'
            },
            
            {
                'codigo': 'RHN',
                'nombre': 'Repuestos Hidráulicos y Neumáticos',
                'tipo_categoria': 'repuestos',
                'seccion_aplicable': 'MAN - Mantenimiento',
                'descripcion': 'Componentes hidráulicos y neumáticos'
            },
            
            # Consumibles
            {
                'codigo': 'CSO',
                'nombre': 'Consumibles de Soldadura',
                'tipo_categoria': 'consumibles',
                'seccion_aplicable': 'S1 - Soldadura, Corte y Perforación',
                'descripcion': 'Electrodos, alambres y gases para soldadura'
            },
            
            {
                'codigo': 'CMA',
                'nombre': 'Consumibles de Maquinado',
                'tipo_categoria': 'consumibles',
                'seccion_aplicable': 'S2 - Maquinado y Mecanizado',
                'descripcion': 'Herramientas de corte, brocas, fresas'
            },
            
            # EPP
            {
                'codigo': 'EPP',
                'nombre': 'Elementos de Protección Personal (EPP)',
                'tipo_categoria': 'epp',
                'seccion_aplicable': 'SEG - Seguridad Industrial',
                'descripcion': 'Equipos de protección personal'
            },
            
            # Lubricantes y Fluidos
            {
                'codigo': 'LUB',
                'nombre': 'Lubricantes y Fluidos',
                'tipo_categoria': 'lubricantes',
                'seccion_aplicable': 'MAN - Mantenimiento',
                'descripcion': 'Aceites, grasas y fluidos industriales'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for cat_data in categorias:
            categoria, created = CategoriaRepuesto.objects.get_or_create(
                codigo=cat_data['codigo'],
                defaults=cat_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Creada: {categoria.codigo} - {categoria.nombre}')
                )
            else:
                # Actualizar campos si la categoría ya existe
                for field, value in cat_data.items():
                    setattr(categoria, field, value)
                categoria.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Actualizada: {categoria.codigo} - {categoria.nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Proceso completado:\n'
                f'   • {created_count} categorías creadas\n'
                f'   • {updated_count} categorías actualizadas\n'
                f'   • Total: {created_count + updated_count} categorías procesadas'
            )
        )