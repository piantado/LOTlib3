# -*- coding: utf-8 -*-


from copy import copy
from LOTlib3.Miscellaneous import flip, weighted_sample, ifelse, log
from LOTlib3.DataAndObjects import UtteranceData

from .SimpleLexicon import SimpleLexicon

class WeightedLexicon(SimpleLexicon):
    """

            A weighted lexicon is a lexicon where each word has a weight.

            We generate from the presuppositionally-valid utterances with probability palpha,
            and then when valid, we generate from the true utterances with probability alpha, and then
            within each set proportional to weightfunction(utterance, context).
    """

    def __init__(self,  make_hypothesis, alpha=0.90, palpha=0.90, **kwargs):
        SimpleLexicon.__init__(self, make_hypothesis, **kwargs)
        self.alpha=alpha
        self.palpha=palpha

    def __call__(self, utterance, context):
        """
                Evaluate this lexicon on a possible utterance, passing the context as an argument
        """
        return self.value[utterance](context)

    def __copy__(self):
        """ Copy a.valueicon. We don't re-create the fucntions since that's unnecessary and slow"""
        new = type(self)(None, words=None, alpha=self.alpha, palpha=self.palpha)
        for w in self.all_words():
            new.set_word(w, copy(self.get_word(w)))

        # And copy everything else
        for k in list(self.__dict__.keys()):
            if k not in ['self', 'value']:
                new.__dict__[k] = copy(self.__dict__[k])

        return new

    def weightfunction(self, u, context):
        """
                The weight of an uterance in a context. Defaults to 1.0 (uniform)
        """
        return 1.0

    def partition_utterances(self, utterances, context):
        """
                Take some utterances and a context. Returns 3 lists, giving those utterances
                that are true/false/other in the context
        """
        trues, falses, others = [], [], []
        for u in utterances:
            ret = self(u,context)
            if ret is True:    trues.append(u)
            elif ret is False: falses.append(u)
            else:              others.append(u)
        return trues, falses, others


    def compute_single_likelihood(self, udi):
        """
                Compute the likelihood of a single data point, udi, an utteranceData
        """
        assert isinstance(udi, UtteranceData)

        # Types of utterances
        trues, falses, others = self.partition_utterances( udi.possible_utterances, udi.context)
        #print "T:", trues
        #print "F:", falses
        #print "U:", others
        u = udi.utterance

        # compute the weights
        all_weights  = sum([self.weightfunction(u, udi.context) for u in udi.possible_utterances])
        true_weights = sum([self.weightfunction(u, udi.context) for u in trues])
        met_weights  = sum([self.weightfunction(u, udi.context) for u in falses]) + true_weights

        w = self.weightfunction(u, udi.context) # the current word weight
        if(u in trues):
            p = self.palpha * self.alpha * w / true_weights + self.palpha *  \
            (1.0 - self.alpha) * w / met_weights + (1.0 - self.palpha) * w / \
            all_weights # choose from the trues
        elif (u in falses):
            p = ifelse(true_weights==0, 1.0, 1.0-self.alpha) * self.palpha * w / met_weights + (1.0 - self.palpha) * w / all_weights # choose from the trues
        else:
            p = ifelse(met_weights==0, 1.0, (1.0 - self.palpha)) * w / all_weights

        """
        TODO: WHY NOT THIS WAY, IGNORING tre_weights==0? Because if we sample, then we have 0 chance of getting a true when true_weights is like that. This causes problems in CCGLexicon
        w = self.weightfunction(u, udi.context) # the current word weight
        if   (u in trues):  p = self.palpha * (self.alpha * w / true_weights + (1.0 - self.alpha) * w / met_weights) + (1.0 - self.palpha) * w / all_weights # choose from the trues
        elif (u in falses): p = self.palpha * (1.0-self.alpha) * w / met_weights + (1.0 - self.palpha) * w / all_weights # choose from the trues
        else:               p = (1.0 - self.palpha) * w / all_weights
        """


        return log(p)


    # take a set of utterances and sample them according to our probability model
    def sample_utterance(self, possible_utterances, context):

        t, f, others = self.partition_utterances( possible_utterances, context)

        m = set(t).union(f)

        if flip(self.palpha) and (len(m) > 0): # if we sample from a presup is true
            if (flip(self.alpha) and (len(t)>0)):
                return weighted_sample(t, probs=[self.weightfunction(u, context) for u in t], log=False)
            else:   return weighted_sample(m, probs=[self.weightfunction(u, context) for u in m], log=False)
        else:           return weighted_sample(possible_utterances, probs=[self.weightfunction(u, context) for u in possible_utterances], log=False) # sample from all utterances
