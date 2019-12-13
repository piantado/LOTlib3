from LOTlib3.Miscellaneous import Infinity, attrmem
from copy import copy, deepcopy
import numpy

class Hypothesis(object):
    """A hypothesis bundles together a value (hypothesis value) with a bunch of remembered states,
    like posterior_score, prior, likelihood.

    This class is typically a superclass of the thing you really want.

    Note:
        Temperatures: By default, a Hypothesis has a prior_temperature and likelihood_temperature. These
          are taken into account in setting the posterior_score (for computer_prior and compute_likelihood),
          in the values returned by these, AND in the stored values under self.prior and self.likelihood

    Args:
        value: The default value for the hypothesis.
        prior_temperature: Temperature used when running compute_prior.
        likelihood_temperature: Temperature used when running compute_likelihood.

    """
    def __init__(self, value=None, prior_temperature=1.0, likelihood_temperature=1.0, display="%s", **kwargs):
        """
        :param value:  - the value of teh hypothesis
        :param prior_temperature: A prior temperature to be included in compute_prior
        :param likelihood_temperature: A likelihood temperature to be included in compute_likelihood
        :param display: A string specifying the display formatting
        :param kwargs: Additional arguments
        :return:
        """
        self.display = display
        self.__dict__.update(kwargs)

        self.set_value(value)

        # zero out prior, likelhood, posterior_score
        self.prior, self.likelihood, self.posterior_score = [-Infinity, -Infinity, -Infinity]
        self.prior_temperature = prior_temperature
        self.likelihood_temperature = likelihood_temperature
        self.stored_likelihood = None


    def set_value(self, value):
        """Sets the (self.)value of this hypothesis to value."""
        self.value = value

    def __copy__(self, value=None):
        """Returns a copy of the Hypothesis. Allows you to pass in value to set to that instead of a copy."""

        thecopy = type(self)() # Empty initializer

        # copy over all the relevant attributes and things.
        # Note objects like Grammar are not copied
        thecopy.__dict__.update(self.__dict__)

        # and then we need to explicitly *deepcopy* the value (in case its a dict or tree, or whatever)
        if value is None:
            value = deepcopy(self.value)

        thecopy.set_value(value)

        return thecopy

    # ========================================================================================================
    #  All instances of this must implement these:

    @attrmem('prior')
    def compute_prior(self):
        """Compute the prior and stores it in self.prior.

        Note:
            This method must be implemented when writing subclasses of Hypothesis
            This *should* take into account prior_temperature

        """
        raise NotImplementedError

    def compute_single_likelihood(self, datum, **kwargs):
        """Compute the likelihood of a single data point datum, under this hypothesis.

        Note:
            This method must be implemented when writing subclasses of Hypothesis.
            It should NOT take into account likelihood_temperature, as this is done in compute_likelihood.

        """
        raise NotImplementedError

    # And the main likelihood function just maps compute_single_likelihood over the data
    @attrmem('likelihood')
    def compute_likelihood(self, data, shortcut=-Infinity, **kwargs):
        """Compute the likelihood of the iterable of data.

        This is typically NOT subclassed, as compute_single_likelihood is what subclasses should implement.

        Shortcut here allows us to stop evaluation if the likelihood falls below the shortcut value (taking into account temperature)

        Versions using decayed likelihood can be found in Hypothesis.DecayedLikelihoodHypothesis.
        """

        ll = 0.0
        for datum in data:
            ll += self.compute_single_likelihood(datum, **kwargs) / self.likelihood_temperature
            if ll < shortcut:
                # print "** Shortcut", self
                return -Infinity

        return ll

    def compute_predictive_likelihood(self, data, include_last=False, **kwargs):
        """
        The predictive likelihood is a list of likelihoods aligned to data. The i'th predictive likelihood
        is the likelihood of 0..(i-1) data points (thus it is the likelihood used in the predictive
        posterior for the i'th data point)
        """

        # all but the last data point unless include_last
        lls = [0.0] + [self.compute_single_likelihood(datum, **kwargs) for datum in data[:(None if include_last else -1)]]

        return numpy.cumsum(lls)

    # ========================================================================================================
    #  Methods for accessing likelihoods etc. on a big arrays of data

    def propose(self):
        """Generic proposal used by MCMC methods.

        This should return a list fb, newh, where fb is the forward-minus-backward log probability of the
        proposal, and newh is the proposal itself (of the same type as self).

        Note:
            This method must be implemented when writing subclasses of Hypothesis

        """
        raise NotImplementedError

    @attrmem('posterior_score')
    def compute_posterior(self, d, **kwargs):
        """Computes the posterior score by computing the prior and likelihood scores.
        Defaultly if the prior is -inf, we don't compute the likelihood (and "pretend" it's -Infinity).
        This saves us from computing likelihoods on hypotheses that we know are bad.
        """

        p = self.compute_prior()
        
        if p > -Infinity:
            l = self.compute_likelihood(d, **kwargs)
            return p + l
        else:
            self.likelhood = None # We haven't computed this
            return -Infinity

    def update_posterior(self):
        """So we can save on space when writing this out in every hypothesis."""
        self.posterior_score = self.prior + self.likelihood

    # ========================================================================================================
    #  These are just handy:
    def __str__(self):
        return self.display % str(self.value)
    def __repr__(self):
        return str(self)

    # for hashing hypotheses
    def __hash__(self):
        return hash(self.value)
    def __cmp__(self, x):
        return cmp(self.value, x.value)

    # this is for heapq algorithm in FiniteSample, which uses <= instead of cmp
    # since python implements a "min heap" we can compare log probs
    def __le__(self, x):
        return self.posterior_score <= x.posterior_score
    def __eq__(self, other):
        return self.value.__eq__(other.value)
    def __ne__(self, other):
        return self.value.__ne__(other.value)
