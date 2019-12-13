

"""Mixing Insert and Delete Proposers for backward compatibility"""

from LOTlib3.Hypotheses.Proposers.DeleteProposer import *
from LOTlib3.Hypotheses.Proposers.InsertProposer import *
from LOTlib3.Hypotheses.Proposers.RegenerationProposer import *
from LOTlib3.Hypotheses.Proposers.MixtureProposer import *
from LOTlib3.Miscellaneous import lambdaOne, nicelog

class InsertDeleteRegenerationProposer(MixtureProposer):
    def __init__(self, proposer_weights=[1.0,1.0,1.0]):
        MixtureProposer.__init__(self,proposers=[InsertProposer(),DeleteProposer(), RegenerationProposer()],proposer_weights=proposer_weights)

