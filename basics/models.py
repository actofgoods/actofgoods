from django.db import models
from datetime import datetime
from django.contrib.auth.models import User, Group

# Create your models here.
class Message(models.Model):
	text = models.CharField(max_length=300)

# Not acces now errors incomings
class Userdata(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	pseudonym = models.CharField(max_length=15)
	phone = models.CharField(max_length=13)
	messages= models.ManyToManyField(Message)
	GENDER = (('m', 'Male'),('f', 'Female'),)
	gender = models.CharField(max_length=1, choices=GENDER)

class CategoriesNeeds(models.Model):
	name = models.CharField(max_length=50)

class CategoriesInf(models.Model):
	name = models.CharField(max_length=50)

class CategoriesRep(models.Model):
	name = models.CharField(max_length=50)

class Groupdata(models.Model):
	group = models.OneToOneField(Group, on_delete=models.CASCADE)
	email = models.EmailField(max_length=254)
	phone = models.CharField(max_length=15)
	is_NGO = models.BooleanField(default=True)
	# mabye changed
	adresse = models.CharField(max_length=254)

class Need(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
	headline = models.CharField(max_length=30, default='')
	text = models.TextField(default='')
	closed = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now=True)
	categorie = models.ForeignKey(CategoriesNeeds)

class Information(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
	headline = models.CharField(max_length=30, default='')
	text = models.TextField(default='')
	closed = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now=True)

class Comment(models.Model):
	inf = models.ForeignKey(Information,on_delete=models.CASCADE)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.TextField(default='')
	date = models.DateTimeField(auto_now=True)

class Vote(models.Model):
	date = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	info = models.ForeignKey(Information, on_delete=models.CASCADE)

class Report(models.Model):
	text = models.TextField(default='')
	categorie = models.ForeignKey(CategoriesRep)
	need = models.ForeignKey(Need)
	info = models.ForeignKey(Information)
	Comment = models.ForeignKey(Comment)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

class Address(models.Model):
	street = models.TextField(default='')
	city = models.TextField(default='')
	state = models.TextField(default='')
	postcode = models.TextField(default='')
	country = models.TextField(default='')
