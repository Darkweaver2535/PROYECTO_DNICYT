from django.urls import path
from . import views

app_name = 'operaciones'

urlpatterns = [
    path('procedimientos-pop/', views.procedimientos_pop_view, name='procedimientos-pop'),
    path('crear-pop/', views.crear_pop_view, name='crear-pop'),
    path('editar-pop/<str:codigo>/', views.editar_pop_view, name='editar-pop'),
    path('ver-pop/<str:codigo>/', views.ver_pop_view, name='ver-pop'),
    path('eliminar-pop/<str:codigo>/', views.eliminar_pop_view, name='eliminar-pop'),
    path('aprobar-pop/<str:codigo>/', views.aprobar_pop_view, name='aprobar-pop'),
    path('renovar-pop/<str:codigo>/', views.renovar_pop_view, name='renovar-pop'),
    path('descargar-pop-pdf/<str:codigo>/', views.descargar_pop_pdf_view, name='descargar-pop-pdf'),
    path('analisis-riesgos/', views.analisis_riesgos_view, name='analisis-riesgos'),
    
    # NUEVA URL PARA MOVIMIENTOS UNIFICADOS
    path('movimientos/', views.movimientos_unificados_view, name='movimientos-unificados'),
]