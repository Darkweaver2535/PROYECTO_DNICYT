from django.contrib import messages
from django.shortcuts import render

def mi_vista(request):
    messages.success(request, '¡Inicio de sesión exitoso!')
    messages.error(request, 'Usuario o contraseña incorrectos')

# Create your views here.
