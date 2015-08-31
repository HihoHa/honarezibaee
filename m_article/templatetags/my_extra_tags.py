from django import template


register = template.Library()


@register.filter
def comma_seperated(value_list):
    return ', '.join([str(x) for x in value_list])
