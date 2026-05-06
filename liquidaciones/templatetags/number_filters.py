from django import template
from django.utils.safestring import mark_safe
import locale

register = template.Library()

@register.filter
def format_integer(value):
    """
    Format a number as integer with thousands separators.
    Removes decimals and adds thousands separators (dots for Paraguay locale).
    """
    try:
        # Convert to integer (removes decimals)
        int_value = int(float(value) if value else 0)
        
        # Format with thousands separator using dot (Paraguay style)
        formatted = f"{int_value:,}".replace(',', '.')
        
        return formatted
    except (ValueError, TypeError):
        return "0"

@register.filter
def format_guaranies(value):
    """
    Format a number as Guaranies with 'Gs.' suffix.
    """
    formatted_number = format_integer(value)
    return f"{formatted_number} Gs."

@register.filter
def format_decimal(value):
    """
    Format a decimal number with thousands separators (dots) and 2 decimal places (comma).
    Example: 1234567.89 -> "1.234.567,89"
    """
    try:
        from decimal import Decimal
        dec = Decimal(str(value)) if value else Decimal('0')
        # Format with 2 decimal places using Python's built-in
        formatted = f"{dec:,.2f}"  # "1,234,567.89"
        # Convert to Paraguay style: swap separators
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
    except (ValueError, TypeError):
        return "0,00"