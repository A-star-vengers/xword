"""
    From http://bryanhelmig.com/python-crossword-puzzle-generator/
    Released under a BSD license according to web site.
"""

import random
import re
import time
from copy import copy as duplicate


class Crossword(object):
    def __init__(self, cols, rows, empty='-', maxloops=2000,
                 available_words=[]):
        self.cols = cols
        self.rows = rows
        self.empty = empty
        self.maxloops = maxloops
        self.available_words = available_words
        self.randomize_word_list()
        self.current_word_list = []
        self.debug = 0
        self.clear_grid()

    def clear_grid(self):  # initialize grid and fill with empty character
        self.grid = []
        for i in range(self.rows):
            ea_row = []
            for j in range(self.cols):
                ea_row.append(self.empty)
            self.grid.append(ea_row)

    def randomize_word_list(self):  # also resets words and sorts by length
        temp_list = []
        for word in self.available_words:
            if isinstance(word, Word):
                temp_list.append(Word(word.word, word.clue))
            else:
                temp_list.append(Word(word[0], word[1]))
        random.shuffle(temp_list)  # randomize word list
        temp_list.sort(key=lambda i: len(i.word), reverse=True)  # sort by len
        self.available_words = temp_list

    def compute_crossword(self, time_permitted=1.00, spins=2):
        time_permitted = float(time_permitted)
        count = 0
        copy = Crossword(self.cols, self.rows,
                         self.empty, self.maxloops, self.available_words)
        start_full = float(time.time())
        while (float(time.time()) - start_full) < time_permitted \
                or count == 0:  # only run for x seconds
            self.debug += 1
            copy.current_word_list = []
            copy.clear_grid()
            copy.randomize_word_list()
            x = 0
            while x < spins:  # spins; 2 seems to be plenty
                for word in copy.available_words:
                    if word not in copy.current_word_list:
                        copy.fit_and_add(word)
                x += 1
            # buffer the best crossword by comparing placed words
            if len(copy.current_word_list) > len(self.current_word_list):
                self.current_word_list = copy.current_word_list
                self.grid = copy.grid
            count += 1
        return

    def suggest_coord(self, word):
        coordlist = []
        glc = -1
        for given_letter in word.word:  # cycle through letters in word
            glc += 1
            rowc = 0
            for row in self.grid:  # cycle through rows
                rowc += 1
                colc = 0
                for cell in row:  # cycle through  letters in rows
                    colc += 1
                    # check match letter in word to letters in row
                    if given_letter == cell:
                        try:  # suggest vertical placement
                            # don't suggest a start point off the grid
                            if rowc - glc > 0:
                                # make sure word doesn't go off of grid
                                if ((rowc - glc) + word.length) <= self.rows:
                                    toappend = [colc, rowc - glc, 1,
                                                colc + (rowc - glc), 0]
                                    coordlist.append(toappend)
                        except:
                            pass
                        try:  # suggest horizontal placement
                            # don't suggest a start point off the grid
                            if colc - glc > 0:
                                # make sure word doesn't go off of grid
                                if ((colc - glc) + word.length) <= self.cols:
                                    toappend = [colc - glc, rowc, 0,
                                                rowc + (colc - glc), 0]
                                    coordlist.append(toappend)
                        except:
                            pass
        new_coordlist = self.sort_coordlist(coordlist, word)
        return new_coordlist

    def sort_coordlist(self, coordlist, word):  # score coordinates, then sort
        new_coordlist = []
        for coord in coordlist:
            col, row, vertical = coord[0], coord[1], coord[2]
            coord[4] = self.check_fit_score(col, row, vertical, word)
            if coord[4]:  # 0 scores are filtered
                new_coordlist.append(coord)
        random.shuffle(new_coordlist)  # randomize coord list; why not?
        # put the best scores first
        new_coordlist.sort(key=lambda i: i[4], reverse=True)
        return new_coordlist

    def fit_and_add(self, word):
        # doesn't check fit except for the first word;
        # otherwise just adds if score is good
        fit = False
        count = 0
        coordlist = self.suggest_coord(word)
        while not fit and count < self.maxloops:
            # this is the first word: the seed
            if len(self.current_word_list) == 0:
                # top left seed of longest word yields best results
                vertical, col, row = random.randrange(0, 2), 1, 1
                if self.check_fit_score(col, row, vertical, word):
                    fit = True
                    self.set_word(col, row, vertical, word, force=True)
            else:  # a subsequent words have scores calculated
                try:
                    col = coordlist[count][0]
                    row = coordlist[count][1]
                    vertical = coordlist[count][2]
                except IndexError:
                    return  # no more cordinates, stop trying to fit
                # already filtered these out, but double check
                if coordlist[count][4]:
                    fit = True
                    self.set_word(col, row, vertical, word, force=True)
            count += 1
        return

    def check_fit_score(self, col, row, vertical, word):
        """
        And return score (0 signifies no fit). 1 means a fit, 2+ means a cross.
        The more crosses the better.
        """
        if col < 1 or row < 1:
            return 0
        # score: standard value of 1, override with 0 if collisions detected
        count, score = 1, 1
        for letter in word.word:
            try:
                active_cell = self.get_cell(col, row)
            except IndexError:
                return 0
            if active_cell == self.empty or active_cell == letter:
                pass
            else:
                return 0
            if active_cell == letter:
                score += 1
            if vertical:
                # check surroundings

                # don't check surroundings if cross point
                if active_cell != letter:
                    # check right cell
                    if not self.check_if_cell_clear(col+1, row):
                        return 0
                    # check left cell
                    if not self.check_if_cell_clear(col-1, row):
                        return 0
                if count == 1:  # check top cell only on first letter
                    if not self.check_if_cell_clear(col, row-1):
                        return 0
                # check bottom cell only on last letter
                if count == len(word.word):
                    if not self.check_if_cell_clear(col, row+1):
                        return 0
            else:  # else horizontal
                # check surroundings

                # don't check surroundings if cross point
                if active_cell != letter:
                    # check top cell
                    if not self.check_if_cell_clear(col, row-1):
                        return 0
                    # check bottom cell
                    if not self.check_if_cell_clear(col, row+1):
                        return 0
                if count == 1:  # check left cell only on first letter
                    if not self.check_if_cell_clear(col-1, row):
                        return 0
                # check right cell only on last letter
                if count == len(word.word):
                    if not self.check_if_cell_clear(col+1, row):
                        return 0
            if vertical:  # progress to next letter and position
                row += 1
            else:  # else horizontal
                col += 1
            count += 1
        return score

    # also adds word to word list
    def set_word(self, col, row, vertical, word, force=False):
        if force:
            word.col = col
            word.row = row
            word.vertical = vertical
            self.current_word_list.append(word)
            for letter in word.word:
                self.set_cell(col, row, letter)
                if vertical:
                    row += 1
                else:
                    col += 1
        return

    def set_cell(self, col, row, value):
        self.grid[row-1][col-1] = value

    def get_cell(self, col, row):
        return self.grid[row-1][col-1]

    def check_if_cell_clear(self, col, row):
        try:
            cell = self.get_cell(col, row)
            if cell == self.empty:
                return True
        except IndexError:
            pass
        return False

    def solution(self):  # return solution grid
        out_str = ""
        for r in range(self.rows):
            for c in self.grid[r]:
                out_str += '%s ' % c
            out_str += '\n'
        return out_str

    def word_find(self):  # return solution grid
        out_str = ""
        for r in range(self.rows):
            for c in self.grid[r]:
                out_str += '%s ' % c
            out_str += '\n'
        return out_str

    # orders words and applies numbering system to them
    def order_number_words(self):
        self.current_word_list.sort(key=lambda i: (i.col + i.row))
        count, icount = 1, 1
        for word in self.current_word_list:
            word.number = count
            if icount < len(self.current_word_list):
                if word.col == self.current_word_list[icount].col \
                        and word.row == self.current_word_list[icount].row:
                    pass
                else:
                    count += 1
            icount += 1

    # the grid with numbers not words (and order/number wordlist)
    def display(self, order=True):
        out_str = ""
        if order:
            self.order_number_words()
        copy = self
        for word in self.current_word_list:
            copy.set_cell(word.col, word.row, word.number)
        for r in range(copy.rows):
            for c in copy.grid[r]:
                out_str += '%s ' % c
            out_str += '\n'
        out_str = re.sub(r'[a-z]', ' ', out_str)
        return out_str

    def word_bank(self):
        out_str = ''
        temp_list = duplicate(self.current_word_list)
        random.shuffle(temp_list)  # randomize word list
        for word in temp_list:
            out_str += '%s\n' % word.word
        return out_str

    def legend(self):  # must order first
        out_str = ''
        for w in self.current_word_list:
            out_str += '%d. (%d,%d) %s: %s\n' % \
                       (w.number, w.col, w.row, w.down_across(), w.clue)
        return out_str


