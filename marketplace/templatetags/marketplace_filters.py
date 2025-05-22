from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sum_list(value, key):
    """Suma los valores de una lista de diccionarios usando la clave especificada"""
    try:
        return sum(item.get(key, 0) for item in value)
    except (ValueError, TypeError):
        return 0 