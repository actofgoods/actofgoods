from django import template
from basics.models import *

register = template.Library()
@register.filter(name="filter_cats")
def filter_cats(value):
    return Need.objects.filter(categorie=value)
