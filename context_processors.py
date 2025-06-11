from apps.inventario.models import Repuesto
from django.db.models import F

def sidebar_context(request):
    """Contexto global para el sidebar con alertas de inventario"""
    try:
        # Calcular solo las alertas críticas reales
        repuestos_agotados = Repuesto.objects.filter(
            activo=True,
            stock_actual=0
        ).count()
        
        # Repuestos críticos con stock bajo
        repuestos_criticos_bajo = Repuesto.objects.filter(
            activo=True,
            es_activo_critico=True,
            stock_actual__lte=F('stock_minimo')
        ).count()
        
        # Total de alertas CRÍTICAS (solo agotados + críticos bajo stock)
        total_alertas_criticas = repuestos_agotados + repuestos_criticos_bajo
        
        return {
            'sidebar_alertas': {
                'total_alertas_criticas': total_alertas_criticas,
            }
        }
    except Exception as e:
        # En caso de error, devolver valores por defecto
        return {
            'sidebar_alertas': {
                'total_alertas_criticas': 0,
            }
        }