class Word(object):
    def __init__(self, word=None, clue=None):
        self.word = re.sub(r'\s', '', word.lower())
        self.clue = clue
        self.length = len(self.word)
        # the below are set when placed on board
        self.row = None
        self.col = None
        self.vertical = None
        self.number = None

    def down_across(self):  # return down or across
        if self.vertical:
            return 'down'
        else:
            return 'across'

    def __repr__(self):
        return self.word

# end class, start execution
# start_full = float(time.time())

if __name__ == "__main__":
    word_list = ['saffron',
                 'The dried, orange yellow plant used also' +
                 ' as dye and as a cooking spice.'], \
                ['pumpernickel',
                 'Dark, sour bread made from coarse ground rye.'], \
                ['leaven',
                 'An agent, such as yeast, that cause batter ' +
                 'or dough to rise.'], \
                ['coda',
                 'Musical conclusion of a movement or composition.'], \
                ['paladin', 'A heroic champion or paragon of chivalry.'], \
                ['syncopation',
                 'Shifting the emphasis of a beat to ' +
                 'the normally weak beat.'], \
                ['albatross',
                 'A large bird of the ocean having a hooked beak ' +
                 'and long, narrow wings.'], \
                ['harp',
                 'Musical instrument with 46 or more open ' +
                 'strings played by plucking.'], \
                ['piston',
                 'A solid cylinder or disk that fits snugly in ' +
                 'a larger cylinder and moves under pressure as ' +
                 'in an engine.'], \
                ['caramel',
                 'A smooth chery candy made from sugar, butter, ' +
                 'cream or milk with flavoring.'], \
                ['coral', 'A rock-like deposit of organism skeletons ' +
                 'that make up reefs.'], \
                ['dawn',
                 'The time of each morning at which daylight begins.'], \
                ['pitch',
                 'A resin derived from the sap of various pine trees.'], \
                ['fjord',
                 'A long, narrow, deep inlet of the sea between ' +
                 'steep slopes.'], \
                ['lip',
                 'Either of two fleshy folds surrounding the mouth.'], \
                ['lime',
                 'The egg-shaped citrus fruit having a green ' +
                 'coloring and acidic juice.'], \
                ['mist',
                 'A mass of fine water droplets in the air near ' +
                 'or in contact with the ground.'], \
                ['plague',
                 'A widespread affliction or calamity.'], \
                ['yarn',
                 'A strand of twisted threads or a long elaborate' +
                 ' narrative.'], \
                ['snicker',
                 'A snide, slightly stifled laugh.']

    a = Crossword(30, 30, '-', 5000, word_list)
    a.compute_crossword(2)
    print(a.word_bank())
    print(a.solution())
    print(a.word_find())
    print(a.display())
    print(a.legend())
    print(len(a.current_word_list), 'out of', len(word_list), 'placed')
    print(a.debug)
    cwl = a.current_word_list
    tmp = map(lambda x: (str(x), x.row, x.col, x.down_across()), cwl)
    print(list(tmp))
