import datetime
from datetime import timedelta
import random
import smtplib
import string
import requests
import json
import numpy as np
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.template import loader
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.message import MIMEMessage
from django.utils import timezone
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
# Create your views here.
from .forms import *
from .models import *
from itertools import chain
from math import *



"""
    Index:
    -input: Cookies -> Informationen ob der Nutzer bereits Einlogg daten Hinterlegt hat
    -output: Main- or Indexpage
"""
def actofgoods_startpage(request):
    registerform = UserFormRegister()
    needs = Need.objects.all()
    if request.user.is_authenticated():
        return redirect('basics:home')
    return render(request, 'basics/actofgoods_startpage.html', {'counter':len(needs),'registerform':registerform})

"""
    Input: request

    aboutus page will be rendered and returned.
"""
def aboutus(request):
    return render(request, 'basics/aboutus.html')

"""
    Input: request

    admin_page will be rendered and returned.
"""
def admin_page(request):
    return render(request, 'basics/admin_page.html')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    ...
"""
def change_password(request):
    if request.user.is_authenticated():
        if not request.user.is_active:
            return render(request, 'basics/verification.html', {'active':False})
        user=request.user
        if request.method=="POST":
        	form=PasswordForm(request.POST)
        	if form.is_valid():
        		oldpw=request.POST['oldpw']
        		newpw1=request.POST.get('newpw1')
        		newpw2=request.POST.get('newpw2')
        		if (authenticate(username=user.email,password=oldpw)==user) and (newpw1 == newpw2):
        			user.set_password(newpw1)
        			user.save()
        			return render(request, 'basics/profil.html', {'Userdata':user.userdata})

        		else :
        			change=True
        			return render(request,'basics/change_password.html',{'change':change})

        form=PasswordForm()
        change=False
        return render(request,'basics/change_password.html',{'form':form,'change':change})
    return redirect('basics:actofgoods_startpage')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise the chat page will be rendered and returned.
"""
def chat(request):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated():
        if request.method == "GET":
            try:
                room=get_valid_rooms(request.user).latest('last_message')
                return redirect('basics:chat_room', roomname=room.name)
            except:
                return render(request,'basics/no_chat.html')
    return redirect('basics:actofgoods_startpage')

def get_valid_rooms(user):
    return Room.objects.filter(Q(need__author =user) | Q(user_req = user, helper_out=False))

def kick_user(request, roomname):
    if request.user.is_authenticated():
        room = Room.objects.get(name=roomname)
        text = "Helper was kicked."
        if request.user == room.user_req:
            text = "Helper leaved."
        room.helper_out = True
        room.save()
        ChatMessage.objects.create(room=room, text=text, author=None)
    return redirect('basics:actofgoods_startpage')

def needs_finish(request, roomname):
    if request.user.is_authenticated():
        room = Room.objects.get(name=roomname)
        text = request.user.username + " finished."
        print(room.name, request.user.username)
        room.set_room_finished(request.user)
        ChatMessage.objects.create(room=room, text=text, author=None)
    return redirect('basics:actofgoods_startpage')
"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise the chat_room page will be rendered and returned.
"""
def chat_room(request, roomname):
    if request.user.is_authenticated():
        room = Room.objects.get(name=roomname)
        name = room.need.headline
        if room.need.author == request.user or (room.user_req == request.user and not room.helper_out):
            room.set_saw(request.user)
            messages = ChatMessage.objects.filter(room=roomname).order_by('date')
            message_json = messages_to_json(messages)
            #Get all rooms where request.user is in contact with
            rooms = get_valid_rooms(request.user).exclude(name=roomname).order_by('-last_message')
            rooms_json = rooms_to_json(rooms, request.user)
            return render(request, 'basics/chat.html',{'name':name, 'room':room, 'roomname':roomname, 'messages':message_json, 'rooms':rooms, 'rooms_json':rooms_json})

    return redirect('basics:actofgoods_startpage')


def messages_to_json(messages):
    message_json = "["
    for message in messages:
        try:
            message_json += json.dumps({
                'message': message.text,
                'username': message.author.username,
                'date': message.date.__str__()[:-13]
            }) + ","
        except:
            message_json += json.dumps({
                'message': message.text,
                'username': 'null',
                'date': message.date.__str__()[:-13]
            }) + ","
    message_json += "]"
    return message_json

def rooms_to_json(rooms, user):
    rooms_json = "["
    if len(rooms) > 0:
        for room in rooms:
            new_message =  "true" if room.new_message(user) else "false"
            rooms_json   += json.dumps({
                'name': room.need.headline,
                'hash': room.name,
                'new': new_message,
                'last_message': room.recent_message(),
                'date': room.last_message.__str__()[:-13]
            }) + ","
        rooms_json = rooms_json[:-1]
    rooms_json += "]"
    print(rooms_json)
    return rooms_json
"""
    Input: request

    contact_us page will be rendered and returned.
