import numpy
from copy import copy
from scipy.stats import norm
from scipy.stats import dirichlet, gamma, beta

from LOTlib3 import break_ctrlc
from LOTlib3.Miscellaneous import Infinity, attrmem, logit, ilogit, sample1
from LOTlib3.Hypotheses.Hypothesis import Hypothesis


class Stochastic(Hypothesis):
    """
    A Stochastic is a small class to allow MCMC on hypothesis parameters like temperature, noise, etc.
    It works as a Hypothesis, but is typically stored as a component of another hypothesis.
    """
    @attrmem('likelihood')
    def compute_likelihood(self, data, shortcut=-Infinity, **kwargs):
        #raise NotImplementedError
        return 0.0

class NormalDistribution(Stochastic):

    def __init__(self, value=None, mean=0.0, sd=1.0, proposal_sd=1.0, **kwargs):
        Stochastic.__init__(self, value=value, **kwargs)
        self.mean = mean
        self.sd   = sd
        self.proposal_sd = proposal_sd

        if value is None:
            self.set_value(norm.rvs(loc=mean, scale=sd))

    @attrmem('prior')
    def compute_prior(self):
        return norm.logpdf(self.value, loc=self.mean, scale=self.sd)

    def propose(self):
        ret = copy(self)
        ret.value = norm.rvs(loc=self.value, scale=self.proposal_sd)

        return ret, 0.0 # symmetric

class GammaDistribution(Stochastic):

    def __init__(self, value=None, a=1.0, scale=1.0, proposal_scale=1.0, **kwargs):
        Stochastic.__init__(self, value=value, **kwargs)
        self.a = a
        self.scale = scale
        self.proposal_scale = proposal_scale

        if value is None:
            self.set_value(gamma.rvs(a, scale=scale))

    @attrmem('prior')
    def compute_prior(self):
        return gamma.logpdf(self.value, self.a, scale=self.scale)

    def propose(self):
        ret = copy(self)
        ret.value = gamma.rvs(self.value * self.proposal_scale, scale=1./self.proposal_scale)

        fb = gamma.logpdf(ret.value, self.value * self.proposal_scale, scale=1./self.proposal_scale) -\
             gamma.logpdf(self.value, ret.value * self.proposal_scale, scale=1./self.proposal_scale)

        return ret, fb

class LogitNormalDistribution(Stochastic):
    """
    Same as NormalDistribution, but value stores the logit value
    """

    def __init__(self, value=None, mean=0.0, sd=1.0, proposal_sd=1.0, **kwargs):
        Stochastic.__init__(self, value=value, **kwargs)
        self.mean = mean
        self.sd   = sd
        self.proposal_sd = proposal_sd

        if value is None:
            self.set_value(ilogit(norm.rvs(loc=mean, scale=sd)))

    @attrmem('prior')
    def compute_prior(self):
        return norm.logpdf(logit(self.value), loc=self.mean, scale=self.sd)

    def propose(self):
        ret = copy(self)
        ret.value = ilogit(norm.rvs(loc=logit(self.value), scale=self.proposal_sd))

        return ret, 0.0 # symmetric


class DirichletDistribution(Stochastic):

    SMOOTHING = 1e-6

    def __init__(self, value=None, alpha=None, proposal_scale=50.0, **kwargs):
        """
        Can be specified as value=numpy.array([...]), n= and alpha=
        """
        self.alpha = alpha

        if value is None and alpha is not None:
            value = numpy.random.dirichlet(alpha)

        Stochastic.__init__(self, value=value, **kwargs)

        self.proposal_scale = proposal_scale

    @attrmem('prior')
    def compute_prior(self):
        return dirichlet.logpdf(self.value, self.alpha)

    def propose(self):

        if len(self.value) == 1: return copy(self), 0.0 # handle singleton rules

        v = numpy.random.dirichlet(self.value * self.proposal_scale)

        # add a tiny bit of smoothing away from 0/1
        v = (1.0 - DirichletDistribution.SMOOTHING) * v + DirichletDistribution.SMOOTHING / 2.0
        # and renormalize it (both slightly breaking MCMC)
        v = v / sum(v)

        ret = copy(self)
        ret.set_value(v)

        fb = dirichlet.logpdf(ret.value, self.value * self.proposal_scale) -\
             dirichlet.logpdf(self.value, ret.value * self.proposal_scale)

        return ret, fb

class GibbsDirchlet(DirichletDistribution):

    def propose(self):
        ret = copy(self)

        if len(ret.value) == 1: return ret, 0.0 # handle singleton rules

        inx = sample1(list(range(0,self.alpha.shape[0])))
        ret.value[inx] = numpy.random.beta(self.value[inx]*self.proposal_scale,
                                           self.proposal_scale - self.value[inx] * self.proposal_scale)

        # add a tiny bit of smoothing away from 0/1
        ret.value[inx] = (1.0 - DirichletDistribution.SMOOTHING) * ret.value[inx] + DirichletDistribution.SMOOTHING / 2.0
        v = sum(ret.value)

        fb = sum(gamma.logpdf(ret.value, self.value)) + gamma.logpdf(v, 1) -\
             sum(gamma.logpdf(self.value, ret.value)) - gamma.logpdf(1, v)


        # and renormalize it, slightly breaking MCMC
        ret.value = ret.value / sum(ret.value)

        return ret, fb

class PriorDirichletDistribution(DirichletDistribution):
    """ propose from the prior (useful for debugging)
    """

    def propose(self):
        if len(self.value) == 1: return PriorDirichletDistribution(value=self.value,alpha=self.value), 0.0 # handle singleton rules

        ret = PriorDirichletDistribution(value = numpy.random.dirichlet(self.alpha), alpha=self.alpha)

        fb = dirichlet.logpdf(ret.value, self.alpha) - dirichlet.logpdf(self.value, self.alpha)

        return ret, fb

class BetaDistribution(DirichletDistribution):
    def __init__(self, a=1, b=1, **kwargs):
        DirichletDistribution.__init__(self, alpha=[a,b], **kwargs)



if __name__ == "__main__":
    from LOTlib3.Inference.Samplers.MetropolisHastings import MHSampler

    h0 = BetaDistribution(1,2)
    for h in break_ctrlc(MHSampler(h0, [])):
        print(h)