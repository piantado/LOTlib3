from LOTlib3.Eval import primitive

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# counting list
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from collections import defaultdict

# the next word in the list -- we'll implement these as a hash table
word_list = ['one_', 'two_', 'three_', 'four_', 'five_', 'six_', 'seven_', 'eight_', 'nine_', 'ten_']
next_hash, prev_hash = [defaultdict(lambda: 'undef'), defaultdict(lambda: 'undef')]
for i in range(1, len(word_list)-1):
    next_hash[word_list[i]] = word_list[i+1]
    prev_hash[word_list[i]] = word_list[i-1]
next_hash['one_'] = 'two_'
next_hash['ten_'] = 'undef'
prev_hash['one_'] = 'undef'
prev_hash['ten_'] = 'nine_'
next_hash['X'] = 'X'
prev_hash[''] = 'X'

# Map a word like 'four_' to its number, 4
word_to_number = dict()
for i in range(len(word_list)):
    word_to_number[word_list[i]] = i+1
word_to_number['ten_'] = 'A' # so everything is one character
word_to_number['undef'] = 'U'

prev_hash[None] = None

@primitive
def next_(w): return next_hash[w]

@primitive
def prev_(w): return prev_hash[w]

@primitive
def ifU_(C,X):
    if C:
        return X
    else:
        return 'undef'

@primitive
def ends_in_(n, d):
    """Return `n` if it ends with digit `d`, 0 otherwise. E.g. ends_in_(427, 7) == 427"""

    if (n % 10) == d:
        return n
    else:
        return 0

@primitive
def contains_digit_(n, d):
    """Return `n` if it contains digit `d`, 0 otherwise. E.g. contains_digit_(86, 8) == 86"""
    if str(n) == 'nan':
        return 0
    if d in [int(i) for i in set(str(n))]:
        return n
    else:
        return 0

@primitive
def isprime_(n):
    """Is `n` a prime number?"""
    if n > 1000 or str(n) == 'nan':
        # raise OverflowError
        return 0

    try:
        for a in range(2, int(n**0.5)+1):
            if n % a == 0:
                return 0
    except (ValueError, MemoryError):
        raise OverflowError

    return n

@primitive
def primes_in_set_(A):
    return [n for n in A if isprime_(n)]

@primitive
def in_domain_(A, domain):
    return [n for n in A if (n <= domain)]