"""
@csrf_protect
def claim(request, name):
    if request.user.is_authenticated():
        if request.user.groups.filter(name=name).exists():
            categories=CategoriesNeeds.objects.all
            return render(request, 'basics/map_claim.html', {'categories': categories,'group': name, 'polygons': ClaimedArea.objects.all(), 'polyuser': ClaimedArea.objects.order_by('pk').filter(group=request.user.groups.get(name=name))})
    return redirect('basics:actofgoods_startpage')

@csrf_protect
def claim_post(request, name):
    if request.user.is_authenticated():
        if request.user.groups.filter(name=name).exists():
            if request.method=="POST":
                poly_path=request.POST['path']
                #name=request.POST['name']
                response_data = {}
                claimname=request.POST['claimname']
                wkt = "POLYGON(("+poly_path+"))"
                gro = request.user.groups.get(name=name)
                claim = ClaimedArea.objects.create(claimer=request.user,group=gro, poly=wkt, title=claimname)
                claim.save()
                response_data['result'] = 'Creation successful!'
                response_data['owner']=request.user.email
                response_data['poly']=claim.poly.geojson
                response_data['pk']=claim.pk
                response_data['claimname']=claim.title

                return JsonResponse(response_data)
    return redirect('basics:actofgoods_startpage')

@csrf_protect
def claim_delete(request,name):
    if request.user.is_authenticated():
        if request.user.groups.filter(name=name).exists():
            if request.method=="POST":
                pk=request.POST['pk']
                ClaimedArea.objects.all().get(pk=pk).delete()
                response_data = {}
                response_data['result'] = 'Deletion successful!'
                return JsonResponse(response_data)
    return redirect('basics:actofgoods_startpage')

@csrf_protect
def claim_refresh(request,name):
   if request.user.is_authenticated():
        if request.user.groups.filter(name=name).exists():
            index=request.POST['index']
            pk = request.POST['pk']
            t = loader.get_template('snippets/claim.html')
            return HttpResponse(t.render({'index':index, 'poly': ClaimedArea.objects.get(pk=pk)}))

@csrf_protect
def claim_needs(request, name):
    if request.user.is_authenticated():
        #TODO: Change this to somehing like user distance
        group = Groupdata.objects.get(name=name)
        liste=request.POST.getlist('liste[]')
        if liste:
            claims = ClaimedArea.objects.filter(pk__in=liste)
        else:
            claims = ClaimedArea.objects.filter(group=group.group)
        needs=Need.objects.all().order_by('-priority', 'pk')

        #for claim in claims:
        if claims.exists():
            query = Q(adrAsPoint__within=claims[0].poly)
            for q in claims[1:]:
                query |= Q(adrAsPoint__within=q.poly)
            needs = needs.filter(query)
        if "" != request.POST['category'] and "All" != request.POST['category']:
            category = request.POST['category']
            needs = needs.filter(categorie=CategoriesNeeds.objects.get(name=category))
        if "" != request.POST['wordsearch']:
            wordsearch = request.POST['wordsearch']
            needs = needs.filter(Q(headline__contains=wordsearch) | Q(text__contains=wordsearch))
        t = loader.get_template('snippets/claim_needs.html')
        return HttpResponse(t.render({'user': request.user, 'needs':needs}))
    return redirect('basics:actofgoods_startpage')

@csrf_protect
def claim_information(request, name):
    if request.user.is_authenticated():
        #TODO: Change this to somehing like user distance
        group = Groupdata.objects.get(name=name)
        liste=request.POST.getlist('liste[]')
        if liste:
            claims = ClaimedArea.objects.filter(pk__in=liste)
        else:
            claims = ClaimedArea.objects.filter(group=group.group)
        infos=Information.objects.all().order_by('priority', 'pk').reverse()

        #for claim in claims:
        if claims.exists():
            query = Q(adrAsPoint__within=claims[0].poly)
            for q in claims[1:]:
                query |= Q(adrAsPoint__within=q.poly)
            infos = infos.filter(query)
        if "" != request.POST['wordsearch']:
            wordsearch = request.POST['wordsearch']
            infos = infos.filter(Q(headline__contains=wordsearch) | Q(text__contains=wordsearch))
        t = loader.get_template('snippets/claim_informations.html')
        return HttpResponse(t.render({'user': request.user, 'infos':infos}))
    return redirect('basics:actofgoods_startpage')

@csrf_protect
def claim_report(request, name):
    pk=int(request.POST['pk'])
    #print(pk)
    need = Need.objects.get(pk=pk)
    need.was_reported = True
    need.number_reports += 1
    need.save()
    need.reported_by.add(request.user.userdata)
    #print(Need.objects.get(pk=pk).reported_by.all())
    t = loader.get_template('snippets/claim_report.html')
    return HttpResponse(t.render({'user': request.user, 'need':need}))


@csrf_protect
def contact_us(request):
    if request.method == "POST":
        form = ContactUsForm(request.POST)
        if form.is_valid() :
            email = request.POST.get('email')
            headline = request.POST.get('headline')
            text = request.POST.get('text')
            if email != "":
                if headline != "":
                    if text != "":
                        contactUsData = ContactUs(email=email, headline=headline, text=text)
                        contactUsData.save()
                        messages.add_message(request, messages.INFO, 'success contact us')
                        return redirect('basics:actofgoods_startpage')
                    else:
                        messages.add_message(request, messages.INFO, 'no_description')
                else:
                    messages.add_message(request, messages.INFO, 'no_headline')
            else:
                messages.add_message(request, messages.INFO, 'empty_email')
        else:
            messages.add_message(request, messages.INFO, 'wrong_email')
    return render(request, 'basics/contact_us.html')

"""
    Input: String with an address

    getLatLng will send an request to googleapis and recieve an json containing
    latitude and longditude.
"""
def getLatLng(location):
    location = location.replace(" ", "%20")
    req = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % location #parameter
    response = requests.get(req)
    jsongeocode = response.json()
    return jsongeocode['results'][0]['geometry']['location']['lat'], jsongeocode['results'][0]['geometry']['location']['lng']

def faq_startpage(request):
    return render(request, 'basics/faq_startpage.html')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise the faq page will be rendered and returned.
"""
def faq_signin(request):
    if request.user.is_authenticated():
        return render(request, 'basics/faq_signin.html')
    return redirect('basics:actofgoods_startpage')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise a list of needs will be pult out of the database and added to ...
    The home page will be rendered and returned.
