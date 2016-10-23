import random


def check_word_index_conformability(word_to_place, start_ind, end_ind):
    assert 2 == len(start_ind) and 2 == len(end_ind), "indices should be 2 element lists"

    vert_dim = end_ind[1] - start_ind[1]
    horz_dim = end_ind[0] - start_ind[0]

    assert 0 <= vert_dim and 0 <= horz_dim, "need for end_ind >= start_ind"

    is_horz = 0 == horz_dim
    is_vert = 0 == vert_dim
    assert is_horz or is_vert, "one of the dimensions should match"

    word_size = vert_dim + horz_dim
    assert len(word_to_place) == word_size, "location to place should match dimensions of word to be placed"


def enumerate_indices_between(startpoint, endpoint):
    vert_dim = endpoint[1] - startpoint[1]
    horz_dim = endpoint[0] - startpoint[0]

    word_size = vert_dim + horz_dim
    indices_between = [None] * word_size

    for idx in range(word_size):
        w = idx / word_size
        r = round(startpoint[0] * (1 - w) + endpoint[0] * w) # round may be a bit fragile, better to do this with int sequences
        c = round(startpoint[1] * (1 - w) + endpoint[1] * w)
        indices_between[idx] = [r, c]
    return indices_between


def place_word_on_grid(word_to_place, start_ind, end_ind, grid):
    letters = grid["letters"]
    is_filled = grid["is_filled"]
    indices_between = enumerate_indices_between(start_ind, end_ind)

    for counter, ind in enumerate(indices_between):
        idx0 = ind[0]
        idx1 = ind[1]
        letters[idx0][idx1] = word_to_place[counter]
        is_filled[idx0][idx1] = True

    out = dict(letters=letters, is_filled=is_filled)
    return out


def check_word_is_placeable(word_to_place, start_ind, end_ind, grid):
    check_word_index_conformability(word_to_place, start_ind, end_ind)
    letters = grid["letters"]
    is_filled = grid["is_filled"]
    indices_between = enumerate_indices_between(start_ind, end_ind)
    is_placeable_index = [True] * len(indices_between)

    for counter, ind in enumerate(indices_between):
        idx0 = ind[0]
        idx1 = ind[1]
        is_placeable_index[counter] = (not is_filled[idx0][idx1]) or (letters[idx0][idx1] == word_to_place[counter])

    return all(is_placeable_index)


def update_grid_with_placed_word(word, startpoint, orientation, grid):
    # print_grid(grid)
    endpoint = get_word_endpoint(word, startpoint, orientation)
    assert check_word_is_placeable(word, startpoint, endpoint, grid), "Should not be overriding letter"
    return place_word_on_grid(word, startpoint, endpoint, grid)


def print_grid(grid):
    letters = grid["letters"]
    is_filled = grid["is_filled"]

    d0 = len(letters)
    d1 = len(letters[0])

    assert len(is_filled) == d0, "first dimension mismatch"
    assert len(is_filled[0]) == d1, "second dimension mismatch"

    for dim0 in range(d0):
        for dim1 in range(d1):
            if is_filled[dim0][dim1]:
                print(letters[dim0][dim1], end="")
            else:
                print('.', end="")
        print('\n')


def get_word_endpoint(word, startpoint, orientation):
    word_len = len(word)
    assert ("vertical" == orientation) or ("horizontal" == orientation), "unknown orientation"
    if "vertical" == orientation:
        endpoint = [startpoint[0] + word_len, startpoint[1]]
    else:
        endpoint = [startpoint[0], startpoint[1] + word_len]
    return endpoint


def get_random_start_point(grid):
    is_filled = grid["is_filled"]
    d0 = len(is_filled)
    d1 = len(is_filled[0])
    proposal = [random.randrange(0, d0), random.randrange(0, d1)]
    return proposal

def find_open_location_for_word_no_clashes(grid, word):
    max_tries = 100
    tries = 0

    while True:
        location = find_open_location_for_word(grid, word)
        startpoint = location["point"]
        endpoint = get_word_endpoint(word, startpoint, location["orientation"])
        is_done = check_word_is_placeable(word, startpoint, endpoint, grid)

        if is_done:
            break
        tries = tries + 1
        assert tries < max_tries, "finding an open location is not working"

    startpoint = location["point"]
    endpoint = get_word_endpoint(word, startpoint, location["orientation"])
    assert check_word_is_placeable(word, startpoint, endpoint, grid), "Should not be overriding letter"
    return location

