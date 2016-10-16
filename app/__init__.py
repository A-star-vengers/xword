from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
from app import views # flake8: noqa