"""
def home(request):
    if request.user.is_authenticated():
        needs = list(Need.objects.all().filter(author=request.user))
        #print("You help here: ", needs)
        infos = list(Information.objects.all().filter(author=request.user))
        needs_you_help = list(map(lambda x: x.need, list(Room.objects.all().filter(user_req=request.user))))
        comm = list(Comment.objects.all().filter(author=request.user))
        rel_comms = []
        for c in comm:
            if not c.inf in rel_comms:
                rel_comms.append(c)
        result_list = sorted(
            chain(needs, infos, needs_you_help, rel_comms),
            key=lambda instance: instance.was_helped_at.was_helped_at if hasattr(instance, 'was_helped_at') and instance not in needs else instance.date, reverse=True)
        #print(list(map(lambda x: x.pk, needs_you_help)))
        #print(result_list)
        #print(list(map(lambda x: x.pk, result_list)))
        return render(request, 'basics/home.html', {'needs': needs, 'infos': infos, 'needs_you_help': needs_you_help, 'result_list': result_list})

    return redirect('basics:actofgoods_startpage')

def delete_comment_timeline(request, pk):
    if request.user.is_authenticated():
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return redirect('basics:home')
    return redirect('basics:actofgoods_startpage')

"""
    id_generator generates a random string 6 chars long if no other size is provided.
"""
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise a list of needs will be pult out of the database and added to ...
    The needs_all page will be rendered and returned.
"""
@csrf_protect
def information_all(request):
    if request.user.is_authenticated():
        if request.user.userdata:
            dist = request.user.userdata.aux
        else:
            dist=500
        cards_per_page = "Cards per page"
        infos = Information.objects.all()
        for i in infos:
            if i.update_at.update_at < timezone.now():
                hours_elapsed = int((timezone.now() - i.date).seconds/3600)
                i.update_at.update_at = timezone.now() + timedelta(hours=1)
                if i.group:
                    priority = priority_info_group(hours_elapsed, i.number_likes)
                else:
                    priority = priority_info_user(hours_elapsed, i.number_likes)
                i.priority = priority
                i.save()
        infos = Information.objects.order_by('priority', 'pk').reverse()
        if request.method == "POST":
            #print(request.POST['range'], request.POST['cards_per_page'])
            if "" != request.POST['range']:
                range = request.POST['range']
            if "" != request.POST['cards_per_page']:
                cards_per_page = int(request.POST['cards_per_page'])
                infos = infos[:cards_per_page]
            #print(request)
        else:
            print("will nicgt")
        return render(request, 'basics/information_all.html',{'infos':infos, 'cards_per_page':cards_per_page, 'range':dist})

    return redirect('basics:actofgoods_startpage')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    If request method is POST 'immediate_aid' will check info form.
    All being well, a new information is created and stored in database.

"""
@csrf_protect
def information_new(request):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated():
        if request.method == "POST":
            info = InformationFormNew(request.POST)
            if info.is_valid():
                lat, lng = getAddress(request)
                #print(lat,lng)
                u=Update.objects.create(update_at=(timezone.now() + timedelta(hours=1)))
                priority = 0
                group = None
                author_is_admin = False
                data = info.cleaned_data
                #print(request.POST)
                if request.POST.get('group') != 'no_group' and request.POST.get('group') != None and request.POST.get('group') != 'admin':
                    group = Group.objects.get(pk=request.POST.get('group'))
                    priority = priority_info_group(0, 0)
                elif request.POST.get('group') == 'no_group':
                    priority = priority_info_user(0, 0)
                elif request.POST.get('group') == 'admin':
                    priority = priority_info_group(0, 0)
                    author_is_admin = True

                if lat == None or lng == None:
                    lat, lng = Userdata.objects.get(user=request.user).get_lat_lng();
                infodata = Information(author=request.user, author_is_admin=author_is_admin, headline=data['headline'], text=data['text'], adrAsPoint=GEOSGeometry('POINT(%s %s)' % (lat, lng)), priority=priority, update_at=u)
                infodata.group = group
                infodata.save()
                return redirect('basics:information_all')
            else:
                messages.add_message(request, messages.INFO, 'not_valid')
        info = InformationFormNew()
        return render(request, 'basics/information_new.html', {'info':info})

    return redirect('basics:actofgoods_startpage')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise the information_timeline page will be rendered and returned.
"""
def information_timeline(request):
    if request.user.is_authenticated():
        return render(request, 'basics/information_timeline.html')

    return redirect('basics:actofgoods_startpage')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise the needs_view_edit page will be rendered and returned.
"""
def information_view(request, pk):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated:
        information = get_object_or_404(Information, pk=pk)
        comments = Comment.objects.filter(inf=information).order_by('date')
        return render (request, 'basics/information_view.html', {'information':information, 'comments':comments})
    return redirect('basics:actofgoods_startpage')

def information_delete_comment(request, pk_inf, pk_comm):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated:
        comment = Comment.objects.get(pk=pk_comm)
        comment.delete()
        return redirect('basics:information_view', pk=pk_inf)
    return redirect('basics:actofgoods_startpage')

def information_view_comment(request, pk):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated:
        information = get_object_or_404(Information, pk=pk)
        if request.method == "POST":
            group = None
            if request.POST.get('group') != 'no_group' and request.POST.get('group') != None:
                group = Group.objects.get(pk=request.POST.get('group'))
            comment = Comment.objects.create(inf=information, author=request.user, group=group, text=request.POST['comment_text'])
        return redirect('basics:information_view', pk=pk)

    return redirect('basics:actofgoods_startpage')

def information_update(request, pk):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated():
        information= Information.objects.all().get(pk=pk)
        if request.method == "POST":
            text = request.POST.get('text', None)
            lat, lng = getAddress(request)
            if lat != None and lng != None:
                information.address=Address.objects.create(latitude=lat, longditude=lng)
            if text != "":
                information.text = information.text + "\n UPDATE " + timezone.now().strftime("%Y-%m-%d %H:%M:%S %Z") +"\n" + text
            else:
                messages.add_message(request, messages.INFO, 'empty_text')
                return render(request, 'basics/information_update.html', {'information':information})
            information.save()
            return actofgoods_startpage(request)
        form = InformationFormNew()
        return render(request, 'basics/information_update.html', {'information':information})
    return redirect('basics:actofgoods_startpage')

def follow(request, pk):
    if request.user.is_authenticated():
        info = Information.objects.get(pk=pk)
        info.followed_by.add(request.user.userdata)
        info.save()
        return redirect('basics:information_all')
    return redirect('basics:actofgoods_startpage')

def unfollow(request, pk):
    if request.user.is_authenticated():
        info = Information.objects.get(pk=pk)
        info.followed_by.remove(request.user.userdata)
        info.save()
        return redirect('basics:information_all')
    return redirect('basics:actofgoods_startpage')

"""
    Input: request(Email, Password)

    If request method is POST 'immediate_aid' will check the need and user form.
    Is everything valid, the method will proceed by creating a new password and user,
    creating a new need and finaly send an email to the new created user, providing
    greatings and his password.
