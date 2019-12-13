"""
    A mixture proposal - given a weighted list of other proposal
    methods, create a proposal which uses these as subproposals in
    proportion to their weight.

    NOTE: ONLY ERGODIC IF MIXTURE IS ERGODIC!
"""

from LOTlib3.Hypotheses.Proposers.Proposer import *
from LOTlib3.Miscellaneous import lambdaOne, logsumexp, nicelog, self_update, weighted_sample

class MixtureProposer(Proposer):
    def __init__(self,proposers=[],proposer_weights=[],**kwargs):
        assert len(proposers) == len(proposer_weights) , "MixtureProposer.py >> __init__: different number of proposals and weights!"
        self_update(self,locals())
        Proposer.__init__(self,**kwargs)

    def propose_tree(self,grammar,tree,resampleProbability=lambdaOne):
        """ sample a sub-proposer and propose from it """
        chosen_proposer = weighted_sample(self.proposers, probs=self.proposer_weights)
        return chosen_proposer.propose_tree(grammar,tree,resampleProbability)

    def compute_proposal_probability(self,grammar, t1, t2, resampleProbability=lambdaOne, **kwargs):
        """
            sum over all possible ways of generating t2 from t1 over all
            proposers, adjusted for their weight
        """
        lps = []
        for idx,proposer in enumerate(self.proposers):
            lp = proposer.compute_proposal_probability(grammar,t1,t2,
                                                       resampleProbability=resampleProbability,
                                                       **kwargs)
            lw = nicelog(self.proposer_weights[idx])
            lps += [lw+lp]
        return logsumexp(lps)

if __name__ == "__main__": # test code
    from LOTlib3.Examples.Magnetism.Simple import grammar, make_data
    from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis
    from LOTlib3.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood
    from LOTlib3.Hypotheses.Proposers.RegenerationProposal import RegenerationProposer
    from LOTlib3.Hypotheses.Proposers.CopyProposal import CopyProposer
    from LOTlib3.Inference.Samplers.StandardSample import standard_sample

    class CRHypothesis(BinaryLikelihood, MixtureProposer, LOTHypothesis):
        """
        A recursive LOT hypothesis that computes its (pseudo)likelihood using a string edit
        distance
        """
        def __init__(self, *args, **kwargs ):
            LOTHypothesis.__init__(self, grammar, display='lambda x,y: %s', **kwargs)
            super(CRHypothesis, self).__init__(*args, **kwargs)

    def make_hypothesis(**kwargs):
        return CRHypothesis(proposers=[RegenerationProposer(),CopyProposer()],proposer_weights=[1.0,1.0],**kwargs)

    standard_sample(make_hypothesis, make_data, save_top=False)
