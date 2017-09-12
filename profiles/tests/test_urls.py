from django.test import TestCase
from django.core.urlresolvers import resolve
from profiles import views


class ProfilesURLsTestCase(TestCase):

    def test_root_url_uses_index_view(self):
        """Test that the root of the site resolves to the correct view"""
        root = resolve('/')
        self.assertEqual(root.func.view_class, views.IndexView)

    def test_user_registration_url(self):
        """Test that the user registration url resolves to the correct view"""
        user_registration_view = resolve('/accounts/register/')
        self.assertEqual(user_registration_view.func.view_class, views.MyRegistrationView)

    def test_profile_registration_url(self):
        """Test that the profile registration url resolves to the correct view"""
        profile_registration_view = resolve('/register_profile/')
        self.assertEqual(profile_registration_view.func.view_class, views.RegisterProfileView)

    def test_profile_url(self):
        """Test that the profile url resolves to the correct view"""
        profile_view = resolve('/profile/jan_nowak/')
        self.assertEqual(profile_view.func.view_class, views.ProfileView)

    def test_suggestion_url(self):
        suggestion_view = resolve('/search/')
        self.assertEqual(suggestion_view.func.view_class, views.SearchView)

    def test_add_note_url(self):
        suggestion_view = resolve('/add_note/')
        self.assertEqual(suggestion_view.func.view_class, views.AddNoteView)

    def test_remove_note_url(self):
        suggestion_view = resolve('/remove_note/')
        self.assertEqual(suggestion_view.func.view_class, views.RemoveNoteView)

    def test_edit_note_url(self):
        suggestion_view = resolve('/edit_note/')
        self.assertEqual(suggestion_view.func.view_class, views.EditNoteView)

    def test_like_url(self):
        suggestion_view = resolve('/like/')
        self.assertEqual(suggestion_view.func.view_class, views.LikeView)
