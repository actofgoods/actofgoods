from django import template
from basics.models import *

register = template.Library()

@register.filter
def get_short_text( need , max_len=100):
    if len(need.text) > max_len:
        return need.text[:max_len] + "..."
    return need.text

@register.filter
def is_own(roomname, user):
    if Room.objects.get(name=roomname).need.author == user:
        return True;
    return False;

@register.filter
def get_roomname(need, user):
    return Room.objects.get(need=need, user_req=user).name

@register.filter
def has_number(user):
    print("fuck of")
    print(user.username)
    print(Userdata.objects.get(user=user).phone)
    if  Userdata.objects.get(user=user).phone != None and Userdata.objects.get(user=user).phone != "":
        print("True")
        return True
    print("False")
    return False
