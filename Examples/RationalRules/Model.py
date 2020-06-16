# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.DataAndObjects import FunctionData, Obj

def make_data(n=1, alpha=0.999):
    return [FunctionData(input=[Obj(shape='square', color='red')], output=True, alpha=alpha),
            FunctionData(input=[Obj(shape='square', color='blue')], output=False, alpha=alpha),
            FunctionData(input=[Obj(shape='triangle', color='blue')], output=False, alpha=alpha),
            FunctionData(input=[Obj(shape='triangle', color='red')], output=False, alpha=alpha)]*n

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Grammar
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.DefaultGrammars import DNF
from LOTlib3.Miscellaneous import q, random

# DNF defaultly includes the logical connectives so we need to add predicates to it.
grammar = DNF

# Two predicates for checking x's color and shape
# Note: per style, functions in the LOT end in _
grammar.add_rule('PREDICATE', 'is_color_', ['x', 'COLOR'], 1.0)
grammar.add_rule('PREDICATE', 'is_shape_', ['x', 'SHAPE'], 1.0)

# Some colors/shapes each (for this simple demo)
# These are written in quotes so they can be evaled
grammar.add_rule('COLOR', q('red'), None, 1.0)
grammar.add_rule('COLOR', q('blue'), None, 1.0)
grammar.add_rule('COLOR', q('green'), None, 1.0)
grammar.add_rule('COLOR', q('mauve'), None, 1.0)

grammar.add_rule('SHAPE', q('square'), None, 1.0)
grammar.add_rule('SHAPE', q('circle'), None, 1.0)
grammar.add_rule('SHAPE', q('triangle'), None, 1.0)
grammar.add_rule('SHAPE', q('diamond'), None, 1.0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hypothesis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib3.Hypotheses.Priors.RationalRules import RationaRulesPrior
from LOTlib3.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood


# from LOTlib3.Hypotheses.Proposers.RegenerationProposer import RegenerationProposer
# from LOTlib3.Hypotheses.Proposers.Proposer import ProposalFailedException

class MyHypothesis(RationaRulesPrior, BinaryLikelihood, LOTHypothesis):
    def __init__(self, **kwargs):
        LOTHypothesis.__init__(self, grammar=grammar, **kwargs)
        self.rrAlpha=2.0

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