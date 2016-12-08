""" Test Front End """

# https://github.com/asap/psychic-ironman/blob/master/flask/tests/test_frontend.py

import requests
import unittest
from selenium import webdriver
from selenium.webdriver.support import ui

import time

from app import app
from app.db import db, init_db

def register(driver, url, email, username, password):
    driver.get(url + '/login')

    element = driver.find_element_by_id("register-form-link")
    element.click()

    time.sleep(3)

    username_elem = driver.find_element_by_xpath("//*[@id=\"username_register\"]")
    email_elem    = driver.find_element_by_xpath("//*[@id=\"email\"]")
    password_elem = driver.find_element_by_xpath("//*[@id=\"password_register\"]")
    confirm_elem  = driver.find_element_by_xpath("//*[@id=\"confirm\"]")

    time.sleep(3)

    username_elem.send_keys(username)
    email_elem.send_keys(email)
    password_elem.send_keys(password)
    confirm_elem.send_keys(password) 

    time.sleep(3)
    driver.find_element_by_xpath("//*[@id=\"register-submit\"]").click() 
    time.sleep(3)


def login(driver, url, username, password):
    driver.get(url + '/login')

    driver.find_element_by_xpath("//*[@id=\"username\"]").send_keys(username) 
    driver.find_element_by_xpath("//*[@id=\"password\"]").send_keys(password) 
    driver.find_element_by_xpath("//*[@id=\"login-submit\"]").click() 

class LoggedInSeleniumTest(unittest.TestCase):

    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        db.drop_all()
        init_db()

        self.driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
        self.url = 'http://127.0.0.1:5000'
        self.email = "test@test.com"
        self.password = "test"
        self.username = "test"

#        register(self.driver, self.url, self.email, self.username, self.password)
#        login(self.driver, self.url, self.username, self.password)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.driver.close()

class SeleniumLoginTest(LoggedInSeleniumTest):
    def test_is_logged_in(self):
        pass
        # self.assertIn("Login successful", self.driver.page_source)

if __name__ == "__main__":
    unittest.main()


