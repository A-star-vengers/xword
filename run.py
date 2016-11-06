#flask/bin/python
from app import app
from app.db import init_db

import logging
from logging.handlers import RotatingFileHandler

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

init_db()

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = RotatingFileHandler('xword.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

app.run(debug=True)
