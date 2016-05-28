from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
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

class Information(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	headline = models.CharField(max_length=30, default='')
	text = models.CharField(max_length=300, default='')
	closed = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now=True)

class Need(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	headline = models.CharField(max_length=30, default='')
	text = models.CharField(max_length=300, default='')
	closed = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now=True)

class Comment(models.Model):
	inf = models.ForeignKey(Information,on_delete=models.CASCADE)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	test = models.CharField(max_length=300)
	date = models.DateTimeField(auto_now=True)

