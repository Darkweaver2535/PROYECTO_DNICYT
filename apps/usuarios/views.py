from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from .models import PerfilUsuario, SesionUsuario, ConfiguracionUsuario
from .forms import (
    UsuarioCreateForm, PerfilUsuarioForm, UsuarioUpdateForm, 
    CambiarPasswordForm, ConfiguracionUsuarioForm
)

def es_administrador(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and (
        user.is_superuser or 
        hasattr(user, 'perfil') and user.perfil.rol_sistema == 'administrador'
    )

@login_required
@user_passes_test(es_administrador)
def usuarios_view(request):
    """Vista principal de administración de usuarios"""
    
    # Filtros
    search_query = request.GET.get('search', '')
    rol_filtro = request.GET.get('rol', '')
    estado_filtro = request.GET.get('estado', '')
    conexion_filtro = request.GET.get('ultima_conexion', '')
    
    # Query base CON ORDENAMIENTO para evitar warning
    usuarios = User.objects.select_related('perfil').order_by('username')
    
    # Aplicar filtros
    if search_query:
        usuarios = usuarios.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if rol_filtro:
        usuarios = usuarios.filter(perfil__rol_sistema=rol_filtro)
    
    if estado_filtro == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif estado_filtro == 'inactivo':
        usuarios = usuarios.filter(is_active=False)
    
    # Filtro por última conexión
    if conexion_filtro:
        ahora = timezone.now()
        if conexion_filtro == 'hoy':
            usuarios = usuarios.filter(perfil__ultima_actividad__date=ahora.date())
        elif conexion_filtro == 'semana':
            usuarios = usuarios.filter(perfil__ultima_actividad__gte=ahora - timedelta(days=7))
        elif conexion_filtro == 'mes':
            usuarios = usuarios.filter(perfil__ultima_actividad__gte=ahora - timedelta(days=30))
        elif conexion_filtro == 'nunca':
            usuarios = usuarios.filter(perfil__ultima_actividad__isnull=True)
    
    # ✅ CREAR/CORREGIR PERFILES ANTES DE ESTADÍSTICAS
    for user in User.objects.all():
        perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        if created or perfil.rol_sistema == 'operario' and user.is_superuser:
            # Corregir rol si es necesario
            if user.is_superuser or user.username == 'admin':
                perfil.rol_sistema = 'administrador'
                perfil.save()
                print(f"🔧 Corregido rol de {user.username} a administrador")
    
    # Estadísticas
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    administradores = User.objects.filter(
        Q(is_superuser=True) | Q(perfil__rol_sistema='administrador')
    ).count()
    operarios = User.objects.filter(perfil__rol_sistema='operario').count()
    
    # Conexiones hoy
    conexiones_hoy = User.objects.filter(
        perfil__ultima_actividad__date=timezone.now().date()
    ).count()
    
    # Paginación
    paginator = Paginator(usuarios, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Enriquecer datos de usuarios
    for usuario in page_obj:
        if hasattr(usuario, 'perfil'):
            usuario.rol_display = usuario.perfil.get_rol_sistema_display()
            usuario.rol_sistema = usuario.perfil.rol_sistema
            usuario.ultima_conexion = usuario.perfil.ultima_actividad
            usuario.iniciales = usuario.perfil.get_iniciales()
            usuario.color_avatar = usuario.perfil.get_color_avatar()
            
            # ✅ CORREGIR LÓGICA DE PERMISOS
            if usuario.perfil.rol_sistema == 'administrador' or usuario.is_superuser:
                usuario.permisos_display = ['Sistema', 'Reportes', 'Usuarios', 'Configuración']
            else:
                usuario.permisos_display = ['Básico', 'Operación']
        else:
            # Crear perfil si no existe
            perfil, created = PerfilUsuario.objects.get_or_create(user=usuario)
            # Asignar rol correcto al crear
            if usuario.is_superuser or usuario.username == 'admin':
                perfil.rol_sistema = 'administrador'
                perfil.save()
            
            usuario.rol_display = perfil.get_rol_sistema_display()
            usuario.rol_sistema = perfil.rol_sistema
            usuario.ultima_conexion = None
            usuario.iniciales = usuario.username[:2].upper()
            usuario.color_avatar = '#6b7280'
            usuario.permisos_display = ['Básico'] if perfil.rol_sistema == 'operario' else ['Sistema', 'Reportes']
    
    context = {
        'usuarios': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'rol_filtro': rol_filtro,
        'estado_filtro': estado_filtro,
        'conexion_filtro': conexion_filtro,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'administradores': administradores,
        'operarios': operarios,
        'conexiones_hoy': conexiones_hoy,
        'titulo': 'Administración de Usuarios',
    }
    
    return render(request, 'sistema_interno/usuarios.html', context)

@login_required
@user_passes_test(es_administrador)
def crear_usuario_view(request):
    """Vista para crear nuevo usuario"""
    
    if request.method == 'POST':
        user_form = UsuarioCreateForm(request.POST)
        perfil_form = PerfilUsuarioForm(request.POST, request.FILES)
        
        # Debug: imprimir errores
        if not user_form.is_valid():
            print("Errores en user_form:", user_form.errors)
        if not perfil_form.is_valid():
            print("Errores en perfil_form:", perfil_form.errors)
        
        if user_form.is_valid() and perfil_form.is_valid():
            try:
                # Crear usuario
                usuario = user_form.save()
                
                # Crear perfil
                perfil = perfil_form.save(commit=False)
                perfil.user = usuario
                perfil.save()
                
                # Crear configuración por defecto
                ConfiguracionUsuario.objects.create(usuario=usuario)
                
                messages.success(
                    request, 
                    f'Usuario "{usuario.username}" creado exitosamente.'
                )
                return redirect('usuarios:lista-usuarios')
                
            except Exception as e:
                print(f"Error al crear usuario: {e}")
                messages.error(
                    request, 
                    f'Error interno al crear el usuario: {str(e)}'
                )
        else:
            # Mostrar errores específicos
            error_msg = "Errores encontrados: "
            if user_form.errors:
                for field, errors in user_form.errors.items():
                    error_msg += f"{field}: {', '.join(errors)}. "
            if perfil_form.errors:
                for field, errors in perfil_form.errors.items():
                    error_msg += f"{field}: {', '.join(errors)}. "
            
            messages.error(request, error_msg)
    else:
        user_form = UsuarioCreateForm()
        perfil_form = PerfilUsuarioForm()
    
    # Estadísticas para el contexto
    stats = {
        'total_usuarios': User.objects.count(),
        'usuarios_activos': User.objects.filter(is_active=True).count(),
        'administradores': User.objects.filter(
            Q(is_superuser=True) | Q(perfil__rol_sistema='administrador')
        ).count(),
    }
    
    context = {
        'form': user_form,
        'perfil_form': perfil_form,
        'accion': 'crear',
        'titulo': 'Crear Nuevo Usuario',
        'stats': stats,
    }
    
    return render(request, 'sistema_interno/crear_editar_usuarios.html', context)

@login_required
def detalle_usuario_view(request, pk):
    """Vista de detalle de usuario"""
    
    usuario = get_object_or_404(User, pk=pk)
    
    # Verificar permisos (solo administradores o el mismo usuario)
    if not (es_administrador(request.user) or request.user == usuario):
        messages.error(request, 'No tiene permisos para ver este perfil.')
        return redirect('sistema_interno:dashboard')
    
    # Obtener o crear perfil
    perfil, created = PerfilUsuario.objects.get_or_create(user=usuario)
    
    # Estadísticas del usuario
    ahora = timezone.now()
    sesiones_recientes = SesionUsuario.objects.filter(
        usuario=usuario,
        fecha_inicio__gte=ahora - timedelta(days=30)
    ).order_by('-fecha_inicio')[:10]
    
    # Actividad reciente
    total_sesiones = SesionUsuario.objects.filter(usuario=usuario).count()
    sesiones_mes = SesionUsuario.objects.filter(
        usuario=usuario,
        fecha_inicio__gte=ahora - timedelta(days=30)
    ).count()
    
    # Tiempo promedio de sesión
    sesiones_completadas = SesionUsuario.objects.filter(
        usuario=usuario,
        fecha_fin__isnull=False
    )
    
    tiempo_promedio_sesion = None
    if sesiones_completadas.exists():
        duraciones = [s.duracion_sesion().total_seconds() for s in sesiones_completadas]
        tiempo_promedio_sesion = sum(duraciones) / len(duraciones) / 3600  # en horas
    
    context = {
        'usuario': usuario,
        'perfil': perfil,
        'sesiones_recientes': sesiones_recientes,
        'total_sesiones': total_sesiones,
        'sesiones_mes': sesiones_mes,
        'tiempo_promedio_sesion': round(tiempo_promedio_sesion, 2) if tiempo_promedio_sesion else 0,
        'puede_editar': es_administrador(request.user) or request.user == usuario,
        'titulo': f'Perfil de {usuario.get_full_name() or usuario.username}',
    }
    
    return render(request, 'sistema_interno/detalle_usuario.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_usuario_view(request, pk):
    """Vista para editar usuario existente"""
    
    usuario = get_object_or_404(User, pk=pk)
    perfil, created = PerfilUsuario.objects.get_or_create(user=usuario)
    
    if request.method == 'POST':
        user_form = UsuarioUpdateForm(request.POST, instance=usuario)
        perfil_form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            
            messages.success(
                request, 
                f'Usuario "{usuario.username}" actualizado exitosamente.'
            )
            return redirect('usuarios:detalle-usuario', pk=usuario.pk)
        else:
            messages.error(
                request, 
                'Error al actualizar el usuario. Por favor revise los campos marcados.'
            )
    else:
        user_form = UsuarioUpdateForm(instance=usuario)
        perfil_form = PerfilUsuarioForm(instance=perfil)
    
    context = {
        'form': user_form,
        'perfil_form': perfil_form,
        'usuario': usuario,
        'accion': 'editar',
        'titulo': f'Editar Usuario - {usuario.username}',
    }
    
    return render(request, 'sistema_interno/crear_editar_usuarios.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_usuario_view(request, pk):
    """Vista para eliminar usuario"""
    
    usuario = get_object_or_404(User, pk=pk)
    
    # Prevenir auto-eliminación
    if usuario == request.user:
        messages.error(request, 'No puede eliminar su propia cuenta.')
        return redirect('usuarios:lista-usuarios')
    
    if request.method == 'POST':
        # Verificar confirmación del nombre de usuario
        confirmacion_username = request.POST.get('confirmacion_username', '')
        
        if confirmacion_username != usuario.username:
            messages.error(
                request, 
                'El nombre de usuario de confirmación no coincide. Eliminación cancelada.'
            )
            return render(request, 'sistema_interno/confirmar_eliminar_usuario.html', {
                'usuario': usuario,
                'titulo': f'Eliminar Usuario - {usuario.username}',
            })
        
        nombre_usuario = usuario.get_full_name() or usuario.username
        
        try:
            usuario.delete()
            messages.success(
                request, 
                f'Usuario "{nombre_usuario}" eliminado exitosamente.'
            )
        except Exception as e:
            messages.error(
                request, 
                f'Error al eliminar el usuario: {str(e)}'
            )
        
        return redirect('usuarios:lista-usuarios')
    
    context = {
        'usuario': usuario,
        'titulo': f'Eliminar Usuario - {usuario.username}',
    }
    
    return render(request, 'sistema_interno/confirmar_eliminar_usuario.html', context)

@login_required
def cambiar_password_view(request, pk=None):
    """Vista para cambiar contraseña"""
    
    if pk and es_administrador(request.user):
        usuario = get_object_or_404(User, pk=pk)
    else:
        usuario = request.user
    
    if request.method == 'POST':
        form = CambiarPasswordForm(usuario, request.POST)
        
        if form.is_valid():
            nueva_password = form.cleaned_data['password_nueva']
            usuario.set_password(nueva_password)
            usuario.save()
            
            messages.success(
                request, 
                'Contraseña cambiada exitosamente.'
            )
            
            if usuario == request.user:
                # Si cambió su propia contraseña, redireccionar al login
                return redirect('login')
            else:
                return redirect('usuarios:detalle-usuario', pk=usuario.pk)
        else:
            messages.error(
                request, 
                'Error al cambiar la contraseña. Por favor revise los campos marcados.'
            )
    else:
        form = CambiarPasswordForm(usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'titulo': f'Cambiar Contraseña - {usuario.username}',
    }
    
    return render(request, 'sistema_interno/cambiar_password.html', context)

@login_required
def mi_perfil_view(request):
    """Vista del perfil del usuario actual"""
    return detalle_usuario_view(request, request.user.pk)

@login_required
def configuracion_usuario_view(request):
    """Vista para configuraciones del usuario"""
    
    config, created = ConfiguracionUsuario.objects.get_or_create(
        usuario=request.user
    )
    
    if request.method == 'POST':
        form = ConfiguracionUsuarioForm(request.POST, instance=config)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada exitosamente.')
            return redirect('usuarios:configuracion')
        else:
            messages.error(request, 'Error al guardar la configuración.')
    else:
        form = ConfiguracionUsuarioForm(instance=config)
    
    context = {
        'form': form,
        'titulo': 'Configuración de Usuario',
    }
    
    return render(request, 'sistema_interno/configuracion_usuario.html', context)

# API Views para AJAX
@login_required
def api_usuarios_stats(request):
    """API para estadísticas de usuarios"""
    
    if not es_administrador(request.user):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    ahora = timezone.now()
    
    stats = {
        'usuarios_activos': User.objects.filter(is_active=True).count(),
        'conexiones_hoy': User.objects.filter(
            perfil__ultima_actividad__date=ahora.date()
        ).count(),
        'nuevos_usuarios_mes': User.objects.filter(
            date_joined__gte=ahora - timedelta(days=30)
        ).count(),
        'administradores': User.objects.filter(
            Q(is_superuser=True) | Q(perfil__rol_sistema='administrador')
        ).count(),
    }
    
    return JsonResponse(stats)
