from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
# Create your views here.
from .models import Users


"""
    Index:
    -input: Cookies -> Informationen ob der Nutzer bereits Einlogg daten Hinterlegt hat
    -output: Main- or Indexpage
"""
def actofgoods_startpage(request):

    if request.user.is_authenticated():
        return redirect('basics:home')

    return render(request, 'basics/actofgoods_startpage.html', {})

"""
    Login:
    -input: request(Email, Password, ToggleButton (keep signed in?))
    -output: Main- or Indexpage
"""
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
        if 'email' and 'password' and 'check_password'  in request.POST :
            email = request.POST.get('email',None)
            password = request.POST.get('password',None)
            check_password = request.POST.get('check_password',None)
            country = request.POST.get('country',None)
            if password == check_password:
                #   TODO: with Djangos Users we need a username
                user = User.objects.create_user(username=email, password=password, email="email ")
                return login(request)

    return render(request, 'basics/actofgoods_startpage.html', {})


"""
    Profil:
    -input: Cookies ->
    -output: Profilpage
"""
def profil(request):
    return render(request, 'basics/profil.html')

def chat(request):
    return render(request, 'basics/chat.html')

def aboutus(request):
    return render(request, 'basics/aboutus.html')
def privacy(request):
    return render(request, 'basics/privacy.html')

def home(request):
    return render(request, 'basics/home.html')
