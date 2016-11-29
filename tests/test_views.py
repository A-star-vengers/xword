#!venv3/bin/python

import unittest
from flask_testing import TestCase
from app import app
from app.db import db, init_db
from app.dbmodels import CrosswordPuzzle, Theme, HintAnswerPair, HintAnswerThemeMap

import json

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

    def test_multi_submission(self):

        response = self.client.post('/submit_pairs', data=dict(
            hint_0="Things pushed around a super market",
            answer_0="carts",
            hint_1="Afer curfew",
            answer_1="late",
            hint_2="Economist Smith",
            answer_2="Adam"
        ), follow_redirects=True)

        self.assertIn("Successful Submissions 3", response.data)

    def test_multi_theme_submission(self):

        response = self.client.post('/submit_pairs', data=dict(
            hint_0="Things pushed around a super market",
            answer_0="carts",
            theme_0 ="groceries",
            hint_1="Afer curfew",
            answer_1="late",
            theme_1="general",
            hint_2="Economist Smith",
            theme_2="history",
            answer_2="Adam"
        ), follow_redirects=True)

        self.assertIn("Successful Submissions 3", response.data)

    def test_mismatch_theme_submission(self):

        response = self.client.post('/submit_pairs', data=dict(
            hint_0="Things pushed around a super market",
            answer_0="carts",
            hint_1="Afer curfew",
            answer_1="late",
            theme_1="general",
            hint_2="Economist Smith",
            answer_2="Adam"
        ), follow_redirects=True)

        self.assertIn("Successful Submissions 3", response.data)


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

class ThemesAPITest(LoggedInAppTest):

    def create_fake_themes(self):

       themes = ["history", "geography", "sports",
                 "fashion", "television", "animals",
                 "cars"
                ]

       for x in themes:
            newTheme = Theme(x)
            db.session.add(newTheme)
            db.session.commit()

    def test_empty_themes(self):

        response = self.client.get('/themes',
                                    query_string={
                                            "num_themes" : 6
                                                 },
                                    follow_redirects=True)

        rdata = json.loads(response.data.decode('utf8'))

        self.assertIn('themes', rdata)

        self.assertEqual(rdata['themes'], [])

    def test_adequate_themes(self):

        self.create_fake_themes()

        response = self.client.get('/themes',
                                    query_string = {'num_themes' : 6},
                                    follow_redirects=True)

        print( dir(response.data) )

        rdata = json.loads(response.data.decode('utf8'))

        self.assertIn('themes', rdata)

        self.assertEqual(len(rdata['themes']), 6)

    def test_not_enough_themes(self):

        self.create_fake_themes()

        response = self.client.get('/themes',
                                    query_string={'num_themes':8},
                                    follow_redirects=True)

        print( dir(response.data) )

        rdata = json.loads(str(response.data.decode('utf8')))

        self.assertIn('themes', rdata)

        self.assertEqual(len(rdata['themes']), 7)

    def test_prefix_exist_themes(self):

        self.create_fake_themes()

        response = self.client.get('/themes',
                                    query_string={
                                                    'num_themes':6,
                                                    'prefix':'geo'
                                                 },
                                    follow_redirects=True)

        rdata = json.loads(response.data.decode('utf8'))

        self.assertIn('themes', rdata)

        self.assertIs(len(rdata['themes']), 1)

        self.assertEqual(rdata['themes'][0], 'geography')

    def test_prefix_noexist_themes(self):

        self.create_fake_themes()

        response = self.client.get('/themes',
                                    query_string={
                                                    'num_themes':6,
                                                    'prefix':'ki'
                                                 },
                                    follow_redirects=True)

        print( dir(response.data) )

        rdata = json.loads(response.data.decode('utf8'))

        self.assertIn('themes', rdata)

        self.assertEqual(rdata['themes'], [])

