from LOTProposer import LOTProposer
import numpy
from LOTlib3.Miscellaneous import weighted_sample
from LOTlib3.Hypotheses.Proposers import ProposalFailedException

from RegenerationProposer  import RegenerationProposer
from InsertDeleteProposer  import InsertDeleteProposer
from .InverseInlineProposer import InverseInlineProposer
N_PROPOSALS = 3

class MixtureProposer(LOTProposer):
    """
      For now our MixtureProposal will mix together InsertDelete, InverseInline and Regeneration, but some weights
      can be set to zero.

    """

    def set_proposal_probabilities(self, proposals, probs=None):
        self.proposals = proposals

        if probs is None:
            probs = numpy.array([1.] * len(proposals))

        self.proposal_probabilities = probs

    def propose_tree(self, t, **kwargs):

        while True:
            try:
                idx = weighted_sample(list(range(N_PROPOSALS)), probs=getattr(self, 'proposal_probabilities', numpy.ones(N_PROPOSALS)), log=False)

                if idx == 0:
                    return RegenerationProposer.propose_tree(t, **kwargs)
                elif idx == 1:
                    return InsertDeleteProposer.propose_tree(t, **kwargs)
                elif idx == 2:
                    return InverseInlineProposer.propose_tree(t, **kwargs)

            except ProposalFailedException: # Proposal fails, keep looping
                pass
