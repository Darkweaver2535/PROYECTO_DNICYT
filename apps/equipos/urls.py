from django.urls import path
from .views import (
    EquipoListView,
    EquipoDetailView,
    EquipoCreateView,
    generar_qr_view,
)

app_name = 'equipos'

urlpatterns = [
    path('', EquipoListView.as_view(), name='equipo-lista'),
    path('detalle/<int:pk>/', EquipoDetailView.as_view(), name='equipo-detalle'),
    path('crear/', EquipoCreateView.as_view(), name='equipo-crear'),
    path('generar-qr/<int:pk>/', generar_qr_view, name='generar-qr'),
]