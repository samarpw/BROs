from django.test import LiveServerTestCase
from selenium import webdriver
from config import chrome_driver_path


class UserTestCase(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome(chrome_driver_path)
        self.browser.implicitly_wait(2)

    def tearDown(self):
        self.browser.quit()

    def test_user_can_search_for_friends(self):
        """
        Test that user can search for friends
        """
        # User open home page
        home_page = self.browser.get(self.live_server_url + '/')
        # and sees name of the site in the heading
        self.assertEqual(self.browser.find_element_by_css_selector('.navbar-brand').text, 'BROs')
        # and login and register menus
        self.assertIsNotNone(self.browser.find_element_by_link_text('Log In'))
        self.assertIsNotNone(self.browser.find_element_by_link_text('Sign Up'))
        #
        self.fail('Incomplete test')
