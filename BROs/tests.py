from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from BROs.settings import get_env_variable
from os import path, remove


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
        try:
            remove('./media/avatars/example_avatar.jpg')
        except:
            pass

    def test_user_can_add_post_and_comment(self):
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
        post_field = self.browser.find_element_by_id('post_text')
        add_post_button = self.browser.find_element_by_id('add_post')
        post_field.send_keys(self.post_text)
        add_post_button.click()

        # post is visible on his wall
        posts = self.browser.find_elements_by_css_selector('.post')
        self.assertTrue(self.post_text in posts[0].text)
        self.assertTrue(' '.join([self.user1['first_name'], self.user1['last_name']]) in posts[0].text)

        # user can add comment to post
        comment_field = posts[0].find_element_by_id('comment_text')
        add_comment_button = posts[0].find_element_by_id('add_comment')
        comment_field.send_keys(self.comment_text)
        add_comment_button.click()

        # comment is visible under post
        comments = self.browser.find_elements_by_css_selector('.comment')
        self.assertTrue(self.comment_text in comments[0].text)
        self.assertTrue(' '.join([self.user1['first_name'], self.user1['last_name']]) in comments[0].text)

        # user can remove post (only on his wall)


        # user can like post

        # user can like comment

        import pdb;pdb.set_trace()
        self.fail('Incomplete test')

    def create_user(self, user: dict):
        sign_up_button = self.browser.find_element_by_link_text('Sign Up')
        sign_up_button.click()
        self.browser.find_element_by_id('id_username').send_keys(user['username'])
        self.browser.find_element_by_id('id_email').send_keys(user['email'])
        self.browser.find_element_by_id('id_password1').send_keys(user['password'])
        self.browser.find_element_by_id('id_password2').send_keys(user['password'])
        self.browser.find_element_by_css_selector('form button').click()
        # 2nd step of registration
        self.browser.find_element_by_id('id_avatar').send_keys(user['avatar'])
        self.browser.find_element_by_id('id_first_name').send_keys(user['first_name'])
        self.browser.find_element_by_id('id_last_name').send_keys(user['last_name'])
        bod_field = self.browser.find_element_by_id('id_birthday')
        bod_field.clear()
        bod_field.send_keys(user['birthday'])
        self.browser.find_element_by_id('id_town').send_keys(user['town'])
        Select(self.browser.find_element_by_id('id_relationship')).select_by_visible_text(user['relationship'])
        self.browser.find_element_by_css_selector('form button').click()
        # user is created and logged in. He is redirected to index page
        self.assertEqual(self.browser.current_url, self.live_server_url + '/')

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
        self.browser.find_element_by_link_text('Home').click()
