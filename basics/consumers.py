import datetime
import json
import re
import urllib.parse
import logging
from .models import *
from channels import Group
from channels.sessions import channel_session, enforce_ordering
from .views import sendmail
import psycopg2
from django.db import transaction
import threading
import time
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http


@enforce_ordering(slight=True)
@channel_session_user_from_http
@channel_session
def ws_add(message, room):
    query_string = message.user.username
    if not (type(query_string) is str):
        query_string = query_string.decode('utf-8')
    query = {"username" : message.user.username}
    if 'username' not in query:
        print("ws_add: no username")
        return
    Group('chat-%s' % room).add(message.reply_channel)
    message.channel_session['room'] = room
    message.channel_session['username'] = query['username']

@enforce_ordering(slight=True)
@channel_session_user
@channel_session
def ws_echo(message):
    if 'username' not in message.channel_session:
        print("no username")
        return
    with transaction.atomic():
        room = message.channel_session['room']
        logging.info('Echoing message %s from username %s in room %s',
                     message.content['text'], message.channel_session['username'],
                     room)
        db_room = Room.objects.get(name=room)
        if db_room.helper_out:
            return
        author = User.objects.get(username=message.channel_session['username'])
        text = message.content['text']
        if text == "ack":
            db_room.set_saw(author)
            return
    if text == "number" :
        if Userdata.objects.get(user=author).phone == "" or Userdata.objects.get(user=author).phone == None:
            return
        text = "You can contact me via this phone number: "+Userdata.objects.get(user=author).phone
    pattern = re.compile(u'^[\n ]+$')
    if pattern.search(text) is not None or text == "":
        return
    chatMessage = ChatMessage(author=author, room=db_room, text=text)
    chatMessage.save()
    db_room.incomming_message(author)
    db_room.last_message = datetime.now()
    db_room.save()
    user = db_room.user_req
    if user == author:
        user = db_room.need.author
    t1 = threading.Thread(target=email_check,args=(user,author, room, text,))
    t1.start()
    Group('chat-%s' % room).send({
        'text': json.dumps({
            'name': db_room.need.headline,
            'hash': db_room.name,
            'last_message': db_room.recent_message(),
            'new': "true",
            'message': text,
            'username': message.channel_session['username'],
            'room': message.channel_session['room'],
            'date': datetime.now().__str__()[:-7]
        }),
    })

class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)

#Email check will send the user an email if the message is not viewed within a minute
def email_check(user, author, roomname, text ):
    time.sleep(10)
    print("stop sleep")
    room = Room.objects.get(name=roomname)
    if user != None and room.new_message(user):
        print("email was send because: req:"+ room.req_saw.__str__() + " off:"+room.off_saw.__str__())

        sendmail(user.email, "Message from " + author.username, text)
