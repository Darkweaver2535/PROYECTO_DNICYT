from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from .models import Equipo
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

class EquipoListView(ListView):
    model = Equipo
    template_name = 'equipos/lista.html'
    context_object_name = 'equipos'
    paginate_by = 10

class EquipoDetailView(DetailView):
    model = Equipo
    template_name = 'equipos/detalle.html'
    context_object_name = 'equipo'

class EquipoCreateView(CreateView):
    model = Equipo
    template_name = 'equipos/crear.html'
    fields = [
        'codigo_interno', 'nombre', 'modelo', 'serie', 'fabricante', 'año_fabricacion',
        'potencia', 'capacidad', 'ubicacion_fisica', 'seccion', 'tipo_equipo',
        'estado', 'foto', 'responsable', 'observaciones'
    ]
    success_url = reverse_lazy('equipos:equipo-lista')

def generar_qr_view(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    url = request.build_absolute_uri(reverse('equipos:equipo-detalle', kwargs={'pk': equipo.pk}))
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    filename = f'equipo_{equipo.pk}_qr.png'
    equipo.qr_code.save(filename, ContentFile(buffer.getvalue()), save=True)
    return redirect('equipos:equipo-detalle', pk=equipo.pk)

@login_required
def mi_vista(request):
    messages.success(request, '¡Inicio de sesión exitoso!')
    messages.error(request, 'Usuario o contraseña incorrectos')

def mi_ajax_view(request):
    return JsonResponse({'success': True, 'message': 'OK'})
