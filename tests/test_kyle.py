# coding: utf-8
from app import app
from app.util import validate_table
from app.db import db, init_db

import flask_wtf

from functools import wraps

import unittest


real_validate = flask_wtf.csrf.validate_csrf


def check_csrf(test_method):
    """Decorate a test method in order to check the CSRF token."""
    @wraps(test_method)
    def wrapper(self, *args, **kwargs):
        flask_wtf.csrf.validate_csrf = real_validate
        return test_method(self, *args, **kwargs)
    return wrapper


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        # For most tests we don't care about the CSRF token.
        flask_wtf.csrf.validate_csrf = lambda token: True
        db.drop_all()
        init_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Ensure that Flask was set up correctly
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_slash(self):
        tester = app.test_client(self)
        response = tester.get('/')
        self.assertIn(b'Xword: A Social Crossword Application', response.data)

    # Ensure that the login page loads correctly
    def test_login_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/login')
        self.assertIn(b'Login', response.data)

    def test_logout(self):
        tester = app.test_client(self)
        response = tester.post('/register', data=dict(
                        username_register='test1',
                        email='test@gmail.com',
                        password_register='test1',
                        confirm='test1'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200, response.data.decode())
        assert 'Registration successful' in response.data.decode()

        response = tester.post('/login', data=dict(
                        username_login='test1',
                        password_login='test1'
        ), follow_redirects=True)

        assert 'Login successful' in response.data.decode()

        response = tester.get('/logout', follow_redirects=True)

        self.assertIn(b'Xword: A Social Crossword Application', response.data)
        # above should really be something like
        # 'assert render_template('index.html') == response.data'

    def test_validate_table(self):
        import flask
        app = flask.Flask(__name__)

        with app.test_request_context('/login'):
            assert flask.request.path == '/login'
            assert not validate_table(['a', 'b'], flask.request.form)

    def test_validate_submit_get(self):
        tester = app.test_client(self)
        response = tester.post('/register', data=dict(
                        username_register='test1',
                        email='test@gmail.com',
                        password_register='test1',
                        confirm='test1'
        ), follow_redirects=True)

        assert 'Registration successful' in response.data.decode()

        response = tester.post('/login', data=dict(
                        username_login='test1',
                        password_login='test1'
        ), follow_redirects=True)

        assert 'Login successful' in response.data.decode()

        response = tester.get('/submit_pairs', follow_redirects=True)
        self.assertIn(b'Submit Hint/Answer Pair', response.data)

    def test_hint_answer_already_exists(self):
        tester = app.test_client(self)
        response = tester.post('/register', data=dict(
                        username_register='test1',
                        email='test@gmail.com',
                        password_register='test1',
                        confirm='test1'
        ), follow_redirects=True)

        assert 'Registration successful' in response.data.decode()

        response = tester.post('/login', data=dict(
                        username_login='test1',
                        password_login='test1'
        ), follow_redirects=True)

        assert 'Login successful' in response.data.decode()

        response = tester.post('/submit_pairs', data=dict(
                hint_0='aaa',
                answer_0='aaa'), follow_redirects=True)

        self.assertIn(b'Successful Submissions', response.data)

        # response = tester.post('/submit_pairs', data=dict(
        #        hint_0='aaa',
        #        answer_0='aaa'), follow_redirects=True)

    def test_browse_puzzles(self):
        tester = app.test_client(self)

        response = tester.post('/register', data=dict(
                        username_register='test1',
                        email='test@gmail.com',
                        password_register='test1',
                        confirm='test1'
        ), follow_redirects=True)

        assert 'Registration successful' in response.data.decode()

        response = tester.post('/login', data=dict(
                        username_login='test1',
                        password_login='test1'
        ), follow_redirects=True)

        assert 'Login successful' in response.data.decode()
        response = tester.get('/browse_puzzles/page/1', follow_redirects=True)

        self.assertIn(b'Browse existing puzzles to play', response.data)

    def test_selenium_register(self):
        from selenium import webdriver
        import time
      
        url = 'http://127.0.0.1:5000'
        email = "test@test.com"
        username = "test"
        password = "testpw"

        driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
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

        self.assertIn("Registration successful", driver.page_source)

# import datetime
# driver.maximize_window()
# fmt = '%f'
# filename = 'out' + datetime.datetime.now().strftime(fmt) + '.png';
# driver.save_screenshot(filename)

    @check_csrf
    def test_csrf_token_missing(self):
        tester = app.test_client(self)

        response = tester.post('/register', data=dict(
                        username_register='test1',
                        email='test@gmail.com',
                        password_register='test1',
                        confirm='test1'
        ), follow_redirects=True)

        response = tester.post('/login', data=dict(
                        username_login='test1',
                        password_login='test1'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 400, msg=response.data.decode())
        self.assertIn('CSRF token missing', response.data.decode())


if __name__ == '__main__':
    unittest.main()
