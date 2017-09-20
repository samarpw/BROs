from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from BROs.settings import get_env_variable
from os import path, remove, listdir
from time import sleep


class UserTestCase(StaticLiveServerTestCase):

    def setUp(self):
        chrome_driver_path = get_env_variable('CHROMEDRIVER_PATH')
        self.browser = webdriver.Chrome(chrome_driver_path)
        self.browser.implicitly_wait(2)
        self.user1 = dict(
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
        self.user2 = dict(
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

        self.post_text = 'Test post. Hello all.'
        self.comment_text = 'I Like It'

    def tearDown(self):
        self.browser.quit()
        dir = './media/avatars/'
        for item in listdir('./media/avatars/'):
            if item.startswith('example_avatar'):
                remove(path.join(dir, item))

    def test_1_user_can_add_post_and_comment(self):
        """
        Test that user can search for friends
        """
        # User open home page
        self.browser.get(self.live_server_url + '/')
        # and sees name of the site in the heading
        self.assertEqual(self.browser.find_element_by_css_selector('.navbar-brand').text, 'BROs')
        # and login and register menus
        log_in_button = self.browser.find_element_by_link_text('Log In')
        self.assertIsNotNone(log_in_button)
        sign_up_button = self.browser.find_element_by_link_text('Sign Up')
        self.assertIsNotNone(sign_up_button)
        # can create user
        self.create_user(self.user1)
        # Profile and Logout menus are visible
        profile_button = self.browser.find_element_by_link_text('Profile')
        self.assertIsNotNone(profile_button)
        logout_button = self.browser.find_element_by_link_text('Logout')
        self.assertIsNotNone(logout_button)
        # Profile have correct informations
        self.validate_user(self.user1)

        # user can add post to his wall
        post_field = self.browser.find_element_by_id('post_form_text')
        add_post_button = self.browser.find_element_by_id('add_post')
        post_field.send_keys(self.post_text)
        add_post_button.click()

        # post is visible on his wall
        posts = self.browser.find_elements_by_css_selector('.post')
        self.assertEqual(self.post_text, posts[0].find_element_by_css_selector('.post .note_text').text)
        self.assertEqual(' '.join([self.user1['first_name'], self.user1['last_name']]),
                         posts[0].find_element_by_css_selector('.author').text)

        # user can add comment to post
        comment_field = posts[0].find_element_by_id('comment_form_text')
        add_comment_button = posts[0].find_element_by_id('add_comment')
        comment_field.send_keys(self.comment_text)
        add_comment_button.click()

        # comment is visible under post
        comments = self.browser.find_elements_by_css_selector('.comment')
        self.assertEqual(self.comment_text, comments[0].find_element_by_css_selector('.comment .note_text').text)
        self.assertEqual(' '.join([self.user1['first_name'], self.user1['last_name']]),
                         comments[0].find_element_by_css_selector('.author').text)

        # user can like post
        like_post_count = int(self.browser.find_element_by_css_selector('.post .likes_count').text)
        like_post_button = self.browser.find_element_by_css_selector('.post .like')
        like_post_button.click()
        sleep(0.5)
        self.assertEqual(like_post_count + 1,
                        int(self.browser.find_element_by_css_selector('.post .likes_count').text))

        # and unlike post
        like_post_button.click()
        sleep(0.5)
        self.assertEqual(like_post_count,
                         int(self.browser.find_element_by_css_selector('.post .likes_count').text))

        # user can like comment
        like_comment_count = int(self.browser.find_element_by_css_selector('.comment .likes_count').text)
        like_comment_button = self.browser.find_element_by_css_selector('.comment .like')
        like_comment_button.click()
        sleep(0.5)
        self.assertEqual(like_comment_count + 1,
                         int(self.browser.find_element_by_css_selector('.comment .likes_count').text))

        # and unlike comment
        like_comment_button.click()
        sleep(0.5)
        self.assertEqual(like_comment_count,
                         int(self.browser.find_element_by_css_selector('.comment .likes_count').text))

        # user can edit post
        # import pdb;pdb.set_trace()
        self.browser.find_element_by_css_selector('.post .edit_note').click()
        self.browser.find_element_by_css_selector('#edit_post_form .note_text').send_keys(' edited')
        self.browser.find_element_by_id('update_post').click()
        self.assertEqual(self.browser.find_element_by_css_selector('.post .note_text').text,
                         self.post_text + ' edited')

        # user can edit comment
        self.browser.find_element_by_css_selector('.comment .edit_note').click()
        self.browser.find_element_by_css_selector('#edit_comment_form .note_text').send_keys(' edited')
        self.browser.find_element_by_id('update_comment').click()
        self.assertEqual(self.browser.find_element_by_css_selector('.comment .note_text').text,
                         self.comment_text + ' edited')

        # user can remove comment
        remove_comment_button = self.browser.find_element_by_css_selector('.remove_comment_form button')
        remove_comment_button.click()
        self.assertFalse(self.browser.find_elements_by_css_selector('.comment'))

        # user can remove post (only his own)
        remove_post_button = self.browser.find_element_by_css_selector('.remove_post_form button')
        remove_post_button.click()
        self.assertFalse(self.browser.find_elements_by_css_selector('.post'))

    def test_2_user_can_add_friend(self):
        # User open home page
        self.browser.get(self.live_server_url + '/')

        # create users
        self.create_user(self.user1, logout=True)
        self.create_user(self.user2)

        # find user
        name = ' '.join([self.user1['first_name'], self.user1['last_name']])
        search_input = self.browser.find_element_by_css_selector('.search-form .search-input')
        search_input.send_keys(self.user1['first_name'])
        suggestion = self.browser.find_element_by_css_selector('#suggestions .search-result')
        self.assertEqual(suggestion.get_attribute('value'), name)
        search_input.send_keys(' {}'.format(self.user1['last_name']))
        self.assertEqual(self.browser.current_url, self.live_server_url + '/profile/{}/'.format(self.user1['username']))

        # import pdb;pdb.set_trace()
        self.fail('Incomplete test')

    def create_user(self, user: dict, logout: bool=False):
        sign_up_button = self.browser.find_element_by_link_text('Sign Up')
        sign_up_button.click()
        self.browser.find_element_by_id('id_username').send_keys(user['username'])
        self.browser.find_element_by_id('id_email').send_keys(user['email'])
        self.browser.find_element_by_id('id_password1').send_keys(user['password'])
        self.browser.find_element_by_id('id_password2').send_keys(user['password'])
        self.browser.find_element_by_css_selector('form button#submit_registration').click()
        # 2nd step of registration
        self.browser.find_element_by_id('id_avatar').send_keys(user['avatar'])
        self.browser.find_element_by_id('id_first_name').send_keys(user['first_name'])
        self.browser.find_element_by_id('id_last_name').send_keys(user['last_name'])
        bod_field = self.browser.find_element_by_id('id_birthday')
        bod_field.clear()
        bod_field.send_keys(user['birthday'])
        self.browser.find_element_by_id('id_town').send_keys(user['town'])
        Select(self.browser.find_element_by_id('id_relationship')).select_by_visible_text(user['relationship'])
        self.browser.find_element_by_css_selector('form button#submit_registration').click()
        # user is created and logged in. He is redirected to index page
        self.assertEqual(self.browser.current_url, self.live_server_url + '/')
        if logout:
            self.browser.find_element_by_link_text('Logout').click()

    def validate_user(self, user: dict):
        profile_button = self.browser.find_element_by_link_text('Profile')
        profile_button.click()
        avatar_path = self.browser.find_element_by_css_selector("img[alt='{}']".format(user['username'])) \
            .get_attribute('src')
        self.assertTrue(path.splitext(path.basename(user['avatar']))[0] in avatar_path)
        self.assertEqual(self.browser.find_element_by_id('id_first_name').get_attribute('value'),
                         user['first_name'])
        self.assertEqual(self.browser.find_element_by_id('id_last_name').get_attribute('value'),
                         user['last_name'])
        self.assertEqual(self.browser.find_element_by_id('id_birthday').get_attribute('value'),
                         user['birthday'])
        self.assertEqual(self.browser.find_element_by_id('id_town').get_attribute('value'),
                         user['town'])
        self.assertEqual(Select(self.browser.find_element_by_id('id_relationship')).first_selected_option.text,
                         user['relationship'])
        self.browser.find_element_by_link_text('BROs').click()
