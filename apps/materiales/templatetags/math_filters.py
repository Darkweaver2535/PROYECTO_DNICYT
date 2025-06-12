from django import template

register = template.Library()

@register.filter
def abs_value(value):
    """Retorna el valor absoluto de un número"""
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiplica value por arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    """Resta arg de value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0