"""
    Standard PCFG prior for LOTHypotheses
"""
from LOTlib3.Miscellaneous import attrmem, Infinity

class PCFGPrior(object):

    @attrmem('prior')
    def compute_prior(self):
        """Compute the log of the prior probability.
        """
        # If we exceed the maximum number of nodes, give -Infinity prior
        if self.value.count_subnodes() > getattr(self, 'maxnodes', Infinity):

            return -Infinity

        else:

            # Compute the grammar's probability
            return self.grammar.log_probability(self.value) / self.prior_temperature
