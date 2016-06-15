import json
import urllib.parse
import logging
from .models import *
from channels import Group
from channels.sessions import channel_session

@channel_session
def ws_add(message, room):
    query = urllib.parse.parse_qs(message['query_string'])
    if 'username' not in query:
        return
    logging.info('Adding websocket with username %s in room %s',
                 query['username'][0], room)
    Group('chat-%s' % room).add(message.reply_channel)
    message.channel_session['room'] = room
    message.channel_session['username'] = query['username'][0]


@channel_session
def ws_echo(message):
    if 'username' not in message.channel_session:
        return
    room = message.channel_session['room']
    logging.info('Echoing message %s from username %s in room %s',
                 message.content['text'], message.channel_session['username'],
                 room)
    db_room = Room.objects.get(name=room)
    print(message.channel_session['username'])
    chatMessage = ChatMessage(author=User.objects.get(username=message.channel_session['username']), room=db_room, text=message.content['text'])
    chatMessage.save()
    Group('chat-%s' % room).send({
        'text': json.dumps({
            'message': message.content['text'],
            'username': message.channel_session['username']
        }),
    })
