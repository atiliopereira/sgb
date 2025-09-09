from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def currency_format(value):
    """Format currency with thousands separators (Paraguay format: dots)"""
    if value is None:
        return "0"
    
    try:
        # Convert to integer (no decimals)
        int_value = int(round(float(value)))
        # Format with thousands separators
        formatted = f"{int_value:,}".replace(',', '.')
        return formatted
    except (ValueError, TypeError):
        return "0"

@register.filter
def currency_format_safe(value):
    """Format currency with thousands separators and return as safe HTML"""
    return mark_safe(currency_format(value))