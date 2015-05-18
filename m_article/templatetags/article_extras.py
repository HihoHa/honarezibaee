from django import template
from lxml import etree
from StringIO import StringIO

register = template.Library()

@register.filter(is_safe=True, needs_autoescape=False)
def first_paragraph(content):
    parser = etree.HTMLParser()
    root   = etree.parse(StringIO(content), parser)
    p = root.find('.//p')
    return p.text