from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

class LoginTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(LoginTest, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LoginTest, cls).tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.assertIn('Familiengeschichte', self.selenium.title)
        # username_input = self.selenium.find_element_by_id("id_identification")
        # username_input.send_keys('myuser')
        # password_input = self.selenium.find_element_by_id("id_password")
        # password_input.send_keys('secret')
        # self.selenium.find_element_by_id('id_submit_button').click()
