# flask/bin/python
from app import app
from app.db import init_db

import logging
from logging.handlers import RotatingFileHandler

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

init_db()

# create formatter
fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fmt)

handler = RotatingFileHandler('xword.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

app.run(debug=True)
