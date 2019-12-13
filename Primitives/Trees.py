from LOTlib3.Eval import primitive
from LOTlib3.FunctionNode import FunctionNode, isFunctionNode

import re ## TODO: WHY? PROBABLY BAD FORM

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tree operations
# In a tree T, check relations between some elements. Sometimes T is
# not used, but we leave it in all functions for simplicity
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@primitive
def is_(x,y): return (x is y)

@primitive
def equals_(x,y): return (x == y)

@primitive
def co_referents_(T,x):
    """
            The co-referents of x in t
    """
    return [si for si in T if co_refers(si,x)]

@primitive
def sisters_(x, y, equality=False):
    """
            Check if x,y are sisters in T
    """
    if not(isFunctionNode(x) and isFunctionNode(y)):
        return False

    return (x.parent is not None) and x.parent == y.parent

#@ We define a non-LOTlib version so we can use this in other definitions
def immediately_dominates(x, y):
    if isinstance(x, FunctionNode):
        for s in x.args:
            if s is y: return True

    return False

@primitive
def immediately_dominates_(x, y):
    return immediately_dominates(x,y)

@primitive
def dominates_(x,y):
    """
            This checks if x >> y, but using object identity ("is") rather than equality
    """
    if x is y: return False # A node does not dominate itself

    if isinstance(x, FunctionNode):
        for s in x:
            if s is y:
                return True
    return False

@primitive
def tree_up_(x):
    if isFunctionNode(x):
        return x.parent
    else:
        return None


@primitive
def children_(x):
    if isinstance(x, FunctionNode): return [ c for c in x.args ]
    else: return []

@primitive
def descendants_(x):
    if isinstance(x, FunctionNode): return [ c for c in x ]
    else: return []

@primitive
def tree_root_(T):
    return T

@primitive
def is_nonterminal_type_(x,y): return is_nonterminal_type(x,y)

no_coref_regex = re.compile(r"\..+$")
def is_nonterminal_type(x,y):
    # Check if x is of a given type, but remove corefence information from X (y is the type)

    if x is None or y is None: return False
    if isinstance(x,list): return False # a list can't be a nonterminal

    if not isinstance(x,str): x = x.name

    # remove the .coreference info
    x = no_coref_regex.sub("", x)

    return (x==y)

@primitive
def ancestors_(x):
    if not isFunctionNode(x):
        return []

    out = []
    while x.parent is not None:
        out.append(x.parent)
        x = x.parent
    return out

@primitive
def whole_tree_(T):
    # LIST type of all elements of T
    return [ti for ti in T ]

@primitive
def tree_is_(x,y): return (x is y)


@primitive
def non_xes_(x,T):
    return [v for v in T if v is not x]

import re

coref_matcher = re.compile(r".+\.([0-9]+)$") ## Co-reference (via strings)
@primitive
def co_refers_(x,y):

    if x is y: return False # By stipulation, nothing co-refers to itself

    # Weird corner cases
    if isinstance(x,list) or isinstance(y,list): return False
    if x is None or y is None: return False

    ## Check if two FunctionNodes or strings co-refer (e.g. are indexed with the same .i in their name)
    xx = x.name if isFunctionNode(x) else x
    yy = y.name if isFunctionNode(y) else y

    mx = coref_matcher.search(xx)
    my = coref_matcher.search(yy)

    if mx is None or my is None:
        return False
    else:
        return (mx.groups("X")[0] == my.groups("Y")[0]) # set the default in groups so that they won't be equal if there is no match