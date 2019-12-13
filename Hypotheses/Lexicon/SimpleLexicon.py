from copy import copy
from LOTlib3.Miscellaneous import flip, qq, attrmem
from LOTlib3.Hypotheses.Hypothesis import Hypothesis
from LOTlib3.Hypotheses.FunctionHypothesis import FunctionHypothesis
from LOTlib3.Hypotheses.Proposers import ProposalFailedException
from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis

class SimpleLexicon(Hypothesis):
    """
        A class for mapping words to hypotheses.

        This defaultly assumes that the data comes from sampling with probability alpha from
        the true utteranecs
    """

    def __init__(self, value=None, propose_p=0.5, **kwargs):
        """
            make_hypothesis -- a function to make each individual word meaning. None will leave it empty (for copying)
            words -- words to initially add (sampling from the prior)
            propose_p -- the probability of proposing to each word
        """

        if value is None:
            value = dict()
        else:
            assert isinstance(self.value, dict)

        Hypothesis.__init__(self, value=value, **kwargs)

        self.propose_p = propose_p

    def __copy__(self):

        thecopy = type(self)()  # Empty initializer

        # copy over all the relevant attributes and things.
        # Note objects like Grammar are not given new copies
        thecopy.__dict__.update(self.__dict__)

        # and copy the self.value
        thecopy.value = dict()
        for k,v in list(self.value.items()):
            thecopy.set_word(k, copy(v))

        return thecopy

    def __call__(self, word, *args):
        """
        Just a wrapper so we can call like SimpleLexicon('hi', 4)
        """
        return self.value[word](*args)

    # this sets the word and automatically compute its function
    def set_word(self, w, v):
        """
            This sets word w to value v. v can be either None, a FunctionNode or a  Hypothesis, and
            in either case it is copied here.
        """
        assert isinstance(v, Hypothesis)

        self.value[w] = v

    def get_word(self, w):
        return self.value[w]

    def all_words(self):
        return list(self.value.keys())

    def __str__(self):
        """
            This defaultly puts a \0 at the end so that we can sort -z if we want (e.g. if we print out a posterior first)
        """
        return '\n'+'\n'.join(["%-15s: %s" % (qq(w), str(v)) for w, v in sorted(self.value.items())]) + '\0'

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return (str(self) == str(other))  # simple but there are probably better ways

    def force_function(self, w, f):
        """
            Allow force_function
        """

        # If this does not exist, make a function hypothesis from scratch with nothing in it.
        if w not in self.value:
            self.value[w] = FunctionHypothesis(value=None, args=None)

        self.value[w].force_function(f)

    def pack_ascii(self):
        """ Packing function for more concise representations """

        out = ''
        for w in sorted(self.all_words()):
            assert isinstance(self.value[w], LOTHypothesis), "*** Can only pack Lexicons with FunctionNode values"
            out += "%s:%s;" % (w, self.value[w].grammar.pack_ascii(self.value[w].value) )
        return out

    ###################################################################################
    ## MH stuff
    ###################################################################################

    def propose(self):
        """
        Propose to the lexicon by flipping a coin for each word and proposing to it.

        This permits ProposalFailExceptions on individual words, but does not return a lexicon
        unless we can propose to something.
        """


        fb = 0.0
        changed_any = False

        while not changed_any:
            new = copy(self)  ## Now we just copy the whole thing

            for w in self.all_words():
                    if flip(self.propose_p):
                        try:
                            xp, xfb = self.get_word(w).propose()

                            changed_any = True
                            new.set_word(w, xp)
                            fb += xfb

                        except ProposalFailedException:
                            pass


            return new, fb

    @attrmem('prior')
    def compute_prior(self):
        return sum([x.compute_prior() for x in list(self.value.values())]) / self.prior_temperature












