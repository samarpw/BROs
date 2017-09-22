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
    relation_user = models.ManyToManyField('self', blank=True, related_name='relationship')
    visible_name = models.CharField(blank=True, max_length=128)
    url = models.CharField(blank=True, max_length=256)
    friends = models.ManyToManyField('self', blank=True, related_name='friends')
    friend_requests = models.ManyToManyField('self', blank=True, related_name='friend_requests')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.visible_name = self.get_visible_name()
        self.url = reverse('profile', args=[self.user.username])
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def get_visible_name(self):
        return ' '.join([str(self.first_name), str(self.last_name)]).strip()

    def send_friend_request(self, user_profile):
        self.friend_requests.add(user_profile)
        noti = Notification.objects.create(owner=self, type=Notification.FRIEND_REQUEST, sender=user_profile.user.username)
        self.notification_set.add(noti)
        return self.friend_requests.count()

    def cancel_friend_request(self, user_profile):
        self.friend_requests.remove(user_profile)
        self.notification_set.get(type=Notification.FRIEND_REQUEST, sender=user_profile.user.username).delete()
        noti = Notification.objects.create(owner=user_profile, type=Notification.DECLINED_FRIEND_REQUEST, sender=self.user.username)
        user_profile.notification_set.add(noti)
        return self.friend_requests.count()

    def add_friend(self, user_profile):
        self.friend_requests.remove(user_profile)
        self.notification_set.get(type=Notification.FRIEND_REQUEST, sender=user_profile.user.username).delete()
        self.friends.add(user_profile)
        user_profile.friends.add(self)
        noti = Notification.objects.create(owner=user_profile, type=Notification.ACCEPTED_FRIEND_REQUEST, sender=self.user.username)
        user_profile.notification_set.add(noti)
        return self.friends.count()

    def remove_friend(self, user_profile):
        self.friends.remove(user_profile)
        user_profile.friends.remove(self)
        noti = Notification.objects.create(owner=user_profile, type=Notification.REMOVED_FRIEND, sender=self.user.username)
        user_profile.notification_set.add(noti)
        return self.friends.count()

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

    def add_note(self, text, author):
        return self.post_set.create(text=text, author=author)


class Notification(models.Model):
    type = models.CharField(blank=False, max_length=64)
    text = models.CharField(blank=True, max_length=128)
    url = models.CharField(blank=True, max_length=256)
    owner = models.ForeignKey(UserProfile, blank=False)
    sender = models.CharField(blank=True, max_length=128)
    date = models.DateTimeField(auto_now_add=True)

    FRIEND_REQUEST = 'friend_request'
    _FRIEND_REQUEST_TEXT = '{} send you friend request!'
    ACCEPTED_FRIEND_REQUEST = 'accept_friend_request'
    _ACCEPTED_FRIEND_REQUEST_TEXT = '{} accepted your request. You are now friends!'
    DECLINED_FRIEND_REQUEST = 'decline_friend_request'
    _DECLINED_FRIEND_REQUEST_TEXT = '{} declined your friend request.'
    REMOVED_FRIEND = 'removed_friend'
    _REMOVED_FRIEND_TEXT = '{} removed you from friends.'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.type == Notification.FRIEND_REQUEST:
            assert self.sender, 'Provide username for friend request'
            sender_user = User.objects.get(username=self.sender)
            sender_profile = UserProfile.objects.get(user=sender_user)
            self.text = self._FRIEND_REQUEST_TEXT.format(sender_profile.visible_name)
            self.url = reverse('friends', kwargs={'username': self.owner.user.username})
        elif self.type == Notification.ACCEPTED_FRIEND_REQUEST:
            assert self.sender, 'Provide username for accepted request'
            sender_user = User.objects.get(username=self.sender)
            sender_profile = UserProfile.objects.get(user=sender_user)
            self.text = self._ACCEPTED_FRIEND_REQUEST_TEXT.format(sender_profile.visible_name)
            self.url = reverse('friends', kwargs={'username': self.owner.user.username})
        elif self.type == Notification.DECLINED_FRIEND_REQUEST:
            assert self.sender, 'Provide username for declined request'
            sender_user = User.objects.get(username=self.sender)
            sender_profile = UserProfile.objects.get(user=sender_user)
            self.text = self._DECLINED_FRIEND_REQUEST_TEXT.format(sender_profile.visible_name)
            self.url = reverse('friends', kwargs={'username': self.owner.user.username})
        elif self.type == Notification.REMOVED_FRIEND:
            assert self.sender, 'Provide username of friend who removed you'
            sender_user = User.objects.get(username=self.sender)
            sender_profile = UserProfile.objects.get(user=sender_user)
            self.text = self._REMOVED_FRIEND_TEXT.format(sender_profile.visible_name)
            self.url = reverse('friends', kwargs={'username': self.owner.user.username})

        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


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
    parent = models.ForeignKey(UserWall, null=True)
    shares = models.ManyToManyField(UserProfile, blank=True, related_name='post_share_user')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.url = self.parent.profile.url + '#post_{}'.format(self.id)
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def add_note(self, text, author):
        return self.comment_set.create(text=text, author=author)

    def share(self, user_profile):
        user_profile.userwall.post_set.add(self)
        self.shares.add(user_profile)
        return self.shares.count()

    def get_wall(self):
        return self.parent


class Comment(Note, Likable):
    parent = models.ForeignKey(Post, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.url = self.get_wall().profile.url + '#comment_{}'.format(self.id)
        return super().save(force_insert=force_insert, force_update=force_update, using=using,
                            update_fields=update_fields)

    def get_wall(self):
        return self.parent.get_wall()
