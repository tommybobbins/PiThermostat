from django import template
from collections import OrderedDict

register = template.Library()

@register.filter(name='sort')
def listsort(value):
    if isinstance(value, dict):
        new_dict = collections.OrderedDict()
        key_list = sorted(value.keys())
        for key in key_list:
            new_dict[key] = value[key]
        return new_dict
    elif isinstance(value, list):
        return sorted(value)
    else:
        return value
    listsort.is_safe = True
