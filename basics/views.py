from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

# Create your views here.

"""
    Index:
    -input: Cookies -> Informationen ob der Nutzer bereits Einlogg daten Hinterlegt hat
    -output: Main- or Indexpage
"""
def index(request):
    #Todo: Check Cookies; if valid send user to Mainpage else Indexpage

    if 'keep_logged_in' in request.COOKIES:
        value = request.COOKIES['keep_logged_in']
        if value == 'true':
            if 'email' in request.COOKIES and 'password' in request.COOKIES:
                return HttpResponse("Here should be the Mainpage")#mainpage(EMAIL_VALUE, PASSWORD_VALUE, true)


    return HttpResponse("here should be your Indexpage")

"""
    Login:
    -input: Email, Password, ToggleButton (keep signed in?)
    -output: Main- or Indexpage
"""
def login(request):
    response = HttpResponse("this should return the main Login page.")
    email_value = ""
    password_value = ""
    toggle_button = False;

    """
        TODO: Get Email/Password and ToggleButton from request.POST['key']

        if request.POST['toggle_button'] = "true"
            toggle_button = true
    """

    #    TODO: Check if Data is Valid if not -> Return to Indexpage

    #    TODO: Add new User Model to Database


    return mainpage(email_value, password_value, toggle_button)

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
    return HttpResponse("Here should be our profil page.")
