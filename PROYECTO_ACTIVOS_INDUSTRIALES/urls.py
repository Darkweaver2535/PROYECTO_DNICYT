"""
URL configuration for PROYECTO_ACTIVOS_INDUSTRIALES project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from views import landing  # Ajusta el import según tu estructura
from django.views.generic import TemplateView
from apps.dashboard.views import dashboard_view  # ← CORREGIDO: Importar desde dashboard
from apps.equipos.views import EquipoListView  # ← Solo el EquipoListView desde equipos

urlpatterns = [
    path('', landing, name='landing'),
    path('admin/', admin.site.urls),
    path('equipos/', include('apps.equipos.urls')),
    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('destacadas/', TemplateView.as_view(template_name="secciones/destacadas.html"), name='destacadas'),
    path('comunicados/', TemplateView.as_view(template_name="secciones/comunicados.html"), name='comunicados'),
    path('multimedia/', TemplateView.as_view(template_name="secciones/multimedia.html"), name='multimedia'),
    path('videos/', TemplateView.as_view(template_name="secciones/videos.html"), name='videos'),
    path('cursos/', TemplateView.as_view(template_name="secciones/cursos.html"), name='cursos'),
    path('laboratorio/', TemplateView.as_view(template_name="secciones/laboratorio.html"), name='laboratorio'),
    path('documentos/', TemplateView.as_view(template_name="secciones/documentos.html"), name='documentos'),
    path('contacto/', TemplateView.as_view(template_name="secciones/contacto.html"), name='contacto'),
    path('inventario/', EquipoListView.as_view(), name='inventario_equipos'),
    path('dashboard/', dashboard_view, name='dashboard'),  # ← CORREGIDO: Usar dashboard_view importado correctamente
    path('mantenimiento/', include('apps.mantenimiento.urls')),
    path('operaciones/', include('apps.operaciones.urls')),
    path('inventario/', include('apps.inventario.urls')),  # <- AGREGAR ESTA LÍNEA
    path('materiales/', include('apps.materiales.urls')),  # <- AGREGAR ESTA LÍNEA
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
