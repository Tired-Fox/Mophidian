all_chars = [
    'a',
    'b',
    'c',
    'd',
    'e',
    'f',
    'g',
    'h',
    'i',
    'j',
    'k',
    'l',
    'm',
    'n',
    'o',
    'p',
    'q',
    'r',
    's',
    't',
    'u',
    'v',
    'w',
    'x',
    'y',
    'z',
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    '0',
    ',',
    '.',
    "'",
    '"',
    '_',
    '-',
    '+',
    '=',
    '~',
    '`',
    '!',
    '@',
    '#',
    '$',
    '%',
    '^',
    '&',
    '*',
    '(',
    ')',
    '{',
    '}',
    '[',
    ']',
    '|',
    '\\',
    '/',
    '?',
    '<',
    '>',
]

import sys


def insertion_sort(array):
    # Loop from the second element of the array until
    # the last element
    for i in range(1, len(array)):
        # This is the element we want to position in its
        # correct place
        key_item = array[i]

        # Initialize the variable that will be used to
        # find the correct position of the element referenced
        # by `key_item`
        j = i - 1

        # Run through the list of items (the left
        # portion of the array) and find the correct position
        # of the element referenced by `key_item`. Do this only
        # if `key_item` is smaller than its adjacent values.
        while j >= 0 and array[j] > key_item:
            # Shift the value one position to the left
            # and reposition j to point to the next element
            # (from right to left)
            array[j + 1] = array[j]
            j -= 1

        # When you finish shifting the elements, you can position
        # `key_item` in its correct location
        array[j + 1] = key_item

    return array


def output_array(array):
    out = sys.stdout
    out.write("[\n")
    for i, char in enumerate(array):
        out.write(f"'{char}' ")
        if i % 5 == 1 and i != 0:
            out.write("\n")
    out.write("]\n")
    out.flush()


def sort_func(e):
    if e == "index":
        return "!index"
    else:
        return f"~{e}"


test_array = [
    "!index",
    "~blog",
    "~docs",
]

test2_array = ["!index", "~build", "~new"]

output_array(test2_array)
test2_array.sort(key=sort_func)
output_array(test2_array)
