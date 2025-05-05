PROYECTO_DNICYT

PROPUESTA DE LÍNEAS DE TRABAJO PRACTICANTES LABORALES (LABORATORIO DE METAL MECÁNICA), desarrollado por estudiantes de ingeniería de sistemas e ingeniería mecatrónica con la supervisión del ingeniero Alaro.

Guía de instalación

Requisitos previos:
Python 3.6 o superior debe estar instalado en tu sistema.
Pip: El gestor de paquetes de Python (pip) debe estar instalado.
Git: Opcionalmente, si deseas clonar el repositorio desde GitHub.
En Mac
Paso 1: Verificar si Python está instalado

Abre una terminal y ejecuta:
python3 --version
Si Python no está instalado, puedes instalarlo con Homebrew:
brew install python
Paso 2: Crear y activar un entorno virtual

Navega a la carpeta donde deseas crear el proyecto (en este caso, la carpeta PROYECTO_DNICYT):
cd /ruta/a/PROYECTO_DNICYT
Crea un entorno virtual con el siguiente comando:
python3 -m venv .venv
Activa el entorno virtual:
source .venv/bin/activate
Paso 3: Instalar Django

Con el entorno virtual activado, instala Django:
pip install django
Paso 4: Crear el proyecto Django en la carpeta actual

En la terminal, dentro de la carpeta PROYECTO_DNICYT, ejecuta:
django-admin startproject proyecto_django .
Paso 5: Iniciar el servidor de desarrollo

Inicia el servidor de desarrollo de Django:
python manage.py runserver
Abre un navegador y visita http://127.0.0.1:8000/ para verificar que el proyecto está funcionando correctamente.
En Windows
Paso 1: Verificar si Python está instalado

Abre la terminal de Command Prompt o PowerShell y ejecuta:
python --version
Si Python no está instalado, descarga el instalador desde python.org y asegúrate de marcar la opción "Add Python to PATH" durante la instalación.
Paso 2: Crear y activar un entorno virtual

Navega a la carpeta donde deseas crear el proyecto (en este caso, PROYECTO_DNICYT):
cd \ruta\a\PROYECTO_DNICYT
Crea un entorno virtual con el siguiente comando:
python -m venv .venv
Activa el entorno virtual:
En Command Prompt:
.\.venv\Scripts\activate
En PowerShell:
.\.venv\Scripts\Activate.ps1
Paso 3: Instalar Django

Con el entorno virtual activado, instala Django:
pip install django
Paso 4: Crear el proyecto Django en la carpeta actual

En la terminal, dentro de la carpeta PROYECTO_DNICYT, ejecuta:
django-admin startproject proyecto_django .
Paso 5: Iniciar el servidor de desarrollo

Inicia el servidor de desarrollo de Django:
python manage.py runserver
Abre un navegador y visita http://127.0.0.1:8000/ para verificar que el proyecto está funcionando correctamente.
Estructura del Proyecto
Después de seguir estos pasos, la estructura de tu proyecto será la siguiente:

PROYECTO_DNICYT/
│
├── .venv/                 # Entorno virtual
├── manage.py              # Herramienta de gestión de Django
├── proyecto_django/       # Código del proyecto Django
│   ├── __init__.py
│   ├── settings.py        # Configuraciones del proyecto
│   ├── urls.py            # Rutas de la aplicación
│   ├── wsgi.py            # Entrada para WSGI
│   └── asgi.py            # Entrada para ASGI
└── README.md              # Este archivo