"""
@csrf_protect
def immediate_aid(request):

    form = ImmediateAidFormNew(initial={'email': ''})
    need = NeedFormNew()

    if request.method == "POST":
        #This method is super deprecated we need to make it more secure
        #it could lead to data sniffing and shitlot of problems;
        #But to demonstrate our features and only to demonstrate
        #it will send the given email his password


        form = ImmediateAidFormNew(request.POST)
        need = NeedFormNew(request.POST)

        # form.data.username = "user#" + str(User.objects.count())
        ##print(request.POST)
        ##print(form.data)
        if form.is_valid() and need.is_valid():
            ##print(need.data)
            password_d = id_generator(9)
            check_password = password_d
            if request.POST.get('email', "") != "":
                lat, lng = getAddress(request)
                if lat != None and lng != None:
                    user_data = form.cleaned_data
                    user = User.objects.create_user(username=user_data['email'], password=password_d, email=user_data['email'])
                    userdata = Userdata(user=user,pseudonym=("user" + str(User.objects.count())), adrAsPoint=GEOSGeometry('POINT(%s %s)' % (lat, lng)))
                    userdata.save()
                    content = "Thank you for joining Actofgoods \n\n You will soon be able to help people in your neighbourhood \n\n but please verify your account first on http://127.0.0.1:8000/verification/%s"%(userdata.pseudonym)
                    subject = "Confirm Your Account"
                    #print("\n",need.cleaned_data['categorie'],"\n")
                    data = need.cleaned_data
                    u=Update.objects.create(update_at=(timezone.now() + timedelta(hours=1)))
                    needdata = Need(author=user, group=None, headline=data['headline'], text=data['text'], categorie=data['categorie'], was_reported=False, adrAsPoint=GEOSGeometry('POINT(%s %s)' % (lat, lng)), priority=priority_need_user(0), update_at=u)
                    needdata.save()


                    #Content could also be possibly HTML! this way beautifull emails are possible
                    content = "You are a part of Act of Goods! \n Help people in your hood. \n See ya http://127.0.0.1:8000 \n Maybe we should give a direct link to your need, but its not implemented yet. \n Oh you need your password: %s"% (password_d)
                    subject = "Welcome!"
                    user = authenticate(username=user_data['email'],password=password_d)
                    auth_login(request,user)

                    sendmail(user.email, content, subject )
                    return redirect('basics:actofgoods_startpage')
                else:
                    messages.add_message(request, messages.INFO, 'location_failed')
            else:
                messages.add_message(request, messages.INFO, 'wp')

        else:
            messages.add_message(request, messages.INFO, 'eae')
            #print(need.data)

    return render(request, 'basics/immediate_aid.html', {'categories': CategoriesNeeds.objects.all, 'form' : form, 'need' : need })



"""
    Input: request(Email, Password)

    If request method is POST 'login' will authenticate a user with the
    email and password provided. If a suitable user is found it will be logged in.
    Otherwise the login page will be returned with an error above login form.
"""
@csrf_protect
def login(request):

    if request.method == 'POST':
        email = request.POST.get('email',None)
        password = request.POST.get('password',None)
        user = authenticate(username=email,password=password)
        #print(user)
        if user is not None:
            if user.is_active:
                auth_login(request,user)
        else :
            messages.add_message(request, messages.INFO, 'lw')
    return redirect('basics:actofgoods_startpage')

"""
    Needs authentication!

    Input: request (user)

    Current user will be loged out.
"""
def logout(request):
    auth_logout(request)
    return HttpResponse(actofgoods_startpage(request))
    #return render(request, 'basics/actofgoods_startpage.html')
"""
    will return map_testing for resing purposes
