from flask import render_template, request, session, redirect, url_for
from app import app
from app.db import db
from app.dbmodels import User, HintAnswerPair, CrosswordPuzzle
from app.dbmodels import UserCreatedPuzzles, PuzzleHintsMapTable
from app.util import validate_table, getsalt, createhash
from app.puzzle.crossword import Crossword
from functools import wraps
from os import urandom
import random

register_form = ['username', 'email', 'password', 'confirm']
login_form = ['username', 'password']
submit_form = ['hint', 'answer']  # , 'theme']

app.secret_key = urandom(24)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


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
@login_required
def logout():
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
@login_required
def submit_pair():
    if request.method == 'GET':
        return render_template('submit.html')

    if request.method == 'POST':
        if validate_table(submit_form, request.form):
            hint = request.form['hint']
            answer = request.form['answer']

            # Check if hint/answer pair already exists
            # in the database

            pair_exists = HintAnswerPair.query.filter(
                                            HintAnswerPair.hint == hint,
                                            HintAnswerPair.answer == answer
                                                        ).scalar()

            if pair_exists is None:
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
            else:
                message = "Error: Hint/Answer pair already exists."
                return render_template(
                                        'index.html',
                                        message=message
                                      )

    return redirect(url_for('login'))


@app.route("/browse_puzzles/", defaults={"page": 1})
@app.route("/browse_puzzles/page/<int:page>",
           methods=['GET', 'POST'])
@login_required
def browse_puzzles(page):

    query = CrosswordPuzzle.query
    paginated = query.paginate(page, 12)
    # http://flask-sqlalchemy.pocoo.org/2.1/api/#flask.ext.sqlalchemy.Pagination
    # https://www.reddit.com/r/flask/comments/3nsfr3/afflasksqlalchemy_pagination/
    # paginated = Table.query.filter(things==t, this==t).paginate(page, 10)
    # return render_template("mypage.html", paginated=paginated)
    # flask.ext.sqlalchemy.Pagination(query, page, per_page, total, items)
    # https://pythonguy.wordpress.com/category/sqlalchemy/
    if request.method == 'GET':
        return render_template('browse_puzzles.html', paginated=paginated)


