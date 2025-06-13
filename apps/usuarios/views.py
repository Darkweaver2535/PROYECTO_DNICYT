from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from .models import (
    PerfilUsuario, SesionUsuario, ConfiguracionUsuario, 
    RolPersonalizado, PermisoSistema, HistorialRoles
)
from .forms import (
    UsuarioCreateForm, PerfilUsuarioForm, UsuarioUpdateForm, 
    CambiarPasswordForm, ConfiguracionUsuarioForm,
    RolPersonalizadoForm, AsignarRolForm, PermisoSistemaForm
)

import subprocess
import os
from django.conf import settings
from django.http import HttpResponse, FileResponse
import zipfile
import tempfile
from datetime import datetime
import json

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

@login_required
@user_passes_test(es_administrador)
def roles_permisos_view(request):
    """Vista principal para administrar roles y permisos del sistema"""
    
    # Roles del sistema (predefinidos)
    roles_sistema = [
        {
            'id': 'administrador',
            'nombre': 'Administrador',
            'descripcion': 'Control total del sistema, incluyendo usuarios, equipos y configuraciones',
            'usuarios_count': User.objects.filter(perfil__rol_sistema='administrador').count(),
            'color': '#ef4444',
            'icono': 'bi-shield-lock',
            'es_sistema': True,
            'permisos': [
                {'nombre': 'Gestionar Usuarios', 'descripcion': 'Crear, editar y eliminar usuarios', 'codigo': 'gestionar_usuarios'},
                {'nombre': 'Configurar Sistema', 'descripcion': 'Modificar parámetros globales del sistema', 'codigo': 'configurar_sistema'},
                {'nombre': 'Administrar Equipos', 'descripcion': 'Control total sobre equipos industriales', 'codigo': 'eliminar_equipos'},
                {'nombre': 'Ver Todos los Reportes', 'descripcion': 'Acceso a todos los reportes del sistema', 'codigo': 'ver_todos_reportes'},
                {'nombre': 'Gestionar Mantenimientos', 'descripcion': 'Crear y asignar tareas de mantenimiento', 'codigo': 'gestionar_mantenimiento'},
                {'nombre': 'Gestionar Inventario', 'descripcion': 'Control total de inventario y materiales', 'codigo': 'gestionar_inventario'},
                {'nombre': 'Eliminar Registros', 'descripcion': 'Eliminar registros permanentemente', 'codigo': 'eliminar_registros'},
                {'nombre': 'Exportar Datos', 'descripcion': 'Exportar datos del sistema', 'codigo': 'exportar_datos'},
            ]
        },
        {
            'id': 'operario',
            'nombre': 'Operario',
            'descripcion': 'Acceso limitado al sistema para operaciones diarias',
            'usuarios_count': User.objects.filter(perfil__rol_sistema='operario').count(),
            'color': '#10b981',
            'icono': 'bi-person-badge',
            'es_sistema': True,
            'permisos': [
                {'nombre': 'Ver Equipos', 'descripcion': 'Ver lista y detalles de equipos', 'codigo': 'ver_equipos'},
                {'nombre': 'Crear Reportes', 'descripcion': 'Crear reportes de operaciones', 'codigo': 'crear_reportes'},
                {'nombre': 'Ver Inventario', 'descripcion': 'Ver niveles de inventario', 'codigo': 'ver_inventario'},
                {'nombre': 'Registrar Operaciones', 'descripcion': 'Registrar operaciones diarias', 'codigo': 'registrar_operaciones'},
                {'nombre': 'Ver Manuales', 'descripcion': 'Ver manuales y documentación técnica', 'codigo': 'ver_manuales'},
            ]
        }
    ]
    
    # Roles personalizados
    roles_personalizados = []
    for rol in RolPersonalizado.objects.filter(activo=True):
        permisos_data = []
        for permiso in rol.permisos.filter(activo=True):
            permisos_data.append({
                'nombre': permiso.nombre,
                'descripcion': permiso.descripcion,
                'codigo': permiso.codigo
            })
        
        roles_personalizados.append({
            'id': f'custom_{rol.id}',
            'obj': rol,
            'nombre': rol.nombre,
            'descripcion': rol.descripcion,
            'usuarios_count': rol.get_usuarios_count(),
            'color': rol.color,
            'icono': rol.icono,
            'es_sistema': False,
            'permisos': permisos_data
        })
    
    # Combinar todos los roles
    todos_roles = roles_sistema + roles_personalizados
    
    # Estadísticas mejoradas
    stats = {
        'total_usuarios': User.objects.count(),
        'administradores': User.objects.filter(perfil__rol_sistema='administrador').count(),
        'operarios': User.objects.filter(perfil__rol_sistema='operario').count(),
        'roles_personalizados': RolPersonalizado.objects.filter(activo=True).count(),
        'permisos_sistema': PermisoSistema.objects.filter(activo=True).count(),
        'usuarios_con_roles_personalizados': User.objects.filter(perfil__rol_personalizado__isnull=False).count(),
    }
    
    # Actividad reciente desde el historial
    actividad_reciente = HistorialRoles.objects.select_related(
        'usuario', 'rol_afectado', 'usuario_afectado'
    ).order_by('-fecha')[:10]
    
    # Permisos por categoría para estadísticas CON PORCENTAJES
    permisos_por_categoria = {}
    max_permisos = 0
    
    for permiso in PermisoSistema.objects.filter(activo=True):
        categoria = permiso.get_categoria_display()
        if categoria not in permisos_por_categoria:
            permisos_por_categoria[categoria] = []
        permisos_por_categoria[categoria].append(permiso)
    
    # Encontrar el máximo para calcular porcentajes
    if permisos_por_categoria:
        max_permisos = max(len(permisos) for permisos in permisos_por_categoria.values())
    
    # Agregar información de porcentaje
    permisos_con_stats = {}
    for categoria, permisos in permisos_por_categoria.items():
        count = len(permisos)
        percentage = (count / max_permisos * 100) if max_permisos > 0 else 0
        permisos_con_stats[categoria] = {
            'permisos': permisos,
            'count': count,
            'percentage': round(percentage, 1)
        }
    
    context = {
        'titulo': 'Roles y Permisos',
        'roles': todos_roles,
        'stats': stats,
        'actividad_reciente': actividad_reciente,
        'permisos_por_categoria': permisos_con_stats,  # ✅ USAR LA NUEVA ESTRUCTURA
    }
    
    return render(request, 'sistema_interno/roles_permisos.html', context)

