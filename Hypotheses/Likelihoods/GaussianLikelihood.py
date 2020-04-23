
from LOTlib3.Miscellaneous import Infinity, normlogpdf
from math import isnan

class GaussianLikelihood(object):

    def compute_single_likelihood(self, datum):
        """ Compute the likelihood with a Gaussian. Wraps to avoid nan"""

        try:
            ret = normlogpdf(self(*datum.input), datum.output, datum.ll_sd)
            if isnan(ret):
                return -Infinity
            return ret
        except: # catch general fp errors
            return -Infinity
