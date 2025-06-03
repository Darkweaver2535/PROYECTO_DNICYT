from django.shortcuts import render

def landing(request):
    comunicados = [
        {
            "icon": "fas fa-exclamation-triangle",
            "titulo": "Suspensión Temporal - Área de Soldadura",
            "texto": "Por trabajos de mantenimiento crítico en el sistema de ventilación, el área de soldadura permanecerá cerrada desde hoy hasta el viernes 7 de junio. Se reprogramarán todas las prácticas.",
            "meta": "Seguridad Industrial · Hoy, 14:30"
        },
        {
            "icon": "fas fa-calendar-alt",
            "titulo": "Horarios Extendidos de Laboratorio",
            "texto": "Este jueves el laboratorio abrirá sus puertas desde las 7:00 hasta las 15:00 para prácticas supervisadas. Aprovecha el tiempo adicional para tus proyectos y consulta con los encargados sobre el uso de equipos.",
            "meta": "Lab. Central - Área Industrial · Hace 2 horas"
        },
        # ...más comunicados...
    ]
    return render(request, 'landing.html', {'comunicados': comunicados})