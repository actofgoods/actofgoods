import random
import smtplib
import string
import requests
import json
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
# Create your views here.
from .forms import UserFormRegister, NeedFormNew, InformationFormNew, CaptchaForm,ProfileForm, ImmediateAidFormNew,PasswordForm, ContactUsForm
from .models import *



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
                room=Room.objects.filter(Q(need__author =request.user) | Q(user_req = request.user)).latest('last_message')
                return redirect('basics:chat_room', roomname=room.name)
            except:
                return render(request,'basics/no_chat.html')

    return redirect('basics:actofgoods_startpage')


def kick_user(request, roomname):
    if request.user.is_authenticated():
        room = Room.objects.get(name=roomname)
        room.user_req = None
        room.save()
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
        if room.need.author == request.user or room.user_req == request.user:
            messages = ChatMessage.objects.filter(room=roomname)
            message_json = "["
            for message in messages:
                message_json += json.dumps({
                    'message': message.text,
                    'username': message.author.username
                }) + ","
            message_json += "]"
            print(message_json)
            #Get all rooms where request.user is in contact with
            rooms = Room.objects.filter(Q(need__author =request.user) | Q(user_req = request.user)).exclude(name=roomname)
            print(rooms)
            return render(request, 'basics/chat.html',{'roomname':roomname, 'messages':message_json, 'rooms':rooms})

    return redirect('basics:actofgoods_startpage')

"""
    Input: request

    contact_us page will be rendered and returned.
"""
@csrf_protect
def contact_us(request):
    if request.method == "POST":
        form = ContactUsForm(request.POST)
        if form.is_valid() :
            email = request.POST.get('email')
            headline = request.POST.get('headline')
            text = request.POST.get('text')
            contactUsData = ContactUs(email=email, headline=headline, text=text)
            print(contactUsData.text)
            contactUsData.save()
            return render(request, 'basics/actofgoods_startpage.html')
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

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise the help page will be rendered and returned.
"""
def help(request):
    if request.user.is_authenticated():
        return render(request, 'basics/help.html')

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
        needs = Need.objects.order_by('date')
        return render(request, 'basics/home.html', {'needs': needs})

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
        infos = Information.objects.order_by('date')
        return render(request, 'basics/information_all.html',{'infos':infos})

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
                print(lat,lng)
                if lat != None and lng != None:
                    address = Address.objects.create(latitude=lat, longditude=lng)
                    data = info.cleaned_data
                    infodata = Information(author=request.user, headline=data['headline'], text=data['text'], address =address)
                    infodata.save()
                    return redirect('basics:information_all')

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
        comments = Comment.objects.filter(inf=information).order_by('-date')
        return render (request, 'basics/information_view.html', {'information':information, 'comments':comments})

    return redirect('basics:actofgoods_startpage')

def information_view_comment(request, pk):
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated:
        information = get_object_or_404(Information, pk=pk)
        if request.method == "POST":
            comment = Comment.objects.create(inf=information, author=request.user, text=request.POST['comment_text'])
        return redirect('basics:information_view', pk=pk)

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
    need_form = NeedFormNew()

    if request.method == "POST":
        #This method is super deprecated we need to make it more secure
        #it could lead to data sniffing and shitlot of problems;
        #But to demonstrate our features and only to demonstrate
        #it will send the given email his password


        form = ImmediateAidFormNew(request.POST)
        need_form = NeedFormNew(request.POST)

        # form.data.username = "user#" + str(User.objects.count())
        print(request.POST)
        #print(form.data)
        if form.is_valid() and need_form.is_valid():
            # print(form.cleaned_data)
            password_d = id_generator(9)
            check_password = password_d
            if password_d != "" and check_password != "" and request.POST.get('email', "") != "":
                if password_d == check_password:
                    lat, lng = getAddress(request)
                    if lat != None and lng != None:
                        user_data = form.cleaned_data
                        need_data = need_form.cleaned_data
                        address = Address.objects.create(latitude=lat, longditude=lng)
                        user = User.objects.create_user(username=user_data['email'], password=password_d, email=user_data['email'])
                        userdata = Userdata(user=user,pseudonym=("user" + str(User.objects.count())), address=address)
                        userdata.save()
                        content = "Thank you for joining Actofgoods \n\n You will soon be able to help people in your neighbourhood \n\n but please verify your account first on http://127.0.0.1:8000/verification/%s"%(userdata.pseudonym)
                        subject = "Confirm Your Account"
                        needdata = Need(author=user, headline=need_data['headline'], text=need_data['text'], categorie=need_data['categorie'], address = address)
                        needdata.save()
                        room = Room.objects.create(name=id_generator(), need=needdata)
                        room.save()

                        #need = NeedFormNew(request.POST)

                        #Content could also be possibly HTML! this way beautifull emails are possible
                        content = "You are a part of Act of Goods! \n Help people in your hood. \n See ya http://127.0.0.1:8000 \n Maybe we should give a direct link to your need, but its not implemented yet. \n Oh you need your password: %s"% (password_d)
                        subject = "Welcome!"


                        sendmail(user.email, content, subject )
                        return redirect('basics:home')
                    else:
                        messages.add_message(request, messages.INFO, 'location_failed')
                else:
                    messages.add_message(request, messages.INFO, 'wp')

        else:
            messages.add_message(request, messages.INFO, 'eae')





    return render(request, 'basics/immediate_aid.html', {'categories': CategoriesNeeds.objects.all, 'form' : form, 'need_form' : need_form })


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
        print(user)
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

def fill_needs(request):
    return redirect()

"""
    Needs authentication!

    Input: request (user)

    If user is not authenticated redirect to startpage.
    Otherwise a list of needs will be pult out of the database and added to ...
    The needs_all page will be rendered and returned.
