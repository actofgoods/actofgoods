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
    if  Userdata.objects.get(user=user).phone != None and Userdata.objects.get(user=user).phone != "":
        return True
    return False

@register.filter
def get_room_helper_out(need):
    if len(Room.objects.filter(need=need, helper_out=False)) == 1:
        return False
    return True

@register.filter
def get_roomname_off_inactive_chat(need, user):
    return Room.objects.get(need=need, user_req=user).name

@register.filter
def get_roomname_off_active_chat(need):
    return Room.objects.get(need=need, helper_out=False).name

@register.filter
def get_room_need_user_finished_off_active_chat(need):
    return Room.objects.get(need=need, helper_out=False).need_user_finished

@register.filter
def get_room_helper_out_becuase_of_kick_or_leave(need, user):
    return Room.objects.get(need=need, user_req=user).helper_out

@register.filter
def get_groups_of_user(user):
    return user.groups.all().order_by('name')

@register.filter
def concatenate(string1, string2):
    return string1 + ""+string2
