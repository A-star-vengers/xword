""" Test Front End """

# https://github.com/asap/psychic-ironman/blob/master/flask/tests/test_frontend.py

import requests
import unittest
from selenium import webdriver
from selenium.webdriver.support import ui

# site_url = 'http://localhost:5000'
site_url = 'http://127.0.0.1:5000'

class PageTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.url = site_url

    def test_homepage(self):
        driver = self.driver
        driver.get(self.url)
        self.assertIn("Xword", driver.title)

class LoggedInPageTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.url = site_url 
        driver.get(self.url)
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# 
# site_url = 'http://127.0.0.1:5000'
# 
# # driver = webdriver.PhantomJS()
# driver = webdriver.Chrome() 
# driver.get(site_url + '/login')
# 
# element = driver.find_element_by_id("register-form-link")
# element.click()
# 
# 
# username = driver.find_element_by_css_selector("html body div.container div.row div.col-md-6.col-md-offset-3 div.panel.panel-login div.panel-body div.row div.col-lg-12 form#register-form div.form-group input#username.form-control")
# 
# username.send_keys("test")
# 
# email = driver.find_element_by_css_selector("html body div.container div.row div.col-md-6.col-md-offset-3 div.panel.panel-login div.panel-body div.row div.col-lg-12 form#register-form div.form-group input#email.form-control")
# email.send_keys("test@test.com")
# 
# 
# password = driver.find_element_by_css_selector("html body div.container div.row div.col-md-6.col-md-offset-3 div.panel.panel-login div.panel-body div.row div.col-lg-12 form#register-form div.form-group input#password.form-control")
# 
# password.send_keys("test")
# 
# 
# confirm = driver.find_element_by_css_selector("html body div.container div.row div.col-md-6.col-md-offset-3 div.panel.panel-login div.panel-body div.row div.col-lg-12 form#register-form div.form-group input#confirm.form-control")
# 
# confirm.send_keys("test") 
# 
# 
# driver.find_element_by_xpath("//*[@id=\"register-submit\"]").click() 


 # # Generally I found the following might be useful for verifying the page:
 # driver.current_url
 # driver.title
 # 
 # # The following might be useful for verifying the driver instance:
 # driver.name
 # driver.orientation
 # driver.page_source
 # driver.window_handles
 # driver.current_window_handle
 # driver.desired_capabilities
 # 



    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()


