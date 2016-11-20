from app.db import db
from app import app # flake8: noqa

class User(db.Model):
    """Class to represent the Users table.  This table
       contains all user data in the application.     
       UID | Username | Password | IsAdmin"""
    __tablename__ = "user"
    __table_args__ = {'sqlite_autoincrement' : True}

    uid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    uname = db.Column(db.String(45), unique=True)
    #Allow more than one account with the same email
    #Also max out email length at 255 characters
    email = db.Column(db.String(255), unique=False)
    salt = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(128), unique=False)

    def __init__(self, uname, email, salt, password):
        self.uname = uname
        self.email = email
        self.salt = salt
        self.password = password

class XwordSourceSite(db.Model):
    """Class to contain third party crossword source that can be used to assign
       as source of a given hint/answer pair."""
    __tablename__ = "xword_source"
    __table_args__ = {'sqlite_autoincrement' : True}

    xid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    wsite = db.Column(db.String(100), unique=True)

    def __init__(self, wsite):
        self.wsite = wsite

class Theme(db.Model):
    """Class to contain list of themes of which hint/answer pairs are optionally
       assigned to."""
    __tablename__ = "theme"
    __table_args__ = {'sqlite_autoincrement' : True}

    tid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    theme = db.Column(db.String(20), unique=True)

    def __init__(self, theme):
        self.theme = theme

class HintAnswerThemeMap(db.Model):
    """Class to represent the relationship between a hint/answer pair
       and its corresponding theme. This table can be used to query
       for suggestions of hint/answer pairs with similar themes.
    """
    __tablename__ = "theme_map"
    __table_args__ = {'sqlite_autoincrement' : True}

    tmap_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    haid = db.Column(db.Integer, db.ForeignKey("pairs.haid"), nullable=False)
    theme = db.Column(db.Integer, db.ForeignKey("theme.tid"))

    def __init__(self, haid, theme):
        self.haid = haid
        self.theme = theme

class HintAnswerPair(db.Model):
    """Class to represent the Hint/Answer pairs. These pairs are used
       in the construction of new crossword puzzles"""
    __tablename__ = "pairs"
    __table_args__ = {'sqlite_autoincrement' : True}

    haid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    answer = db.Column(db.String(32), unique=False)
    hint = db.Column(db.String(100), unique=False)
    author = db.Column(db.Integer, db.ForeignKey("user.uid"), nullable=True)

    def __init__(self, answer, hint, author):
        self.answer = answer
        self.hint = hint
        self.author = author

class PuzzleHintsMapTable(db.Model):
    """Class to represent the container relationship between the crossword puzzle and a list
       of hint/answer pairs used to create the puzzle."""
    __tablename__ = "puzzle_hint_map"
    __table_args__ = {'sqlite_autoincrement' : True}

    # Contain the crossword id foreign key to use to map a crossword puzzle to a list of hints
    cid = db.Column(db.Integer, db.ForeignKey("crosswords.cid"), primary_key=True)
    haid = db.Column(db.Integer, db.ForeignKey("pairs.haid"), primary_key=True)
    # Number of hint in puzzle, e.g. 1 in 1 Across
    hint_num = db.Column(db.Integer)
    # Down vs Across
    axis = db.Column(db.String(6))
    # Start cell for the first letter of the hint
    cell_across = db.Column(db.Integer)
    cell_down = db.Column(db.Integer)

    def __init__(self, cid, haid, hint_num, axis, cell_across, cell_down):
        self.cid = cid
        self.haid = haid
        self.hint_num = hint_num
        self.axis = axis
        self.cell_across = cell_across
        self.cell_down = cell_down

class UserPuzzleTimes(db.Model):
    """Class to contain the relation between user, puzzle, and time
       it took the user to complete the puzzle.
    """
    __tablename__ = "puzzle_times"
    __table_args__ = {'sqlite_autoincrement' : True}

    cid = db.Column(db.Integer, db.ForeignKey("crosswords.cid"), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.uid"), primary_key=True)
    time = db.Column(db.DateTime, unique=False)

    def __init__(self, cid, uid, time):
        self.cid = cid
        self.uid = uid
        self.time = time

class UserPuzzleRatings(db.Model):
    """Class to represent the relation between user, puzzle, and the rating
       the user gave the puzzle after completing it.
    """
    __tablename__ = "puzzle_ratings"
    __table_args__ = {'sqlite_autoincrement' : True}

    cid = db.Column(db.Integer, db.ForeignKey("crosswords.cid"), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.uid"), primary_key=True)

    # Rating should be between 0 and 5
    rating = db.Column(db.Integer, unique=False)

    def __init__(self, cid, uid, rating):
        self.cid = cid
        self.uid = uid
        self.rating = rating

class UserCreatedPuzzles(db.Model):
    """Class to represent the relation between a user and a crossword puzzle he or she
       has created.
    """
    __tablename__ = "user_puzzles"
    __table_args__ = {'sqlite_autoincrement' : True}

    # More than one user should not be able to construct the same puzzle
    cid = db.Column(db.Integer, db.ForeignKey("crosswords.cid"), primary_key=True, unique=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.uid"), unique=False)

    def __init__(self, cid, uid):

        self.cid = cid
        self.uid = uid

class CrosswordPuzzle(db.Model):
    """Class to represent a crossword puzzle that has been completed at least once
       by a user. It will contain relationships that describe the layout, hints/answer
       pairs used to construct the puzzle, the ratings from users, and the ranking compared
       to other crossword puzzles"""
    __tablename__ = "crosswords"
    __table_args__ = {'sqlite_autoincrement' : True}

    cid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    #Number of hints in the puzzle
    num_hints = db.Column(db.Integer)
    #Number of cells vertically in the puzzle
    num_cells_down = db.Column(db.Integer)
    #Number of cells horizontally in the puzzle
    num_cells_across = db.Column(db.Integer)
    title = db.Column(db.String(32), unique=False)

    def __init__(self, num_hints, num_cells_down, num_cells_across, title):
        self.num_hints = num_hints
        self.num_cells_down = num_cells_down
        self.num_cells_across = num_cells_across
        self.title = title
