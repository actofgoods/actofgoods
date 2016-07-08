from django.contrib import admin
from .models import *

admin.site.register(
    CategoriesNeeds,
    list_display=["name"],

)

admin.site.register(
    Information,
    list_display=["headline", "text", "adrAsPoint"],

)


admin.site.register(
	Room,
	list_display=["name","user_req", "slug", "need"],
	prepopulated_fields={"slug": ("name",)},

)

admin.site.register(
	ChatMessage,
	list_display=["author","date", "room", "text"],

)

admin.site.register(
	Need,
	list_display=["author","date", "headline","text"],

)

admin.site.register(
    ClaimedArea,
    list_display=['claimer', 'group', 'title'],
)
# Register your models here.
