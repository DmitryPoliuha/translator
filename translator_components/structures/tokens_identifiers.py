"""
Tokens identifiers
"""
tokens_identifiers = {
    # token => token id
    'int': 1,
    'float': 2,
    'begin': 3,
    'end': 4,
    'goto': 5,
    'cin': 6,
    'cout': 7,
    'for': 8,
    'by': 9,
    'to': 10,
    'do': 11,
    'rof': 12,
    'if': 13,
    'then': 14,
    'fi': 15,
    ';': 16,
    ':': 17,
    ',': 18,
    '=': 19,
    '>>': 20,
    '<<': 21,
    '>': 22,
    '<': 23,
    '>=': 24,
    '<=': 25,
    '==': 26,
    '!=': 27,
    '+': 28,
    '-': 29,
    '*': 30,
    '/': 31,
    '(': 32,
    ')': 33,
    'or': 34,
    'and': 35,
    'not': 36,
    '[': 37,
    ']': 38,
    'IDN': 100,
    'CON': 101,
    'LAB': 102,
}

tokens_identifiers_reversed = {val: key for key, val in tokens_identifiers.items()}
