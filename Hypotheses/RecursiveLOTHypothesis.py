
from .LOTHypothesis import LOTHypothesis, raise_exception
from LOTlib3.Eval import RecursionDepthException, TooBigException, EvaluationException

class RecursiveLOTHypothesis(LOTHypothesis):
    """
    A LOTHypothesis that permits recursive calls to itself via the primitive "recurse" (previously, L).

    Here, RecursiveLOTHypothesis.__call__ does essentially the same thing as LOTHypothesis.__call__, but it binds
    the symbol "recurse" to RecursiveLOTHypothesis.recursive_call so that recursion is processed internally.

    This bind is done in compile_function, NOT in __call__

    For a Demo, see LOTlib3.Examples.Number
    """

    def __init__(self, grammar, recurse_bound=25, display="lambda recurse_, x: %s", **kwargs):
        """
        Initializer. recurse gives the name for the recursion operation internally.
        """
        assert "lambda recurse_" in display, "*** RecursiveLOTHypothesis must have 'recurse_' as first display element." # otherwise it can't eval

        # save recurse symbol
        self.recursive_depth_bound = recurse_bound # how deep can we recurse?
        self.recursive_call_depth = 0 # how far down have we recursed?

        LOTHypothesis.__init__(self, grammar, display=display)

    def recursive_call(self, *args):
        """
        This gets called internally on recursive calls. It keeps track of the depth and throws an error if you go too deep
        """

        self.recursive_call_depth += 1

        if self.recursive_call_depth > self.recursive_depth_bound:
            raise RecursionDepthException

        # Call with sending myself as the recursive call
        return LOTHypothesis.__call__(self, self.recursive_call, *args)

    def __call__(self, *args):
        """
        The main calling function. Resets recursive_call_depth and then calls
        """
        self.recursive_call_depth = 0

        # call with passing self.recursive_Call as the recursive call
        return LOTHypothesis.__call__(self, self.recursive_call, *args)

