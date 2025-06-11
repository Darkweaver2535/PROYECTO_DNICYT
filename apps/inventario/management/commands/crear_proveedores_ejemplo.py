from django.core.management.base import BaseCommand
from apps.inventario.models import Proveedor

class Command(BaseCommand):
    help = 'Crea proveedores de ejemplo para el laboratorio'

    def handle(self, *args, **options):
        proveedores = [
            {
                'codigo': 'PROV-001',
                'nombre': 'Distribuidora Industrial La Paz S.R.L.',
                'contacto_principal': 'Carlos Mendoza',
                'telefono': '+591-2-2451234',
                'email': 'ventas@dilapaz.com.bo',
                'direccion': 'Av. Buenos Aires #1234, Zona Central',
                'ciudad': 'La Paz',
                'pais': 'Bolivia',
                'nit': '1234567890',
                'calificacion': 4,
                'tiempo_entrega_promedio': 15,
                'es_proveedor_critico': True,
                'certificaciones': 'ISO 9001:2015, ISO 14001:2015'
            },
            {
                'codigo': 'PROV-002',
                'nombre': 'Herramientas y Equipos Industriales HEIN',
                'contacto_principal': 'María Rodriguez',
                'telefono': '+591-2-2789456',
                'email': 'contacto@hein.com.bo',
                'direccion': 'C. Comercio #567, Zona Sur',
                'ciudad': 'La Paz',
                'pais': 'Bolivia',
                'nit': '2345678901',
                'calificacion': 5,
                'tiempo_entrega_promedio': 10,
                'es_proveedor_critico': True,
                'certificaciones': 'ISO 9001:2015'
            },
            {
                'codigo': 'PROV-003',
                'nombre': 'Soldaduras y Cortes Técnicos S.A.',
                'contacto_principal': 'Roberto Silva',
                'telefono': '+591-2-2123789',
                'email': 'ventas@solcorte.bo',
                'direccion': 'Av. Montes #890, El Alto',
                'ciudad': 'El Alto',
                'pais': 'Bolivia',
                'nit': '3456789012',
                'calificacion': 4,
                'tiempo_entrega_promedio': 7,
                'es_proveedor_critico': True,
                'certificaciones': 'AWS D1.1, AWS D1.6, ISO 9001:2015'
            },
            {
                'codigo': 'PROV-004',
                'nombre': 'Repuestos Maquinaria Industrial RMI',
                'contacto_principal': 'Ana Gutierrez',
                'telefono': '+591-2-2456123',
                'email': 'info@rmi.com.bo',
                'direccion': 'Av. 6 de Agosto #345, Zona Norte',
                'ciudad': 'La Paz',
                'pais': 'Bolivia',
                'nit': '4567890123',
                'calificacion': 3,
                'tiempo_entrega_promedio': 20,
                'es_proveedor_critico': False,
                'certificaciones': 'ISO 9001:2015'
            },
            {
                'codigo': 'PROV-005',
                'nombre': 'Lubricantes y Fluidos Industriales LFI',
                'contacto_principal': 'Jorge Morales',
                'telefono': '+591-2-2567234',
                'email': 'ventas@lfi.bo',
                'direccion': 'Av. del Ejercito #678, Zona Villa Fatima',
                'ciudad': 'La Paz',
                'pais': 'Bolivia',
                'nit': '5678901234',
                'calificacion': 4,
                'tiempo_entrega_promedio': 5,
                'es_proveedor_critico': False,
                'certificaciones': 'ISO 14001:2015, OHSAS 18001'
            },
            {
                'codigo': 'PROV-006',
                'nombre': 'Metales y Aleaciones Especiales MAE',
                'contacto_principal': 'Patricia Vargas',
                'telefono': '+591-2-2678345',
                'email': 'contacto@mae.com.bo',
                'direccion': 'C. Potosí #234, Zona Central',
                'ciudad': 'La Paz',
                'pais': 'Bolivia',
                'nit': '6789012345',
                'calificacion': 5,
                'tiempo_entrega_promedio': 25,
                'es_proveedor_critico': True,
                'certificaciones': 'ASTM A240, ASTM A36, ISO 9001:2015'
            },
            {
                'codigo': 'PROV-007',
                'nombre': 'Equipos de Protección Personal EPP Bolivia',
                'contacto_principal': 'Miguel Torres',
                'telefono': '+591-2-2789456',
                'email': 'ventas@eppbolivia.com',
                'direccion': 'Av. América #456, Zona Sur',
                'ciudad': 'La Paz',
                'pais': 'Bolivia',
                'nit': '7890123456',
                'calificacion': 4,
                'tiempo_entrega_promedio': 12,
                'es_proveedor_critico': True,
                'certificaciones': 'ISO 45001:2018, CE, ANSI'
            },
            {
                'codigo': 'PROV-008',
                'nombre': 'Instrumentos de Medición y Calibración IMC',
                'contacto_principal': 'Elena Castro',
                'telefono': '+591-2-2890567',
                'email': 'info@imc.bo',
                'direccion': 'C. Murillo #789, Zona Central',
                'ciudad': 'La Paz',
                'pais': 'Bolivia',
                'nit': '8901234567',
                'calificacion': 5,
                'tiempo_entrega_promedio': 30,
                'es_proveedor_critico': True,
                'certificaciones': 'ISO 17025:2017, ISO 9001:2015'
            },
            {
                'codigo': 'PROV-009',
                'nombre': 'Químicos Industriales Bolivia QIB',
                'contacto_principal': 'Fernando López',
                'telefono': '+591-2-2901678',
                'email': 'ventas@qib.com.bo',
                'direccion': 'Av. Blanco Galindo Km 5, Quillacollo',
                'ciudad': 'Cochabamba',
                'pais': 'Bolivia',
                'nit': '9012345678',
                'calificacion': 3,
                'tiempo_entrega_promedio': 45,
                'es_proveedor_critico': False,
                'certificaciones': 'ISO 14001:2015, REACH'
            },
            {
                'codigo': 'PROV-010',
                'nombre': 'Suministros Eléctricos Profesionales SEP',
                'contacto_principal': 'Claudia Mamani',
                'telefono': '+591-2-3012789',
                'email': 'contacto@sep.bo',
                'direccion': 'Av. Camacho #123, Zona Central',
                'ciudad': 'La Paz',
                'pais': 'Bolivia',
                'nit': '0123456789',
                'calificacion': 4,
                'tiempo_entrega_promedio': 8,
                'es_proveedor_critico': True,
                'certificaciones': 'IEC 61439, ISO 9001:2015'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for prov_data in proveedores:
            proveedor, created = Proveedor.objects.get_or_create(
                codigo=prov_data['codigo'],
                defaults=prov_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Creado: {proveedor.codigo} - {proveedor.nombre}')
                )
            else:
                # Actualizar datos si ya existe
                for field, value in prov_data.items():
                    setattr(proveedor, field, value)
                proveedor.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Actualizado: {proveedor.codigo} - {proveedor.nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Proceso completado:\n'
                f'   • {created_count} proveedores creados\n'
                f'   • {updated_count} proveedores actualizados\n'
                f'   • Total: {created_count + updated_count} proveedores procesados'
            )
        )