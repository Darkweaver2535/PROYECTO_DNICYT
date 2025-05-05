# PROYECTO_DNICYT

**PROPUESTA DE LÍNEAS DE TRABAJO PRACTICANTES LABORALES (LABORATORIO DE METAL MECÁNICA)**

Desarrollado por estudiantes de Ingeniería de Sistemas e Ingeniería Mecatrónica con la supervisión del Ing. Alaro.

## Guía de Instalación

### Requisitos previos:
* **Python 3.6 o superior** instalado en el sistema
* **Pip**: Gestor de paquetes de Python
* **Git**: Opcional, para clonar el repositorio

## Instalación en macOS

### Paso 1: Verificar la instalación de Python
```bash
python3 --version
```

Si Python no está instalado, instálalo con Homebrew:
```bash
brew install python
```

### Paso 2: Crear y activar un entorno virtual
```bash
# Navegar a la carpeta del proyecto
cd /ruta/a/PROYECTO_DNICYT

# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate
```

### Paso 3: Instalar Django
```bash
pip install django
```

### Paso 4: Crear el proyecto Django
```bash
django-admin startproject proyecto_django .
```

### Paso 5: Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```

Abre un navegador y visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) para verificar que el proyecto está funcionando correctamente.

## Instalación en Windows

### Paso 1: Verificar la instalación de Python
```bash
python --version
```

Si Python no está instalado:
1. Descarga el instalador desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, marca la opción **"Add Python to PATH"**

### Paso 2: Crear y activar un entorno virtual
```bash
# Navegar a la carpeta del proyecto
cd \ruta\a\PROYECTO_DNICYT

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Command Prompt)
.\.venv\Scripts\activate

# O si usas PowerShell
# .\.venv\Scripts\Activate.ps1
```

### Paso 3: Instalar Django
```bash
pip install django
```

### Paso 4: Crear el proyecto Django
```bash
django-admin startproject proyecto_django .
```

### Paso 5: Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```

Abre un navegador y visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) para verificar que el proyecto está funcionando correctamente.

## Estructura del Proyecto

Después de completar la instalación, la estructura del proyecto será la siguiente:

```
PROYECTO_DNICYT/
│
├── .venv/                  # Entorno virtual
├── manage.py               # Herramienta de gestión de Django
├── proyecto_django/        # Código del proyecto Django
│   ├── __init__.py
│   ├── settings.py         # Configuraciones del proyecto
│   ├── urls.py             # Rutas de la aplicación
│   ├── wsgi.py             # Entrada para WSGI
│   └── asgi.py             # Entrada para ASGI
└── README.md               # Este archivo
```