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

    def get_visible_name(self):
        return ' '.join([str(self.first_name), str(self.last_name)])

    def __str__(self):
        return self.get_visible_name()

    @staticmethod
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return 'user_{0}/{1}'.format(instance.user.id, filename)


class UserWall(models.Model):
    profile = models.OneToOneField(UserProfile)

    def add_post(self, text, author):
        return self.post_set.create(text=text, author=author)


class Post(models.Model):
    text = models.CharField(blank=True, max_length=8128)
    user_wall = models.ForeignKey(UserWall, null=True)
    author = models.ForeignKey(UserProfile, related_name='post_author')
    date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to=UserProfile.user_directory_path, blank=True)
    likes = models.ManyToManyField(UserProfile, blank=True, related_name='post_like_user')
    shares = models.ManyToManyField(UserProfile, blank=True, related_name='post_share_user')

    def add_comment(self, text, author):
        return self.comment_set.create(text=text, author=author)

    def like(self, user_profile):
        self.likes.add(user_profile)
        return self.likes.count()

    def unlike(self, user_profile):
        self.likes.remove(user_profile)
        return self.likes.count()

    def share(self, user_profile):
        user_profile.userwall.post_set.add(self)
        self.shares.add(user_profile)
        return self.shares.count()


class Comment(models.Model):
    text = models.CharField(blank=True, max_length=8128)
    author = models.ForeignKey(UserProfile, related_name='comment_author')
    post = models.ForeignKey(Post, null=True)
    date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to=UserProfile.user_directory_path, blank=True)
    replies = models.ForeignKey('self', null=True, blank=True, related_name='replies_set')
    likes = models.ManyToManyField(UserProfile, blank=True, related_name='comment_like_user')

    def add_reply(self, text, author):
        return self.replies_set.create(text=text, author=author)

    def like(self, user_profile):
        self.likes.add(user_profile)
        return self.likes.count()

    def unlike(self, user_profile):
        self.likes.remove(user_profile)
        return self.likes.count()
