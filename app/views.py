from flask import render_template, request, session, redirect, url_for
from flask_wtf.csrf import CsrfProtect
from app import app
from app.db import db
from app.dbmodels import User, HintAnswerPair, CrosswordPuzzle
from app.dbmodels import UserCreatedPuzzles, PuzzleHintsMapTable
from app.dbmodels import Theme, HintAnswerThemeMap
from app.dbmodels import UserPuzzleRatings, UserPuzzleTimes
from app.util import validate_table, getsalt, createhash
from app.puzzle.crossword import Crossword
from functools import wraps
from os import urandom
from sqlalchemy import not_, and_
from sqlalchemy.sql import func
import random
import json

register_form = ['username_register', 'email', 'password_register', 'confirm']
login_form = ['username_login', 'password_login']
# submit_form = ['hint', 'answer']  # , 'theme']

app.secret_key = urandom(24)
max_xw_size = 25
max_hint_len = 25
min_hint_len = 2

message_hint_empty = "Error: Submitted Hint/Answer pair has empty Hint"
message_too_long = "Error: Answer '{0}' must not be longer than {1} letters"
message_too_short = "Error: Answer '{0}' must not be shorter than {1} letters"
message_nonalpha = "Error: Answer '{0}' must only contain the letters A to Z."
message_len_hint_keys = "Error: Got zero hints"
message_len_hint_answer_keys = "Error: amount of hints and answers must match"


def is_valid_answer(x):
    return all(ord(char) < 128 for char in x) and x.isalpha()


CsrfProtect(app)


@app.after_request
def after_request(response):
    response.headers.add('Cache-Control', 'no-store, no-cache, ' +
                         'must-revalidate post-check=0, pre-check=0')
    return response


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    app.logger.info('reached /')
    return render_template('index.html', session=session)


