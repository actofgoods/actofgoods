from django.db import models
from datetime import datetime

# Create your models here.
class User(models.Model):
    email = models.Charfield(max_length=60)
    password = models.Charfield(max_length=60)
    last_login_date = models.DateTimeField(default=datetime.now, blank=True)
    register_date = models.DateTimeField(default=datetime.now, blank=True)
