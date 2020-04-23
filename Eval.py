"""
    Routines for evaling
"""
import sys
import builtins

class EvaluationException(Exception):
    pass

class TooBigException(EvaluationException):
    pass

class RecursionDepthException(EvaluationException):
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# We define two variables, one for how many function calls have been
# used in a single function/hypothesis, and one for how many have been
# run over the entire course of the experiment
# LOCAL_PRIMITIVE_OPS = 0
# GLOBAL_PRIMITIVE_OPS = 0
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def primitive(fn):
    """A decocator for basic primitives that increments our counters. Used to be known as @LOTlib_primitive"""

    """
    def inside(*args, **kwargs):

        global LOCAL_PRIMITIVE_OPS
        LOCAL_PRIMITIVE_OPS += 1

        global GLOBAL_PRIMITIVE_OPS
        GLOBAL_PRIMITIVE_OPS += 1

        return fn(*args, **kwargs)

    return inside
    """

    # Just register the primitive
    register_primitive(fn)

    return fn


def None2None(fn):
    """
    A decorator to map anything with "None" as a *list* arg (NOT a keyword arg)
    this will make it return None overall

    If you want to have this not prevent incrementing (via LOTlib_primitive), then
    we need to put it *after* LOTlib_primitive:

    @None2None
    def f(...):

    """
    def inside(*args, **kwargs):
        if any([a is None for a in args]): return None
        return fn(*args, **kwargs)

    return inside

def register_primitive(function, name=None):
    """
        This allows us to load new functions into the evaluation environment.
        Defaultly all in LOTlib3.Primitives are imported. However, we may want to add our
        own functions, and this makes that possible. As in,

        register_primitive(flatten)

        or

        register_primitive(flatten, name="myflatten")

        where flatten is a function that is defined in the calling context and name
        specifies that it takes a different name when evaled in LOTlib

        NOTE: For primitives, this is now defaultly called by the decorator @LOT_primitive

    """

    if name is None: # if we don't specify a name
        name = function.__name__

        builtins.__dict__[name] = function

