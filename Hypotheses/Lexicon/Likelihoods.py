
from .SimpleLexicon import SimpleLexicon
from math import log

class BooleanConditionedOnWord(SimpleLexicon):
    """
        The likelihood is just conditioned on each word,
    """
    def compute_single_likelihood(self, datum):
        p = (1.-self.alpha) / 2.0
        if self(*datum.input) == datum.output:
            p += self.alpha
        return log(p)


class SampleTrueWord(SimpleLexicon):
    """
        A lexicon where you sample from the true words on the given input
        datum here is
            input: arguments to a word
            output: a word
    """

    def compute_single_likelihood(self, datum):
        matches = [w for w in self.all_words() if self.value[w](*datum.input)]

        p = (1.0-self.alpha) / len(self.all_words())

        if datum.output in matches:
            p += self.alpha / len(matches)

        return log(p)


class OutlierLikelihoodLexicon(SimpleLexicon):
    """
         A lexicon with a likelihood function that treats false as outliers with likelihood 1-self.alpha
    """

    def compute_single_likelihood(self, datum):
        if self(datum) == datum.output:
            return log(self.alpha)
        else:
            return log(1.0-self.alpha)
