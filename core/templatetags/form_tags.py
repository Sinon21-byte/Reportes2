from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    """
    Añade la clase CSS al widget de un campo de formulario.
    Uso en plantilla: {{ form.campo|add_class:"form-control" }}
    """
    return field.as_widget(attrs={'class': css})
