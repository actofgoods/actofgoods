from django.db import models
from datetime import datetime
# Create your models here.


class Message(models.Model):
	text = models.CharField(max_length=300)

class Userdata(models.Model):
	pseudonym = models.CharField(max_length=15, primary_key=True)
	email = models.CharField(max_length=60)
	phone = models.CharField(max_length=13)
	register_date = models.DateTimeField(default=datetime.now, blank=True)
	messages= models.ManyToManyField(Message)
	GENDER = (('m', 'Male'),('f', 'Female'),)
	gender = models.CharField(max_length=1, choices=GENDER)

class Comment(models.Model):
	author = models.ForeignKey(Userdata, on_delete=models.CASCADE)
	test = models.CharField(max_length=300)

class Information(models.Model):
	author = models.ForeignKey(Userdata, on_delete=models.CASCADE)
	headline = models.CharField(max_length=30)
	text = models.CharField(max_length=300)
	comments = models.ManyToManyField(Comment)

class Need(models.Model):
	author = models.ForeignKey(Userdata, on_delete=models.CASCADE)
	headline = models.CharField(max_length=30)
	text = models.CharField(max_length=300)

class Users(models.Model):
	email = models.CharField(max_length=60)
	password = models.CharField(max_length=60)
	last_login_date = models.DateTimeField(default=datetime.now, blank=True)
	register_date = models.DateTimeField(default=datetime.now, blank=True)
