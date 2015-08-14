from django import template

register = template.Library()

@register.filter
def space_to_plus(content):
    return '+'.join(content.split())