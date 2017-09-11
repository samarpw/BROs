from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(blank=True, max_length=128)
    last_name = models.CharField(blank=True, max_length=128)
    avatar = models.ImageField(upload_to='avatars', blank=True)
    birthday = models.DateField(blank=True, default='1990-12-01')
    town = models.CharField(blank=True, max_length=128)
    relationship = models.CharField(blank=True, max_length=128,
                                    choices=[('1', 'married'), ('2', 'in relationship'), ('3', 'single')])
    visible_name = models.CharField(blank=True, max_length=128)
    url = models.CharField(blank=True, max_length=256)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.visible_name = self.get_visible_name()
        self.url = reverse('profile', args=[self.user.username])
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def get_visible_name(self):
        return ' '.join([str(self.first_name), str(self.last_name)]).strip()

    def __str__(self):
        return self.get_visible_name()

    @staticmethod
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return 'user_{0}/{1}'.format(instance.user.id, filename)


class UserWall(models.Model):
    profile = models.OneToOneField(UserProfile)
    url = models.CharField(blank=True, max_length=256)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.url = self.profile.url
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def add_post(self, text, author):
        return self.post_set.create(text=text, author=author)


class Likable(models.Model):
    likes = models.ManyToManyField(UserProfile, blank=True, related_name='likes_%(class)s')

    class Meta:
        abstract = True

    def like(self, user_profile):
        self.likes.add(user_profile)
        return self.likes.count()

    def unlike(self, user_profile):
        self.likes.remove(user_profile)
        return self.likes.count()


class Note(models.Model):
    text = models.CharField(blank=True, max_length=8128)
    author = models.ForeignKey(UserProfile, related_name='author_%(class)s')
    date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to=UserProfile.user_directory_path, blank=True)
    url = models.CharField(blank=True, max_length=256)

    class Meta:
        abstract = True


class Post(Note, Likable):
    user_wall = models.ForeignKey(UserWall, null=True)
    shares = models.ManyToManyField(UserProfile, blank=True, related_name='post_share_user')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.url = self.user_wall.profile.url + '#post_{}'.format(self.id)
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def add_comment(self, text, author):
        return self.comment_set.create(text=text, author=author)

    def share(self, user_profile):
        user_profile.userwall.post_set.add(self)
        self.shares.add(user_profile)
        return self.shares.count()


class Comment(Note, Likable):
    post = models.ForeignKey(Post, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.url = self.post.user_wall.profile.url + '#comment_{}'.format(self.id)
        return super().save(force_insert=force_insert, force_update=force_update, using=using,
                            update_fields=update_fields)
