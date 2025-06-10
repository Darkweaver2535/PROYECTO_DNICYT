import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """
    Extrae el nombre base de un archivo de su ruta completa
    """
    if not value:
        return ''
    return os.path.basename(str(value))

@register.filter
def file_extension(value):
    """
    Extrae la extensión de un archivo
    """
    if not value:
        return ''
    return os.path.splitext(str(value))[1].lower()

@register.filter
def file_size_format(value):
    """
    Formatea el tamaño de archivo en bytes a una representación legible
    """
    if not value:
        return '0 bytes'
    
    try:
        size = int(value)
    except (ValueError, TypeError):
        return '0 bytes'
    
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            if unit == 'bytes':
                return f"{size} {unit}"
            else:
                return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"