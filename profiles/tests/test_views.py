from django.test import TestCase, RequestFactory
from profiles.views import *
from profiles.models import *
from profiles.forms import *


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
        self.userprofile = UserProfile.objects.create(user=self.user, first_name='Jan', last_name='Nowak', town='Radom')

    def test_profile_view_basic(self):
        """Test that profile view return a 200 response and uses the correct template"""
        self.client.login(username='jan_nowak', password='top_secret')
        with self.assertTemplateUsed('profiles/profile.html'):
            response = self.client.get('/profile/jan_nowak/')
            self.assertEqual(response.status_code, 200)

    def test_user_can_edit_profile(self):
        """Test that logged user can edit his profile"""
        self.client.login(username='jan_nowak', password='top_secret')
        response = self.client.get('/profile/jan_nowak/')
        form = response.context['form']
        data = form.initial
        data['first_name'] = 'Janek'
        post_response = self.client.post('/profile/jan_nowak/', data)
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(UserProfile.objects.get(user=self.user).first_name, 'Janek')


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


class NoteViewsTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jan_nowak', email='jan_nowak@gmail.com', password='top_secret')
        self.userprofile = UserProfile.objects.create(user=self.user, first_name='Jan', last_name='Nowak', town='Radom')
        self.wall = UserWall.objects.create(profile=self.userprofile)

    def test_adding_post(self):
        """Test that Post can be added to wall"""
        self.client.login(username='jan_nowak', password='top_secret')
        data = dict()
        data['_class'] = 'Post'
        data['note_text'] = 'post text'
        data['parent_id'] = str(self.wall.id)
        data['author_id'] = str(self.userprofile.id)
        response = self.client.post('/add_note/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserWall.objects.get(profile=self.userprofile).post_set.get(id=1).text, 'post text')

    def test_adding_comment(self):
        """Test that Comment can be added to wall"""
        self.client.login(username='jan_nowak', password='top_secret')
        self.post = self.wall.add_note(text='post text', author=self.userprofile)
        data = dict()
        data['_class'] = 'Comment'
        data['note_text'] = 'comment text'
        data['parent_id'] = str(self.post.id)
        data['author_id'] = str(self.userprofile.id)
        response = self.client.post('/add_note/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.get(id=1).comment_set.get(id=1).text, 'comment text')

    def test_editing_post(self):
        """Test that Post can be edited"""
        self.client.login(username='jan_nowak', password='top_secret')
        self.post = self.wall.add_note(text='post text', author=self.userprofile)
        data = dict()
        data['_class'] = 'Post'
        data['note_text'] = 'post text v2'
        data['note_id'] = str(self.post.id)
        response = self.client.post('/edit_note/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.get(id=1).text, 'post text v2')

    def test_removing_comment(self):
        """Test that Comment can be removed"""
        self.client.login(username='jan_nowak', password='top_secret')
        self.post = self.wall.add_note(text='post text', author=self.userprofile)
        self.comment = self.post.add_note(text='comment text', author=self.userprofile)
        data = dict()
        data['_class'] = 'Comment'
        data['note_id'] = str(self.post.id)
        data['userprofile_id'] = str(self.userprofile.id)
        response = self.client.post('/remove_note/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.all().count(), 0)

    def test_like_post(self):
        """Test that Post can be liked"""
        self.client.login(username='jan_nowak', password='top_secret')
        self.post = self.wall.add_note(text='post text', author=self.userprofile)
        data = dict()
        data['_class'] = 'Post'
        data['object_id'] = str(self.post.id)
        data['profile_id'] = str(self.userprofile.id)
        # like
        response = self.client.get('/like/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.get(id=self.post.id).likes.count(), 1)
        # unlike
        response = self.client.get('/like/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.get(id=self.post.id).likes.count(), 0)
