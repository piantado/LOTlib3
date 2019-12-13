
from LOTlib3.Miscellaneous import Infinity, normlogpdf
from math import isnan

class GaussianLikelihood(object):

    def compute_single_likelihood(self, datum):
        """ Compute the likelihood with a Gaussian. Wraps to avoid nan"""

        ret = normlogpdf(self(*datum.input), datum.output, datum.ll_sd)

        if isnan(ret):
            return -Infinity
        else:
            return ret

class MultidimensionalGaussianLikelihood(object):
    """ Assumes that the output is a vector and everything is normal
    """
    def compute_single_likelihood(self, datum):
        v = self(*datum.input)

        ret = sum([normlogpdf(vi, di, datum.ll_sd) for vi, di in zip(v, datum.output)])

        if isnan(ret):
            return -Infinity
        else:
            return ret