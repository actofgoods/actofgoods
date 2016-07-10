from .models import *
import json
from django.db.models import Q
def add_rooms(request):

    user = request.user
    if user.is_authenticated():
        rooms = Room.objects.filter(Q(need__author =user) | Q(user_req = user))
        if len(rooms) > 0 :
            new_messages_count = 0
            rooms_json = "["
            for room in rooms:
                if room.new_message(user):
                    new_messages_count += 1
                else:
                    rooms_json   += json.dumps({
                        'name': room.need.headline,
                        'hash': room.name,
                        'date': room.last_message.__str__()
                    }) + ","
            rooms_json = rooms_json[:-1]
            rooms_json += "]"
            return {'channels':rooms_json, 'new_messages':new_messages_count}
    return {'channels':'[]', 'new_messages':0}
