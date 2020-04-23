""" A simple exmaple to show use of a Lexicon """

WORDS = ['even', 'odd']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Grammar
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.Grammar import Grammar
from LOTlib3.Miscellaneous import q

grammar = Grammar()
grammar.add_rule('START', '', ['BOOL'], 1.)

grammar.add_rule('BOOL', '(%s == %s)', ['NUMBER', 'NUMBER'], 1.)
grammar.add_rule('BOOL', '(not %s)', ['BOOL'], 1.)

grammar.add_rule('BOOL', '(%s and %s)', ['BOOL', 'BOOL'], 1.)
grammar.add_rule('BOOL', '(%s or %s)',  ['BOOL', 'BOOL'], 1.)  # use the short_circuit form

grammar.add_rule('NUMBER', 'x', None, 1.)
grammar.add_rule('NUMBER', '1', None, 1.)
grammar.add_rule('NUMBER', '0', None, 1.)
grammar.add_rule('NUMBER', 'plus_', ['NUMBER', 'NUMBER'], 1.)
grammar.add_rule('NUMBER', 'minus_', ['NUMBER', 'NUMBER'], 1.)

for w in WORDS:
    grammar.add_rule('BOOL', 'lexicon', [q(w), 'NUMBER'], 1.)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.DataAndObjects import FunctionData

def make_data(n=1, alpha=0.99):
    data = []
    for x in range(1, 10):
        data.append( FunctionData(input=['even', x], output=(x % 2 == 0), alpha=alpha) )
        data.append( FunctionData(input=['odd',  x], output=(x % 2 == 1), alpha=alpha) )
    return data*n

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hypothesis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.Hypotheses.Lexicon.RecursiveLexicon import RecursiveLexicon
from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib3.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood

class MyHypothesis(BinaryLikelihood, RecursiveLexicon):
    def __init__(self, **kwargs):
        RecursiveLexicon.__init__(self, **kwargs)
        for w in WORDS:
            self.set_word(w, LOTHypothesis(grammar, display='lambda lexicon, x: %s'))


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

