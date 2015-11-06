from django import template
from django.template.defaulttags import register

@register.filter(name='lookup')
def lookup(dictionary, key):
    return dictionary.get(key)
