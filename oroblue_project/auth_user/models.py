from django.db import models
from django.contrib.auth.models import User

class auth_user(models.Model):
    user = models.ForeignKey(User,  on_delete=models.SET_NULL , null=True , blank=True)