def find_open_location_for_word(grid, word): # just guarantees that the endpoint lies on the board
    is_filled = grid["is_filled"]
    d0 = len(is_filled)
    d1 = len(is_filled[0])
    max_tries = 100
    tries = 0

    while True:
        random_start_point = get_random_start_point(grid)
        random_orientation = "vertical" if bool(random.getrandbits(1)) else "horizontal"
        random_end_point = get_word_endpoint(word, random_start_point, random_orientation)
        is_open = (random_end_point[0] <= d0) and (random_end_point[1] <= d1)
        if is_open:
            break
        tries = tries + 1
        assert tries < max_tries, "finding an open location is not working"

    return dict(point=random_start_point, orientation=random_orientation)


def is_overlap_with_grid(word, grid, startpoint, endpoint):
    indices_bewteen = enumerate_indices_between(startpoint, endpoint)
    word_len = len(word)
    assert len(indices_bewteen) == word_len, "word does not fit endpoints"
    is_overlap = [0] * word_len
    letters = grid["letters"]
    is_filled = grid["is_filled"]

    for counter, point in enumerate(indices_bewteen):
        d0 = point[0]
        d1 = point[1]
        if is_filled[d0][d1] and (word[counter] == letters[d0][d1]):
            is_overlap[counter] = 1
    return is_overlap


def total_overlap_with_grid(word, grid, startpoint, orientation):
    endpoint = get_word_endpoint(word, startpoint, orientation)
    return sum(is_overlap_with_grid(word, grid, startpoint, endpoint))


# stackoverflow.com/questions/16945518/python-argmin-argmax-finding-the-index-of-the-value-which-is-the-min-or-max
def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]

def initialise_answers(word_list):
    assert len(word_list) == len(set(word_list)), "Duplicate answers not supported"

    num_word = len(word_list)
    xcoord = [None] * num_word
    ycoord = [None] * num_word
    orientation = [None] * num_word
    is_placed = [False] * num_word

    return dict(words=word_list,
                index=range(num_word),
                xcoord=xcoord,
                ycoord=ycoord,
                orientation=orientation,
                is_placed=is_placed)


def get_unplaced_words(answers):
    unplaced_words = [word for index, word in enumerate(answers["words"]) if not answers["is_placed"][index]]
    return unplaced_words


def get_tryable_words(answers, is_tryable):
    tryable_words = [word for index, word in enumerate(answers["words"]) if (not answers["is_placed"][index] and is_tryable[index])]
    return tryable_words


def initialise_board_for_answers(grid_width, grid_height, answers):
    longest_word = max(answers["words"], key=len)
    longest_word_len = len(longest_word)
    assert min(grid_width, grid_height) >= longest_word_len, "both board dimensions should exceed longest word length"
    letters = [[0 for x in range(grid_width)] for y in range(grid_height)]
    is_filled = [[False for x in range(grid_width)] for y in range(grid_height)]
    grid = dict(letters=letters, is_filled=is_filled)
    return grid


def update_answers_with_placed_word(word, start_ind, orientation, answers):
    index = answers["words"].index(word)
    answers["xcoord"][index] = start_ind[0]
    answers["ycoord"][index] = start_ind[1]
    answers["orientation"][index] = orientation
    answers["is_placed"][index] = True

    return answers


def place_word(grid, answers):

    if all(answers["is_placed"]):
        was_placed = False
    elif not any(answers["is_placed"]):
        word = max(answers["words"], key=len)
        fw = place_first_word(grid, word)
        start_ind = fw["start_ind"]
        orientation = fw["orientation"]
        was_placed = fw["was_placed"]
    else:
        is_tryable = [not x for x in answers["is_placed"]]

        while any(is_tryable):
            word = max(get_tryable_words(answers, is_tryable), key=len)

            sw = place_subsequent_word(grid, word)
            start_ind = sw["start_ind"]
            orientation = sw["orientation"]
            was_placed = sw["was_placed"]

            if was_placed:
                break
            else:
                is_tryable[answers["words"].index(word)] = False

    if was_placed:
        grid = update_grid_with_placed_word(word, start_ind, orientation, grid)
        answers = update_answers_with_placed_word(word, start_ind, orientation, answers)

    out = dict(grid=grid, answers=answers, was_placed=was_placed)
    return out


