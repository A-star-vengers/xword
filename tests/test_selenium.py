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

    css_pattern = "html body div.container div.row div.col-md-6.col-md-offset-3 div.panel.panel-login div.panel-body div.row div.col-lg-12 form#register-form div.form-group input#{}.form-control"
    username_elem = driver.find_element_by_css_selector(css_pattern.format("username"))
    email_elem    = driver.find_element_by_css_selector(css_pattern.format("email"))
    password_elem = driver.find_element_by_css_selector(css_pattern.format("password"))
    confirm_elem  = driver.find_element_by_css_selector(css_pattern.format("confirm"))

    time.sleep(1)

    username_elem.send_keys(username)
    email_elem.send_keys(email)
    password_elem.send_keys(password)
    confirm_elem.send_keys(password) 

    driver.find_element_by_xpath("//*[@id=\"register-submit\"]").click() 

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

        self.driver = webdriver.PhantomJS()
        self.url = 'http://127.0.0.1:5000'
        self.email = "test@test.com"
        self.password = "test_password"
        self.username = "test_username"

        register(self.driver, self.url, self.email, self.username, self.password)
        login(self.driver, self.url, self.username, self.password)


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.driver.close()

class SeleniumLoginTest(LoggedInSeleniumTest):
    def test_is_logged_in(self):
        self.assertIn("Login successful", self.driver.page_source)

if __name__ == "__main__":
    unittest.main()


