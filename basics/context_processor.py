from .models import *
import json
from django.db.models import Q
def add_rooms(request):
    rooms = Room.objects.filter(Q(need__author =request.user) | Q(user_req = request.user))
    rooms_json = "["
    for room in rooms:
        rooms_json   += json.dumps({
            'name': room.need.headline,
            'hash': room.name,
            'date': room.last_message.__str__()
        }) + ","
    rooms_json = rooms_json[:-1]
    rooms_json += "]"
    print(rooms_json)
    return {'channels':rooms_json}
