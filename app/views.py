from flask import render_template, request, session, redirect, url_for
from app import app
from app.db import db
from app.dbmodels import User, HintAnswerPair
from app.util import validate_table, getsalt, createhash

from os import urandom

register_form = ['username', 'email', 'password', 'confirm']
login_form = ['username', 'password']
submit_form = ['hint', 'answer']  # , 'theme']

app.secret_key = urandom(24)


@app.route('/')
def index():
    return render_template('index.html', session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if validate_table(login_form, request.form):

            username = request.form['username']
            password = request.form['password']

            try:
                user_exists = User.query.filter_by(uname=username).first()
            except:
                user_exists = None

            if user_exists:
                if createhash(user_exists.salt, password) ==\
                   user_exists.password:
                    session['logged_in'] = True
                    session['username'] = username
                    session['uid'] = str(user_exists.uid)
                    return render_template(
                                            'index.html',
                                            message='Login successful'
                                          )

            return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():

    if 'logged_in' not in session:
        return redirect(url_for('index'))

    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        if validate_table(register_form, request.form):

            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm = request.form['confirm']

            if password != confirm:
                # Add template logic for invalid registration.
                return redirect(url_for('login'))

            salt = getsalt()
            passhash = createhash(salt, password)
            newUser = User(username, email, salt, passhash)
            db.session.add(newUser)
            db.session.commit()
            return render_template(
                                    'index.html',
                                    message='Registration successful'
                                  )
        else:
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/submit_pair', methods=['GET', 'POST'])
def submit_pair():

    # Probably shoudl use decorator so we don't have to write this
    # every time
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('submit.html')

    if request.method == 'POST':
        if validate_table(submit_form, request.form):

            hint = request.form['hint']
            answer = request.form['answer']

            newPair = HintAnswerPair(
                                     answer, hint,
                                     session['uid']
                                    )
            db.session.add(newPair)
            db.session.commit()
            return render_template(
                                    'index.html',
                                    message='Submission successful'
                                  )

    return redirect(url_for('login'))


@app.route("/create_puzzle", methods=['GET', 'POST'])
def create_puzzle():

    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('create_puzzle.html')

    if request.method == 'POST':

        hints = []
        answers = []

        post_params = request.form.to_dict()

        hints = filter(lambda x: "hint_" in x, post_params)
        answers = filter(lambda x: "answer_" in x, post_params)

        # Sort hints and answers to make sure listed in order
        # e.g. hint_1, hint_2, hint_3, rather that hint_2, hint_1, hint_3
        hints = sorted(list(hints))
        answers = sorted(list(answers))

        # Should respond with error if hints, answers lengths do not mach

        # If we decide on a minimum length for crossword puzzle questions
        # that should also be enforced here

        # If hint/answer not in database then we need to add it database
        # A cool feature for a second iteration would be an AJAX style
        # drop down.
        # box when typing in hint/answers that will complete based off
        # of contents
        # in the database, that is a little much for first demo though
        for hint, answer in zip(hints, answers):

            print("Hint: " + request.form[hint])
            print("Answer: " + request.form[answer])
            hint = request.form[hint]
            answer = request.form[answer]

            # Check if hint/answer pair already exists, do not report an error
            # just do not add to the database if this happens
            pair_exists = HintAnswerPair.query.filter(
                                            HintAnswerPair.hint == hint,
                                            HintAnswerPair.answer == answer
                                                        ).scalar()

            if pair_exists is None:
                print("New Hint Answer Pair")

                # Add the hint/answer pair to the database
                new_pair = HintAnswerPair(answer, hint, session['uid'])
                db.session.add(new_pair)
                db.session.commit()

        # If puzzle is created successfully should redirect to
        # game page where puzzle game starts

    # If some unexpected HTTP request type simply
    # redirect to root page
    return redirect(url_for('index'))
