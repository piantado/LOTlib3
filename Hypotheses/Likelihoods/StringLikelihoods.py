from Levenshtein import editops
from LOTlib3.Miscellaneous import logplusexp, logsumexp, Infinity
from math import log

def edit_likelihood(x,y, alphabet_size=2, alpha=0.99):
    """
    This computes the likelihood of going from x->y by choosing levenshtein ops uniformly at random,
    and sampling from the alphabet on insertions and replacements.
    """
    ops = editops(x,y)
    lp = log(alpha)*(len(y)-len(ops)) # all the unchanged
    for o, _, _ in ops:
        if   o == 'equal':   assert False # should never get here
        elif o == 'replace': lp += log(1.0-alpha) - log(3.0) - log(alphabet_size)
        elif o == 'insert':  lp += log(1.0-alpha) - log(3.0) - log(alphabet_size)
        elif o == 'delete':  lp += log(1.0-alpha) - log(3.0)
        else: assert False
    return lp


def choppy_likelihood(x,y, alphabet_size=2, alpha=0.99):
    """
    Compute likelihood under a model where with probability alpha we pick a random location in x
    and replace the remainder with a random strong of length l ~ geometric(0.5) (with random characters)
    """

    # find the tail generating probability by summing over all positions in x
    ltail = -Infinity
    for i in range(len(x)+1): # +1 since we'll consider the possibility of first position
        if x[:i] == y[:i]:
            #                         P(trimming)    P(position i, including start)    P(remainder of y)
            ltail = logplusexp(ltail, log(1.0-alpha) - log(len(x)+1)               - (len(y)-i)*log(0.5) - (len(y)-i)*log(alphabet_size))
        else:
            break

    # add together probability under noise and under the copying model (which is prob alpha iff they are equal)
    return logplusexp(ltail, (log(alpha) if x==y else -Infinity))

def prefix_likelihood(x,y, alphabet_size=2, alpha=0.99):
    """
    Sample x with probability alpha, x+s, with len(s) ~ geometric(0.5) with probability 1-alpha.
    The characters in s come from a uniform sample on alphabet size
    """

    if x == y:
        return log(alpha)
    elif x == y[:len(x)]:
        d = len(y) - len(x)
        return log(1.0-alpha) + d * (log(0.5) - log(alphabet_size))
    else:
        # we could not have been generated
        return -Infinity


class PrefixLikelihood(object):

    """
        Data is a dictionary from strings to counts; use the min edit distance if not in the output of the function.
        Requires self.alphabet_size to say how many possible tokens there are
    """

    def compute_single_likelihood(self, datum):
        assert isinstance(datum.output, dict)

        hp = self(*datum.input)  # output dictionary, output->probabilities
        assert isinstance(hp, dict)

        s = 0.0
        for k, dc in list(datum.output.items()):

            if len(list(hp.keys())) > 0:
                # P(k | x) P(x | model)
                s += dc * logsumexp([v + prefix_likelihood(x, k, alphabet_size=self.alphabet_size, alpha=datum.alpha) for x,v in list(hp.items())])
            else:
                s += dc * prefix_likelihood('', k, alphabet_size=self.alphabet_size, alpha=datum.alpha)
        return s

class ChoppyLikelihod(object):

    """
        Data is a dictionary from strings to counts; use the min edit distance if not in the output of the function.
        Requires self.alphabet_size to say how many possible tokens there are
    """

    def compute_single_likelihood(self, datum):
        assert isinstance(datum.output, dict)

        hp = self(*datum.input)  # output dictionary, output->probabilities
        assert isinstance(hp, dict)

        s = 0.0
        for k, dc in list(datum.output.items()):

            if len(list(hp.keys())) > 0:
                # P(k | x) P(x | model)
                s += dc * logsumexp([v + choppy_likelihood(x, k, alphabet_size=self.alphabet_size, alpha=datum.alpha) for x,v in list(hp.items())])
            else:
                s += dc * choppy_likelihood('', k, alphabet_size=self.alphabet_size, alpha=datum.alpha)
        return s


class LevenshteinPseudoLikelihood(object):

    """
        Data is a dictionary from strings to counts; use the min edit distance if not in the output of the function.
        Requires self.alphabet_size to say how many possible tokens there are
    """

    def compute_single_likelihood(self, datum):
        assert isinstance(datum.output, dict)

        hp = self(*datum.input)  # output dictionary, output->probabilities
        assert isinstance(hp, dict)

        s = 0.0
        for k, dc in list(datum.output.items()):
            if len(list(hp.keys())) > 0:
                # probability of each string under this editing model
                s += dc * logsumexp([ v + edit_likelihood(x, k, alphabet_size=self.alphabet_size, alpha=datum.alpha) for x, v in list(hp.items()) ]) # the highest probability string; or we could logsumexp
            else:
                # If hp is empty, the only thing we cna create is the empty string
                s += dc * edit_likelihood('', k, alphabet_size=self.alphabet_size, alpha=datum.alpha)
        return s

class MonkeyNoiseLikelihood(object):
    """
    Data is a dictionary from strings to counts.
    Assume that out of dictionary strings are generated by a random typing process
    Requires self.alphabet_size to say how many possible tokens there are
    Data here requires an alpha for noise
    """

    def compute_single_likelihood(self, datum):
        assert isinstance(datum.output, dict)

        hp = self(*datum.input)  # output dictionary, output->probabilities
        assert isinstance(hp, dict)

        s = 0.0
        for k, dc in list(datum.output.items()):

            lp = -log(self.alphabet_size+1)*(len(k)+1) + log(1.0-datum.alpha) # probability of generating under random typing; +1 is for an EOS marker
            if k in hp:
                lp = logplusexp(lp, hp[k] + log(datum.alpha)) # if we could have been generated
            s += dc*lp

        return s

