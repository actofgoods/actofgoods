from django.test import TestCase, Client
from .models import *
# Create your tests here.

class RegisterTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='test@test.test', password='test', email='test@test.test',)

    def test_register_wrong_post_data(self):
        c = Client()
        response = c.post('/register/', {'password': 'bla', 'check_password': 'bla' , 'address': 'Berlin Germany', 'lat':'', 'lng':''}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_register_without_email(self):
        c = Client()
        response = c.post('/register/', {'email': '', 'password': 'bla', 'check_password': 'bla' , 'address': 'Berlin Germany', 'lat':'', 'lng':''}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_register_without_password(self):
        c = Client()
        response = c.post('/register/', {'email': 'actofgoods@gmail.com', 'password': '', 'check_password': 'bla' , 'address': '', 'lat':'', 'lng':''}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_register_without_check_password(self):
        c = Client()
        response = c.post('/register/', {'email': 'actofgoods@gmail.com', 'password': 'bla', 'check_password': '' , 'address': '', 'lat':'', 'lng':''}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_register_without_address(self):
        c = Client()
        response = c.post('/register/', {'email': 'actofgoods@gmail.com', 'password': 'bla', 'check_password': 'bla' , 'address': '', 'lat':'', 'lng':''}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_register_without_lng(self):
        c = Client()
        response = c.post('/register/', {'email': 'actofgoods@gmail.com', 'password': 'bla', 'check_password': 'bla' , 'address': '', 'lat':'54.0', 'lng':''}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_register_without_lat(self):
        c = Client()
        response = c.post('/register/', {'email': 'actofgoods@gmail.com', 'password': 'bla', 'check_password': 'bla' , 'address': '', 'lat':'', 'lng':'54.0'}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_register_new_user_address(self):
        c = Client()
        response = c.post('/register/', {'email': 'actofgoods@gmail.com', 'password': 'bla', 'check_password': 'bla' , 'address': 'Germany Berlin', 'lat':'', 'lng':''}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/home/')

    def test_register_new_user_latlng(self):
        c = Client()
        response = c.post('/register/', {'email': 'actofgoods@gmail.com', 'password': 'bla', 'check_password': 'bla' , 'address': '', 'lat':'-10.234', 'lng':'43.543'}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/home/')

    def test_register_already_exist(self):
        c = Client()
        response = c.post('/register/', {'email': 'test@test.test', 'password': 'bla', 'check_password': 'bla' , 'address': 'Germany Berlin', 'lat':'', 'lng':''}, follow = True)
        print(response.redirect_chain)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

class LoginTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test@test.test', password='test', email='test',)

    def test_login_wrong_password(self):
        c = Client()
        response = c.post('/login/', {'email': 'test@test.test', 'password': 'bla'}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_login_wrong_email(self):
        c = Client()
        response = c.post('/login/', {'email': 'taest@test.test', 'password': 'test'}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_login_missing_all(self):
        c = Client()
        response = c.post('/login/', {'else': 'test@test.test','some_other': 'test'}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_login_missing_email(self):
        c = Client()
        response = c.post('/login/', {'password': 'test'}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_login_correct(self):
        c = Client()
        response = c.post('/login/', {'email': 'test@test.test','password': 'test'}, follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/home/')

class AuthenticatedTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='adam@test.test', password='adam', email='adam@test.test',)
        c = Client()
        response = c.post('/register/', {'email': 'test@test.test', 'password': 'test', 'check_password': 'test' , 'address': '', 'lat':'-10.234', 'lng':'43.543'}, follow = True)

    def test_authenticated_chat_no_permition(self):
        c = Client()
        response = c.post('/chat/', follow = True)
        print(response.redirect_chain, "Fuck yeah", response.content)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_authenticated_chat_permition(self):
        c = Client()
        response = c.post('/login/', {'email': 'test@test.test','password': 'test'})
        response = c.get('/chat/')
        print(response)
        self.assertTrue(response.status_code == 200)

    def test_authenticated_home_no_permition(self):
        c = Client()
        response = c.post('/profil/', follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_authenticated_information_all_no_permition(self):
        c = Client()
        response = c.post('/profil/', follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_authenticated_information_new_no_permition(self):
        c = Client()
        response = c.post('/profil/', follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_authenticated_needs_all_no_permition(self):
        c = Client()
        response = c.post('/needs_all/', follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

    def test_authenticated_need_new_no_permition(self):
        c = Client()
        response = c.post('/profil/', follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')


    def test_authenticated_profil_permition(self):
        c = Client()
        response = c.post('/login/', {'email': 'test@test.test','password': 'test'}, follow = True)
        response = c.get('/profil/')
        #file1 = open('templates/basics/.txt', 'r')
        #TODO: compare response.content with profil.html
        self.assertTrue(response.content)
        self.assertTrue(response.status_code == 200)

    def test_authenticated_profil_no_permition(self):
        c = Client()
        response = c.post('/profil/', follow = True)
        self.assertTrue(response.redirect_chain[len(response.redirect_chain)-1][0] == '/')

class NewNeedTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='adam@test.test', password='adam', email='adam@test.test',)
        c = Client()
        response = c.post('/register/', {'email': 'test@test.test', 'password': 'test', 'check_password': 'test' , 'address': '', 'lat':'-10.234', 'lng':'43.543'}, follow = True)

    #TODO: New Need with/out headlin/text/location/group/

class NewInfoTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='adam@test.test', password='adam', email='adam@test.test',)
        c = Client()
        response = c.post('/register/', {'email': 'test@test.test', 'password': 'test', 'check_password': 'test' , 'address': '', 'lat':'-10.234', 'lng':'43.543'}, follow = True)

class NewCommentTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='adam@test.test', password='adam', email='adam@test.test',)
        c = Client()
        response = c.post('/register/', {'email': 'test@test.test', 'password': 'test', 'check_password': 'test' , 'address': '', 'lat':'-10.234', 'lng':'43.543'}, follow = True)
        
class NewGroupTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='adam@test.test', password='adam', email='adam@test.test',)
        c = Client()
        response = c.post('/register/', {'email': 'test@test.test', 'password': 'test', 'check_password': 'test' , 'address': '', 'lat':'-10.234', 'lng':'43.543'}, follow = True)

class AdminTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='adam@test.test', password='adam', email='adam@test.test',)
        c = Client()
        response = c.post('/register/', {'email': 'test@test.test', 'password': 'test', 'check_password': 'test' , 'address': '', 'lat':'-10.234', 'lng':'43.543'}, follow = True)

class ChatTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='adam@test.test', password='adam', email='adam@test.test',)
        c = Client()
        response = c.post('/register/', {'email': 'test@test.test', 'password': 'test', 'check_password': 'test' , 'address': '', 'lat':'-10.234', 'lng':'43.543'}, follow = True)
