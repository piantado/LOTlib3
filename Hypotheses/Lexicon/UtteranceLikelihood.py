


"""
    Sample an utterance out of some possible ones
"""

from .SimpleLexicon import SimpleLexicon

class UtteranceLikelihood(SimpleLexicon):

    def compute_single_likelihood(self, datum):
        """
        Compute the likelihood of a single data point.
        NOTE: This defaultly assumes datum is an UtteranceData, and that we sampled from the true
        ones with probability alpha
        """

        if self(datum.utterance, datum.context):
            possible = [u for u in datum.possible_utterances if self(u, datum.context)]
            p = self.alpha / len(possible)

        p += (1.-self.alpha) / len(datum.possible_utterances)

        return log(p)