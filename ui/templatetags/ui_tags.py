from django.template import Library
register = Library()

@register.filter
def cssclass(name):
    return name.lower().replace('_','-')
