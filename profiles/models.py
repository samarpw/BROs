from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(blank=True, max_length=128)
    last_name = models.CharField(blank=True, max_length=128)
    avatar = models.ImageField(upload_to='avatars', blank=True)
    birthday = models.DateField(blank=True, default='1990-12-01')
    town = models.CharField(blank=True, max_length=128)
    relationship = models.CharField(blank=True, max_length=128,
                                    choices=[('1', 'married'), ('2', 'in relationship'), ('3', 'single')])

    def __str__(self):
        return self.user.username
