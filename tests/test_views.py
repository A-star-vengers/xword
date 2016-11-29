#!venv3/bin/python

import unittest
from flask_testing import TestCase
from app import app
from app.db import db, init_db
from app.dbmodels import CrosswordPuzzle

import flask_wtf

def register_and_login(x, username):
    # password and email are pretty unused at the moment
     response = x.client.post('/register', data=dict(
                        username=username,
                        email='test@gmail.com',
                        password='test',
                        confirm='test',
     ), follow_redirects=True)

     response = x.client.post('/login', data=dict(
                        username=username,
                        password='test'
     ), follow_redirects=True)



class AppTest(TestCase):

    Testing = True

    def create_app(self):
        return app

    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        flask_wtf.csrf.validate_csrf = lambda token: True
        db.drop_all()
        init_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class LoggedInAppTest(AppTest):

    def setUp(self):
        super(LoggedInAppTest, self).setUp()
        register_and_login(self, 'test')
#        response = self.client.post('/register', data=dict(
#                        username='test',
#                        email='test@gmail.com',
#                        password='test',
#                        confirm='test',
#        ), follow_redirects=True)
#
#        response = self.client.post('/login', data=dict(
#                        username='test',
#                        password='test'
#        ), follow_redirects=True)

class LoggedInAppTestWithFilledQuestionDb(LoggedInAppTest):

    def setUp(self):
        super(LoggedInAppTestWithFilledQuestionDb, self).setUp()

        response = self.client.post('/create_puzzle', data=dict(
                title="Geography Questions",
                hint_1="The movement of people from one place to another ",
                answer_1="migration",
                hint_2="The number of deaths each year per 1,000 people ",
                answer_2="deathrate",
                hint_3="Owners and workers who make products ",
                answer_3="producers",
                    ), follow_redirects=True)



class LoginTest(AppTest):

    def test_login(self):

        response = self.client.post('/login', data=dict(
                        username='test',
                        password='test2'
        ), follow_redirects=True)

        assert 'Login successful' not in response.data.decode()

    def test_empty_login(self):

        response = self.client.post('/login', data=dict(
                        username='',
                        password='test2'
        ), follow_redirects=True)

        text = b'<form id="login-form" action="/login"'

        self.assertIn(text, response.data)

        response = self.client.post('/login', data=dict(
                        username='test',
                        password=''
        ), follow_redirects=True)

        self.assertIn(text, response.data)

        response = self.client.post('/login', data=dict(
                        username='',
                        password=''
        ), follow_redirects=True)

        self.assertIn(text, response.data)

    def test_invalid_login(self):

        response = self.client.post('/login', data=dict(
                        username='test',
                        password='test3'
                    ), follow_redirects=True)

        text = b'<form id="login-form" action="/login"'

        self.assertIn(text, response.data)

    def test_login_required(self):
        response = self.client.get('/play_puzzle', follow_redirects=True)
        self.assertIn(b'<form id="login-form" action="/login"', response.data)

    def test_non_existent_user(self):
        response = self.client.post('/login', data=dict(username='idontexist', password='idontexist'),
                                    follow_redirects=True)
        self.assertIn(b'<form id="login-form" action="/login"', response.data)


class RegisterTest(AppTest):

    def test_register(self):

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='test@gmail.com',
                        password='test',
                        confirm='test'
        ), follow_redirects=True)

        assert 'Registration successful' in response.data.decode()

    def test_empty_register(self):

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='test@gmail.com',
                        password='test',
                        confirm=''
                    ), follow_redirects=True)

        text = b'<form id="login-form" action="/login"'

        self.assertIn(text, response.data)

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='test@gmail.com',
                        password='',
                        confirm='test'
                    ), follow_redirects=True)

        self.assertIn(text, response.data)

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='',
                        password='test',
                        confirm='test'
                    ), follow_redirects=True)

        self.assertIn(text, response.data)

        response = self.client.post('/register', data=dict(
                        username='',
                        email='test@gmail.com',
                        password='test',
                        confirm='test'
                    ), follow_redirects=True)

        self.assertIn(text, response.data)

    def test_invalid_confirm(self):

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='test@gmail.com',
                        password='test',
                        confirm='testing'
                    ), follow_redirects=True)

        text = b'<form id="login-form" action="/login"'

        self.assertIn(text, response.data)

    def test_already_registered(self):

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='test@gmail.com',
                        password='test',
                        confirm='test'
        ), follow_redirects=True)

        assert 'Registration successful' in response.data.decode()

        text = b'Error account already exists'

        response = self.client.post('/register', data=dict(
                        username='test',
                        email='test@gmail.com',
                        password='test',
                        confirm='test'
        ), follow_redirects=True)

        self.assertIn(text, response.data)


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


