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


