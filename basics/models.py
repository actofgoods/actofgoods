from django.db import models
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import User, Group
from django.contrib.gis.db import models
from django.core.validators import RegexValidator

# Create your models here.
class Message(models.Model):
	text = models.CharField(max_length=300)

class Address(models.Model):
	latitude = models.FloatField()
	longditude = models.FloatField()

class CategoriesInf(models.Model):
	name = models.CharField(max_length=50)


class CategoriesNeeds(models.Model):
	name = models.CharField(max_length=50)

class ClaimedArea(models.Model):
	claimer=models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
	poly=models.PolygonField()
	objects = models.GeoManager()
	def __unicode__(self):
		return self.pk

# Not acces now errors incomings
class Userdata(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	pseudonym = models.CharField(max_length=15)
	phone = models.CharField(max_length=13)
	messages= models.ManyToManyField(Message)
	GENDER = (('m', 'Male'),('f', 'Female'),)
	gender = models.CharField(max_length=1, choices=GENDER)
	address = models.ForeignKey(Address, on_delete=models.CASCADE)
	get_notifications = models.BooleanField(default=False)
	inform_about = models.ManyToManyField(CategoriesNeeds)
	aux = models.PositiveIntegerField(default=50)
	adrAsPoint=models.PointField(null=True)
	def __unicode__(self):
		return self.pseudonym

class CategoriesRep(models.Model):
	name = models.CharField(max_length=50)

class Groupdata(models.Model):
	group = models.OneToOneField(Group, on_delete=models.CASCADE)
	alphanumeric = RegexValidator(r'^[0-9a-zA-Z ]*$', 'Only alphanumeric characters are allowed.')
	name = models.CharField(max_length=30, validators=[alphanumeric])
	email = models.EmailField(max_length=254)
	phone = models.CharField(max_length=15)
	is_GO = models.BooleanField(default=False)
	webpage = models.CharField(max_length=256)
	description = models.TextField(default='')
	# mabye changed
	address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)

class Update(models.Model):
	update_at = models.DateTimeField()

class Need(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
	headline = models.CharField(max_length=30, default='')
	text = models.TextField(default='')
	closed = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)
	categorie = models.ForeignKey(CategoriesNeeds)
	address = models.ForeignKey(Address, on_delete=models.CASCADE)
	was_reported = models.BooleanField(default=False)
	number_reports = models.PositiveIntegerField(default=0)
	reported_by = models.ManyToManyField(Userdata)
	adrAsPoint=models.PointField(null=True)
	objects = models.GeoManager()
	priority = models.FloatField(default=1000)
	update_at = models.ForeignKey(Update, on_delete=models.CASCADE, blank=True, null=True)

class Information(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
	headline = models.CharField(max_length=30, default='')
	text = models.TextField(default='')
	closed = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)
	address = models.ForeignKey(Address, on_delete=models.CASCADE)
	was_reported = models.BooleanField(default=False)
	number_reports = models.PositiveIntegerField(default=0)
	adrAsPoint=models.PointField(null=True)
	objects = models.GeoManager()
	reported_by = models.ManyToManyField(Userdata, related_name="report")
	was_liked = models.BooleanField(default=False)
	number_likes = models.PositiveIntegerField(default=0)
	liked_by = models.ManyToManyField(Userdata, related_name="like")
	priority = models.FloatField(default=5000)
	update_at = models.ForeignKey(Update, on_delete=models.CASCADE, blank=True, null=True)


class Comment(models.Model):
	inf = models.ForeignKey(Information,on_delete=models.CASCADE)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
	text = models.TextField(default='')
	date = models.DateTimeField(auto_now_add=True)
	was_reported = models.BooleanField(default=False)
	number_reports = models.PositiveIntegerField(default=0)
	reported_by = models.ManyToManyField(Userdata)

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

class ContactUs(models.Model):
    email = models.EmailField(max_length=254)
    headline = models.CharField(max_length=30, default='')
    text = models.TextField(default='')
    works_on = models.ForeignKey(User,null=True,default=None)
    create_date = models.DateTimeField(auto_now_add=True)#timezone.now()#models.DateTimeField(default = timezone.now


class Room(models.Model):
	name = models.CharField(primary_key=True , max_length=20)
	user_req = models.ForeignKey(User, blank=True, null=True)
	need = models.ForeignKey(Need)
	slug = models.SlugField()
	act_req = models.BooleanField(default=False)
	act_off = models.BooleanField(default=False)
	last_message = models.DateTimeField(auto_now=True)
	req_saw = models.BooleanField(default=True)
	off_saw =  models.BooleanField(default=True)

	def __unicode__(self):
		return self.name

	def new_message(self, user):
		if self.user_req ==user:
			return not self.req_saw
		return not self.off_saw

	def set_saw(self, user):
		print(user.username + " saw the chat "+ self.name)
		print(user.username + "got chat with user_req:"+str(self.req_saw) +"; need_user:"+str(self.off_saw))
		if self.user_req ==user:
			self.req_saw = True
		else:
			self.off_saw = True
		self.save()

	def incomming_message(self, user):
		print("incoming message of "+ user.username)
		if self.user_req ==user:
			self.off_saw = False
		else:
			self.req_saw = False
		self.save()



class ChatMessage(models.Model):
	author = models.ForeignKey(User, null=True)
	date = models.DateTimeField(auto_now = True)
	room = models.ForeignKey(Room)
	text=models.TextField(default='', max_length=500)
