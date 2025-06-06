from django.urls import path
from .views import (
    EquipoListView,
    EquipoDetailView,
    EquipoCreateView,
    EquipoUpdateView,      # <-- Agrega esta importación
    EquipoDeleteView,      # <-- Agrega esta importación
    generar_qr_view,
)

app_name = 'equipos'

urlpatterns = [
    path('', EquipoListView.as_view(), name='equipo-lista'),
    path('detalle/<int:pk>/', EquipoDetailView.as_view(), name='equipo-detalle'),
    path('crear/', EquipoCreateView.as_view(), name='equipo-crear'),
    path('editar/<int:pk>/', EquipoUpdateView.as_view(), name='equipo-editar'),      # <-- Agrega esta línea
    path('eliminar/<int:pk>/', EquipoDeleteView.as_view(), name='equipo-eliminar'),  # <-- Agrega esta línea
    path('generar-qr/<int:pk>/', generar_qr_view, name='generar-qr'),
]