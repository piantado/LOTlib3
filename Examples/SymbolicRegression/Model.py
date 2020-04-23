"""
    A simple version of symbolic regression.
    Defaultly we use Galileo's ball rolling data (see below)
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the grammar
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TERMINAL_WEIGHT = 5.0

from LOTlib3.Grammar import Grammar

grammar = Grammar()
grammar.add_rule('START', '', ['EXPR'], 1.0)

grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0) # or use plus_
grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0) # or use times_
grammar.add_rule('EXPR', 'divide_', ['EXPR', 'EXPR'], 1.0) # use a version safe to division by zero
grammar.add_rule('EXPR', '(%s - %s)', ['EXPR', 'EXPR'], 1.0) # or use subtract_

grammar.add_rule('EXPR', 'exp_', ['EXPR'], 1.0)
grammar.add_rule('EXPR', 'log_', ['EXPR'], 1.0)
grammar.add_rule('EXPR', 'pow_', ['EXPR', 'EXPR'], 1.0) # including this gives lots of overflow

grammar.add_rule('EXPR', 'sin_', ['EXPR'], 1.0)
grammar.add_rule('EXPR', 'cos_', ['EXPR'], 1.0)
grammar.add_rule('EXPR', 'tan_', ['EXPR'], 1.0)

grammar.add_rule('EXPR', 'x', None, TERMINAL_WEIGHT) # these terminals should have None for their function type; the literals

grammar.add_rule('EXPR', '1.0', None, TERMINAL_WEIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
This uses Galileo's data on a falling ball.

See: http://www.amstat.org/publications/jse/v3n1/datasets.dickey.html
See also: Jeffreys, W. H., and Berger, J. O. (1992), "Ockham's Razor and Bayesian Analysis," American
    Scientist, 80, 64-72 (Erratum, p. 116).
"""

from LOTlib3.DataAndObjects import FunctionData

# NOTE: these must be floats, else we get hung up on powers of ints
data_sd = 50.0

def make_data(n=1):
    return [ FunctionData(input=[1000.], output=1500., ll_sd=data_sd),
             FunctionData(input=[828.], output=1340., ll_sd=data_sd),
             FunctionData(input=[800.], output=1328., ll_sd=data_sd),
             FunctionData(input=[600.], output=1172., ll_sd=data_sd),
             FunctionData(input=[300.], output=800., ll_sd=data_sd),
             FunctionData(input=[0.], output=0., ll_sd=data_sd) # added 0,0 since it makes physical sense.
    ]*n

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hypothesis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib3.Hypotheses.Likelihoods.GaussianLikelihood import GaussianLikelihood

class MyHypothesis(GaussianLikelihood, LOTHypothesis):
    def __init__(self, **kwargs):
        LOTHypothesis.__init__(self, grammar=grammar, **kwargs)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":
    from LOTlib3 import break_ctrlc
    from LOTlib3.Miscellaneous import qq
    from LOTlib3.TopN import TopN
    from LOTlib3.Samplers.MetropolisHastings import MetropolisHastingsSampler

    h0   = MyHypothesis()
    data = make_data()
    top  = TopN(N=10)
    thin = 100

    for i, h in enumerate(break_ctrlc(MetropolisHastingsSampler(h0, data))):

        top << h

        if i % thin == 0:
            print("#", i, h.posterior_score, h.prior, h.likelihood, qq(h))

    for h in top:
        print(h.posterior_score, h.prior, h.likelihood, qq(h))
