from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='avatars', blank=True)
    birthday = models.DateField(blank=True)
    town = models.CharField(blank=True, max_length=128)
    relationship = models.CharField(blank=True, max_length=128)

    def __str__(self):
        return self.user.username
