from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
# Create your views here.
from .forms import UserFormRegister, NeedFormNew, InformationFormNew
from .models import Userdata, Need, Information
from django.views.decorators.csrf import csrf_protect


"""
    Index:
    -input: Cookies -> Informationen ob der Nutzer bereits Einlogg daten Hinterlegt hat
    -output: Main- or Indexpage
"""
def actofgoods_startpage(request):
    registerform = UserFormRegister()

    if request.user.is_authenticated():
        return redirect('basics:home')

    return render(request, 'basics/actofgoods_startpage.html', {'registerform':registerform})

"""
    Login:
    -input: request(Email, Password, ToggleButton (keep signed in?))
    -output: Main- or Indexpage
"""
@csrf_protect
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email',None)
        password = request.POST.get('password',None)
        user = authenticate(username=email,password=password)
        if user is not None:
            if user.is_active:
                auth_login(request,user)

        """

                return HttpResponse(aboutus(request))
            else:
                # TODO deactivate user page
                return HttpResponse(actofgoods_startpage(request))
        """
    # default backfall
    return redirect('basics:actofgoods_startpage')

def logout(request):
    auth_logout(request)
    return HttpResponse(actofgoods_startpage(request))

"""
    Register:
    -input: request(Email, Password ...)
    -output: Main- or Indexpage
"""
@csrf_protect
def register(request):
    """
    email_value = ""
    password_value = ""
    toggle_button = False;

        TODO: Get Email/Password and ToggleButton from request.POST['key']

        if request.POST['toggle_button'] = "true"
            toggle_button = true

    if 'email' in request.POST and 'password' in request.POST:
        email_value = request.POST['email']
        password_value = request.POST['password']
        if request.POST['toggle_button'] == "True":
            toggle_button = True;

        user = Users(email=email_value, password="password")
        #   TODO: Add new User Model to Database
        user.save()
        #   TODO: Send User Mail

        return redirect('basics:login')


    #   TODO: if something wents wrong:
    return redirect('basics:index')

    """
    if request.method == 'POST':
        form = UserFormRegister(request.POST)
        # form.data.username = "user#" + str(User.objects.count())

        print(form.data)
        if form.is_valid() :
            # print(form.cleaned_data)
            password = request.POST.get('password',None)
            check_password = request.POST.get('check_password',None)
            if password == check_password:
                data = form.cleaned_data
                user = User.objects.create_user(username=data['email'], password=data['password'], email=data['email'])
                userdata = Userdata(user=user,pseudonym=("user#" + str(User.objects.count())))
                userdata.save()

                                
                #   TODO: with Djangos Users we need a username

                return login(request)

    return redirect('basics:actofgoods_startpage')


"""
    Profil:
    -input: Cookies ->
    -output: Profilpage
"""
def profil(request):
    if request.user.is_authenticated():
        return render(request, 'basics/profil.html')

    return redirect('basics:actofgoods_startpage')


def chat(request):
    if request.user.is_authenticated():
        return render(request, 'basics/chat.html')

    return redirect('basics:actofgoods_startpage')

def home(request):
    if request.user.is_authenticated():
        return render(request, 'basics/home.html')

    return redirect('basics:actofgoods_startpage')

def aboutus(request):
    return render(request, 'basics/aboutus.html')

def privacy(request):
    return render(request, 'basics/privacy.html')

def help(request):
    if request.user.is_authenticated():
        return render(request, 'basics/help.html')

    return redirect('basics:actofgoods_startpage')

def needs_all(request):
    if request.user.is_authenticated():
        needs = Need.objects.order_by('date')
        return render(request, 'basics/needs_all.html',{'needs':needs})

    return redirect('basics:actofgoods_startpage')

# Must to change fpr render
def needs_view_edit(request):
    if request.user.is_authenticated:
        return render (request, 'basics/needs_view_edit')

    return redirect('basics:actofgoods_startpage')

@csrf_protect
def needs_new(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            need = NeedFormNew(request.POST)

            if need.is_valid():
                data = need.cleaned_data
                needdata = Need(author=request.user, headline=data['headline'], text=data['text'])
                needdata.save()
                return redirect('basics:needs_all')

        need = NeedFormNew()

        return render(request, 'basics/needs_new.html', {'need':need})

    return redirect('basics:actofgoods_startpage')

def needs_timeline(request):
    if request.user.is_authenticated():
        return render(request, 'basics/needs_timeline.html')

    return redirect('basics:actofgoods_startpage')

def information_all(request):
    if request.user.is_authenticated():
        infos = Information.objects.order_by('date')
        return render(request, 'basics/information_all.html',{'infos':infos})

    return redirect('basics:actofgoods_startpage')

@csrf_protect
def information_new(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            info = InformationFormNew(request.POST)

            if info.is_valid():
                data = info.cleaned_data
                infodata = Information(author=request.user, headline=data['headline'], text=data['text'])
                infodata.save()
                return redirect('basics:information_all')

        info = InformationFormNew()

        return render(request, 'basics/information_new.html', {'info':info})

    return redirect('basics:actofgoods_startpage')

def information_timeline(request):
    if request.user.is_authenticated():
        return render(request, 'basics/information_timeline.html')

    return redirect('basics:actofgoods_startpage')

def immediate_aid(request):
    return render(request, 'basics/immediate_aid.html')

def reset_password_page(request):
    return render(request, 'basics/password_reset.html')


