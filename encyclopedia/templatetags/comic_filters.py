from django import template

register = template.Library()

@register.filter
def replace_underscore(value):
    """Replace underscores with spaces and title case the result."""
    if value:
        return str(value).replace('_', ' ').title()
    return value

@register.filter
def format_field_name(value):
    """Format field names for display."""
    if value:
        # Replace underscores with spaces and title case
        formatted = str(value).replace('_', ' ').title()
        # Handle special cases
        replacements = {
            'Isbn': 'ISBN',
            'Bl Record Id': 'BL Record ID',
            'Id': 'ID',
        }
        for old, new in replacements.items():
            formatted = formatted.replace(old, new)
        return formatted
    return value