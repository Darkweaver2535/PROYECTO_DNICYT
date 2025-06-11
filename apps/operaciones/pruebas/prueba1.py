# Script para crear datos de ejemplo (ejecutar en Django shell: python manage.py shell)
from apps.operaciones.models import AnalisisRiesgo
from datetime import date, timedelta

# Crear algunos riesgos de ejemplo
riesgos_ejemplo = [
    {
        'descripcion': 'Exposición a humos metálicos durante soldadura',
        'area': 'soldadura',
        'tipo': 'quimico',
        'probabilidad': 4,
        'severidad': 4,
        'responsable': 'Supervisor de Soldadura',
        'fecha_revision': date.today() + timedelta(days=30),
        'medidas_control': 'Sistema de ventilación localizada\nUso obligatorio de máscaras respiratorias',
    },
    {
        'descripcion': 'Atrapamiento en máquinas herramientas',
        'area': 'maquinado',
        'tipo': 'mecanico',
        'probabilidad': 3,
        'severidad': 5,
        'responsable': 'Jefe de Maquinado',
        'fecha_revision': date.today() + timedelta(days=60),
        'medidas_control': 'Guardas de seguridad en todas las máquinas\nProcedimientos de bloqueo/etiquetado',
    },
    # Agregar más ejemplos...
]

for riesgo_data in riesgos_ejemplo:
    AnalisisRiesgo.objects.get_or_create(
        descripcion=riesgo_data['descripcion'],
        defaults=riesgo_data
    )