"""
def map_testing(request):
    return render(request, 'basics/map_testing.html')

"""
Fills the Database with count needs of every category thats in the database
"""
def fill_needs(request, count):
    categories = CategoriesNeeds.objects.all()
    for category in categories:
        for i in range(int(count)):
            lat = np.random.random()*50
            lng = np.random.random()*50
            need = Need.objects.create(author=request.user, headline=str(i) + " " + category.name, text=str(i), categorie=category, was_reported=False, adrAsPoint=GEOSGeometry('POINT(%s %s)' % (lat, lng)))
    return redirect(request, 'basics:needs_all')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise a list of needs will be pult out of the database and added to ...
    The needs_all page will be rendered and returned.
"""
def needs_all(request):
    if request.user.is_authenticated():
        #TODO: Change this to somehing like user distance
        if request.user.userdata:
            dist = request.user.userdata.aux
        else:
            dist=500
        category = "All"
        cards_per_page = 10
        wordsearch = ""
        needs = Need.objects.all()
        for n in needs:
            if n.update_at.update_at < timezone.now():
                hours_elapsed = int((timezone.now() - n.date).seconds/3600)
                n.update_at.update_at = timezone.now() + timedelta(hours=1)
                if n.group:
                    priority = priority_need_group(hours_elapsed)
                else:
                    priority = priority_need_user(hours_elapsed)
                n.priority = priority
                n.save()

        needs=needs.order_by('-priority','pk')
        needs = needs.exclude(author=request.user).filter(done=False)
        page = 1
        page_range = np.arange(1, 5)
        if request.method == "GET":
            if not request.user.is_superuser:
                needs=needs.filter(adrAsPoint__distance_lte=(request.user.userdata.adrAsPoint, Distance(km=dist)))
        #TODO: this way is fucking slow and should be changed but i didn't found a better solution
        needs = [s for s in needs if not Room.objects.filter(need=s).filter(Q(helper_out=False)| Q(user_req=request.user)).exists()]
        max_page = int(len(needs)/cards_per_page)+1
        needs = needs[cards_per_page*(page-1):cards_per_page*(page)]
        #needs.sort(key=lambda x: (-x.priority, x.pk))
        page_range = np.arange(1,max_page+1)
        return render(request, 'basics/needs_all.html',{'needs':needs,'categorie':CategoriesNeeds.objects.all, 'category':category, 'wordsearch':wordsearch, 'cards_per_page':cards_per_page, 'range':dist, 'page':page, 'page_range':page_range})

    return redirect('basics:actofgoods_startpage')

def needs_filter(request):
    if request.user.is_authenticated():
        #TODO: Change this to somehing like user distance
        if request.user.userdata:
            dist = request.user.userdata.aux
        else:
            dist=500
        category = "All"
        cards_per_page = 10
        wordsearch = ""
        needs=Need.objects.all().order_by('-priority', 'pk')
        needs = needs.exclude(author=request.user)
        page = 1
        page_range = np.arange(1, 5)
        if request.method == "POST":
            #print(request.POST)
            if "" != request.POST['page']:
                page = int(request.POST['page'])
            if "" != request.POST['category'] and "All" != request.POST['category']:
                category = request.POST['category']
                needs = needs.filter(categorie=CategoriesNeeds.objects.get(name=category))
            if "" != request.POST['range']:
                dist= int(request.POST['range'].replace(',',''))
                if not request.user.is_superuser:
                    needs=needs.filter(adrAsPoint__distance_lte=(request.user.userdata.adrAsPoint, Distance(km=dist)))
            if "" != request.POST['wordsearch']:
                wordsearch = request.POST['wordsearch']
                needs = needs.filter(Q(headline__contains=request.POST['wordsearch']) | Q(text__contains=request.POST['wordsearch']))
            if "" != request.POST['cards_per_page']:
                cards_per_page = int(request.POST['cards_per_page'])
        elif request.method == "GET":
            if not request.user.is_superuser:
                needs=needs.filter(adrAsPoint__distance_lte=(request.user.userdata.adrAsPoint, Distance(km=dist)))
        #TODO: this way is fucking slow and should be changed but i didn't found a better solution
        needs = [s for s in needs if not Room.objects.filter(need=s).filter(Q(helper_out=False)| Q(user_req=request.user)).exists()]
        max_page = int(len(needs)/cards_per_page)+1
        needs = needs[cards_per_page*(page-1):cards_per_page*(page)]
        #needs.sort(key=lambda x: (-x.priority, x.pk))
        page_range = np.arange(1,max_page+1)
        t = loader.get_template('snippets/need_filter.html')
        return HttpResponse(t.render({'user': request.user, 'needs':needs, 'page':page, 'page_range':page_range}))
    return redirect('basics:actofgoods_startpage')


@csrf_protect
def needs_help(request, id):
    #cat = CategoriesNeeds.objects.create(name="cool")
    if request.user.is_authenticated():
        if request.method == "GET":
            need = Need.objects.get(id=id)

            if need.author != request.user:
                #TODO: id_generator will return random string; Could be already in use
                if Room.objects.filter(need=need).filter(Q(user_req=request.user)|Q(helper_out=False)).exists():
                    #TODO: add error message, 'This need is currently in work'
                    return redirect('basics:actofgoods_startpage')
                room = Room.objects.create(name=id_generator(), need=need)
                room.user_req = request.user
                room.save()
                helped_at = Helped.objects.create(was_helped_at=timezone.now())
                need.was_helped_at = helped_at
                need.save()
                return redirect('basics:chat_room', roomname=room.name)
            else:
                print("User: " + request.user.email + " tried to help his own need: " + room.need.headline + "\n TODO: print error message for User" )
        #TODO: what todo if POST data is wrong or get comes in
        #return render(request, 'basics/needs_new.html', {'need':need, 'categories': CategoriesNeeds.objects.all})

    return redirect('basics:actofgoods_startpage')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise the needs_view_edit page will be rendered and returned.
"""
def needs_view(request, pk):
    if request.user.is_authenticated:
        need = get_object_or_404(Need, pk=pk)
        return render (request, 'basics/needs_view.html', {'need':need})

    return redirect('basics:actofgoods_startpage')

"""
    Needs authentication!

    Input: request (user, headline, text: will be maintext of the need)

    If user is not authenticated redirect to startpage.
    Otherwise POST requests will be checked if the form is correctly delivered.
    If so, a new need is created in the database and the user will be redirected
    to needs_all.
