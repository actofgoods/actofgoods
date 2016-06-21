from django import template
from basics.models import *
from basics.models import Need

register = template.Library()

@register.filter(name="filter_cats")
def filter_cats(value):
	n = Need.objects.filter(categorie=value)
	return n