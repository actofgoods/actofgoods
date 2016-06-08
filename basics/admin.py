from django.contrib import admin
from .models import CategoriesNeeds

admin.site.register(
    CategoriesNeeds,
    list_display=["name"],

)
# Register your models here.
