
from .SimpleLexicon import SimpleLexicon
from LOTlib3.Eval import RecursionDepthException

class RecursiveLexicon(SimpleLexicon):
    """
    A lexicon where word meanings can call each other. Analogous to a RecursiveLOTHypothesis from a LOTHypothesis.

    To achieve this, we require the LOThypotheses in self.values to take a "recurse" call that is always passed in by
    default here on __call__ as the first argument.

    This throws a RecursionDepthException when it gets too deep.

    See Examples.EvenOdd

    """
    def __init__(self, recursive_depth_bound=10, *args, **kwargs):
        self.recursive_depth_bound = recursive_depth_bound
        SimpleLexicon.__init__(self, *args, **kwargs)

    def __call__(self, word, *args):
        """
        Wrap in self as a first argument that we don't have to in the grammar. This way, we can use self(word, X Y) as above.
        """
        self.recursive_call_depth = 0
        return self.value[word](self.recursive_call, *args)  # pass in "self" as lex, using the recursive version

    def recursive_call(self, word, *args):
        """
        This gets called internally on recursive calls. It keeps track of the depth to allow us to escape
        """
        self.recursive_call_depth += 1
        if self.recursive_call_depth > self.recursive_depth_bound:
            raise RecursionDepthException

        return self.value[word](self.recursive_call, *args)