"""
@csrf_protect
def needs_new(request):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
        #cat = CategoriesNeeds.objects.create(name="cool")
    if request.user.is_authenticated():
        if request.method == "POST":
            need = NeedFormNew(request.POST)
            #print(need)
            if need.is_valid():
                lat, lng = getAddress(request)
                if lat == None or lng == None:
                    lat, lng =request.user.userdata.get_lat_lng()

                data = need.cleaned_data
                print('head')
                print(data['headline'])
                if data['headline'] != "":
                    if data['text'] != "":
                        group = None
                        priority = 0
                        if request.POST.get('group') != 'no_group' and request.POST.get('group') != None:
                            group = Group.objects.get(pk=request.POST.get('group'))
                            priority = priority_need_group(0)
                        else:
                            priority = priority_need_user(0)
                        u=Update.objects.create(update_at=(timezone.now() + timedelta(hours=1)))
                        needdata = Need(author=request.user, group=group, headline=data['headline'], text=data['text'], categorie=data['categorie'], was_reported=False, adrAsPoint=GEOSGeometry('POINT(%s %s)' % (lat, lng)), priority=priority, update_at=u)
                        needdata.save()

                        send_notifications(needdata)
                        return redirect('basics:actofgoods_startpage')
                    else:
                        messages.add_message(request, messages.INFO, 'no_text')
                else:
                    priority = priority_need_user(0)
                    messages.add_message(request, messages.INFO, 'no_headline')
            else:
                messages.add_message(request, messages.INFO, 'not_valid')
        need = NeedFormNew()
        c = CategoriesNeeds(name="Others")
        c.save
        return render(request, 'basics/needs_new.html', {'need':need, 'categories': CategoriesNeeds.objects.all})

    return redirect('basics:actofgoods_startpage')


def send_notifications(needdata):
    users_to_inform = needdata.categorie.userdata_set.all()
    users_to_inform = filter(lambda x: x.adrAsPoint.distance(needdata.adrAsPoint)< x.aux, users_to_inform)
    for user in users_to_inform:
        sendmail(user.user.email, needdata.headline + "\n\n"+ needdata.text, "Somebody needs your help: " + needdata.categorie.name)

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise the profil page will be rendered and returned.
"""
def needs_timeline(request):
    if request.user.is_authenticated():
        return render(request, 'basics/needs_timeline.html')

    return redirect('basics:actofgoods_startpage')

"""
    privacy, will render and return privacy.html
"""
def privacy(request):
	return render(request, 'basics/privacy.html')

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise the profil page will be rendered and returned.
"""
def profil(request):
    if request.user.is_authenticated():
        userdata=request.user.userdata
        return render(request, 'basics/profil.html',{'Userdata':userdata, 'selected': userdata.inform_about.all()})
    return redirect('basics:actofgoods_startpage')

"""
    Needs authentication!

    Input: request (user, email, pseudonym, phonenumber)

    If user is not authenticated redirect to startpage.
    Else this method will check if user the given data is valid.
    if not it will render the profil_edit page again
    otherwise the profil will be changed.
"""
def profil_edit(request):
    if request.user.is_authenticated():
        if not request.user.is_active:
            return render(request, 'basics/verification.html', {'active': False})
        user=request.user
        userdata=request.user.userdata
        if request.method == "POST":
            if request.POST.get('changePassword') == "on":
                oldpw = request.POST['oldpw']
                newpw1 = request.POST.get('newpw1')
                newpw2 = request.POST.get('newpw2')
                if (authenticate(username=user.email, password=oldpw) == user) and (newpw1 == newpw2):
                    user.set_password(newpw1)
                    user.save()
                else:
                    form = ProfileForm()
                    return render(request, 'basics/profil_edit.html',
                                  {'userdata': userdata, 'categories': CategoriesNeeds.objects.all,
                                   'selected': userdata.inform_about.all(), 'form': form, 'change':True})

            email= request.POST.get('email',None)
            pseudo=request.POST.get('pseudo',None)
            phone = request.POST.get('phone',None)
            aux= request.POST.get('aux',None)
            lat, lng = getAddress(request)
            if lat != None and lng != None:
                userdata.adrAsPoint=GEOSGeometry('POINT(%s %s)' % (lat, lng))
                userdata.save()
            if aux != "":
                try:
                    userdata.aux= float(aux)
                except ValueError:
                    print ("Not a float")
            if email!="":
                user.email=email
                user.save()
            if pseudo!= "":
                userdata.pseudonym=pseudo
            if phone!= "":
                userdata.phone=phone
            if request.POST.get('information') == "on":
                userdata.get_notifications = True
            else:
                userdata.get_notifications=False
            categories= request.POST.getlist('categories[]')
            for c in CategoriesNeeds.objects.all():
                if c.name in categories:
                    userdata.inform_about.add(c)
                else:
                    userdata.inform_about.remove(c)
            userdata.save()
            return render(request, 'basics/profil.html', {'Userdata':userdata, 'selected': userdata.inform_about.all()})
        form = ProfileForm()
        return render(request, 'basics/profil_edit.html', {'userdata':userdata, 'categories': CategoriesNeeds.objects.all, 'selected': userdata.inform_about.all(),'form':form})
    return redirect('basics:actofgoods_startpage')

def profil_delete(request):
    user=request.user
    user.delete()
    sendmail(user.email, "Auf Wiedersehen " + user.username + ", \n schade das sie ihr Profil gelöscht haben, aber keine Angst wir speichern all ihre Daten weiter 50 Jahre. \n"
    +"Wenn sie sich nicht innerhalb von 3 Tagen wieder anmelden werden wir ihren Wohnort an den höchst bietenden verkaufen. Wir bedanken uns für ihr Verständni. \n\n Mit Freundlichen Grüßen Act of Goods", "Auf Wiedersehen!")
    return actofgoods_startpage(request)

"""
    Register:
    -input: request(email, password, check_password)

    register, will check the data submitted from the form. If correct a new user
    will be created and an email send to the email-address submitted.

