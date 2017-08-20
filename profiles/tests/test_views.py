from django.test import TestCase, RequestFactory
from profiles.views import IndexView, MyRegistrationView, RegisterProfileView, ProfileView
from profiles.models import User


class IndexViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_index_view_basic(self):
        """Test that index view return a 200 response and uses the correct template"""
        request = self.factory.get('/')
        with self.assertTemplateUsed('index.html'):
            response = IndexView.as_view()(request)
            self.assertEqual(response.status_code, 200)


class ProfileViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jan_nowak', email='jan_nowak@gmail.com', password='top_secret')

    def test_profile_view_basic(self):
        """Test that profile view return a 200 response and uses the correct template"""
        self.client.login(username='jan_nowak', password='top_secret')
        with self.assertTemplateUsed('profiles/profile.html'):
            response = self.client.get('/profile/jan_nowak/')
            self.assertEqual(response.status_code, 200)


class UserRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_user_registration_view_basic(self):
        """Test that user registration view return a 200 response and uses the correct template"""
        request = self.factory.get('/accounts/register/')
        with self.assertTemplateUsed('registration/registration_form.html'):
            response = MyRegistrationView.as_view()(request)
            self.assertEqual(response.status_code, 200)


class ProfileRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jan_nowak', email='jan_nowak@gmail.com', password='top_secret')

    def test_profile_registration_view_basic(self):
        """Test that profile registration view return a 200 response and uses the correct template"""
        request = self.factory.get('/register_profile/')
        request.user = self.user
        with self.assertTemplateUsed('profiles/profile_registration.html'):
            response = RegisterProfileView.as_view()(request)
            self.assertEqual(response.status_code, 200)
