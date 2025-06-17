# 🏭 Sistema Integral de Gestión Industrial - Laboratorio Metal Mecánica

**PROYECTO DNICYT - Sistema de Gestión para Laboratorio de Metal Mecánica**

Desarrollado por estudiantes de Ingeniería de Sistemas e Ingeniería Mecatrónica con la supervisión del Ing. Álvaro Encinas.

---

## 📋 Descripción del Sistema

Sistema web integral para la gestión completa de un laboratorio de metal mecánica que incluye manejo de equipos, mantenimiento, operaciones, inventarios, seguridad industrial, capacitación y reportes. Desarrollado con Django y diseñado específicamente para entornos industriales educativos.

### 🎯 Objetivo Principal
Digitalizar y optimizar todos los procesos operativos, administrativos y de seguridad del Laboratorio de Metal Mecánica de la Universidad EMI, proporcionando una plataforma integrada para estudiantes, docentes y personal técnico.

---

## 🚀 Características Principales

### 📊 **Dashboard Centralizado**
- Panel de control con métricas en tiempo real
- Indicadores clave de rendimiento (KPIs)
- Gráficos interactivos de equipos, mantenimiento y operaciones
- Alertas y notificaciones importantes
- Estadísticas de uso y productividad

### 🔧 **Gestión de Equipos**
- **Inventario Completo**: Registro detallado de todos los equipos
- **Códigos QR**: Generación automática para identificación rápida
- **Fichas Técnicas**: Especificaciones eléctricas, mecánicas y operativas
- **Estados de Equipos**: Disponible, En Mantenimiento, Fuera de Servicio
- **Historial de Uso**: Tracking completo de utilización
- **Documentación**: Manuales, diagramas y procedimientos

### 🛠️ **Sistema de Mantenimiento**
- **Mantenimiento Preventivo**: Programación automática basada en calendarios
- **Mantenimiento Correctivo**: Gestión de reparaciones y fallas
- **Órdenes de Trabajo**: Creación, asignación y seguimiento
- **Historial de Mantenimiento**: Registro completo de intervenciones
- **Análisis Predictivo**: Indicadores de fallas potenciales
- **Gestión de Técnicos**: Asignación y control de personal

### 📋 **Gestión de Operaciones**
- **Procedimientos Operativos (POPs)**: Biblioteca de procedimientos estándar
- **Análisis de Riesgos**: Evaluación y mitigación de riesgos operativos
- **Diagnósticos**: Sistema de diagnóstico de equipos
- **Control de Calidad**: Verificación de procesos y resultados
- **Movimientos Unificados**: Tracking de materiales y equipos

### 📦 **Inventario y Materiales**
- **Control de Stock**: Gestión de repuestos y materiales
- **Puntos de Reorden**: Alertas automáticas de stock mínimo
- **Gestión de Proveedores**: Base de datos de proveedores
- **Valorización**: Control de costos y presupuestos
- **Movimientos de Inventario**: Entrada, salida y transferencias

### 🛡️ **Normativas y Seguridad Industrial**
- **Seguridad Industrial**: Dashboard de seguridad con indicadores críticos
- **Alertas y Riesgos**: Sistema proactivo de gestión de riesgos
- **Normativas de Seguridad**: Base de conocimiento de normativas vigentes
- **Inspecciones de Seguridad**: Programación y seguimiento
- **Gestión de Incidentes**: Reporte y seguimiento de incidentes
- **Matriz de Riesgos**: Evaluación probabilidad vs impacto

### 🎓 **Sistema de Capacitación**
- **Cursos y Talleres**: Gestión completa de programas de formación
- **Biblioteca Multimedia**: Videos técnicos y documentación
- **Certificaciones**: Control de certificaciones y competencias
- **Evaluaciones**: Sistema de evaluación y seguimiento
- **Progreso de Aprendizaje**: Tracking individual de estudiantes

### 📈 **Reportes y Análisis**
- **Reportes Automáticos**: Generación automática de reportes
- **Análisis de Rendimiento**: Métricas de equipos y operaciones
- **Dashboards Personalizados**: Vistas adaptadas por rol de usuario
- **Exportación de Datos**: Excel, PDF y otros formatos
- **Gráficos Interactivos**: Visualización avanzada de datos

### 👥 **Gestión de Usuarios**
- **Control de Acceso**: Sistema de roles y permisos granular
- **Perfiles de Usuario**: Estudiantes, Docentes, Técnicos, Administradores
- **Auditoría**: Log completo de actividades del sistema
- **Autenticación Segura**: Sistema de login robusto