def place_first_word(grid, word):
    # place the longest word by hand first, roughly in the middle of the grid
    letters = grid["letters"]
    d0 = len(letters)
    d1 = len(letters[0])
    longest_word_len = len(word)

    row = int(d0 / 2)
    col = int((d1 - longest_word_len) / 2) - 1

    start_ind = [row, col]
    orientation = "horizontal"
    was_placed = True
    return dict(start_ind=start_ind, orientation=orientation, was_placed=was_placed)


def place_subsequent_word(grid, word):
    max_tries = 500
    potential_starts = [None] * max_tries
    overlaps = [0] * max_tries
    for idx in range(max_tries): # idx = 2
        potential_starts[idx] = find_open_location_for_word_no_clashes(grid, word)
        startpoint = potential_starts[idx]["point"]
        orientation = potential_starts[idx]["orientation"]

        if True:
            endpoint = get_word_endpoint(word, startpoint, orientation)
            assert check_word_is_placeable(word, startpoint, endpoint, grid), "Violation"

        overlaps[idx] = total_overlap_with_grid(word, grid, startpoint, orientation)

    am = argmax(overlaps)
    tot = overlaps[am]
    if 0 == tot:
        start_ind = None
        orientation = None
        was_placed = False
    else:
        start_ind = potential_starts[am]["point"]
        orientation = potential_starts[am]["orientation"]
        was_placed = True

    return dict(start_ind=start_ind, orientation=orientation, was_placed=was_placed)


if __name__ == "__main__":
    random.seed(0)

    iters = 5 # number of times to pass through
    grid_width = 21
    grid_height = 15

    # Word list from: http://bryanhelmig.com/python-crossword-puzzle-generator/
    # word_list = ['saffron', 'pumpernickel', 'leaven', 'coda', 'paladin', 'syncopation', 'albatross', 'harp', 'piston',
    #             'caramel', 'coral', 'dawn', 'pitch', 'fjord', 'lip', 'lime', 'mist', 'plague', 'yarn', 'snicker']

    word_list = ['saffron', 'pumpernickel', 'leaven', 'coda', 'syncopation', 'albatross', 'harp', 'piston']

    answers = initialise_answers(word_list)
    grid = initialise_board_for_answers(grid_width, grid_height, answers)


    while True:
        out = place_word(grid, answers)
        grid = out["grid"]
        print_grid(grid)
        answers = out["answers"]
        was_placed = out["was_placed"]
        if not was_placed:
            break

    print_grid(grid)


        # word_to_place = longest_word
    # start_ind = [row, left_margin]
    # end_ind = [row, left_margin + longest_word_len]
    # grid = update_grid_with_placed_word(word_to_place, start_ind, end_ind, grid)
    # placed_word = word_to_place
    #
    # remaining_word_set.remove(placed_word)
    #
    # remaining_word_set_next = set([])
    #
    # for iter in range(iters):
    #     num_remaining = len(remaining_word_set)
    #
    #     while len(remaining_word_set) > 0:
    #         word = max(remaining_word_set, key=len)
    #         back = try_to_place_word(word, grid)
    #         grid = back["grid"]
    #         was_placed = back["was_placed"]
    #
    #         remaining_word_set.remove(word)
    #
    #         if was_placed:
    #             remaining_word_set_next.add(word)
    #     num_placed = num_remaining - len(remaining_word_set_next)
    #     print("Placed {0} words in iteration {1}".format(num_placed, iter))
    #     print("Remaining words")
    #     print(remaining_word_set_next)
    #     remaining_word_set = remaining_word_set_next
    #     remaining_word_set_next = set([])


# 1. Create a grid of whatever size and a list of words.
# 2. Shuffle the word list, and then sort the words by longest to shortest.
# 3. Place the first and longest word at the upper left most position, 1,1 (vertical or horizontal).
# 4. Move onto next word, loop over each letter in the word and each cell in the grid looking for letter to letter matches.
# 5. When a match is found, simply add that position to a suggested coordinate list for that word.
# 6. Loop over the suggested coordinate list and "score" the word placement based on how many other words it crosses.
#    Scores of 0 indicate either bad placement (adjacent to existing words) or that there were no word crosses.
# 7. Back to step #4 until word list is exhausted. Optional second pass.
# 8. We should now have a crossword, but the quality can be hit or miss due to some of the random placements. So, we
#    buffer this crossword and go back to step #2. If the next crossword has more words placed on the board, it replaces
#    the crossword in the buffer. This is time limited (find the best crossword in x seconds).
