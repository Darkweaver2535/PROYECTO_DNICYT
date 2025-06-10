from django.urls import path
from .views import (
    EquipoListView,
    EquipoDetailView,
    EquipoCreateView,
    EquipoUpdateView,
    EquipoDeleteView,
    generar_qr_view,
)
from . import views

app_name = 'equipos'

urlpatterns = [
    path('', EquipoListView.as_view(), name='equipo-lista'),
    path('detalle/<int:pk>/', EquipoDetailView.as_view(), name='equipo-detalle'),
    path('crear/', EquipoCreateView.as_view(), name='equipo-crear'),
    path('editar/<int:pk>/', EquipoUpdateView.as_view(), name='equipo-editar'),
    path('eliminar/<int:pk>/', EquipoDeleteView.as_view(), name='equipo-eliminar'),
    path('generar-qr/<int:pk>/', generar_qr_view, name='generar-qr'),
    path('codigos-qr/', views.codigo_qr_view, name='codigo-qr'),
    path('fichas-tecnicas/', views.fichas_tecnicas_view, name='fichas-tecnicas'),
    path('crear-ficha/<int:pk>/', views.crear_ficha_view, name='crear-ficha'),
    path('editar-ficha/<int:pk>/', views.editar_ficha_view, name='editar-ficha'),
    # NUEVAS URLs para PDF
    path('ficha-pdf/<int:pk>/', views.exportar_ficha_pdf_view, name='exportar-ficha-pdf'),
    path('imprimir-ficha/<int:pk>/', views.imprimir_ficha_view, name='imprimir-ficha'),
    path('ficha-detallada/<int:pk>/', views.ficha_detallada_view, name='ficha-detallada'),
]