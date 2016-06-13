from django import template
from basics.models import *

register = template.Library()

@register.filter
def get_short_text( need , max_len=100):
    if len(need.text) > max_len:
        return need.text[:max_len] + "..."
    return need.text
