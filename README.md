# xword

cs4156 course project


xword is a social crossword web application that will challenge players to solve puzzles of different 
difficulties and show them how they fare against other players. 


team a-start-vengers: arc2205@columbia.edu
                      bm2787@columbia.edu
                      km3227@columbia.edu
                      vr2262@columbia.edu

Main task board:
https://trello.com/b/j1ojqHO0/xword-board

Build status:
https://travis-ci.org/A-star-vengers/xword

Contained in this repo is the code for the xword app, written in Python (3.4) using the flask framework. 

See the Travis CI link above for more information, but we anticipate that something like this should 
comprise a canonical run:

git clone https://github.com/A-star-vengers/xword.git
cd xword
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run.py

(open http://127.0.0.1:5000/, or whatever address is shown in the terminal into your favourite web browser).

The layout follows what seems to be the convention for flask: 
  * util -- contains utilities around demoing the app
  * app/views.py -- is the main entry point for the front end logic
  * app/util.py -- contains some utilities used across 'views.py'
  * app/statics -- houses static resources
  * app/templates -- contains the jinja2 templates for the pages in our app
  * app/app.cfg -- contains the configuration for the app
  * app/dbmodels/__init__.py -- initialises the databases
  * app/puzzle/crossword.py -- the engine for generating the crossword puzzle (a cleaned up version of http://bryanhelmig.com/python-crossword-puzzle-generator/)
  
  
  