@login_required
@user_passes_test(es_administrador)
def crear_rol_view(request):
    """Vista para crear un nuevo rol personalizado"""
    
    if request.method == 'POST':
        form = RolPersonalizadoForm(request.POST)
        
        if form.is_valid():
            rol = form.save(commit=False)
            rol.creado_por = request.user
            rol.save()
            form.save_m2m()  # Guardar permisos many-to-many
            
            # ✅ REGISTRAR EN HISTORIAL
            registrar_cambio_historial(
                usuario=request.user,
                accion='crear_rol',
                descripcion=f'Creó el rol "{rol.nombre}" con {rol.permisos.count()} permisos',
                rol_afectado=rol,
                datos_nuevos={
                    'nombre': rol.nombre,
                    'descripcion': rol.descripcion,
                    'permisos': list(rol.permisos.values_list('codigo', flat=True))
                },
                request=request
            )
            
            messages.success(request, f'Rol "{rol.nombre}" creado exitosamente.')
            return redirect('usuarios:roles-permisos')
        else:
            messages.error(request, 'Error al crear el rol. Verifique los datos ingresados.')
    else:
        form = RolPersonalizadoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Rol',
        'accion': 'crear'
    }
    
    return render(request, 'sistema_interno/crear_editar_rol.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_rol_view(request, rol_id):
    """Vista para editar un rol personalizado existente"""
    
    rol = get_object_or_404(RolPersonalizado, id=rol_id)
    
    if request.method == 'POST':
        # Guardar datos antiguos para historial
        datos_antiguos = {
            'nombre': rol.nombre,
            'descripcion': rol.descripcion,
            'permisos': list(rol.permisos.values_list('codigo', flat=True)),
            'activo': rol.activo
        }
        
        form = RolPersonalizadoForm(request.POST, instance=rol)
        
        if form.is_valid():
            rol_actualizado = form.save()
            
            # Datos nuevos para historial
            datos_nuevos = {
                'nombre': rol_actualizado.nombre,
                'descripcion': rol_actualizado.descripcion,
                'permisos': list(rol_actualizado.permisos.values_list('codigo', flat=True)),
                'activo': rol_actualizado.activo
            }
            
            # ✅ REGISTRAR EN HISTORIAL
            registrar_cambio_historial(
                usuario=request.user,
                accion='editar_rol',
                descripcion=f'Editó el rol "{rol_actualizado.nombre}"',
                rol_afectado=rol_actualizado,
                datos_antiguos=datos_antiguos,
                datos_nuevos=datos_nuevos,
                request=request
            )
            
            messages.success(request, f'Rol "{rol_actualizado.nombre}" actualizado exitosamente.')
            return redirect('usuarios:roles-permisos')
        else:
            messages.error(request, 'Error al actualizar el rol. Verifique los datos ingresados.')
    else:
        form = RolPersonalizadoForm(instance=rol)
    
    context = {
        'form': form,
        'rol': rol,
        'titulo': f'Editar Rol - {rol.nombre}',
        'accion': 'editar'
    }
    
    return render(request, 'sistema_interno/crear_editar_rol.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_rol_view(request, rol_id):
    """Vista para eliminar un rol personalizado"""
    
    rol = get_object_or_404(RolPersonalizado, id=rol_id)
    
    if rol.es_sistema:
        messages.error(request, 'No se pueden eliminar roles del sistema.')
        return redirect('usuarios:roles-permisos')
    
    if request.method == 'POST':
        usuarios_afectados = User.objects.filter(perfil__rol_personalizado=rol).count()
        
        if usuarios_afectados > 0:
            # Remover rol de usuarios afectados
            User.objects.filter(perfil__rol_personalizado=rol).update(perfil__rol_personalizado=None)
            
            # Registrar cambios para cada usuario
            for usuario in User.objects.filter(perfil__rol_personalizado=rol):
                HistorialRoles.objects.create(
                    usuario=request.user,
                    accion='cambiar_rol_usuario',
                    descripcion=f'Removió rol "{rol.nombre}" del usuario {usuario.username}',
                    rol_afectado=rol,
                    usuario_afectado=usuario,
                    ip_address=get_client_ip(request)
                )
        
        nombre_rol = rol.nombre
        
        # Registrar eliminación en historial
        HistorialRoles.objects.create(
            usuario=request.user,
            accion='eliminar_rol',
            descripcion=f'Eliminó el rol "{nombre_rol}" (afectó a {usuarios_afectados} usuarios)',
            datos_antiguos={'nombre': nombre_rol, 'usuarios_afectados': usuarios_afectados},
            ip_address=get_client_ip(request)
        )
        
        rol.delete()
        
        messages.success(
            request, 
            f'Rol "{nombre_rol}" eliminado exitosamente. {usuarios_afectados} usuarios fueron afectados.'
        )
        return redirect('usuarios:roles-permisos')
    
    context = {
        'rol': rol,
        'usuarios_afectados': User.objects.filter(perfil__rol_personalizado=rol).count(),
        'titulo': f'Eliminar Rol - {rol.nombre}'
    }
    
    return render(request, 'sistema_interno/eliminar_rol.html', context)

@login_required
@user_passes_test(es_administrador)
def asignar_rol_view(request):
    """Vista para asignar roles a usuarios"""
    
    if request.method == 'POST':
        form = AsignarRolForm(request.POST)
        
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            rol_sistema = form.cleaned_data['rol_sistema']
            rol_personalizado = form.cleaned_data['rol_personalizado']
            
            # Obtener o crear perfil
            perfil, created = PerfilUsuario.objects.get_or_create(user=usuario)
            
            # Guardar datos antiguos
            datos_antiguos = {
                'rol_sistema': perfil.rol_sistema,
                'rol_personalizado': perfil.rol_personalizado.nombre if perfil.rol_personalizado else None
            }
            
            # Actualizar roles
            if rol_sistema:
                perfil.rol_sistema = rol_sistema
            if rol_personalizado:
                perfil.rol_personalizado = rol_personalizado
            elif 'rol_personalizado' in form.cleaned_data:  # Si se envió pero es None
                perfil.rol_personalizado = None
                
            perfil.save()
            
            # Datos nuevos
            datos_nuevos = {
                'rol_sistema': perfil.rol_sistema,
                'rol_personalizado': perfil.rol_personalizado.nombre if perfil.rol_personalizado else None
            }
            
            # ✅ REGISTRAR EN HISTORIAL
            registrar_cambio_historial(
                usuario=request.user,
                accion='cambiar_rol_usuario',
                descripcion=f'Cambió el rol del usuario "{usuario.get_full_name() or usuario.username}"',
                usuario_afectado=usuario,
                rol_afectado=rol_personalizado,
                datos_antiguos=datos_antiguos,
                datos_nuevos=datos_nuevos,
                request=request
            )
            
            messages.success(request, f'Rol asignado exitosamente a {usuario.get_full_name() or usuario.username}.')
            return redirect('usuarios:roles-permisos')
        else:
            messages.error(request, 'Error al asignar el rol. Verifique los datos.')
    else:
        form = AsignarRolForm()
    
    context = {
        'form': form,
        'titulo': 'Asignar Rol a Usuario'
    }
    
    return render(request, 'sistema_interno/asignar_rol.html', context)

@login_required
@user_passes_test(es_administrador)
def gestionar_permisos_view(request):
    """Vista para gestionar permisos del sistema"""
    
    # Obtener permisos agrupados por categoría
    permisos_por_categoria = {}
    for permiso in PermisoSistema.objects.all().order_by('categoria', 'nombre'):
        categoria = permiso.get_categoria_display()
        if categoria not in permisos_por_categoria:
            permisos_por_categoria[categoria] = []
        permisos_por_categoria[categoria].append(permiso)
    
    # Estadísticas
    stats = {
        'total_permisos': PermisoSistema.objects.count(),
        'permisos_activos': PermisoSistema.objects.filter(activo=True).count(),
        'permisos_criticos': PermisoSistema.objects.filter(es_critico=True).count(),
        'categorias': len(PermisoSistema.CATEGORIA_CHOICES),
    }
    
    context = {
        'permisos_por_categoria': permisos_por_categoria,
        'stats': stats,
        'titulo': 'Gestión de Permisos'
    }
    
    return render(request, 'sistema_interno/gestionar_permisos.html', context)

@login_required
@user_passes_test(es_administrador)
def historial_roles_view(request):
    """Vista para ver el historial de cambios en roles"""
    
    # Filtros
    accion_filtro = request.GET.get('accion', '')
    usuario_filtro = request.GET.get('usuario', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    rol_filtro = request.GET.get('rol', '')
    
    # Query base
    historial = HistorialRoles.objects.select_related(
        'usuario', 'rol_afectado', 'usuario_afectado', 'permiso_afectado'
    ).order_by('-fecha')
    
    # Aplicar filtros
    if accion_filtro:
        historial = historial.filter(accion=accion_filtro)
    
    if usuario_filtro:
        historial = historial.filter(
            Q(usuario__username__icontains=usuario_filtro) |
            Q(usuario__first_name__icontains=usuario_filtro) |
            Q(usuario__last_name__icontains=usuario_filtro)
        )
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            historial = historial.filter(fecha__date__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            historial = historial.filter(fecha__date__lte=fecha_hasta_obj)
        except ValueError:
            pass
            
    if rol_filtro:
        historial = historial.filter(
            Q(rol_afectado__nombre__icontains=rol_filtro) |
            Q(descripcion__icontains=rol_filtro)
        )
    
    # Paginación
    paginator = Paginator(historial, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas del historial
    ahora = timezone.now()
    stats = {
        'total_cambios': HistorialRoles.objects.count(),
        'cambios_hoy': HistorialRoles.objects.filter(fecha__date=ahora.date()).count(),
        'cambios_semana': HistorialRoles.objects.filter(fecha__gte=ahora - timedelta(days=7)).count(),
        'cambios_mes': HistorialRoles.objects.filter(fecha__gte=ahora - timedelta(days=30)).count(),
        'usuarios_activos': HistorialRoles.objects.values('usuario').distinct().count(),
        'roles_afectados': HistorialRoles.objects.filter(rol_afectado__isnull=False).values('rol_afectado').distinct().count(),
    }
    
    # Actividad por tipo de acción (para gráfico)
    actividad_por_accion = {}
    for choice in HistorialRoles.ACCION_CHOICES:
        codigo, nombre = choice
        count = HistorialRoles.objects.filter(accion=codigo).count()
        if count > 0:
            actividad_por_accion[nombre] = count
    
    # Top usuarios con más cambios
    top_usuarios = HistorialRoles.objects.values(
        'usuario__username', 'usuario__first_name', 'usuario__last_name'
    ).annotate(
        total_cambios=Count('id')
    ).order_by('-total_cambios')[:5]
    
    # Actividad reciente (últimos 7 días) por día
    actividad_semanal = []
    for i in range(7):
        fecha = ahora.date() - timedelta(days=i)
        cambios = HistorialRoles.objects.filter(fecha__date=fecha).count()
        actividad_semanal.append({
            'fecha': fecha.strftime('%d/%m'),
            'cambios': cambios
        })
    actividad_semanal.reverse()
    
    context = {
        'historial': page_obj,
        'page_obj': page_obj,
        'accion_filtro': accion_filtro,
        'usuario_filtro': usuario_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'rol_filtro': rol_filtro,
        'stats': stats,
        'actividad_por_accion': actividad_por_accion,
        'top_usuarios': top_usuarios,
        'actividad_semanal': actividad_semanal,
        'acciones_choices': HistorialRoles.ACCION_CHOICES,
        'titulo': 'Historial de Roles y Permisos'
    }
    
    return render(request, 'sistema_interno/historial_roles.html', context)

@login_required
@user_passes_test(es_administrador)
def api_usuarios_stats(request):
    """API para estadísticas de usuarios"""
    
    stats = {
        'total_usuarios': User.objects.count(),
        'usuarios_activos': User.objects.filter(is_active=True).count(),
        'administradores': User.objects.filter(
            Q(is_superuser=True) | Q(perfil__rol_sistema='administrador')
        ).count(),
        'operarios': User.objects.filter(perfil__rol_sistema='operario').count(),
        'roles_personalizados': RolPersonalizado.objects.filter(activo=True).count(),
        'conexiones_hoy': User.objects.filter(
            perfil__ultima_actividad__date=timezone.now().date()
        ).count(),
    }
    
    return JsonResponse(stats)

@login_required
@user_passes_test(es_administrador)
def ver_permisos_rol_view(request, rol_id):
    """Vista para ver permisos detallados de un rol específico"""
    
    # Determinar si es rol del sistema o personalizado
    if rol_id in ['administrador', 'operario']:
        # Es un rol del sistema
        es_rol_sistema = True
        rol_nombre = 'Administrador' if rol_id == 'administrador' else 'Operario'
        
        # Permisos predefinidos del sistema
        if rol_id == 'administrador':
            permisos_sistema = [
                {
                    'codigo': 'gestionar_usuarios',
                    'nombre': 'Gestionar Usuarios',
                    'descripcion': 'Crear, editar, eliminar y administrar usuarios del sistema',
                    'categoria': 'Gestión de Usuarios',
                    'es_critico': True,
                    'activo': True,
                    'grupo': 'Administración'
                },
                {
                    'codigo': 'configurar_sistema',
                    'nombre': 'Configurar Sistema',
                    'descripcion': 'Modificar parámetros globales y configuraciones del sistema',
                    'categoria': 'Configuración del Sistema',
                    'es_critico': True,
                    'activo': True,
                    'grupo': 'Administración'
                },
                {
                    'codigo': 'eliminar_equipos',
                    'nombre': 'Administrar Equipos',
                    'descripcion': 'Control total sobre equipos industriales, incluyendo eliminación',
                    'categoria': 'Gestión de Equipos',
                    'es_critico': True,
                    'activo': True,
                    'grupo': 'Equipos'
                },
                {
                    'codigo': 'ver_todos_reportes',
                    'nombre': 'Ver Todos los Reportes',
                    'descripcion': 'Acceso completo a todos los reportes y análisis del sistema',
                    'categoria': 'Reportes y Análisis',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Reportes'
                },
                {
                    'codigo': 'gestionar_mantenimiento',
                    'nombre': 'Gestionar Mantenimientos',
                    'descripcion': 'Crear, asignar y supervisar tareas de mantenimiento',
                    'categoria': 'Mantenimiento',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Operaciones'
                },
                {
                    'codigo': 'gestionar_inventario',
                    'nombre': 'Gestionar Inventario',
                    'descripcion': 'Control total de inventario, materiales y stock',
                    'categoria': 'Gestión de Inventario',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Inventario'
                },
                {
                    'codigo': 'eliminar_registros',
                    'nombre': 'Eliminar Registros',
                    'descripcion': 'Eliminar registros permanentemente del sistema',
                    'categoria': 'Configuración del Sistema',
                    'es_critico': True,
                    'activo': True,
                    'grupo': 'Administración'
                },
                {
                    'codigo': 'exportar_datos',
                    'nombre': 'Exportar Datos',
                    'descripcion': 'Exportar información y generar respaldos de datos',
                    'categoria': 'Reportes y Análisis',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Reportes'
                },
                {
                    'codigo': 'gestionar_roles',
                    'nombre': 'Gestionar Roles y Permisos',
                    'descripcion': 'Crear, editar y asignar roles personalizados',
                    'categoria': 'Gestión de Usuarios',
                    'es_critico': True,
                    'activo': True,
                    'grupo': 'Administración'
                },
                {
                    'codigo': 'ver_auditoria',
                    'nombre': 'Ver Auditoría',
                    'descripcion': 'Acceso al historial completo de cambios y actividades',
                    'categoria': 'Configuración del Sistema',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Administración'
                }
            ]
            usuarios_count = User.objects.filter(
                Q(is_superuser=True) | Q(perfil__rol_sistema='administrador')
            ).count()
            color = '#ef4444'
            icono = 'bi-shield-lock'
            
        else:  # operario
            permisos_sistema = [
                {
                    'codigo': 'ver_equipos',
                    'nombre': 'Ver Equipos',
                    'descripcion': 'Consultar lista y detalles de equipos industriales',
                    'categoria': 'Gestión de Equipos',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Equipos'
                },
                {
                    'codigo': 'crear_reportes',
                    'nombre': 'Crear Reportes',
                    'descripcion': 'Generar reportes de operaciones y actividades diarias',
                    'categoria': 'Reportes y Análisis',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Reportes'
                },
                {
                    'codigo': 'ver_inventario',
                    'nombre': 'Ver Inventario',
                    'descripcion': 'Consultar niveles de stock y disponibilidad de materiales',
                    'categoria': 'Gestión de Inventario',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Inventario'
                },
                {
                    'codigo': 'registrar_operaciones',
                    'nombre': 'Registrar Operaciones',
                    'descripcion': 'Registrar operaciones diarias y actividades de trabajo',
                    'categoria': 'Operaciones Diarias',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Operaciones'
                },
                {
                    'codigo': 'ver_manuales',
                    'nombre': 'Ver Manuales',
                    'descripcion': 'Acceso a manuales técnicos y documentación operativa',
                    'categoria': 'Operaciones Diarias',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Documentación'
                },
                {
                    'codigo': 'reportar_incidencias',
                    'nombre': 'Reportar Incidencias',
                    'descripcion': 'Reportar fallas, problemas y situaciones irregulares',
                    'categoria': 'Seguridad Industrial',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Seguridad'
                },
                {
                    'codigo': 'usar_equipos',
                    'nombre': 'Usar Equipos',
                    'descripcion': 'Operar equipos asignados según protocolos establecidos',
                    'categoria': 'Operaciones Diarias',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Operaciones'
                },
                {
                    'codigo': 'ver_mi_perfil',
                    'nombre': 'Ver Mi Perfil',
                    'descripcion': 'Acceder y modificar información personal básica',
                    'categoria': 'Gestión de Usuarios',
                    'es_critico': False,
                    'activo': True,
                    'grupo': 'Personal'
                }
            ]
            usuarios_count = User.objects.filter(perfil__rol_sistema='operario').count()
            color = '#10b981'
            icono = 'bi-person-badge'
        
        rol_obj = None
        
    else:
        # Es un rol personalizado
        es_rol_sistema = False
        try:
            rol_obj = get_object_or_404(RolPersonalizado, id=int(rol_id))
            rol_nombre = rol_obj.nombre
            usuarios_count = rol_obj.get_usuarios_count()
            color = rol_obj.color
            icono = rol_obj.icono
            
            # Convertir permisos del modelo a formato esperado
            permisos_sistema = []
            for permiso in rol_obj.permisos.filter(activo=True):
                permisos_sistema.append({
                    'codigo': permiso.codigo,
                    'nombre': permiso.nombre,
                    'descripcion': permiso.descripcion,
                    'categoria': permiso.get_categoria_display(),
                    'es_critico': permiso.es_critico,
                    'activo': permiso.activo,
                    'grupo': permiso.get_categoria_display()
                })
                
        except (ValueError, RolPersonalizado.DoesNotExist):
            messages.error(request, 'Rol no encontrado.')
            return redirect('usuarios:roles-permisos')
    
    # Agrupar permisos por categoría
    permisos_por_categoria = {}
    for permiso in permisos_sistema:
        categoria = permiso['grupo']
        if categoria not in permisos_por_categoria:
            permisos_por_categoria[categoria] = []
        permisos_por_categoria[categoria].append(permiso)
    
    # Estadísticas del rol
    stats = {
        'total_permisos': len(permisos_sistema),
        'permisos_criticos': len([p for p in permisos_sistema if p['es_critico']]),
        'permisos_activos': len([p for p in permisos_sistema if p['activo']]),
        'usuarios_asignados': usuarios_count,
        'categorias': len(permisos_por_categoria),
    }
    
    # Usuarios con este rol (para mostrar en la vista)
    if es_rol_sistema:
        if rol_id == 'administrador':
            usuarios_con_rol = User.objects.filter(
                Q(is_superuser=True) | Q(perfil__rol_sistema='administrador')
            ).select_related('perfil')[:10]
        else:
            usuarios_con_rol = User.objects.filter(
                perfil__rol_sistema='operario'
            ).select_related('perfil')[:10]
    else:
        usuarios_con_rol = User.objects.filter(
            perfil__rol_personalizado=rol_obj
        ).select_related('perfil')[:10]
    
    context = {
        'titulo': f'Permisos del Rol: {rol_nombre}',
        'rol_id': rol_id,
        'rol_nombre': rol_nombre,
        'rol_obj': rol_obj,
        'es_rol_sistema': es_rol_sistema,
        'permisos_por_categoria': permisos_por_categoria,
        'stats': stats,
        'usuarios_con_rol': usuarios_con_rol,
        'color': color,
        'icono': icono,
    }
    
    return render(request, 'sistema_interno/ver_permisos_rol.html', context)

# Función auxiliar para obtener IP del cliente
def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Función auxiliar para registrar cambios en el historial
def registrar_cambio_historial(usuario, accion, descripcion, rol_afectado=None, usuario_afectado=None, permiso_afectado=None, datos_antiguos=None, datos_nuevos=None, request=None):
    """Registra un cambio en el historial de roles"""
    ip_address = None
    if request:
        ip_address = get_client_ip(request)
    
    HistorialRoles.objects.create(
        usuario=usuario,
        accion=accion,
        descripcion=descripcion,
        rol_afectado=rol_afectado,
        usuario_afectado=usuario_afectado,
        permiso_afectado=permiso_afectado,
        datos_antiguos=datos_antiguos or {},
        datos_nuevos=datos_nuevos or {},
        ip_address=ip_address
    )

@login_required
@user_passes_test(es_administrador)
def respaldos_view(request):
    """Vista principal para gestión de respaldos del sistema"""
    
    # Directorio de respaldos
    respaldos_dir = os.path.join(settings.BASE_DIR, 'respaldos')
    if not os.path.exists(respaldos_dir):
        os.makedirs(respaldos_dir)
    
    # Listar respaldos existentes
    respaldos_existentes = []
    if os.path.exists(respaldos_dir):
        for archivo in os.listdir(respaldos_dir):
            if archivo.endswith('.zip') or archivo.endswith('.sql'):
                ruta_completa = os.path.join(respaldos_dir, archivo)
                stat = os.stat(ruta_completa)
                
                # Determinar tipo de respaldo
                tipo = 'Completo' if archivo.endswith('.zip') else 'Base de Datos'
                
                respaldos_existentes.append({
                    'nombre': archivo,
                    'ruta': ruta_completa,
                    'tamaño': stat.st_size,
                    'fecha_creacion': datetime.fromtimestamp(stat.st_mtime),
                    'tipo': tipo,
                    'tamaño_legible': format_bytes(stat.st_size)
                })
    
    # Ordenar por fecha (más reciente primero)
    respaldos_existentes.sort(key=lambda x: x['fecha_creacion'], reverse=True)
    
    # Estadísticas del sistema para mostrar en el respaldo
    stats_sistema = {
        'total_usuarios': User.objects.count(),
        'usuarios_activos': User.objects.filter(is_active=True).count(),
        'roles_personalizados': RolPersonalizado.objects.count(),
        'permisos_sistema': PermisoSistema.objects.count(),
        'historial_registros': HistorialRoles.objects.count(),
        'sesiones_registradas': SesionUsuario.objects.count(),
        'configuraciones_usuario': ConfiguracionUsuario.objects.count(),
    }
    
    # Información del sistema
    info_sistema = {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'django_version': django.get_version(),
        'base_dir': str(settings.BASE_DIR),
        'debug_mode': settings.DEBUG,
        'database_engine': settings.DATABASES['default']['ENGINE'],
        'media_root': str(settings.MEDIA_ROOT) if hasattr(settings, 'MEDIA_ROOT') else 'No configurado',
        'static_root': str(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else 'No configurado',
    }
    
    # Último respaldo automático (si existe)
    ultimo_respaldo = respaldos_existentes[0] if respaldos_existentes else None
    
    context = {
        'titulo': 'Gestión de Respaldos del Sistema',
        'respaldos_existentes': respaldos_existentes,
        'stats_sistema': stats_sistema,
        'info_sistema': info_sistema,
        'ultimo_respaldo': ultimo_respaldo,
        'total_respaldos': len(respaldos_existentes),
        'tamaño_total_respaldos': sum(r['tamaño'] for r in respaldos_existentes),
        'tamaño_total_legible': format_bytes(sum(r['tamaño'] for r in respaldos_existentes)),
    }
    
    return render(request, 'sistema_interno/respaldos.html', context)

@login_required
@user_passes_test(es_administrador)
def crear_respaldo_view(request):
    """Vista para crear un nuevo respaldo"""
    
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('usuarios:respaldos')
    
    tipo_respaldo = request.POST.get('tipo_respaldo', 'base_datos')
    incluir_media = request.POST.get('incluir_media') == 'on'
    
    try:
        respaldos_dir = os.path.join(settings.BASE_DIR, 'respaldos')
        if not os.path.exists(respaldos_dir):
            os.makedirs(respaldos_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if tipo_respaldo == 'base_datos':
            # Crear respaldo solo de base de datos
            nombre_archivo = f'respaldo_db_{timestamp}.sql'
            ruta_respaldo = os.path.join(respaldos_dir, nombre_archivo)
            
            # Ejecutar comando de respaldo de SQLite
            db_path = settings.DATABASES['default']['NAME']
            with open(ruta_respaldo, 'w') as f:
                subprocess.run(['sqlite3', str(db_path), '.dump'], stdout=f, check=True)
            
            messages.success(request, f'Respaldo de base de datos creado exitosamente: {nombre_archivo}')
            
        elif tipo_respaldo == 'completo':
            # Crear respaldo completo del sistema
            nombre_archivo = f'respaldo_completo_{timestamp}.zip'
            ruta_respaldo = os.path.join(respaldos_dir, nombre_archivo)
            
            with zipfile.ZipFile(ruta_respaldo, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Agregar base de datos
                db_path = settings.DATABASES['default']['NAME']
                zipf.write(db_path, 'db.sqlite3')
                
                # Agregar archivos de configuración importantes
                config_files = ['manage.py', 'requirements.txt']
                for config_file in config_files:
                    file_path = os.path.join(settings.BASE_DIR, config_file)
                    if os.path.exists(file_path):
                        zipf.write(file_path, config_file)
                
                # Agregar archivos de media si se solicita
                if incluir_media and hasattr(settings, 'MEDIA_ROOT') and os.path.exists(settings.MEDIA_ROOT):
                    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, settings.BASE_DIR)
                            zipf.write(file_path, arcname)
                
                # Agregar información del sistema
                info_sistema = {
                    'fecha_respaldo': datetime.now().isoformat(),
                    'version_django': django.get_version(),
                    'usuario_respaldo': request.user.username,
                    'tipo_respaldo': 'completo',
                    'incluye_media': incluir_media,
                }
                
                info_json = json.dumps(info_sistema, indent=2)
                zipf.writestr('info_respaldo.json', info_json)
            
            messages.success(request, f'Respaldo completo creado exitosamente: {nombre_archivo}')
        
        # Registrar en el historial
        registrar_cambio_historial(
            usuario=request.user,
            accion='crear_respaldo',
            descripcion=f'Creó respaldo del sistema: {nombre_archivo} (tipo: {tipo_respaldo})',
            datos_nuevos={
                'tipo_respaldo': tipo_respaldo,
                'archivo': nombre_archivo,
                'incluir_media': incluir_media
            },
            request=request
        )
        
    except Exception as e:
        messages.error(request, f'Error al crear el respaldo: {str(e)}')
    
    return redirect('usuarios:respaldos')

@login_required
@user_passes_test(es_administrador)
def descargar_respaldo_view(request, nombre_archivo):
    """Vista para descargar un respaldo"""
    
    respaldos_dir = os.path.join(settings.BASE_DIR, 'respaldos')
    ruta_archivo = os.path.join(respaldos_dir, nombre_archivo)
    
    if not os.path.exists(ruta_archivo):
        messages.error(request, 'El archivo de respaldo no existe.')
        return redirect('usuarios:respaldos')
    
    # Determinar tipo de contenido
    content_type = 'application/zip' if nombre_archivo.endswith('.zip') else 'application/sql'
    
    # Registrar descarga en historial
    registrar_cambio_historial(
        usuario=request.user,
        accion='descargar_respaldo',
        descripcion=f'Descargó el respaldo: {nombre_archivo}',
        datos_nuevos={'archivo': nombre_archivo},
        request=request
    )
    
    return FileResponse(
        open(ruta_archivo, 'rb'),
        as_attachment=True,
        filename=nombre_archivo,
        content_type=content_type
    )

@login_required
@user_passes_test(es_administrador)
def eliminar_respaldo_view(request, nombre_archivo):
    """Vista para eliminar un respaldo"""
    
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('usuarios:respaldos')
    
    respaldos_dir = os.path.join(settings.BASE_DIR, 'respaldos')
    ruta_archivo = os.path.join(respaldos_dir, nombre_archivo)
    
    if not os.path.exists(ruta_archivo):
        messages.error(request, 'El archivo de respaldo no existe.')
        return redirect('usuarios:respaldos')
    
    try:
        os.remove(ruta_archivo)
        
        # Registrar eliminación en historial
        registrar_cambio_historial(
            usuario=request.user,
            accion='eliminar_respaldo',
            descripcion=f'Eliminó el respaldo: {nombre_archivo}',
            datos_antiguos={'archivo': nombre_archivo},
            request=request
        )
        
        messages.success(request, f'Respaldo {nombre_archivo} eliminado exitosamente.')
        
    except Exception as e:
        messages.error(request, f'Error al eliminar el respaldo: {str(e)}')
    
    return redirect('usuarios:respaldos')

# Función auxiliar para formatear bytes
def format_bytes(bytes_size):
    """Convierte bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

# Importaciones necesarias al inicio del archivo
import sys
import django
