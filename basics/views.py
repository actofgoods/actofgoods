from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# Create your views here.
from .models import Users
"""
    Index:
    -input: Cookies -> Informationen ob der Nutzer bereits Einlogg daten Hinterlegt hat
    -output: Main- or Indexpage
"""

def actofgoods_startpage(request):
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
                # TODO right response
                return HttpResponse(aboutus(request))
            else:
                # TODO deactivate user page
                return HttpResponse(actofgoods_startpage(request))

    # default backfall
    return HttpResponse(actofgoods_startpage(request))

def logout(request):
    auth_logout(request)
    return HttpResponse(actofgoods_startpage(request))

"""
    Register:
    -input: request(Email, Password ...)
    -output: Main- or Indexpage
"""
def register(request):

    if request.method == 'POST':
        email = request.POST.get('email',None)
        password = request.POST.get('password',None)
        check_password = request.POST.get('check_password',None)
        country = request.POST.get('country',None)

    return render(request, 'basics/actofgoods_startpage.html', {})
>>>>>>> 1c0ab6ce3d4e5b8c498739ee237efb86e5988cdb


"""
    Mainpage:
    -input: email, password, toggle
    -response: Mainpage, filled with user specific info
"""
def mainpage(email, password, toggle_button):
    response = HttpResponse("here should be Our Mainpage")
    response.set_signed_cookie('keep_logged_in', toggle_button.__str__())
    response.set_signed_cookie('email', email)
    response.set_signed_cookie('password', password)



    #   TODO: Get User specific data from Databases

    #   TODO: Add the Data in the context

    context = {
        'key': "value",
    }

    return response

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
