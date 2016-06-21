from django import template
from administration.models import *

register = template.Library()
@register.filter(name="filter_cats")
def filter_cats(needs, value):
    return needs.filter(categorie=value)
