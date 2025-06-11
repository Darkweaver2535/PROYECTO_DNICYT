from apps.inventario.models import Repuesto
from django.db.models import F

def sidebar_context(request):
    """Context processor para el sidebar con datos dinámicos"""
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
        
        # === SECCIÓN INVENTARIO ===
        inventario_items = [
            {
                'name': 'dashboard_inventario',
                'title': 'Dashboard',
                'url': 'inventario:dashboard',
                'icon': 'bi-speedometer2',
                'permission': None,
                'badge_count': None,
            },
            {
                'name': 'repuestos',
                'title': 'Inventario de Repuestos',
                'url': 'inventario:repuestos',
                'icon': 'bi-boxes',
                'permission': None,
                'badge_count': total_alertas_criticas if total_alertas_criticas > 0 else None,
            },
            {
                'name': 'stock_critico',
                'title': 'Stock Crítico',
                'url': 'inventario:stock-critico',
                'icon': 'bi-exclamation-triangle',
                'permission': None,
                'badge_count': repuestos_criticos_bajo if repuestos_criticos_bajo > 0 else None,
            },
            {
                'name': 'movimientos',
                'title': 'Movimientos',
                'url': 'inventario:movimientos',
                'icon': 'bi-arrow-left-right',
                'permission': None,
                'badge_count': None,
            },
            {
                'name': 'proveedores',
                'title': 'Proveedores',
                'url': 'inventario:proveedores',
                'icon': 'bi-building',
                'permission': None,
                'badge_count': None,
            },
            {
                'name': 'reportes_inventario',
                'title': 'Reportes',
                'url': 'inventario:reportes-inventario',
                'icon': 'bi-graph-up',
                'permission': None,
                'badge_count': None,
            },
        ]
        
        return {
            'sidebar_alertas': {
                'total_alertas_criticas': total_alertas_criticas,
            },
            'inventario_items': inventario_items,
        }
    except Exception as e:
        # En caso de error, devolver valores por defecto
        return {
            'sidebar_alertas': {
                'total_alertas_criticas': 0,
            },
            'inventario_items': [],
        }