"""
@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserFormRegister(request.POST)
        # form.data.username = "user#" + str(User.objects.count())
        #print(request.POST)
        ##print(form.data)
        if form.is_valid():
            # #print(form.cleaned_data)
            password = request.POST.get('password', "")
            check_password = request.POST.get('check_password', "")
            if password != "" and check_password != "" and request.POST.get('email', "") != "":
                if password == check_password:
                    lat, lng = getAddress(request)
                    if lat != None and lng != None:
                        data = form.cleaned_data
                        user = User.objects.create_user(username=data['email'], password=data['password'], email=data['email'],)
                        userdata = Userdata(user=user,pseudonym=("user" + str(User.objects.count())), get_notifications= False, adrAsPoint=GEOSGeometry('POINT(%s %s)' % (lat, lng)))
                        userdata.save()
                        content = "Thank you for joining Actofgoods \n\n You will soon be able to help people in your neighbourhood \n\n but please verify your account first on http://127.0.0.1:8000/verification/%s"%(userdata.pseudonym)
                        subject = "Confirm Your Account"
                        sendmail(user.email, content, subject)
                        return login(request)
                    else:
                        messages.add_message(request, messages.INFO, 'location_failed')
                else:
                    messages.add_message(request, messages.INFO, 'wp')

        elif not form.is_valid():
            messages.add_message(request, messages.INFO, 'eae')


    return redirect('basics:actofgoods_startpage')

def verification(request,pk):
    if request.user.is_authenticated():
        if request.user.userdata.pseudonym == pk:
            user=request.user
            user.is_active = True
            user.save()
            return render(request, 'basics/verification.html', {'verified':True, 'active':True})
    if request.method == "POST":
        form = UserFormRegister(request.POST)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        user = authenticate(username=email, password=password)
        #print(email,password)
        if user is not None and user.userdata.pseudonym == pk :
            auth_login(request, user)
            user.is_active = True

            user.save()
            return render(request, 'basics/verification.html', {'verified': True, 'active':True})
    form=UserFormRegister()
    return render (request, 'basics/verification.html', {'verified':False, 'form':form, 'pk': pk, 'active': True})


def getAddress(request):
    try:
        address = request.POST['address']
        lat = request.POST['lat']
        lng = request.POST['lng']
        if not lat == "" and not lng == "":
            lat = float(lat)
            lng = float(lng)
            #print(lat,lng)
        elif address != "":
            lat, lng = getLatLng(address)
        else:
            lat = None
            lng = None

        print("current address lat: ", lat, " lng ", lng)
        return lat, lng
    except:
        return None, None


"""
    Input: request
    Output: if the method is POST and captcher and email are valid, a new
    password is generated and send via his email. He then will be redirected
    to reset_password_confirmation page.
"""
def reset_password_page(request):
    #If request.method is POST, reset_password_page will
    #parse the email provided and send an email
    #Else the reset_password_page.html is shown
    if request.method == "POST":
        capForm = CaptchaForm(request.POST)
        #This method is super deprecated we need to make it more secure
        #it could lead to data sniffing and shitlot of problems;
        #But to demonstrate our features and only to demonstrate
        #it will send the given email his password
        if 'email' in request.POST:
            if capForm.is_valid():
                email = request.POST['email']
                user = User.objects.get(email = email)
                if user is not None:
                    new_password = id_generator(9)
                    user.set_password(new_password)
                    user.save()
                    #print(new_password)
                    #Content could also be possibly HTML! this way beautifull emails are possible

                    content = 'Your new password is %s. Please change your password after you have logged in. \n http://127.0.0.1:8000'%(new_password)
                    subject = "Reset Password - Act Of Goods"
                    sendmail(email, content, subject )
                    messages.add_message(request, messages.INFO, 'success reset password')
                    return redirect('basics:actofgoods_startpage')
            elif not capForm.is_valid():
                messages.add_message(request, messages.INFO, 'wc')

    return render(request, 'basics/password_reset.html')

"""
    Renders password_reset_confirmation.html and returns it.
"""
def reset_password_confirmation(request):
    return render(request, 'basics/password_reset_confirmation.html')

"""
    Input: email, content: What will be the message body, subject

    sendmail, will send an email via the GMAIL smtp server and the
    our GmailAccount to the given email-address.
