from django.test import TestCase
from django.core.urlresolvers import resolve
from profiles.views import IndexView, ProfileView, MyRegistrationView, RegisterProfileView


class ProfilesURLsTestCase(TestCase):

    def test_root_url_uses_index_view(self):
        """Test that the root of the site resolves to the correct view"""
        root = resolve('/')
        self.assertEqual(root.func.view_class, IndexView)

    def test_user_registration_url(self):
        """Test that the user registration url resolves to the correct view"""
        user_registration_view = resolve('/accounts/register/')
        self.assertEqual(user_registration_view.func.view_class, MyRegistrationView)

    def test_profile_registration_url(self):
        """Test that the profile registration url resolves to the correct view"""
        profile_registration_view = resolve('/register_profile/')
        self.assertEqual(profile_registration_view.func.view_class, RegisterProfileView)

    def test_profile_url(self):
        """Test that the profile url resolves to the correct view"""
        profile_view = resolve('/profile/jan_nowak/')
        self.assertEqual(profile_view.func.view_class, ProfileView)