"""
class SubmitHintAnswerPairTest(LoggedInAppTest):
    expected_ascii_error = b'must only contain the letters A to Z'
    expected_length_error = b'must not be longer than'
    expected_success = b'Submission successful'

    def test_submit_pair(self):

        response = self.client.post('/submit_pair', data=dict(
                        hint="You took these in school.",
                        answer="exams"
        ), follow_redirects=True)

        self.assertIn(self.expected_success, response.data)

    def test_submit_quote(self):
        response = self.client.post('/submit_pair', data=dict(
            hint="Conan ___, TBS late night show host",
            answer="o'brien"
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)

    def test_submit_empty(self):
        response = self.client.post('/submit_pair', data=dict(
            hint="Empty answer",
            answer=""
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)

    def test_submit_numbers(self):
        response = self.client.post('/submit_pair', data=dict(
            hint="The answer to life, the universe and everything",
            answer="42"
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)

    def test_submit_dash(self):
        response = self.client.post('/submit_pair', data=dict(
            hint="The answer to life, the universe and everything",
            answer="Forty-Two"
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)

    def test_submit_spaces(self):
        response = self.client.post('/submit_pair', data=dict(
            hint="The Gettysburg Address",
            answer="Four score and seven years ago our fathers brought forth, on this continent"
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)

    def test_submit_long(self):
        response = self.client.post('/submit_pair', data=dict(
            hint="A very long answer",
            answer="ThisIsAVeryLongAnswerThatMostCertainlyShouldBeRejectedByTheApplication"
        ), follow_redirects=True)

        self.assertIn(self.expected_length_error, response.data)
"""

def SubmitPairsTest(LoggedInAppTest):

    expected_ascii_error = b'must only contain the letters A to Z'
    expected_length_error = b'must not be longer than'
    expected_success = b'Submission successful'

    def test_submit_pair(self):

        response = self.client.post('/submit_pairs', data=dict(
                        hint_0="You took these in school.",
                        answer_0="exams"
        ), follow_redirects=True)

        self.assertIn(self.expected_success, response.data)

    def test_submit_quote(self):
        response = self.client.post('/submit_pairs', data=dict(
            hint_0="Conan ___, TBS late night show host",
            answer_0="o'brien"
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)

    def test_submit_empty(self):
        response = self.client.post('/submit_pairs', data=dict(
            hint_0="Empty answer",
            answer_0=""
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)

    def test_submit_numbers(self):
        response = self.client.post('/submit_pairs', data=dict(
            hint_0="The answer to life, the universe and everything",
            answer_0="42"
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)

    def test_submit_dash(self):
        response = self.client.post('/submit_pairs', data=dict(
            hint_0="The answer to life, the universe and everything",
            answer_0="Forty-Two"
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)


    def test_submit_spaces(self):
        response = self.client.post('/submit_pairs', data=dict(
            hint_0="The Gettysburg Address",
            answer_0="Four score and seven years ago our fathers brought forth, on this continent"
        ), follow_redirects=True)

        self.assertIn(self.expected_ascii_error, response.data)

    def test_submit_long(self):
        response = self.client.post('/submit_pairs', data=dict(
            hint_0="A very long answer",
            answer_0="ThisIsAVeryLongAnswerThatMostCertainlyShouldBeRejectedByTheApplication"
        ), follow_redirects=True)

        self.assertIn(self.expected_length_error, response.data)


class CreatePuzzleTest(LoggedInAppTest):

    def test_create_puzzle(self):

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
                answer_14="economy"
                    ), follow_redirects=True)

        # print( str(response.data.decode()) )

        assert 'Puzzle submitted successfully' in response.data.decode()

    def test_mismatch_create_puzzle(self):

        response = self.client.post('/create_puzzle', data=dict(
                    title = "Geography Questions",
                    hint_1="The movement of people from one place to another",
                    hint_2="The number of deaths each year per 1,000 people",
                    answer_2="deathrate",
                    hint_3="Owners and workers who make products ",
                    answer_3="producers",
                    hint_4="A government in which the king is limited by law ",
                    answer_4="constitutionalmonarchy"
                    ), follow_redirects=True)

        self.assertIn(b'Error: amount of hints and answers must match', response.data)

    def test_notitle_create_puzzle(self):

        response = self.client.post('/create_puzzle', data=dict(
                    hint_1="The movement of people from one place to another",
                    answer_1="migration",
                    hint_2="The number of deaths each year per 1,000 people",
                    answer_2="deathrate"
                    ), follow_redirects=True)

        self.assertIn(b'Error: Need to provide title for puzzle', response.data)

    def test_emptytitle_create_puzzle(self):

        response = self.client.post('/create_puzzle', data=dict(
                    title="",
                    hint_1="The movement of people from one place to another",
                    answer_1="migration",
                    hint_2="The number of deaths each year per 1,000 people",
                    answer_2="deathrate"
                    ), follow_redirects=True)

        self.assertIn(b'Error: Need to provide title for puzzle', response.data)

    def test_empty_hint_answer_puzzle(self):

        response = self.client.post('/create_puzzle', data=dict(
                    title="Geography Questions",
                    hint_1="",
                    answer_1=""
                    ), follow_redirects=True)

        self.assertIn(b"must not be shorter than 2 letters", response.data)

    def test_answer_not_alpha(self):

        response = self.client.post('/create_puzzle', data=dict(
                    title="Geography Questions",
                    hint_1="The movement of people from one place to another",
                    answer_1="\xDE\xAD\xBE\xEF"
                    ), follow_redirects=True)

        message = b"must only contain the letters A to Z"

        self.assertIn(message, response.data)

class PlayPuzzleTest(LoggedInAppTest):

    def create_good_puzzle(self):

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
                answer_14="economy"
                    ), follow_redirects=True)


    def test_no_puzzle(self):

        response = self.client.get('/play_puzzle', follow_redirects=True)

        assert 'No puzzles yet' in response.data.decode()

    def test_with_puzzle(self):

        self.create_good_puzzle()
        response = self.client.get('/play_puzzle', follow_redirects=True)

        assert "puzzleData" in response.data.decode()