@app.route('/about')
def about():
    return render_template('about.html', session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if validate_table(login_form, request.form):

            username = request.form['username_login']
            password = request.form['password_login']

            if username == "" or password == "":
                empty_message = 'Error: Empty username or password'
                return render_template(
                                        'login.html',
                                        message=empty_message,
                                        username=username
                                      )

            user_exists = User.query.filter_by(uname=username).first()

            if user_exists:
                if createhash(user_exists.salt, password) ==\
                   user_exists.password:
                    session['logged_in'] = True
                    session['username'] = username
                    session['uid'] = str(user_exists.uid)

                    next_url = request.form.get('next', '')
                    if next_url:
                        return redirect(next_url)

                    return render_template(
                                            'index.html',
                                            message='Login successful'
                                          )

        return render_template(
                                'login.html',
                                message='Error: Bad Login',
                                username=username
                              )
    else:
        return render_template('login.html', next=request.args.get('next', ""))


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # TODO: Add template logic for trying to register an existing user
    if request.method == 'POST':
        if validate_table(register_form, request.form):

            username = request.form['username_register']
            email = request.form['email']
            password = request.form['password_register']
            confirm = request.form['confirm']

            if username == "" or email == "" or \
               password == "" or confirm == "":
                return redirect(url_for('login'))

            if password != confirm:
                # Add template logic for invalid registration.
                return redirect(url_for('login'))

            user_exists = User.query.filter(
                                  User.uname == username
                                            ).scalar()

            if user_exists is None:
                salt = getsalt()
                passhash = createhash(salt, password)
                new_user = User(username, email, salt, passhash)
                db.session.add(new_user)
                db.session.commit()
                return render_template(
                                        'index.html',
                                        message='Registration successful'
                                      )
            else:
                message = 'Error account already exists'
                return render_template(
                                        'index.html',
                                        message=message
                                      )
        else:
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/submit_pairs', methods=['POST', 'GET'])
@login_required
def submit_pairs():

    if request.method == 'GET':
        return render_template('submit.html')

    post_params = request.form.to_dict()

    print("Post Params: " + str(post_params))

    hints = sorted(filter(lambda x: "hint_" in x, post_params))
    answers = sorted(filter(lambda x: "answer_" in x, post_params))
    themes = sorted(filter(lambda x: "theme_" in x, post_params))

    if len(hints) != len(answers) or len(hints) == 0:
        message = "Error: Invalid Request Arguments."
        return render_template('index.html', message=message)

    bad_pairs = list(filter(lambda x: x[0].split("_")[1] != x[1].split("_")[1],
                            zip(hints, answers)))

    if len(bad_pairs) > 0:
        message = "Error: Invalid Request Arguments."
        return render_template('index.html', message=message)

    report_template = """
        Successful Submissions {}\n
        Errored Submissions:\n{}
    """

    successes = 0

    failures = []

    for hint_key, answer_key in zip(hints, answers):
        hint = request.form[hint_key]
        answer = request.form[answer_key].upper()

        if len(answer) < min_hint_len:
            message = message_too_short.format(answer, min_hint_len)
            app.logger.error(message)
            return render_template(
                                    'index.html',
                                    message=message
                                  )

        if len(answer) > max_hint_len:
            message = message_too_long.format(answer, max_hint_len)
            app.logger.error(message)
            return render_template(
                                    'index.html',
                                    message=message
                                  )

        if not is_valid_answer(answer):
            message = message_nonalpha.format(answer)
            app.logger.error(message)
            return render_template(
                                    'index.html',
                                    message=message
                                  )

        if hint == '' or answer == '':
            message = "Error: Invalid Request Arguments."
            return render_template('index.html', message=message)

        pair_themes = list(filter(lambda x:
                                  x.split("_")[1] == hint_key.split("_")[1],
                                  themes
                                  )
                           )

        pair_themes = list(map(lambda x: request.form[x], pair_themes))

        # Unique the themes
        pair_themes = list(set(pair_themes))

        # print( "Pair Themes: " + str(pair_themes))

        pair_exists = HintAnswerPair.query.filter(
                                HintAnswerPair.hint == hint,
                                HintAnswerPair.answer == answer
                                                  ).scalar()

        if pair_exists is None:

            # Create the pair
            newPair = HintAnswerPair(
                                    answer, hint,
                                    session['uid']
                                    )
            db.session.add(newPair)
            db.session.commit()

            for theme in pair_themes:

                texists = Theme.query.filter_by(theme=theme).first()

                if texists:
                    tid = texists.tid
                else:

                    new_theme = Theme(theme)
                    db.session.add(new_theme)
                    db.session.commit()

                    tid = new_theme.tid

                new_hamap = HintAnswerThemeMap(newPair.haid, tid)
                db.session.add(new_hamap)
                db.session.commit()

            successes += 1
        else:

            # For now silently ignore
            failures.append("Hint " + str(hint) + " : Answer "
                            + str(answer) + " pair exists")

    filled_template = report_template.format(str(successes),
                                             "\n\n".join(failures))

    return render_template(
                            'index.html',
                            report=filled_template
                           )


@app.route("/browse_puzzles/", defaults={"page": 1})
@app.route("/browse_puzzles/page/<int:page>",
           methods=['GET', 'POST'])
@login_required
def browse_puzzles(page):

    query = (
        CrosswordPuzzle.query
                       .outerjoin(User, User.uid == CrosswordPuzzle.creator)
                       .outerjoin(UserPuzzleRatings,
                                  UserPuzzleRatings.cid == CrosswordPuzzle.cid)
                       .group_by(CrosswordPuzzle.cid)
                       .with_entities(func.avg(UserPuzzleRatings.rating)
                                      .label('rating'))
                       .add_columns(User.uname,
                                    CrosswordPuzzle.cid,
                                    CrosswordPuzzle.num_hints,
                                    CrosswordPuzzle.num_cells_down,
                                    CrosswordPuzzle.num_cells_across,
                                    CrosswordPuzzle.title,
                                    CrosswordPuzzle.creator)
    )

    paginated = query.paginate(page, 12)
    # http://flask-sqlalchemy.pocoo.org/2.1/api/#flask.ext.sqlalchemy.Pagination
    # https://www.reddit.com/r/flask/comments/3nsfr3/afflasksqlalchemy_pagination/
    # paginated = Table.query.filter(things==t, this==t).paginate(page, 10)
    # return render_template("mypage.html", paginated=paginated)
    # flask.ext.sqlalchemy.Pagination(query, page, per_page, total, items)
    # https://pythonguy.wordpress.com/category/sqlalchemy/
    if request.method == 'GET':
        return render_template('browse_puzzles.html', paginated=paginated)


@app.route("/themes", methods=['GET'])
@login_required
def themes():

    num_themes = int(request.args.get('num_themes', 0))

    if num_themes <= 0:
        return json.dumps({})

    # Prefix from the keyup even in the theme field
    prefix = request.args.get('prefix', "")

    if prefix != "":
        themes = Theme.query.filter(Theme.theme.like(prefix + "%")).all()
    else:
        themes = Theme.query.all()

    tdict = {}

    if len(themes) < num_themes:
        tdict = {
                    "themes": list(map(lambda x: x.theme, themes))
                }
    else:
        ts = list(map(lambda x: x.theme, themes))

        # Chose a num_themes random entries from the themes
        ts = random.sample(ts, num_themes)

        tdict = {
                    "themes": ts
                }

    return json.dumps(tdict)


@app.route("/suggests", methods=['POST'])
@login_required
def suggests():

    post_params = request.form.to_dict()

    num_suggests = 0
    if 'num_suggests' in post_params:
        num_suggests = int(post_params['num_suggests'])

    if num_suggests == 0:
        return json.dumps({})

    theme = ''
    if 'theme' in post_params:
        theme = post_params['theme']

    hints = []
    if 'hints' in post_params:
        hints = json.loads(post_params['hints'])

    answers = []
    if 'answers' in post_params:
        answers = json.loads(post_params['answers'])

    if theme != '':
        # Check if theme exists otherwise just return random
        # suggestions
        texists = Theme.query.filter_by(theme=theme).first()

        if not texists:
            return json.dumps({})

        tid = texists.tid

        # Get num suggests Hint/Answer pairs that match
        # the theme
        ids = set(map(lambda x: x[0],
                      HintAnswerThemeMap.query.with_entities(
                      HintAnswerThemeMap.haid).
                      filter_by(theme=tid)
                      )
                  )

        if hints != [] and answers != []:

            # Filter out pairs that are already selected to be
            # included in the puzzle
            sids = set(map(lambda x: x.haid,
                           HintAnswerPair.query.
                           filter(
                                  and_(
                                       not_(HintAnswerPair.hint.in_(hints)),
                                       not_(HintAnswerPair.answer.in_(answers))
                                       )
                                  )
                           )
                       )

            ids = ids.intersection(sids)

        if len(ids) >= num_suggests:
            samples = random.sample(ids, num_suggests)
        else:
            samples = ids
    else:
        # Could also add another get parameter to ensure that we do
        # not return hints we have already suggested

        ids = set(map(lambda x: x[0],
                      HintAnswerPair.query.with_entities(
                      HintAnswerPair.haid).all()
                      )
                  )

        if hints != [] and answers != []:

            # Filter out pairs that are already selected to be
            # included in the puzzle
            sids = set(map(lambda x: x.haid,
                           HintAnswerPair.query.
                           filter(
                                  and_(
                                       not_(HintAnswerPair.hint.in_(hints)),
                                       not_(HintAnswerPair.answer.in_(answers))
                                       )
                                  )
                           )
                       )

            ids = ids.intersection(sids)

        if len(ids) >= num_suggests:
            samples = random.sample(ids, num_suggests)
        else:
            samples = ids

    pairs = HintAnswerPair.query.filter(HintAnswerPair.haid.in_(samples))

    suggestions = []

    for pair in pairs:

        username = User.query.filter_by(uid=pair.author).first().uname

        suggestions.append(
            {
                "hint": pair.hint,
                "answer": pair.answer,
                "author": username,
            }
        )

    return json.dumps(suggestions)


@app.route("/create_puzzle", methods=['GET', 'POST'])
@login_required
def create_puzzle():

    if request.method == 'GET':

        # Initialize suggestions with 6 Hint/Answer pairs
        # randomly chosen from the Hint/Answer pair table

        ids = set(map(lambda x: x[0],
                      HintAnswerPair.query.with_entities(
                      HintAnswerPair.haid).all()
                      )
                  )

        if len(ids) >= 6:
            samples = random.sample(ids, 6)
        else:
            samples = ids

        if len(ids) == 0:
            return render_template(
                                   'index.html',
                                   message="No hint/answer pairs to create"
                                           " puzzle from. Please create them."
                                  )

        uid = HintAnswerPair.query[0].author
        username = User.query.filter_by(uid=uid).first().uname

        pairs = HintAnswerPair.query.filter(HintAnswerPair.haid.in_(samples))

        suggestions = []

        for pair in pairs:

            username = User.query.filter_by(uid=pair.author).first().uname

            suggestions.append(
                {
                    "hint": pair.hint,
                    "answer": pair.answer,
                    "author": username,
                }
            )

        return render_template('create_puzzle.html', suggestions=suggestions)

    if request.method == 'POST':
        post_params = request.form.to_dict()

        title = post_params.get('title', None)

        if title is None or title == "":
            message = "Error: Need to provide title for puzzle."
            return render_template('index.html', message=message)

        # Sort hints and answers to make sure listed in order
        # e.g. hint_1, hint_2, hint_3, rather that hint_2, hint_1, hint_3
        hint_keys = sorted(filter(lambda x: "hint_" in x, post_params))
        answer_keys = sorted(filter(lambda x: "answer_" in x, post_params))

        # Should respond with error if hints, answers lengths do not match
        if len(hint_keys) == 0:
            message = message_len_hint_keys
            app.logger.warning(message)
            return render_template('index.html', message=message)

        if len(hint_keys) != len(answer_keys):
            message = message_len_hint_answer_keys
            app.logger.warning(message)
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

            if len(answer) < min_hint_len:
                message = message_too_short.format(answer, min_hint_len)
                app.logger.error(message)
                return render_template(
                                        'index.html',
                                        message=message
                                      )
            if len(answer) > max_hint_len:
                message = message_too_long.format(answer, max_hint_len)
                app.logger.error(message)
                return render_template(
                                        'index.html',
                                        message=message
                                      )

            if not is_valid_answer(answer):
                message = message_nonalpha.format(answer)
                app.logger.error(message)
                return render_template(
                                        'index.html',
                                        message=message
                                      )

            app.logger.info("Hint: " + hint)
            app.logger.info("Answer: " + answer)

            if hint == '' or answer == '':
                message = "Error: Invalid Request Arguments."
                return render_template('index.html', message=message)

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

                app.logger.info("New Hint Answer Pair")

                # Add the hint/answer pair to the database
                new_pair = HintAnswerPair(answer, hint, session['uid'])
                db.session.add(new_pair)
                db.session.commit()
                hint_ids[pair] = new_pair.haid

        word_list = [x[0] for x in pairs]
        print("Word list: ", word_list)
        print("Pairs: ", pairs)

        new_puzzle = Crossword(max_xw_size, max_xw_size, "-", 5000, pairs)
        new_puzzle.compute_crossword(3)
        new_puzzle.order_number_words()

        print("Crossword Current Word List", new_puzzle.current_word_list)
        word_descriptions = {str(x).upper(): (x.row, x.col, x.down_across(),
                                              x.number)
                             for x in new_puzzle.current_word_list}
        print("Word descriptions", word_descriptions)

        if len(word_list) != len(word_descriptions):
            message = "Error: Could not place all words on the board."
            app.logger.error(message)
            return render_template('index.html', message=message)

        # Create the crossword puzzle
        creator = session['uid']

        puzzle = CrosswordPuzzle(len(pairs),
                                 max_xw_size,
                                 max_xw_size,
                                 title,
                                 creator)
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
        puzzle_id = session.get("puzzle_id", None)
        rating = int(request.form.get("rating", None))
        time = int(request.form.get("time", None))

        if not all((puzzle_id, rating, time)):
            return render_template(
                'play_puzzle.html', message='An error occured!', puzzleData={})

        del session['puzzle_id']
        user_id = session['uid']

        prev_time = UserPuzzleTimes.query.filter(
            UserPuzzleTimes.cid == puzzle_id,
            UserPuzzleTimes.uid == user_id
        ).scalar()

        if prev_time is not None:
            print(time, prev_time, prev_time.time)
            time = min(time, prev_time.time)

        db.session.merge(UserPuzzleTimes(puzzle_id, user_id, time))
        db.session.merge(UserPuzzleRatings(puzzle_id, session['uid'], rating))
        db.session.commit()

        return render_template(
            'play_puzzle.html', message='Time and rating submited!',
            puzzleData={}, leaderboard=[])

    # If a puzzle has not been selected, choose one at random
    try:
        selected_id = request.args.get('puzzle_id', random_puzzle_id())
    except IndexError:
        return render_template(
            'play_puzzle.html', message='No puzzles yet!', puzzleData={},
            leaderboard=[])

    raw_hints = (
        HintAnswerPair.query
        .join(PuzzleHintsMapTable)
        .add_columns(
            HintAnswerPair.hint,
            HintAnswerPair.answer,
            HintAnswerPair.author,
            PuzzleHintsMapTable.axis,
            PuzzleHintsMapTable.cell_across,
            PuzzleHintsMapTable.cell_down,
            PuzzleHintsMapTable.hint_num
        ).filter_by(cid=selected_id)
        .all()
    )
    if not raw_hints:
        return render_template(
            'play_puzzle.html', message='Puzzle not found!', puzzleData={},
            leaderboard=[])

    puzzle = CrosswordPuzzle.query.get(selected_id)

    def get_uname(uid):
        return User.query.filter_by(uid=uid).first().uname
    # lambda uid: User.query.filter_by(uid=puzzle.creator).first().uname

    # creator = User.query.filter_by(uid=puzzle.creator).first()
    # creator_username = creator.uname
    creator_username = get_uname(uid=puzzle.creator)

    # authors = User.query.filter_by(uid=puzzle.creator).first()
    # authors_string = 'ABC';
    author_uids = [hint.author for hint in raw_hints]
    author_unames = [get_uname(uid) for uid in author_uids]
    author_unique_unames = list(set(author_unames))

    # print('Author UIDs')
    # print(author_uids)

    # print('Author unames')
    # print(author_unames)

    # print('Unique Authors')
    # print(author_unique_unames)

    def fmt(x):
        return ', '.join(x[:-1]) + ', and ' + x[-1]

    # f = lambda x: ', '.join(x[:-1]) + ', and ' + x[-1]

    if 1 == len(author_unique_unames):
        authors_string = author_unique_unames[0]
    elif 2 == len(author_unique_unames):
        authors_string = author_unique_unames[0] + ' and ' + \
                         author_unique_unames[1]
    else:
        authors_string = fmt(author_unique_unames)

    puzzleData = {
        'title': puzzle.title,
        'creator': creator_username,
        'authors': authors_string,
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

    raw_leaderboard = (
        UserPuzzleTimes.query
        .join(User)
        .add_columns(
            User.uname,
            UserPuzzleTimes.time
        )
        .filter(UserPuzzleTimes.cid == selected_id)
        .order_by(UserPuzzleTimes.time)
        .limit(10)
    )

    leaderboard = [{'username': entry.uname, 'time': entry.time}
                   for entry in raw_leaderboard]

    session['puzzle_id'] = selected_id
    return render_template('play_puzzle.html', puzzleData=puzzleData,
                           leaderboard=leaderboard)
