from django import template

register = template.Library()
@register.filter(name="filter_cats")
def filter_cats(value):
    return Need.objects.filter(categorie=value)
