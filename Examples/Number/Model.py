
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Primitives
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from collections import defaultdict
from LOTlib3.Eval import primitive

# counting list
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
prev_hash['X'] = 'X'

word_to_number = dict() # map a word like 'four_' to its number, 4
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.Miscellaneous import random, weighted_sample
from LOTlib3.DataAndObjects import FunctionData, sample_sets_of_objects, make_all_objects

WORDS = ['one_', 'two_', 'three_', 'four_', 'five_', 'six_', 'seven_', 'eight_', 'nine_', 'ten_']

def make_data(data_size=300, alpha=0.75):
    """
    Sample some data according to the target
    """
    data = []
    for i in range(data_size):
        # how many in this set
        set_size = weighted_sample( list(range(1,10+1)), probs=[7187, 1484, 593, 334, 297, 165, 151, 86, 105, 112] )
        # get the objects in the current set
        s = set(sample_sets_of_objects(set_size, all_objects))

        # sample according to the target
        if random() < alpha: r = WORDS[len(s)-1]
        else:                r = weighted_sample( WORDS )

        # and append the sampled utterance
        data.append(FunctionData(input=[s], output=r, alpha=alpha))
    return data


#here this is really just a dummy -- one type of object, which is replicated in sample_sets_of_objects
all_objects = make_all_objects(shape=['duck'])

# all possible data sets on 10 objects
all_possible_data = [ ('', set(sample_sets_of_objects(n, all_objects))) for n in range(1,10) ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Grammar
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.Grammar import Grammar
from LOTlib3.Miscellaneous import q

# The priors here are somewhat hierarchical by type in generation, tuned to be a little more efficient
# (but the actual RR prior does not care about these probabilities)

grammar = Grammar()

grammar.add_rule('START', '', ['WORD'], 1.0)

grammar.add_rule('BOOL', 'and_',    ['BOOL', 'BOOL'], 1./3.)
grammar.add_rule('BOOL', 'or_',     ['BOOL', 'BOOL'], 1./3.)
grammar.add_rule('BOOL', 'not_',    ['BOOL'], 1./3.)

grammar.add_rule('BOOL', 'True',    None, 1.0/2.)
grammar.add_rule('BOOL', 'False',   None, 1.0/2.)

# note that this can take basically any types for return values
grammar.add_rule('WORD', '(%s if %s else %s)',    ['WORD', 'BOOL', 'WORD'], 0.5)

grammar.add_rule('WORD', q('undef'), None, 0.5)
# grammar.add_rule('WORD', 'if_',    ['BOOL', 'WORD', q('undef')], 0.5)
# grammar.add_rule('WORD', 'ifU_',    ['BOOL', 'WORD'], 0.5)  # if returning undef if condition not met

grammar.add_rule('BOOL', 'cardinality1_',    ['SET'], 1.0)
grammar.add_rule('BOOL', 'cardinality2_',    ['SET'], 1.0)
grammar.add_rule('BOOL', 'cardinality3_',    ['SET'], 1.0)

grammar.add_rule('BOOL', 'equal_',    ['WORD', 'WORD'], 1.0)

grammar.add_rule('SET', 'union_',     ['SET', 'SET'], 1./3.)
grammar.add_rule('SET', 'intersection_',     ['SET', 'SET'], 1./3.)
grammar.add_rule('SET', 'setdifference_',     ['SET', 'SET'], 1./3.)
grammar.add_rule('SET', 'select_',     ['SET'], 1.0)

grammar.add_rule('SET', 'x',     None, 4.0)

grammar.add_rule('WORD', 'recurse_',        ['SET'], 1.0)

grammar.add_rule('WORD', 'next_', ['WORD'], 1.0)
grammar.add_rule('WORD', 'prev_', ['WORD'], 1.0)

# These are quoted (q) since they are strings when evaled
for w in WORDS:
    grammar.add_rule('WORD', q(w), None, 1./len(WORDS))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hypothesis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib3.Hypotheses.RecursiveLOTHypothesis import RecursiveLOTHypothesis
from LOTlib3.Miscellaneous import log, Infinity, log1mexp, attrmem
from LOTlib3.Eval import EvaluationException

class MyHypothesis(RecursiveLOTHypothesis):
    
    def __init__(self, gamma=-30, **kwargs):
        RecursiveLOTHypothesis.__init__(self, grammar, **kwargs)
        self.gamma=gamma
        self.lg1mgamma=log1mexp(gamma)

    def __call__(self, *args):
        try:
            return RecursiveLOTHypothesis.__call__(self, *args)
        except EvaluationException: # catch recursion and too big
            return None

    @attrmem('prior') # save this in the prior
    def compute_prior(self):
        """Compute the number model prior.
        Log_probability() with a penalty on whether or not recursion is used.
        """
        if self.value.count_nodes() > self.maxnodes:
            return -Infinity
        else:
            if self.value.contains_function('recurse_'):
                recursion_penalty = self.gamma
            else:
                recursion_penalty = self.lg1mgamma

        return (recursion_penalty + self.grammar.log_probability(self.value)) / self.prior_temperature

    def compute_single_likelihood(self, datum):
        """Computes the likelihood of data.

            TODO: Make sure this precisely matches the number paper.
        """
        response = self(*datum.input)
        if response == 'undef' or response == None:
            return log(1.0/10.0) # if undefined, just sample from a base distribution
        else:
            return log((1.0 - datum.alpha)/10.0 + datum.alpha * (response == datum.output))

    def sample_output(self, datum):
        # return a sample of my output given the input in datum
        if random() < datum.alpha:
            return self(*datum.input)
        else:
            return weighted_sample( WORDS ) # uniform sample

    def get_knower_pattern(self):
        # compute a string describing the behavior of this knower-level
        resp = [ self(set(sample_sets_of_objects(n, all_objects))) for n in range(1, 10)]
        return ''.join([str(word_to_number[x]) if (x is not None and x is not 'undef') else 'U' for x in resp])

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
    print(h.posterior_score, h.prior, h.likelihood, h.get_knower_pattern(), qq(h))