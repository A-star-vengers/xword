#!flask/bin/python

import unittest
from flask_testing import TestCase
from app import app
from app.db import db, init_db


class AppTest(TestCase):

    Testing = True

    def create_app(self):
        return app

    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        db.drop_all()
        init_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class LoginTest(AppTest):

    def test_login(self):

        response = self.client.post('/login', data=dict(
                        username='test',
                        password='test2'
        ), follow_redirects=True)

        assert 'Login successful' not in response.data.decode()


class RegisterTest(AppTest):

    def test_register(self):

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='test@gmail.com',
                        password='test',
                        confirm='test'
        ), follow_redirects=True)

        assert 'Registration successful' in response.data.decode()


class RegisterAndLoginTest(AppTest):

    def test_register_and_login(self):

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='test@gmail.com',
                        password='test',
                        confirm='test'
        ), follow_redirects=True)

        assert 'Registration successful' in response.data.decode()

        response = self.client.post('/login', data=dict(
                        username='test',
                        password='test'
        ), follow_redirects=True)

        assert 'Login successful' in response.data.decode()


class SubmitHintAnswerPairTest(AppTest):

    def test_submit_pair(self):

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='test@gmail.com',
                        password='test',
                        confirm='test'
        ), follow_redirects=True)

        assert 'Registration successful' in response.data.decode()

        response = self.client.post('/login', data=dict(
                        username='test',
                        password='test'
        ), follow_redirects=True)

        assert 'Login successful' in response.data.decode()

        response = self.client.post('/submit_pair', data=dict(
                        hint="You took these in school.",
                        answer="exams"
        ), follow_redirects=True)

        assert 'Submission successful' in response.data.decode()


if __name__ == '__main__':
    unittest.main()