---

## 🏗️ **Arquitectura del Sistema**

### **Backend (Django 4.2+)**
- **Framework**: Django con arquitectura MVT (Model-View-Template)
- **Base de Datos**: SQLite para desarrollo, escalable a PostgreSQL
- **APIs**: Django REST Framework para integraciones
- **Autenticación**: Sistema integrado de Django con roles personalizados
- **Seguridad**: CSRF protection, XSS prevention, SQL injection protection

### **Frontend**
- **HTML5 Semántico**: Estructura moderna y accesible
- **CSS3 Avanzado**: Grid, Flexbox, Animaciones CSS
- **JavaScript ES6+**: Interactividad y funcionalidad dinámica
- **Bootstrap Icons**: Iconografía consistente
- **Responsive Design**: Adaptable a dispositivos móviles y tablets

### **Características Técnicas**
- **Diseño Responsive**: Compatible con móviles, tablets y escritorio
- **PWA Ready**: Preparado para Progressive Web App
- **Modo Offline**: Funcionalidad básica sin conexión
- **Carga Optimizada**: Lazy loading y optimización de recursos
- **SEO Friendly**: Estructura optimizada para motores de búsqueda

---

## 🛠️ **Instalación y Configuración**

### **Requisitos del Sistema**
- **Python**: 3.8 o superior
- **pip**: Gestor de paquetes de Python
- **Git**: Para control de versiones
- **Navegador**: Chrome, Firefox, Safari, Edge (versiones recientes)

### **Instalación en macOS**

#### 1. **Preparar el Entorno**
```bash
# Verificar Python
python3 --version

# Instalar Python si es necesario (con Homebrew)
brew install python

# Navegar al directorio del proyecto
cd /Users/alvaroencinas/Desktop/PROY.\ ALTO\ IRPAVI/PROYECTO_DNICYT
```

#### 2. **Configurar Entorno Virtual**
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip
```

#### 3. **Instalar Dependencias**
```bash
# Instalar Django y dependencias
pip install django==4.2
pip install djangorestframework
pip install pillow
pip install reportlab
pip install openpyxl
pip install qrcode[pil]
pip install python-decouple
pip install django-crispy-forms
pip install crispy-bootstrap5
pip install django-widget-tweaks
```

#### 4. **Configurar Base de Datos**
```bash
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

#### 5. **Cargar Datos de Prueba (Opcional)**
```bash
# Cargar datos de ejemplo
python manage.py loaddata fixtures/sample_data.json
```

#### 6. **Iniciar Servidor**
```bash
python manage.py runserver
```

### **Instalación en Windows**

#### 1. **Preparar el Entorno**
```cmd
# Verificar Python
python --version

# Navegar al directorio del proyecto
cd C:\path\to\PROYECTO_DNICYT
```

#### 2. **Configurar Entorno Virtual**
```cmd
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Actualizar pip
pip install --upgrade pip
```

#### 3. **Instalar Dependencias**
```cmd
# Instalar todas las dependencias
pip install -r requirements.txt
```

