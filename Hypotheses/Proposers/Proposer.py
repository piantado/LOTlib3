from LOTlib3.Miscellaneous import lambdaOne, Infinity

class ProposalFailedException(Exception):
    """
    This gets raised when we have a proposal that can't succeed
    """
    pass

class Proposer(object):
    def propose(self, **kwargs):
        ret_value, fb = None, None
        while not ret_value: # keep trying to propose
            try:
                ret_value, fb =  self.proposal_content(self.grammar, self.value, **kwargs)
            except ProposalFailedException:
                pass
        ret = self.__copy__(value=ret_value)
        return ret, fb

    def proposal_content(self, grammar, tree, resampleProbability=lambdaOne):
        t = self.propose_tree(grammar,tree,resampleProbability)
        fb = self.compute_fb(grammar,tree,t,resampleProbability)
        return t,fb

    def compute_fb(self, grammar, t1, t2, resampleProbability=lambdaOne):
        return (self.compute_proposal_probability(grammar,t1,t2,resampleProbability) -
                self.compute_proposal_probability(grammar,t2,t1,resampleProbability))

    def propose_tree(self, grammar,tree,resampleProbability=lambdaOne):
        raise NotImplementedError

    def compute_proposal_probability(self, grammar, t1, t2, resampleProbability=lambdaOne, recurse=True):
        raise NotImplementedError

def test_proposer(the_class):
    # We'd probably see better performance on a grammar with fewer
    # distinct types, but this one is a good testbed *because* it's
    # complex (lambdas, etc.)
    from LOTlib3.Examples.Magnetism.Simple import grammar, make_data
    from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis
    from LOTlib3.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood
    from LOTlib3.Inference.Samplers.StandardSample import standard_sample

    class CRHypothesis(BinaryLikelihood, the_class, LOTHypothesis):
        """
        A recursive LOT hypothesis that computes its (pseudo)likelihood using a string edit
        distance
        """
        def __init__(self, *args, **kwargs ):
            LOTHypothesis.__init__(self, grammar, display='lambda x,y: %s', **kwargs)

    def make_hypothesis(**kwargs):
        return CRHypothesis(**kwargs)

    standard_sample(make_hypothesis, make_data, save_top=False)