class BrowsePuzzleTest(LoggedInAppTest):

    def fill_fake_puzzle_db(self):

        title = "Puzzle"
        creator = 1

        for x in range(100):
            puzzle = CrosswordPuzzle(10, 25, 25, title + str(x), creator)
            db.session.add(puzzle)
            db.session.commit()

    def test_browse_no_puzzles(self):

        response = self.client.get('/browse_puzzles', follow_redirects=True)

        assert "thumbnail" not in response.data.decode()

    def test_browse_puzzles(self):

        self.fill_fake_puzzle_db()

        response = self.client.get('/browse_puzzles', follow_redirects=True)

        assert "Next" in response.data.decode()

        response = self.client.get('/browse_puzzles/page/2', follow_redirects=True)

        assert "Next" in response.data.decode() and "Prev" in response.data.decode()


class JapaneseTest(LoggedInAppTest):

    def test_submit_pair(self):

        response = self.client.post('/submit_pairs', data=dict(
                        hint_0="Japanese hint",
                        answer_0="的場"
        ), follow_redirects=True)

        assert "only contain the letters A to Z" in response.data.decode()


class AboutTest(AppTest):

    def test_about(self):
        response = self.client.get('/about', follow_redirects=True)
        self.assertIn(b'xword is a social crossword web application that will challenge players', response.data)


class PuzzleCreatorRenderTest(LoggedInAppTestWithFilledQuestionDb):
    def test_puzzle_creator_renders(self):
        response = self.client.get('/play_puzzle', follow_redirects=True)

        self.assertIn(b'"creator": "test", "', response.data)

# 
# class QuestionAuthorsRenderTest(LoggedInAppTestWithFilledQuestionDb):
#     def test_quastion_authors_renders(self):
#         response = self.client.get('/logout', follow_redirects=True)
#         register_and_login(self, 'test2')
#         response = self.client.post('/submit_pair', data=dict(
#                         hint="Another hint",
#                         answer="AnotherAnswer"
#         ), follow_redirects=True)
# 
#         response = self.client.get('/play_puzzle', follow_redirects=True)
#         # self.assertIn(b'With answers authored by test and test2', response.data)
#         self.assertIn(b'With answers authored by test and test2', response.data)
