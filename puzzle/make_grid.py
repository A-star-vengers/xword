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


def place_word(word_to_place, start_ind, end_ind, grid):
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


def place_word_safe(word_to_place, startpoint, endpoint, grid):
    print_grid(grid)
    assert check_word_is_placeable(word_to_place, startpoint, endpoint, grid), "Should not be overriding letter"
    return place_word(word_to_place, startpoint, endpoint, grid)


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


def get_random_unfilled_point(grid):
    is_filled = grid["is_filled"]

    d1 = len(is_filled)
    d2 = len(is_filled[0])
    done = False
    while not done:
        proposal = [random.randrange(0, d1), random.randrange(0, d2)]
        done = not is_filled[proposal[0]][proposal[1]]
    return proposal


def find_open_location_for_word(grid, word):
    is_filled = grid["is_filled"]
    d0 = len(is_filled)
    d1 = len(is_filled[0])

    is_open = False

    while not is_open:
        random_unfilled_start_point = get_random_unfilled_point(grid)
        random_orientation = "vertical" if bool(random.getrandbits(1)) else "horizontal"
        random_unfilled_end_point = get_word_endpoint(word, random_unfilled_start_point, random_orientation)
        is_open = (random_unfilled_end_point[0] <= d0) and (random_unfilled_end_point[1] <= d1)

    return dict(point=random_unfilled_start_point, orientation=random_orientation)


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


def total_overlap_with_grid(word, grid, startpoint, endpoint):
    return sum(is_overlap_with_grid(word, grid, startpoint, endpoint))


# stackoverflow.com/questions/16945518/python-argmin-argmax-finding-the-index-of-the-value-which-is-the-min-or-max
def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]


def try_to_place_word(word, grid):
    max_tries = 100
    potential_starts = [None] * max_tries
    overlaps = [0] * max_tries

    for idx in range(max_tries):
        potential_starts[idx] = find_open_location_for_word(grid, word)
        startpoint = potential_starts[idx]["point"]
        orientation = potential_starts[idx]["orientation"]
        endpoint = get_word_endpoint(word, startpoint, orientation)
        overlaps[idx] = total_overlap_with_grid(word, grid, startpoint, endpoint)

    am = argmax(overlaps)
    tot = overlaps[am]
    sp = potential_starts[am]["point"]
    ep = get_word_endpoint(word, sp, potential_starts[am]["orientation"])
    if tot > 0:
        print("Suggested location for word '{0}' is between ({1}, {2}) and ({3}, {4}) with overlap {5}".format(word,
                                                                                                           sp[0], sp[1],
                                                                                                           ep[0], ep[1],
                                                                                                           tot))
    was_placed = tot > 0
    if was_placed:
        grid = place_word_safe(word, sp, ep, grid)
    return dict(grid=grid, was_placed=was_placed)


if __name__ == "__main__":
    random.seed(0)

    iters = 5 # number of times to pass through
    grid_width = 21
    grid_height = 15

    # Word list from: http://bryanhelmig.com/python-crossword-puzzle-generator/
    # word_list = ['saffron', 'pumpernickel', 'leaven', 'coda', 'paladin', 'syncopation', 'albatross', 'harp', 'piston',
    #             'caramel', 'coral', 'dawn', 'pitch', 'fjord', 'lip', 'lime', 'mist', 'plague', 'yarn', 'snicker']

    word_list = ['saffron', 'pumpernickel', 'leaven', 'coda', 'syncopation', 'albatross', 'harp', 'piston']


    remaining_word_set = set(word_list)
    longest_word = max(remaining_word_set, key=len)

    longest_word_len = len(longest_word)
    assert min(grid_width, grid_height) >= longest_word_len, "both board dimensions should exceed longest word length"

    grid = dict(letters = [[0 for x in range(grid_width)] for y in range(grid_height)],
                is_filled  = [[False for x in range(grid_width)] for y in range(grid_height)])

    # place the longest word by hand first, roughly in the middle of the grid
    row = int(grid_height/2)
    left_margin = int((grid_width - longest_word_len)/2)-1

    word_to_place = longest_word
    start_ind = [row, left_margin]
    end_ind = [row, left_margin + longest_word_len]
    grid = place_word_safe(word_to_place, start_ind, end_ind, grid)
    placed_word = word_to_place

    remaining_word_set.remove(placed_word)

    # grid = place_word_safe('test', [6, 13], get_word_endpoint("test", [6, 13], "vertical"), grid)

    remaining_word_set_next = set([])

    for iter in range(iters):
        num_remaining = len(remaining_word_set)

        while len(remaining_word_set) > 0:
            word = max(remaining_word_set, key=len)
            back = try_to_place_word(word, grid)
            grid = back["grid"]
            was_placed = back["was_placed"]

            remaining_word_set.remove(word)

            if was_placed:
                remaining_word_set_next.add(word)
        num_placed = num_remaining - len(remaining_word_set_next)
        print("Placed {0} words in iteration {1}".format(num_placed, iter))
        print("Remaining words")
        print(remaining_word_set_next)
        remaining_word_set = remaining_word_set_next
        remaining_word_set_next = set([])





    print_grid(grid)


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
