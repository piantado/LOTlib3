
import numpy

from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib3.Miscellaneous import Infinity, beta, attrmem
from LOTlib3.FunctionNode import FunctionNode
from collections import defaultdict

def get_rule_counts(grammar, t):
    """
            A list of vectors of counts of how often each nonterminal is expanded each way

            TODO: This is probably not super fast since we use a hash over rule ids, but
                    it is simple!
    """

    counts = defaultdict(int) # a count for each hash type

    for x in t:
        if type(x) != FunctionNode:
            raise NotImplementedError("Rational rules not implemented for bound variables")
        
        counts[x.get_rule_signature()] += 1

    # and convert into a list of vectors (with the right zero counts)
    out = []
    for nt in list(grammar.rules.keys()):
        v = numpy.array([ counts.get(r.get_rule_signature(),0) for r in grammar.rules[nt] ])
        out.append(v)
    return out

def RR_prior(grammar, t, alpha=1.0):
    """
            Compute the rational rules prior from Goodman et al.

            NOTE: This has not yet been extensively debugged, so use with caution

            TODO: Add variable priors (different vectors, etc)
    """
    lp = 0.0

    for c in get_rule_counts(grammar, t):
        theprior = numpy.array( [alpha] * len(c), dtype=float )
        #theprior = np.repeat(alpha,len(c)) # Not implemented in numpypy
        lp += (beta(c+theprior) - beta(theprior))
    return lp

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from LOTlib3.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood

class RationaRulesPrior(object):
    """
            A FunctionHypothesis built from a grammar.
            Implement a Rational Rules (Goodman et al 2008)-style grammar over Boolean expressions.

    """

    @attrmem('prior')
    def compute_prior(self):
        """
            Rational rules prior
        """
        if self.value.count_subnodes() > self.maxnodes:
            return -Infinity
        else:
            # compute the prior with either RR or not.
            return RR_prior(self.grammar, self.value, alpha=self.__dict__.get('rrAlpha', 1.0)) / self.prior_temperature