"""
def sendmail(email, content, subject):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg.attach(MIMEText(content))

    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login('actofgoods@gmail.com', 'actofgoods123')
    mail.sendmail('actofgoods@gmail.com', email, msg.as_string())
    mail.close()

@csrf_protect
def report_need(request):
    pk=int(request.POST['pk'])
    #print(pk)
    need = Need.objects.get(pk=pk)

    need.was_reported = True
    need.number_reports += 1
    need.save()
    need.reported_by.add(request.user.userdata)
    #print(Need.objects.get(pk=pk).reported_by.all())
    return needs_filter(request)

def report_information(request, pk):
    info = Information.objects.get(pk=pk)
    info.was_reported = True
    info.number_reports += 1
    info.reported_by.add(request.user.userdata)
    return redirect('basics:information_all')

def like_information(request, pk):
    info = Information.objects.get(pk=pk)
    info.was_liked = True
    info.number_likes += 1
    info.liked_by.add(request.user.userdata)
    info.save()
    hours_elapsed = int((timezone.now() - info.date).seconds/3600)
    info.priority = priority_info_user(hours_elapsed, info.number_likes)
    info.save()
    return redirect('basics:information_all')

def unlike_information(request, pk):
    info = Information.objects.get(pk=pk)
    info.number_likes -= 1
    if info.number_likes == 0:
        info.was_liked = False
    info.liked_by.remove(request.user.userdata)
    info.save()
    return redirect('basics:information_all')

def need_delete(request, pk):
    need = Need.objects.all().get(pk=pk)
    need.delete()
    return redirect('basics:actofgoods_startpage')

def info_delete(request, pk):
    info = Information.objects.all().get(pk=pk)
    info.delete()
    return redirect('basics:actofgoods_startpage')

def comm_delete(request, pk):
    comm = Comment.objects.all().get(pk=pk)
    comm.delete()
    return redirect('basics:actofgoods_startpage')

def need_edit(request, pk):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated():
        need= Need.objects.all().get(pk=pk)
        if request.method == "POST":
            text = request.POST.get('text', None)
            desc = request.POST.get('desc', None)
            lat, lng = getAddress(request)
            if lat != None and lng != None:
                need.adrAsPoint=GEOSGeometry('POINT(%s %s)' % (lat, lng))
            if text != "":
                need.text=text
            if desc != "":
                need.headline=desc
            need.save()
            return actofgoods_startpage(request)
        form = NeedFormNew()
        return render(request, 'basics/need_edit.html', {'need':need, 'categories': CategoriesNeeds.objects.all()})
    return redirect('basics:actofgoods_startpage')

def info_edit(request, pk):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated():
        info = Information.objects.all().get(pk=pk)
        if request.method == "POST":
            text = request.POST.get('text', None)
            desc = request.POST.get('desc', None)
            lat, lng = getAddress(request)
            if lat != None and lng != None:
                info.adrAsPoint=GEOSGeometry('POINT(%s %s)' % (lat, lng))
            if text != "":
                info.text = text
            if desc != "":
                info.headline = desc
            info.save()
            return actofgoods_startpage(request)
        form = InformationFormNew()
        return render(request, 'basics/info_edit.html', {'info': info})
    return redirect('basics:actofgoods_startpage')

def report_comment(request, pk):
    comment = Comment.objects.get(pk=pk)
    comment.was_reported = True
    comment.number_reports += 1
    comment.reported_by.add(request.user.userdata)
    return information_view(request, comment.inf.pk)

####################################################################################################################################################
###                             Group functions
####################################################################################################################################################

def groups_all(request):
    groups = Groupdata.objects.all().order_by('name')
    return render(request, 'basics/groups_all.html', {'groups':groups})

def group_detail(request, name):
    if request.user.is_authenticated():
        gro = request.user.groups.get(name=name)
        if request.method == "POST":
            form = GroupAddUserForm(request.POST)
            if form.is_valid():
                if 'add_group_member' in form.data:
                    email = request.POST.get('email')
                    if {'email': email} in User.objects.values('email'):
                        user = User.objects.get(email=email)
                        gro.user_set.add(user)
                    else:
                        messages.add_message(request, messages.INFO, 'wrong_email')
        users = gro.user_set.all()
        group = Groupdata.objects.get(name=gro.name)
        claims = ClaimedArea.objects.filter(group=group.group)

        #for claim in claims:
        needs = []
        infos = []
        if claims.exists():
            query = Q(adrAsPoint__within=claims[0].poly)
            for q in claims[1:]:
                query |= Q(adrAsPoint__within=q.poly)
            needs = Need.objects.filter(query)
            infos = Information.objects.filter(query)


        #print(infos)
        return render(request, 'basics/group_detail.html', {'group':group, 'users':users, 'needs':needs, 'infos':infos})
    return redirect('basics:actofgoods_startpage')


def group_edit(request, pk):
    if request.user.is_authenticated():
        if request.method == "GET":
            group = Groupdata.objects.get(pk=pk)
            return render(request, 'basics/group_edit.html', {'group': group})
        elif request.method == "POST":
            form = GroupEditForm(request.POST)
            lat, lng = getAddress(request)
            if form.is_valid():
                group = Groupdata.objects.get(pk=pk)
                email = request.POST.get('email')
                if request.POST.get('email', "") != "":
                    group.email = request.POST.get('email')
                if request.POST.get('phone') != "" :
                    group.phone = request.POST.get('phone')
                if lat != None and lng != None:
                    address = Address.objects.create(latitude=lat, longditude=lng)
                    group.address =address
                if request.POST.get('page') != "":
                    group.webpage=request.POST.get('page')
                if request.POST.get('description') !="":
                    group.description=request.POST.get('description')
                group.save()
                return group_detail(request, group.name)
    return redirect('basics:actofgoods_startpage')

def group_leave(request, pk):
    #print(User.objects.get(email=request.user))
    if request.user.is_authenticated():
        #if request.method == "POST":
        groupDa = Groupdata.objects.get(pk=pk)
        group = groupDa.group
        group.user_set.remove(request.user)
        group.save()
        if len(group.user_set.all()) == 0:
            group.delete()

    return redirect('basics:home')

def group_detail_for_user(request, name):
    if request.user.is_authenticated():
        gro = request.user.groups.get(name=name)
        group = Groupdata.objects.get(name=gro.name)
        return render(request, 'basics/group_detail_for_user.html', {'group':group})
    return redirect('basics:actofgoods_startpage')


####################################################################################################################################################
###                             Priority Functions
####################################################################################################################################################

def priority_need_user(x):
    """x is number of hours since need was posted"""
    if x < 12 and x >= 0:
        return pow(10, 4-(pow(x-12, 2)/144))
    elif x >= 12:
        return pow(10, 4-(pow((x-12)/6, 2)/144))
    return 0

def priority_need_group(x):
    if x < 12 and x >= 0:
        return pow(10, 4-(pow(x-12, 2)/144)) + 1000
    elif x >= 12:
        return pow(11, 1-(pow(x-12, 2)/5184)) * 1000
    return 0

def priority_info_user(x, likes):
    """x is number of hours since need was posted"""
    if (x-(likes/60)) < 24 and x >= 0:
        return (75000+likes)/15
    elif (x-(likes/60)) >= 24:
        return (75000+likes)/(x-9-(likes/60))
    return 0

def priority_info_group(x, likes):
    if (x-(likes/40)) < 24 and x >= 0:
        return ((3060000/41)+(3*likes))/(24-(384/41))
    elif (x-(likes/40)) >= 24:
        return ((3060000/41)+(3*likes))/(x-(384/41)-(likes/40))
    return 0
