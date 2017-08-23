from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from config import chrome_driver_path
from os import path, remove


class UserTestCase(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome(chrome_driver_path)
        self.browser.implicitly_wait(2)

        self.user_username = 'jan_nowak'
        self.user_email = 'nowak@gmail.com'
        self.user_pwd = 'top_secret'
        self.user_avatar = path.abspath('./media/example_avatar.jpg')
        self.user_first_name = 'Jan'
        self.user_last_name = 'Nowak'
        self.user_bod = '1999-01-01'
        self.user_town = 'Radom'
        self.user_relationship = 'single'

        self.post_text = 'Test post. Hello all.'

    def tearDown(self):
        self.browser.quit()
        remove('./media/avatars/example_avatar.jpg')

    def test_user_can_search_for_friends(self):
        """
        Test that user can search for friends
        """
        # User open home page
        home_page = self.browser.get(self.live_server_url + '/')
        # and sees name of the site in the heading
        self.assertEqual(self.browser.find_element_by_css_selector('.navbar-brand').text, 'BROs')
        # and login and register menus
        log_in_button = self.browser.find_element_by_link_text('Log In')
        self.assertIsNotNone(log_in_button)
        sign_up_button = self.browser.find_element_by_link_text('Sign Up')
        self.assertIsNotNone(sign_up_button)
        # can create user
        sign_up_button.click()
        self.browser.find_element_by_id('id_username').send_keys(self.user_username)
        self.browser.find_element_by_id('id_email').send_keys(self.user_email)
        self.browser.find_element_by_id('id_password1').send_keys(self.user_pwd)
        self.browser.find_element_by_id('id_password2').send_keys(self.user_pwd)
        self.browser.find_element_by_css_selector('form button').click()
        # 2nd step of registration
        self.browser.find_element_by_id('id_avatar').send_keys(self.user_avatar)
        self.browser.find_element_by_id('id_first_name').send_keys(self.user_first_name)
        self.browser.find_element_by_id('id_last_name').send_keys(self.user_last_name)
        bod_field = self.browser.find_element_by_id('id_birthday')
        bod_field.clear()
        bod_field.send_keys(self.user_bod)
        self.browser.find_element_by_id('id_town').send_keys(self.user_town)
        Select(self.browser.find_element_by_id('id_relationship')).select_by_visible_text(self.user_relationship)
        self.browser.find_element_by_css_selector('form button').click()
        # user is created and logged in. He is redirected to index page
        self.assertEqual(self.browser.current_url, self.live_server_url + '/')
        # Profile and Logout menus are visible
        profile_button = self.browser.find_element_by_link_text('Profile')
        self.assertIsNotNone(profile_button)
        logout_button = self.browser.find_element_by_link_text('Logout')
        self.assertIsNotNone(logout_button)
        # Profile have correct informations
        profile_button.click()
        avatar_path = self.browser.find_element_by_css_selector("img[alt='{}']".format(self.user_username))\
            .get_attribute('src')
        self.assertTrue(path.splitext(path.basename(self.user_avatar))[0] in avatar_path)
        self.assertEqual(self.browser.find_element_by_id('id_first_name').get_attribute('value'),
                         self.user_first_name)
        self.assertEqual(self.browser.find_element_by_id('id_last_name').get_attribute('value'),
                         self.user_last_name)
        self.assertEqual(self.browser.find_element_by_id('id_birthday').get_attribute('value'),
                         self.user_bod)
        self.assertEqual(self.browser.find_element_by_id('id_town').get_attribute('value'),
                         self.user_town)
        self.assertEqual(Select(self.browser.find_element_by_id('id_relationship')).first_selected_option.text,
                         self.user_relationship)

        self.browser.find_element_by_link_text('Home').click()

        # user can add post to his wall
        post_field = self.browser.find_element_by_id('post_text')
        add_post_button = self.browser.find_element_by_id('add_post')
        post_field.send_keys(self.post_text)
        add_post_button.click()

        # post is visible on his wall
        posts = self.browser.find_elements_by_css_selector('.post')
        self.assertEqual(posts[0].text, self.post_text)

        # import pdb;pdb.set_trace()
        self.fail('Incomplete test')
