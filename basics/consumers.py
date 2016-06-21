import datetime
import json
import urllib.parse
import logging
from .models import *
from channels import Group
from channels.sessions import channel_session
from .views import sendmail
from django.db import transaction

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

@transaction.atomic
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
    author = User.objects.get(username=message.channel_session['username'])
    text = message.content['text']
    print("THIS IS THE MESSAGE TEXT")
    print(text)
    if text == "ack":
        db_room.set_saw(author)
        print(db_room.req_saw, db_room.off_saw)
        return
    chatMessage = ChatMessage(author=author, room=db_room, text=message.content['text'])
    chatMessage.save()
    db_room.incomming_message(author)
    user = db_room.user_req
    if user == author:
        user = db_room.need.author

    Group('chat-%s' % room).send({
        'text': json.dumps({
            'message': message.content['text'],
            'username': message.channel_session['username'],
            'room': message.channel_session['room'],
            'date': datetime.now().__str__()
        }),
    })

    #sendmail(user.email, "Message from " + author.username, message.content['text'])
