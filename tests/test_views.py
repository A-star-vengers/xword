#!venv3/bin/python

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


class CreatePuzzleTest(AppTest):

    def test_create_puzzle(self):

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

        response = self.client.post('/create_puzzle', data=dict(
                title="Geography Questions",
                hint_1="The movement of people from one place to another ",
                answer_1="migration",
                hint_2="The number of deaths each year per 1,000 people ",
                answer_2="deathrate",
                hint_3="Owners and workers who make products ",
                answer_3="producers",
                hint_4="A government in which the king is limited by law ",
                answer_4="constitutionalmonarchy",
                hint_5="the way a population is spread out over an area ",
                answer_5="populationdistribution",
                hint_6="an economic system in which the central government " +
                       "controls owns factories, farms, and offices",
                answer_6="communism",
                hint_7="a form of government in which all adults take " +
                       " part in decisions",
                answer_7="directdemocracy",
                hint_8="people who move into one country from another ",
                answer_8="immigrants",
                hint_9="nations with many industries and advanced technology ",
                answer_9="developednations",
                hint_10="a king or queen inherits the throne by birth " +
                        "and has complete control",
                answer_10="absolutemonarchy",
                hint_11="the science that studies population " +
                        "distribution and change",
                answer_11="demography",
                hint_12="a region that belongs to another state ",
                answer_12="dependency",
                hint_13="a set of laws that define and often limit a " +
                        "government's power",
                answer_13="constitution",
                hint_14="a system in which people make, exchange, and use " +
                        "things that have value",
                answer_14="economy",
                    ), follow_redirects=True)

        assert 'Puzzle submitted successfully' in response.data.decode()