#### 4. **Configurar y Ejecutar**
```cmd
# Configurar base de datos
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

---

## 📁 **Estructura del Proyecto**

```
PROYECTO_DNICYT/
│
├── 📁 apps/                           # Aplicaciones Django
│   ├── 📁 equipos/                    # Gestión de Equipos
│   │   ├── models.py                  # Modelos de equipos
│   │   ├── views.py                   # Vistas de equipos
│   │   ├── forms.py                   # Formularios
│   │   ├── urls.py                    # URLs de equipos
│   │   └── admin.py                   # Configuración admin
│   │
│   ├── 📁 mantenimiento/              # Sistema de Mantenimiento
│   │   ├── models.py                  # Órdenes de trabajo, historial
│   │   ├── views.py                   # Gestión de mantenimiento
│   │   ├── forms.py                   # Formularios de mantenimiento
│   │   └── tasks.py                   # Tareas automáticas
│   │
│   ├── 📁 operaciones/                # Gestión de Operaciones
│   │   ├── models.py                  # POPs, análisis de riesgos
│   │   ├── views.py                   # Operaciones diarias
│   │   └── utils.py                   # Utilidades operativas
│   │
│   ├── 📁 inventario/                 # Control de Inventario
│   │   ├── models.py                  # Stock, proveedores
│   │   ├── views.py                   # Gestión de inventario
│   │   └── reports.py                 # Reportes de inventario
│   │
│   ├── 📁 normativas/                 # Seguridad y Normativas
│   │   ├── models.py                  # Normativas, incidentes
│   │   ├── views.py                   # Seguridad industrial
│   │   └── safety_utils.py            # Utilidades de seguridad
│   │
│   └── 📁 capacitacion/               # Sistema de Capacitación
│       ├── models.py                  # Cursos, evaluaciones
│       ├── views.py                   # Gestión de capacitación
│       └── multimedia.py              # Manejo de multimedia
│
├── 📁 templates/                      # Plantillas HTML
│   ├── base.html                      # Plantilla base
│   ├── 📁 sistema_interno/            # Templates del sistema
│   │   ├── dashboard.html             # Dashboard principal
│   │   ├── equipos.html               # Gestión de equipos
│   │   ├── mantenimiento.html         # Sistema de mantenimiento
│   │   ├── operaciones.html           # Operaciones diarias
│   │   ├── inventario.html            # Control de inventario
│   │   ├── seguridad_industrial.html  # Seguridad industrial
│   │   ├── alertas_riesgos.html       # Alertas y riesgos
│   │   └── capacitacion.html          # Sistema de capacitación
│   └── 📁 auth/                       # Templates de autenticación
│
├── 📁 static/                         # Archivos estáticos
│   ├── 📁 css/                        # Hojas de estilo
│   ├── 📁 js/                         # JavaScript
│   ├── 📁 images/                     # Imágenes del sistema
│   └── 📁 icons/                      # Iconos personalizados
│
├── 📁 media/                          # Archivos subidos por usuarios
│   ├── 📁 equipos/                    # Imágenes y documentos de equipos
│   ├── 📁 manuales/                   # Manuales técnicos
│   ├── 📁 normativas/                 # Documentos de normativas
│   └── 📁 capacitacion/               # Material de capacitación
│
├── 📁 usuarios/                       # Sistema de usuarios
│   ├── models.py                      # Perfiles de usuario
│   ├── views.py                       # Gestión de usuarios
│   └── permissions.py                 # Sistema de permisos
│
├── 📁 PROYECTO_ACTIVOS_INDUSTRIALES/  # Configuración Django
│   ├── settings.py                    # Configuraciones
│   ├── urls.py                        # URLs principales
│   ├── wsgi.py                        # Despliegue WSGI
│   └── asgi.py                        # Despliegue ASGI
│
├── manage.py                          # Comando de gestión Django
├── requirements.txt                   # Dependencias Python
├── .env.example                       # Variables de entorno ejemplo
├── .gitignore                         # Archivos ignorados por Git
└── README.md                          # Este archivo
```

---

## 🔐 **Sistema de Usuarios y Permisos**

### **Roles de Usuario**

#### 👨‍💼 **Administrador**
- Acceso completo al sistema
- Gestión de usuarios y permisos
- Configuración global del sistema
- Respaldos y mantenimiento

#### 👨‍🔧 **Supervisor Técnico**
- Gestión de equipos y mantenimiento
- Aprobación de órdenes de trabajo
- Supervisión de operaciones
- Reportes de gestión

#### 👨‍🏫 **Docente**
- Gestión de capacitación
- Acceso a material didáctico
- Evaluación de estudiantes
- Creación de contenido

#### 👨‍🔬 **Técnico de Laboratorio**
- Operación de equipos
- Registro de mantenimiento
- Reporte de incidentes
- Seguimiento de inventario

#### 🎓 **Estudiante**
- Acceso a material de capacitación
- Consulta de equipos disponibles
- Reporte de observaciones
- Seguimiento de progreso

---

## 🌐 **APIs y Integraciones**

### **APIs Disponibles**
```python
# Endpoints principales
/api/equipos/                    # Gestión de equipos
/api/mantenimiento/              # Sistema de mantenimiento
/api/inventario/                 # Control de inventario
/api/normativas/                 # Normativas y seguridad
/api/capacitacion/               # Sistema de capacitación
/api/reportes/                   # Generación de reportes
/api/dashboard/stats/            # Estadísticas del dashboard
```

### **Formatos de Respuesta**
- **JSON**: Para integraciones API
- **XML**: Para sistemas legacy
- **CSV/Excel**: Para exportación de datos
- **PDF**: Para reportes formales

---

## 📱 **Compatibilidad y Accesibilidad**

### **Navegadores Soportados**
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### **Dispositivos**
- 💻 **Desktop**: Experiencia completa
- 📱 **Móviles**: Funcionalidad adaptada
- 📟 **Tablets**: Interfaz optimizada
- ⌚ **Smartwatches**: Notificaciones básicas

### **Accesibilidad**
- WCAG 2.1 AA compliance
- Navegación por teclado
- Lectores de pantalla compatible
- Alto contraste disponible

---

## 🔧 **Configuración Avanzada**

### **Variables de Entorno (.env)**
```env
# Configuración de Base de Datos
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgresql://user:pass@localhost/dbname

