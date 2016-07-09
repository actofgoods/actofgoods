import datetime
import json
import re
import urllib.parse
import logging
from .models import *
from channels import Group
from channels.sessions import channel_session
from .views import sendmail
import psycopg2
from django.db import transaction
import threading
import time

@channel_session
def ws_add(message, room):
    print(message)
    query = urllib.parse.parse_qs(message['query_string'])
    if 'username' not in query:
        print("ws_add: no username")
        return
    logging.info('Adding websocket with username %s in room %s',
                 query['username'][0], room)
    Group('chat-%s' % room).add(message.reply_channel)
    message.channel_session['room'] = room
    message.channel_session['username'] = query['username'][0]


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
        print(message.channel_session['username'])
        author = User.objects.get(username=message.channel_session['username'])
        text = message.content['text']
        print("THIS IS THE MESSAGE TEXT")
        print(text)
        if text == "ack":
            db_room.set_saw(author)
            print(db_room.req_saw, db_room.off_saw)
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
    print(user)
    if user == author:
        user = db_room.need.author
    t1 = threading.Thread(target=email_check,args=(user,author, room, text,))
    t1.start()
    Group('chat-%s' % room).send({
        'text': json.dumps({
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
