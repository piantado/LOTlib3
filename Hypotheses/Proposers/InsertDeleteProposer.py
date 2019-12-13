"""Mixing Insert and Delete Proposers for backward compatibility"""

from LOTlib3.Hypotheses.Proposers.DeleteProposer import *
from LOTlib3.Hypotheses.Proposers.InsertProposer import *
from LOTlib3.Hypotheses.Proposers.MixtureProposer import *
from LOTlib3.Miscellaneous import lambdaOne, nicelog

class InsertDeleteProposer(MixtureProposer):
    def __init__(self):
        MixtureProposer.__init__(self,proposers=[InsertProposer(),DeleteProposer()],proposer_weights=[1.0,1.0])

if __name__ == "__main__": # test code
    from LOTlib3.Examples.Magnetism.Simple import grammar, make_data
    from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis
    from LOTlib3.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood
    from LOTlib3.Inference.Samplers.StandardSample import standard_sample

    class CRHypothesis(BinaryLikelihood, InsertDeleteProposer, LOTHypothesis):
        """
        A recursive LOT hypothesis that computes its (pseudo)likelihood using a string edit
        distance
        """
        def __init__(self, *args, **kwargs ):
            LOTHypothesis.__init__(self, grammar, display='lambda x,y: %s', **kwargs)
            super(CRHypothesis, self).__init__(*args, **kwargs)

    def make_hypothesis(**kwargs):
        return CRHypothesis(**kwargs)

    standard_sample(make_hypothesis, make_data, save_top=False)
