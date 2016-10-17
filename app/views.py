from flask import render_template, request, session, redirect, url_for
from app import app
from app.db import db
from app.dbmodels import User, HintAnswerPair
from app.util import validate_table, getsalt, createhash

register_form = ['username', 'email', 'password', 'confirm']
login_form = ['username', 'password']
submit_form = ['hint', 'answer']  # , 'theme']

app.secret_key = 'foobar'


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

            # print "Hint: " + str(hint)
            # print "Answer: " + str(answer)

            newPair = HintAnswerPair(
                                     answer, hint,
                                     None, session['uid'],
                                    )
            db.session.add(newPair)
            db.session.commit()
            return render_template(
                                    'index.html',
                                    message='Submission successful'
                                  )

    return redirect(url_for('login'))
