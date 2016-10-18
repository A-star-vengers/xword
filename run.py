#!flask/bin/python
from app import app
from app.db import init_db

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

init_db()

app.run(debug=True)