@app.route("/create_puzzle", methods=['GET', 'POST'])
@login_required
def create_puzzle():

    if request.method == 'GET':
        return render_template('create_puzzle.html')

    if request.method == 'POST':
        post_params = request.form.to_dict()

        title = post_params.get('title', None)

        if title is None:
            message = "Error: Need to provide title for puzzle."
            return render_template('index.html', message=message)

        # Sort hints and answers to make sure listed in order
        # e.g. hint_1, hint_2, hint_3, rather that hint_2, hint_1, hint_3
        hint_keys = sorted(filter(lambda x: "hint_" in x, post_params))
        answer_keys = sorted(filter(lambda x: "answer_" in x, post_params))

        # Should respond with error if hints, answers lengths do not match
        if len(hint_keys) != len(answer_keys):
            message = "Error: Invalid Request Arguments."
            return render_template('index.html', message=message)

        # If we decide on a minimum length for crossword puzzle questions
        # that should also be enforced here

        # If hint/answer not in database then we need to add it database
        # A cool feature for a second iteration would be an AJAX style
        # drop down.
        # box when typing in hint/answers that will complete based off
        # of contents
        # in the database, that is a little much for first demo though
        pairs = []
        hint_ids = {}
        for hint_key, answer_key in zip(hint_keys, answer_keys):
            hint = request.form[hint_key]
            answer = request.form[answer_key].upper()
            print("Hint: ", hint)
            print("Answer: ", answer)

            if hint == '' or answer == '':
                message = "Error: Invalid Request Arguments."
                return render_template('index.html', message=message)

            # pair = (hint, answer)
            pair = (answer, hint)
            pairs.append(pair)

            # Check if hint/answer pair already exists, do not report an error
            # just do not add to the database if this happens
            existing_pair = HintAnswerPair.query.filter(
                                            HintAnswerPair.hint == hint,
                                            HintAnswerPair.answer == answer
                                            ).first()

            if existing_pair is not None:
                hint_ids[pair] = existing_pair.haid
            else:
                print("New Hint Answer Pair")

                # Add the hint/answer pair to the database
                new_pair = HintAnswerPair(answer, hint, session['uid'])
                db.session.add(new_pair)
                db.session.commit()
                hint_ids[pair] = new_pair.haid

        # word_list = [x[1] for x in pairs]
        word_list = [x[0] for x in pairs]
        print("Word list: ", word_list)
        print("Pairs: ", pairs)
        new_puzzle = Crossword(50, 50, "-", 5000, pairs)
        new_puzzle.compute_crossword(3)
        new_puzzle.order_number_words()

        print("Crossword Current Word List", new_puzzle.current_word_list)
        word_descriptions = {str(x).upper(): (x.row, x.col, x.down_across(), x.number)
                             for x in new_puzzle.current_word_list}
        print("Word descriptions", word_descriptions)

        if len(word_list) != len(word_descriptions):
            message = "Error: Could not place all words on the board."
            return render_template('index.html', message=message)

        # Create the crossword puzzle
        puzzle = CrosswordPuzzle(len(pairs), 25, 25, title)
        db.session.add(puzzle)
        db.session.commit()

        cid = puzzle.cid

        # Create the user to crossword mapping
        uc_entry = UserCreatedPuzzles(cid, session['uid'])
        db.session.add(uc_entry)
        db.session.commit()

        # Create a hint answer pair map entry for each hint answer
        # pair. These will describe how to layout the puzzle.
        for pair in pairs:
            # hint, answer = pair
            answer, hint = pair

            row, col, axis, num = word_descriptions[answer]

            hint_map = PuzzleHintsMapTable(
                                            cid,
                                            hint_ids[pair],
                                            num,
                                            axis,
                                            row,
                                            col
                                          )

            db.session.add(hint_map)
            db.session.commit()

    # If some unexpected HTTP request type simply
    # redirect to root page
    message = "Puzzle submitted successfully!!!"
    return render_template(
                            'index.html',
                            message=message
                          )


def random_puzzle_id():
    """Return the id of a random puzzle, or raise IndexError."""
    all_ids = CrosswordPuzzle.query.with_entities(CrosswordPuzzle.cid).all()
    return random.choice(all_ids)[0]


@app.route("/play_puzzle", methods=['GET', 'POST'])
@login_required
def play_puzzle():
    if request.method == 'POST':
        assert False, request.form

    # If a puzzle has not been selected, choose one at random
    try:
        selected_id = request.args.get('puzzle_id', random_puzzle_id())
    except IndexError:
        return render_template(
            'play_puzzle.html', message='No puzzles yet!', puzzleData={})

    raw_hints = (
        HintAnswerPair.query
        .join(PuzzleHintsMapTable)
        .add_columns(
            HintAnswerPair.hint,
            HintAnswerPair.answer,
            PuzzleHintsMapTable.axis,
            PuzzleHintsMapTable.cell_across,
            PuzzleHintsMapTable.cell_down,
            PuzzleHintsMapTable.hint_num
        ).filter_by(cid=selected_id)
        .all()
    )
    if not raw_hints:
        return render_template(
            'play_puzzle.html', message='Puzzle not found!', puzzleData={})

    puzzle = CrosswordPuzzle.query.get(selected_id)

    puzzleData = {
        'title': puzzle.title,
        'nrows': puzzle.num_cells_down,
        'ncols': puzzle.num_cells_across,
        'hints': [
            {
                'hint': hint.hint,
                'answer': hint.answer,
                'direction': hint.axis,
                'row': hint.cell_across - 1,
                'col': hint.cell_down - 1,
                'num': hint.hint_num,
            } for hint in raw_hints
        ]
    }
    return render_template('play_puzzle.html', puzzleData=puzzleData)
