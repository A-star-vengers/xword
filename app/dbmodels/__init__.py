from app.db import db
from app import app # flake8: noqa

class User(db.Model):
    """Class to represent the Users table.  This table
       contains all user data in the application.     
       UID | Username | Password | IsAdmin"""
    __tablename__ = "user"
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

class State(db.Model):
    """Class to represent the State table. This table
       contains the current state value for a particular user
    """
    __tablename__ = "state"
    sid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uname = db.Column(db.String(45), db.ForeignKey("user.uname", onupdate="cascade"), nullable=False)
    state = db.Column(db.String(255), unique=False)

    def __init__(self, uname, state):
        self.uname = uname
        self.state = state
