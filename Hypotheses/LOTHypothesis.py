from LOTlib3.Eval import * # Necessary for compile_function eval below
from LOTlib3.Hypotheses.FunctionHypothesis import FunctionHypothesis
from LOTlib3.Hypotheses.Proposers import ProposalFailedException
from LOTlib3.Miscellaneous import self_update
from LOTlib3.Primitives import *
from .Priors.PCFGPrior import PCFGPrior
from .Proposers import regeneration_proposal

class LOTHypothesis(PCFGPrior, FunctionHypothesis):
    """A FunctionHypothesis built from a grammar.

    Arguments
    ---------
    grammar : LOTlib3.Grammar
        The grammar for the hypothesis.
    value : FunctionNode
        The value for the hypothesis.
    maxnodes : int
        The maximum amount of nodes that the grammar can have
    args : list
        The arguments to the function.

    Attributes
    ----------
    grammar_vector : np.ndarray
        This is a vector of
    prior_vector : np.ndarray

    """

    def __init__(self, grammar=None, value=None, f=None, maxnodes=25, **kwargs):

        if 'args' in kwargs:
            assert False, "*** Use of 'args' is deprecated. Use display='...' instead."

        # Save all of our keywords
        self_update(self, locals())
        if value is None and grammar is not None:
            value = grammar.generate()

        FunctionHypothesis.__init__(self, value=value, f=f, **kwargs)

        self.likelihood = 0.0
        self.rules_vector = None

    def __call__(self, *args):
        # NOTE: This no longer catches all exceptions.
        try:
            return FunctionHypothesis.__call__(self, *args)
        except TypeError as e:
            print("TypeError in function call: ", e, str(self), "  ;  ", type(self), args)
            raise TypeError
        except NameError as e:
            print("NameError in function call: ", e, " ; ", str(self), args)
            raise NameError

    def type(self):
        return self.value.type()

    def compile_function(self):
        """Called in set_value to compile into a function."""
        if self.value.count_nodes() > self.maxnodes:
            return lambda *args: raise_exception(TooBigException)
        else:
            try:
                return eval(str(self)) # evaluate_expression(str(self))
            except Exception as e:
                print("# Warning: failed to execute evaluate_expression on [" + str(self)+"]")
                print("# ", e)
                return lambda *args: raise_exception(EvaluationException)

    def compute_single_likelihood(self, datum):
        raise NotImplementedError

    def propose(self, **kwargs):
        ret_value, fb = None, None
        while True: # keep trying to propose
            try:
                ret_value, fb = regeneration_proposal(self.grammar, self.value, **kwargs)
                break
            except ProposalFailedException:
                pass

        ret = self.__copy__(value=ret_value)

        return ret, fb
