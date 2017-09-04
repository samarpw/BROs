from django.test import TestCase
from django.utils import timezone
from profiles.models import User, UserProfile, UserWall, Post, Comment


class BaseModelTestCase(TestCase):

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
        self.wall = UserWall.objects.create(profile=self.user_profile)
        self.visible_name = ' '.join([self.user_first_name, self.user_last_name])


class UserProfileModelTestCase(BaseModelTestCase):

    def test_user_profile_basic(self):
        """Test the basic functionality of Profile"""
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.avatar, self.user_avatar)
        self.assertEqual(self.user_profile.first_name, self.user_first_name)
        self.assertEqual(self.user_profile.last_name, self.user_last_name)
        self.assertEqual(self.user_profile.birthday, self.user_bod)
        self.assertEqual(self.user_profile.town, self.user_town)
        self.assertEqual(self.user_profile.relationship, self.user_relationship)

    def test_user_visible_name(self):
        """Test visible name returned from Userprofile"""
        self.assertEqual(self.user_profile.get_visible_name(), self.visible_name)


class UserWallModelTestCase(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.post_text = 'test post'

    def test_add_and_remove_post_from_wall(self):
        """Test that user can add and remove post to wall"""
        self.wall.add_post(author=self.user_profile, text=self.post_text)
        post_count = self.wall.post_set.count()
        post = self.wall.post_set.get(id=1)
        self.assertEqual(post.text, self.post_text)
        self.assertEqual(post.author, self.user_profile)
        self.assertGreaterEqual(timezone.now(), post.date)
        post.delete()
        self.assertEqual(post_count - 1, self.wall.post_set.count())


class PostModelTestCase(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.post_text = 'test post'
        self.post = Post.objects.create(author=self.user_profile, text=self.post_text)
        self.comment_text = 'test comment'
        self.comment_author = self.user_profile

    def test_add_and_remove_comment_from_post(self):
        """Test user can add and remove comment to post"""
        self.post.add_comment(text=self.comment_text, author=self.comment_author)
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
        self.post.like(self.user_profile)
        self.assertTrue(init_val + 1 == self.post.likes.count())
        self.post.unlike(self.user_profile)
        self.assertEqual(init_val, self.post.likes.count())

    def test_share_post(self):
        """Test user can share post and counter is increasing"""
        init_shares = self.post.shares.count()
        self.post.share(self.user_profile)
        shared_post = self.user_profile.userwall.post_set.get(id=1)
        self.assertEqual(self.post, shared_post)
        self.assertEqual(init_shares + 1, self.post.shares.count())


class CommentModelTestCase(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.comment_text = 'test comment'
        self.comment_author = self.user_profile
        self.comment = Comment.objects.create(author=self.comment_author, text=self.comment_text)
        self.reply_text = 'test reply'
        self.reply_author = self.user_profile

    def test_add_and_remove_reply_from_comment(self):
        """Test user can add and remove reply to comment"""
        self.comment.add_reply(author=self.reply_author, text=self.reply_text)
        reply_count = self.comment.replies_set.count()
        reply = self.comment.replies_set.get(id=2)
        self.assertEqual(reply.text, self.reply_text)
        self.assertEqual(reply.author, self.reply_author)
        self.assertGreaterEqual(timezone.now(), reply.date)
        reply.delete()
        self.assertEqual(reply_count - 1, self.comment.replies_set.count())

    def test_like_and_unlike_comment(self):
        """Test user can like comment and counter is increasing"""
        init_val = self.comment.likes.count()
        self.comment.like(self.user_profile)
        self.assertTrue(init_val + 1 == self.comment.likes.count())
        self.comment.unlike(self.user_profile)
        self.assertEqual(init_val, self.comment.likes.count())
