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

    def test_add_post_url(self):
        suggestion_view = resolve('/add_post/')
        self.assertEqual(suggestion_view.func.view_class, views.AddPostView)

    def test_remove_post_url(self):
        suggestion_view = resolve('/remove_post/')
        self.assertEqual(suggestion_view.func.view_class, views.RemovePostView)

    def test_edit_post_url(self):
        suggestion_view = resolve('/edit_post/')
        self.assertEqual(suggestion_view.func.view_class, views.EditPostView)

    def test_like_post_url(self):
        suggestion_view = resolve('/like_post/')
        self.assertEqual(suggestion_view.func.view_class, views.LikePostView)

    def test_add_comment_url(self):
        suggestion_view = resolve('/add_comment/')
        self.assertEqual(suggestion_view.func.view_class, views.AddCommentView)
        # TODO unify add/remove/edit/like...

    def test_remove_comment_url(self):
        suggestion_view = resolve('/remove_comment/')
        self.assertEqual(suggestion_view.func.view_class, views.RemoveCommentView)

    def test_edit_comment_url(self):
        suggestion_view = resolve('/edit_comment/')
        self.assertEqual(suggestion_view.func.view_class, views.EditCommentView)

    def test_like_comment_url(self):
        suggestion_view = resolve('/like_comment/')
        self.assertEqual(suggestion_view.func.view_class, views.LikeCommentView)
