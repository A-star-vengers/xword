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
#        self.assertTrue(driver.getTitle(),
#            "Can't find a title on the page"
#        )

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


#    def test_homepage_click(self):
#        driver = self.driver
#        driver.get(self.url)
#
#        # Sets timeout for wait which we will use after the click
#        wait = ui.WebDriverWait(driver, 2)
#
#        title = driver.find_element_by_css_selector('.title a')
#
#        title.click()
#
#        # Waits until the url changes to '/hello' or till a timeout
#        wait.until(lambda driver: driver.current_url.endswith('/hello'),
#                   "Click Title No Work")

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
