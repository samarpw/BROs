from django.test import TestCase
from profiles.models import User, UserProfile


class UserProfileModelTestCase(TestCase):

    def setUp(self):
        self.user_username = 'jan_nowak'
        self.user_email = 'nowak@gmail.com'
        self.user_pwd = 'top_secret'
        self.user_avatar = './media/example_avatar.jpg'
        self.user_first_name = 'Jan'
        self.user_last_name = 'Nowak'
        self.user_bod = '1999-01-01'
        self.user_town = 'Radom'
        self.user_relationship = 'single'

        self.user = User.objects.create_user(username=self.user_username,
                                             email=self.user_email,
                                             password=self.user_pwd)
        self.user_profile = UserProfile.objects.create(user=self.user,
                                                       avatar=self.user_avatar,
                                                       first_name=self.user_first_name,
                                                       last_name=self.user_last_name,
                                                       birthday=self.user_bod,
                                                       town=self.user_town,
                                                       relationship=self.user_relationship)

    def test_user_profile_basic(self):
        """Test the basic functionality of Profile"""
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.avatar, self.user_avatar)
        self.assertEqual(self.user_profile.first_name, self.user_first_name)
        self.assertEqual(self.user_profile.last_name, self.user_last_name)
        self.assertEqual(self.user_profile.birthday, self.user_bod)
        self.assertEqual(self.user_profile.town, self.user_town)
        self.assertEqual(self.user_profile.relationship, self.user_relationship)