class SuggestsAPITest(LoggedInAppTest):

    def create_pairs(self):

        pair1 = {
                    "hint" : "The movement of people from one place to another",
                    "answer" : "migration",
                    "theme" : "geography",
                    "author" : 1
                }

        pair2 = {
                    "hint" : "Owners and workers who make products",
                    "answer" : "producers",
                    "theme" : "geography",
                    "author" : 1
                }

        pair3 = {
                    "hint" : "The number of deaths each year per 1,000 people",
                    "answer" : "deathrate",
                    "theme" : "geography",
                    "author" : 1
                }

        pair4 = {
                    "hint" : "A government in which the king is limited by law",
                    "answer" : "constitutionalmonarchy",
                    "theme" : "geography",
                    "author" : 1
                }

        pair5 = {
                    "hint" : "People who move from one country to another",
                    "answer" : "immigrants",
                    "theme" : "geography",
                    "author" : 1
                }

        pair6 = {
                    "hint" : "Nations with many industries and advanced technology",
                    "answer" : "developednations",
                    "theme" : "geography",
                    "author" : 1
                }

        pairs = [pair1, pair2, pair3, pair4, pair5, pair6]

        for pair in pairs:

            hpair = HintAnswerPair(pair["answer"], pair["hint"], pair["author"])
            db.session.add(hpair)
            db.session.commit()

            texists = Theme.query.filter_by(theme=pair["theme"]).first()

            if texists:
                tid = texists.tid
            else:
                theme = Theme(pair["theme"])
                db.session.add(theme)
                db.session.commit()

                tid = theme.tid

            new_hamap = HintAnswerThemeMap(hpair.haid, tid)
            db.session.add(new_hamap)
            db.session.commit()

    def create_mixed_pairs(self):

        pair1 = {
                    "hint" : "The movement of people from one place to another",
                    "answer" : "migration",
                    "theme" : "geographyOne",
                    "author" : 1
                }

        pair2 = {
                    "hint" : "Owners and workers who make products",
                    "answer" : "producers",
                    "theme" : "geographyTwo",
                    "author" : 1
                }

        pairs = [pair1, pair2]

        for pair in pairs:

            hpair = HintAnswerPair(pair["answer"], pair["hint"], pair["author"])
            db.session.add(hpair)
            db.session.commit()

            texists = Theme.query.filter_by(theme=pair["theme"]).first()

            if texists:
                tid = texists.tid
            else:
                theme = Theme(pair["theme"])
                db.session.add(theme)
                db.session.commit()

                tid = theme.tid

            new_hamap = HintAnswerThemeMap(hpair.haid, tid)
            db.session.add(new_hamap)
            db.session.commit()


    def test_no_suggests(self):

        response = self.client.post('/suggests', data=dict(
                        num_suggests=0,
        ), follow_redirects=True)  

        rdata = json.loads(response.data.decode('utf8'))

        self.assertEqual(rdata, {})

    def test_empty_except_num(self):

        self.create_pairs()

        response = self.client.post('/suggests', data=dict(
                        num_suggests=6
        ), follow_redirects=True)

        rdata = json.loads(response.data.decode('utf8'))

        self.assertEqual(len(rdata), 6)

    def test_with_hints(self):

        self.create_pairs()

        response = self.client.post('/suggests', data=dict(
                        num_suggests=6,
                        hints=json.dumps(["People who move from one country to another"]),
                        answers=json.dumps(["immigrants"])
                    ), follow_redirects=True)

        rdata = json.loads(response.data.decode('utf8'))

        self.assertEqual(len(rdata), 5)

    def test_with_theme(self):

        self.create_pairs()

        response = self.client.post('/suggests', data=dict(
                        num_suggests=6,
                        theme='geography'
                   ), follow_redirects=True)

        rdata = json.loads(response.data.decode('utf8'))

        self.assertEqual(len(rdata), 6)

    def test_with_hint_and_theme(self):

        self.create_pairs()

        response = self.client.post('/suggests', data=dict(
                        num_suggests=6,
                        hints=json.dumps(["People who move from one country to another"]),
                        answers=json.dumps(["immigrants"]),
                        theme="geography"
                    ), follow_redirects=True)

        rdata = json.loads(response.data.decode('utf8'))

        self.assertEqual(len(rdata), 5)

    def test_mixed_themes(self):

        self.create_mixed_pairs()

        response = self.client.post('/suggests', data=dict(
                        num_suggests=6,
                        theme="geographyOne"
                   ), follow_redirects=True)

        rdata = json.loads(response.data.decode('utf8'))

        self.assertEqual(len(rdata), 1)

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
