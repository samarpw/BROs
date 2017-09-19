from django.test import TestCase
from django.utils import timezone
from profiles.models import User, UserProfile, UserWall, Post, Comment
from os import path


class BaseModelTestCase(TestCase):

    def setUp(self):
        self.user_dict_1 = dict(
            username='jan_nowak',
            email='nowak@gmail.com',
            password='top_secret',
            avatar=path.abspath('./media/example_avatar.jpg'),
            first_name='Jan',
            last_name='Nowak',
            birthday='1999-01-01',
            town='Radom',
            relationship='single'
        )
        self.user_dict_2 = dict(
            username='piotr_kowalski',
            email='kowalski@gmail.com',
            password='top_secret2',
            avatar=path.abspath('./media/example_avatar.jpg'),
            first_name='Piotr',
            last_name='Kowalski',
            birthday='1997-01-01',
            town='Kraków',
            relationship='married'
        )

        self.user_1 = User.objects.create_user(username=self.user_dict_1['username'],
                                               email=self.user_dict_1['email'],
                                               password=self.user_dict_1['password'])
        self.user_profile_1 = UserProfile.objects.create(user=self.user_1,
                                                         avatar=self.user_dict_1['avatar'],
                                                         first_name=self.user_dict_1['first_name'],
                                                         last_name=self.user_dict_1['last_name'],
                                                         birthday=self.user_dict_1['birthday'],
                                                         town=self.user_dict_1['town'],
                                                         relationship=self.user_dict_1['relationship'])
        self.wall_1 = UserWall.objects.create(profile=self.user_profile_1)

        self.user_2 = User.objects.create_user(username=self.user_dict_2['username'],
                                                    email=self.user_dict_2['email'],
                                                    password=self.user_dict_2['password'])
        self.user_profile_2 = UserProfile.objects.create(user=self.user_2,
                                                         avatar=self.user_dict_2['avatar'],
                                                         first_name=self.user_dict_2['first_name'],
                                                         last_name=self.user_dict_2['last_name'],
                                                         birthday=self.user_dict_2['birthday'],
                                                         town=self.user_dict_2['town'],
                                                         relationship=self.user_dict_2['relationship'])
        self.wall_2 = UserWall.objects.create(profile=self.user_profile_2)

        self.visible_name = ' '.join([self.user_dict_1['first_name'], self.user_dict_1['last_name']])
        self.post_text = 'test post'
        self.comment_text = 'test comment'


class UserProfileModelTestCase(BaseModelTestCase):

    def test_user_profile_basic(self):
        """Test the basic functionality of Profile"""
        self.assertEqual(self.user_profile_1.user, self.user_1)
        self.assertEqual(self.user_profile_1.avatar, self.user_dict_1['avatar'])
        self.assertEqual(self.user_profile_1.first_name, self.user_dict_1['first_name'])
        self.assertEqual(self.user_profile_1.last_name, self.user_dict_1['last_name'])
        self.assertEqual(self.user_profile_1.birthday, self.user_dict_1['birthday'])
        self.assertEqual(self.user_profile_1.town, self.user_dict_1['town'])
        self.assertEqual(self.user_profile_1.relationship, self.user_dict_1['relationship'])
        self.assertEqual(self.user_profile_1.visible_name, self.visible_name)
        self.assertEqual(self.user_profile_1.url, '/profile/{}/'.format(self.user_1.username))

    def test_user_visible_name(self):
        """Test visible name returned from Userprofile"""
        self.assertEqual(self.user_profile_1.get_visible_name(), self.visible_name)

    def test_user_can_add_friend(self):
        """Test user is able to add a friend"""

        self.fail('Incomplete test')


class UserWallModelTestCase(BaseModelTestCase):

    def setUp(self):
        super().setUp()

    def test_add_and_remove_post_from_wall(self):
        """Test that user can add and remove post to wall"""
        self.wall_1.add_note(author=self.user_profile_1, text=self.post_text)
        post_count = self.wall_1.post_set.count()
        post = self.wall_1.post_set.get(id=1)
        self.assertEqual(post.text, self.post_text)
        self.assertEqual(post.author, self.user_profile_1)
        self.assertGreaterEqual(timezone.now(), post.date)
        post.delete()
        self.assertEqual(post_count - 1, self.wall_1.post_set.count())


class PostModelTestCase(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.post = self.wall_1.add_note(author=self.user_profile_1, text=self.post_text)
        self.comment_author = self.user_profile_1

    def test_add_and_remove_comment_from_post(self):
        """Test user can add and remove comment to post"""
        self.post.add_note(text=self.comment_text, author=self.comment_author)
        post_count = self.post.comment_set.count()
        comment = self.post.comment_set.get(id=1)
        self.assertEqual(comment.text, self.comment_text)
        self.assertEqual(comment.author, self.comment_author)
        self.assertGreaterEqual(timezone.now(), comment.date)
        comment.delete()
        self.assertEqual(post_count - 1, self.post.comment_set.count())

    def test_like_and_unlike_post(self):
        """Test user can unlike post and counter is changing"""
        init_val = self.post.likes.count()
        self.post.like(self.user_profile_1)
        self.assertTrue(init_val + 1 == self.post.likes.count())
        self.post.unlike(self.user_profile_1)
        self.assertEqual(init_val, self.post.likes.count())

    def test_share_post(self):
        """Test user can share post and counter is increasing"""
        init_shares = self.post.shares.count()
        self.post.share(self.user_profile_1)
        shared_post = self.user_profile_1.userwall.post_set.get(id=1)
        self.assertEqual(self.post, shared_post)
        self.assertEqual(init_shares + 1, self.post.shares.count())


class CommentModelTestCase(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.post = self.wall_1.add_note(author=self.user_profile_1, text=self.post_text)
        self.comment_author = self.user_profile_1
        self.comment = self.post.add_note(author=self.comment_author, text=self.comment_text)
        self.reply_text = 'test reply'
        self.reply_author = self.user_profile_1

    def test_like_and_unlike_comment(self):
        """Test user can like comment and counter is increasing"""
        init_val = self.comment.likes.count()
        self.comment.like(self.user_profile_1)
        self.assertTrue(init_val + 1 == self.comment.likes.count())
        self.comment.unlike(self.user_profile_1)
        self.assertEqual(init_val, self.comment.likes.count())
