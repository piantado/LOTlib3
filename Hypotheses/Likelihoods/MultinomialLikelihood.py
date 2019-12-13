
from math import log
from LOTlib3.Eval import RecursionDepthException
from LOTlib3.Miscellaneous import Infinity, logsumexp

class MultinomialLikelihood(object):
    """
    Compute multinomial likelihood for data where the data is a dictionary and the function
    output is also a dictionary of counts. The self dictionary gets normalized to be a probability
    distribution. Smoothing term called "outlier" is the (unnormalized) probability assigned to
    out of sample items
    """

    def compute_single_likelihood(self, datum):
        outlier = self.__dict__.get('outlier', -Infinity) # pull the outleir prob from self adjective

        assert isinstance(datum.output, dict)

        hp = self(*datum.input) # output dictionary, output->probabilities
        assert isinstance(hp, dict)
        try:
            return sum( dc * (log(hp[k]) if k in hp else outlier) for k, dc in list(datum.output.items()) )
        except ValueError as e:
            print("*** Math domain error", hp, str(self))
            raise e

class MultinomialLikelihoodLog(object):
    """
    Same but assumes the hypothesis (self) returns log likelihoods instead of likelihoods of each data point in hp
    """

    def compute_single_likelihood(self, datum):
        outlier = self.__dict__.get('outlier', -Infinity)  # pull the outleir prob from self adjective

        assert isinstance(datum.output, dict)

        hp = self(*datum.input)  # output dictionary, output->logprobabilities
        assert isinstance(hp, dict)
        try:
            return sum(dc * (hp[k] if k in hp else outlier) for k, dc in list(datum.output.items()))
        except ValueError as e:
            print("*** Math domain error", hp, str(self))
            raise e

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from Levenshtein import distance

class MultinomialLikelihoodLogLevenshtein(object):
    """
    Assume a levenshtein edit distance on strings. Slower, but more gradient. Not a real likelihood
    """

    def compute_single_likelihood(self, datum):
        distance_scale = self.__dict__.get('distance', 1.0)

        assert isinstance(datum.output, dict)

        hp = self(*datum.input)  # output dictionary, output->probabilities
        assert isinstance(hp, dict)
        try:

            # now we have to add up every string that we could get
            return sum(dc * ( logsumexp([rlp - distance_scale*distance(r, k) for r, rlp in list(hp.items())]))\
                           for k, dc in list(datum.output.items()))

        except ValueError as e:
            print("*** Math domain error", hp, str(self))
            raise e

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def prefix_distance(x,s):
    """
    if x is a prefix of s, return the number of chars remaining in s
    otherwise, return -Infinity.
    This is used as a distance metric that prefers to get the beginning of strings right, to allow
    us to model deeper program search as covering more and more of the prefix of a string.
    Interestingly, it doesn't allow x to be longer than s, meaning we really care about getting s right
    """

    if len(x) > len(s): # x cannot be a prefix of s
        return Infinity
    elif s[:len(x)] == x:
        return len(s)-len(x)
    else:
        return Infinity


class MultinomialLikelihoodLogPrefixDistance(object):
    """
    This distance between strings here is the remainder
    """

    def compute_single_likelihood(self, datum):
        distance_scale = self.__dict__.get('distance', 1.0)

        assert isinstance(datum.output, dict)

        hp = self(*datum.input)  # output dictionary, output->probabilities
        assert isinstance(hp, dict)
        try:

            # now we have to add up every string that we could get
            return sum(dc * ( logsumexp([rlp - distance_scale*prefix_distance(r, k) for r, rlp in list(hp.items())]))\
                           for k, dc in list(datum.output.items()))

        except ValueError as e:
            print("*** Math domain error", hp, str(self))
            raise e

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def longest_common_substring(s1, s2):
    # from https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring#Python_2
   m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
   longest, x_longest = 0, 0
   for x in range(1, 1 + len(s1)):
       for y in range(1, 1 + len(s2)):
           if s1[x - 1] == s2[y - 1]:
               m[x][y] = m[x - 1][y - 1] + 1
               if m[x][y] > longest:
                   longest = m[x][y]
                   x_longest = x
           else:
               m[x][y] = 0
   return s1[x_longest - longest: x_longest]


def longest_substring_distance(x,s):
    if len(x) > len(s): # don't over-generate, only treat substrings
        return Infinity
    else:
        return len(s) - len(longest_common_substring(x,s))

class MultinomialLikelihoodLogLongestSubstring(object):
    """
    This distance between strings here is the remainder
    """

    def compute_single_likelihood(self, datum):
        distance_scale = self.__dict__.get('distance', 1.0)

        assert isinstance(datum.output, dict)

        hp = self(*datum.input)  # output dictionary, output->probabilities
        assert isinstance(hp, dict)
        try:

            # now we have to add up every string that we could get
            return sum(dc * ( logsumexp([rlp - distance_scale*longest_substring_distance(r, k) for r, rlp in list(hp.items())]))\
                           for k, dc in list(datum.output.items()))

        except ValueError as e:
            print("*** Math domain error", hp, str(self))
            raise e