from django.db import models
from datetime import datetime
# Create your models here.
class Users(models.Model):
    email = models.CharField(max_length=60)
    password = models.CharField(max_length=60)
    last_login_date = models.DateTimeField(default=datetime.now, blank=True)
    register_date = models.DateTimeField(default=datetime.now, blank=True)