# Configuración de Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Configuración de Seguridad
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuración de Archivos
MEDIA_ROOT=/path/to/media
STATIC_ROOT=/path/to/static

# Configuración de Cache
CACHE_BACKEND=redis://localhost:6379/1
```

### **Configuración de Producción**
```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'proyecto_dnicyt',
        'USER': 'postgres_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Configuración de seguridad adicional
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

---

## 📊 **Monitoreo y Métricas**

### **Métricas del Sistema**
- **Disponibilidad de Equipos**: Porcentaje de equipos operativos
- **Eficiencia de Mantenimiento**: Tiempo medio de reparación
- **Cumplimiento de Seguridad**: Porcentaje de cumplimiento normativo
- **Progreso de Capacitación**: Avance de programas formativos
- **Utilización de Recursos**: Optimización de inventario

### **Alertas Automáticas**
- Equipos próximos a mantenimiento
- Stock bajo de materiales críticos
- Incidentes de seguridad
- Normativas próximas a vencer
- Evaluaciones pendientes

---

## 🚀 **Despliegue y Producción**

### **Despliegue Local**
```bash
# Preparar para producción
python manage.py collectstatic
python manage.py compress

# Ejecutar con Gunicorn
pip install gunicorn
gunicorn PROYECTO_ACTIVOS_INDUSTRIALES.wsgi:application
```

### **Despliegue en la Nube**
- **Heroku**: Configuración incluida
- **AWS**: Compatible con EC2, RDS, S3
- **DigitalOcean**: Droplets optimizados
- **Google Cloud**: App Engine ready

---

## 🧪 **Testing y Calidad**

### **Ejecutar Tests**
```bash
# Tests unitarios
python manage.py test

# Tests con coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report -m
```

### **Linting y Formato**
```bash
# Instalar herramientas
pip install black flake8 isort

# Formatear código
black .
isort .
flake8 .
```

---

## 📚 **Documentación Adicional**

### **Manuales de Usuario**
- 📖 [Manual del Administrador](docs/admin_manual.md)
- 👨‍🔧 [Manual del Técnico](docs/technician_manual.md)
- 🎓 [Manual del Estudiante](docs/student_manual.md)

### **Documentación Técnica**
- 🏗️ [Arquitectura del Sistema](docs/architecture.md)
- 🔌 [Guía de APIs](docs/api_guide.md)
- 🛡️ [Seguridad y Permisos](docs/security.md)

---

## 🤝 **Contribuciones**

### **Cómo Contribuir**
1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### **Estándares de Código**
- Seguir PEP 8 para Python
- Comentarios en español
- Documentación de funciones
- Tests para nuevas funcionalidades

---

## 🐛 **Resolución de Problemas**

### **Problemas Comunes**

#### Error de Migraciones
```bash
python manage.py makemigrations --empty appname
python manage.py migrate --fake appname 0001
python manage.py migrate
```

#### Error de Permisos en Media
```bash
# macOS/Linux
chmod 755 media/
chmod -R 644 media/*

# Windows
icacls media /grant Everyone:F /T
```

#### Error de Static Files
```bash
python manage.py collectstatic --clear
python manage.py collectstatic
```

---

## 📞 **Soporte y Contacto**

### **Equipo de Desarrollo**
- **Supervisor**: Ing. Álvaro Encinas
- **Desarrolladores**: Estudiantes de Ingeniería de Sistemas
- **Testing**: Estudiantes de Ingeniería Mecatrónica

### **Contacto**
- 📧 **Email**: soporte@laboratorio-metalmecanica.edu.bo
- 📱 **WhatsApp**: +591 76260216
- 🌐 **Web**: https://laboratorio-metalmecanica.edu.bo

---

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 🙏 **Agradecimientos**

- Universidad EMI por el apoyo institucional
- Laboratorio de Metal Mecánica por la colaboración
- Estudiantes y docentes por el feedback continuo
- Comunidad Django por las herramientas

---

**Versión del Sistema**: 2.0.0  
**Estado**: En desarrollo activo ✅

---

> 💡 **Nota**: Este README se actualiza constantemente. Para la versión más reciente, consulta el repositorio oficial del proyecto.