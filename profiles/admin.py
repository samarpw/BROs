from django.contrib import admin
from profiles.models import UserProfile, Post, UserWall, Comment

admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(UserWall)
admin.site.register(Comment)