"""
def needs_all(request):
    if request.user.is_authenticated():
        range = "Range"
        category = "Categories"
        cards_per_page = "Cards per page"
        needs = Need.objects.order_by('date')

        if request.method == "POST":
            if "" != request.POST['range']:
                range = request.POST['range']
            if "" != request.POST['category']:
                category = request.POST['category']
                needs = Need.objects.filter(categorie=CategoriesNeeds.objects.get(name=category))
            if "" != request.POST['cards_per_page']:
                cards_per_page = int(request.POST['cards_per_page'])
                needs = needs[:cards_per_page]


        return render(request, 'basics/needs_all.html',{'needs':needs,'categorie':CategoriesNeeds.objects.all, 'category':category, 'cards_per_page':cards_per_page, 'range':range})

    return redirect('basics:actofgoods_startpage')

@csrf_protect
def needs_help(request, id):
    #cat = CategoriesNeeds.objects.create(name="cool")
    if request.user.is_authenticated():
        if request.method == "GET":
            need = Need.objects.get(id=id)
            room = Room.objects.get(need=need)
            room.user_req = request.user
            room.save()
            return redirect('basics:chat_room', roomname=room.name)
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

            if need.is_valid():
                lat, lng = getAddress(request)
                if lat != None and lng != None:
                    address = Address.objects.create(latitude=lat, longditude=lng)
                    data = need.cleaned_data
                    needdata = Need(author=request.user, headline=data['headline'], text=data['text'], categorie=data['categorie'], address = address, was_reported=False)
                    needdata.save()
                    #TODO: id_generator will return random string; Could be already in use
                    room = Room.objects.create(name=id_generator(), need=needdata)
                    room.save()
                    return redirect('basics:needs_all')
        need = NeedFormNew()
        c = CategoriesNeeds(name="Others")
        c.save
        return render(request, 'basics/needs_new.html', {'need':need, 'categories': CategoriesNeeds.objects.all})

    return redirect('basics:actofgoods_startpage')


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
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active': False})
    if request.user.is_authenticated():
        user=request.user
        userdata=request.user.userdata
        if request.method == "POST":
            email= request.POST.get('email',None)
            pseudo=request.POST.get('pseudo',None)
            phone = request.POST.get('phone',None)
            aux= request.POST.get('aux',None)
            lat, lng = getAddress(request)
            if lat != None and lng != None:
                userdata.address.latitude=lat
                userdata.address.longditude=lng
                userdata.address.save()
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
        print(request.POST)
        #print(form.data)
        if form.is_valid():
            # print(form.cleaned_data)
            password = request.POST.get('password', "")
            check_password = request.POST.get('check_password', "")
            if password != "" and check_password != "" and request.POST.get('email', "") != "":
                if password == check_password:
                    lat, lng = getAddress(request)
                    if lat != None and lng != None:
                        data = form.cleaned_data
                        address = Address.objects.create(latitude=lat, longditude=lng)
                        user = User.objects.create_user(username=data['email'], password=data['password'], email=data['email'],)
                        userdata = Userdata(user=user,pseudonym=("user" + str(User.objects.count())), address=address, get_notifications= False)
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
        print(email,password)
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
            print(lat,lng)
        elif address != "":
            lat, lng = getLatLng(address)
        else:
            lat = None
            lng = None

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
                    print(new_password)
                    #Content could also be possibly HTML! this way beautifull emails are possible

                    content = 'Your new password is %s. Please change your password after you have logged in. \n http://127.0.0.1:8000'%(new_password)
                    subject = "Reset Password - Act Of Goods"
                    sendmail(email, content, subject )
                    return redirect('basics:reset_password_confirmation')
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

def groups(request):
    return render(request, 'basics/groups.html')

def report_need(request, pk):
    need = Need.objects.get(pk=pk)
    need.was_reported = True
    need.number_reports += 1
    need.reported_by.add(request.user.userdata)
    need.save()
    return needs_all(request)

def report_information(request, pk):
    info = Information.objects.get(pk=pk)
    info.was_reported = True
    info.number_reports += 1
    info.reported_by.add(request.user.userdata)
    info.save()
    return information_all(request)
