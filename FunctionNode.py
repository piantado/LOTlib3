# -*- coding: utf-8 -*-

import re
from copy import copy, deepcopy
from math import log
from random import random

from LOTlib3.BVRuleContextManager import BVRuleContextManager
from LOTlib3.Miscellaneous import lambdaTrue, lambdaOne, self_update, nicelog


# ------------------------------------------------------------------------------------------------------------
# Helper functions

def isFunctionNode(x):
    # Just because this is nicer, and allows us to map, etc.
    """Returns true if *x* is of type FunctionNode."""
    return isinstance(x, FunctionNode)


def cleanFunctionNodeString(x):
    """Makes FunctionNode strings easier to read."""
    s = re.sub("lambda", "\u03BB", str(x))  # make lambdas the single char
    s = re.sub("_", '', s)  # remove underscores
    return s


# ------------------------------------------------------------------------------------------------------------
# Handle exceptions when sampling

class NodeSamplingException(Exception):
    """Raised when we try to sample a subnode, but nothing has nonzero probability."""
    pass


# ------------------------------------------------------------------------------------------------------------
# FunctionNode main class

class FunctionNode(object):
    """FunctionNode main class.

    Arguments
    ---------
    returntype : type
        The return type of the FunctionNode.
    name : doc?
        The name of the function.
    args : doc?
        Arguments of the function
    bv : doc?
        Stores the actual *rule* that was added (so that we can re-add it when we loop through the tree).

    Note
    ----
    * If a node has [ None ] as args, it is treated as a thunk
    * Each FunctionNode used to store the rule that generated it. This caused problems when loading a FunctionNode from
      a pickle file and trying to compute its probability under a new grammar. Now, matching to rules is done on the fly
      using get_rule_signature()

    """
    NoCopy = {'self', 'parent', 'returntype', 'name', 'args', 'parent'}

    def __init__(self, parent, returntype, name, args):
        self_update(self,locals())
        self.added_rule = None
        
        assert self.name is None or isinstance(self.name, str)

    def setto(self, q):
        """Makes all the parts the same as q, not copies.

        Note that this sets the parent of q to my current parent!

        """
        old_parent = self.parent        # preserve my parent
        self.__dict__ = q.__dict__
        self.__class__ = q.__class__    # to update in case q is a different subtype of FunctionNode.
                                        # NOTE: Setting __class__ is not a recommended thing to do.
        # and we must fix the kid refs. Everything else should be right.
        for a in self.argFunctionNodes():
            a.parent = self
        self.parent = old_parent

    def get_rule_signature(self):
        """ The rule signature is used to pair up FunctionNodes with GrammarRules in computing log probability
            So it needs to be synced to GrammarRule.get_rule_signature and provide a unique identifier
        """
        sig = [self.returntype, self.name]
        if self.args is not None:
            sig.extend([a.returntype if isFunctionNode(a) else a for a in self.args])
        return tuple(sig)

    def __copy__(self, shallow=False):
        """Copy a function node.

        Arguments
        ---------
        shallow : bool
            if True, this does not copy the children (self.to points to the same as what we return)

        Note
        ----
        The rule is NOT deeply copied (regardless of shallow)

        """
        fn = FunctionNode(self.parent, self.returntype, self.name, None)

        # And then then copy the rest -- needed for if we add info to FunctionNodes, like a resample_p
        for k in set(self.__dict__.keys()).difference(FunctionNode.NoCopy): # None of these!
            fn.__dict__[k] = copy(self.__dict__[k])

        if (not shallow) and self.args is not None:
            fn.args = list(map(copy, self.args))
        else:
            fn.args = self.args

        # and update 
        for a in fn.argFunctionNodes():
            a.parent = fn 

        return fn 
        
    def is_nonfunction(self):
        """Returns True if the Node contains no function arguments, False otherwise."""
        return self.args is None

    def is_function(self):
        """Returns True if the Node contains function arguments, False otherwise."""
        return not self.is_nonfunction()

    def is_leaf(self):
        """Returns True if none of the kids are FunctionNodes, meaning this should be considered a "leaf".

        Note
        ----
        A leaf may be a function, but its args are specified in the grammar.

        """
        return (self.args is None) or all([not isFunctionNode(c) for c in self.args])

    def is_root(self):
        return self.parent is None
    
    def check_parent_refs(self):
        """Recurse through the tree and ensure that the parent refs are good."""
        for t in self.argFunctionNodes():
            if (t.parent is not self) or (t.check_parent_refs() is not True):
                print("Bad parent reference at %s" % t.name)
                print("If it prints, the full string is %s, a subnode of %s, whose parent is %s" % \
                      (t, self, t.parent))
                return False
            
        return True

    def as_list(self, d=0, bv_names=None):
        """Returns a list representation of the FunctionNode with function/self.name as the first element.

        This function is subclassed so by BVAdd and BVUse so that those handle other cases

        Arguments
        ---------
        d : int
            An optional argument that keeps track of how far down the tree we are
        bv_names : dict
            A dictionary keeping track of the names of bound variables (keys = UUIDs, values = names)

        """
        # the tree should be represented as the empty set if the function node has no name
        if self.name == '':
            x = []
        else:
            x = [self.name]
            
        # and we're now ready to loop over the function node's arguments
        if self.args is not None:
            x.extend([a.as_list(d=d+1, bv_names=bv_names) if isFunctionNode(a) else a for a in self.args])
        
        return x

    # --------------------------------------------------------------------------------------------------------

    def quickstring(self):
        """A (maybe??) faster string function used for hashing.

        Doesn't handle any details and is meant to just be quick.

        """
        if self.args is None:
            return str(self.name)  # simple call

        else:
            # Don't use + to concatenate strings.
            return '{} {}'.format(str(self.name), ','.join(map(str, self.args)))

    def fullprint(self, d=0):
        """A handy printer for debugging"""
        tabstr = "  .  " * d
        print(tabstr, self.returntype, self.name, "\t", self.added_rule)


        if self.args is not None:
            for a in self.args:
                if isFunctionNode(a):
                    a.fullprint(d+1)
                else:
                    print(tabstr, a)


    def liststring(self, cons="cons_"):
        """This "evals" cons_ so that we can conveniently build lists (of lists) without having to eval.

        Mainly useful for combinatory logic, or "pure" trees

        """
        if self.args is None:
            return self.name
        elif self.name == cons:
            return [x.liststring() for x in self.args]
        else:
            assert False, "FunctionNode must only use cons to call liststring!"

    # NOTE: in the future we may want to change this to do fancy things
    def __str__(self):
        return pystring(self)

    def __repr__(self):
        return pystring(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """Check if two FunctionNodes are equal.

        This is actually a little subtle due to bound variables.

        In (lambda (x) x) and (lambda (y) y) will be equal (since they map to identical strings via
        fullstring), even though the nodes below x and y will not themselves be equal. This is because
        fullstring(x) and fullstring(y) will not know where these came from and will just compare the uuids.

        But fullstring on the lambda keeps track of where bound variables were introduced.

        NOTE: We need to do thsi using fullstring instead of pystring in order to avoid the fact that pystring ignores
        returntypes and nodes whose name is ''

        """
        return fullstring(self) == fullstring(other)

    # TODO: overwrite these with something faster
    # hash trees. This just converts to string -- maybe too slow?
    def __hash__(self):
        # # An attempt to speed things up -- not so great!
        # hsh = self.ruleid
        # if self.args is not None:
        #     for a in filter(isFunctionNode, self.args):
        #         hsh = hsh ^ hash(a)
        # return hsh
        #
        # # use a quicker string hash
        # return hash(self.quickstring())

        # normal string hash -- faster?
        return hash(str(self))


    def __cmp__(self, x):
        return cmp(str(self), str(x))

    def __len__(self):
        return len([a for a in self])

    def log_probability(self):
        """Compute the log probability of a tree."""
        assert False, "*** New change: You must compute log_probability from a grammar. "

    def subnodes(self):
        """Return all subnodes -- no iterator

        """
        return [g for g in self]

    def nargs(self):
        """
        :return: the number of arguments, or -1 if our self.args is None
        """
        if self.args is None:
            return -1
        else:
            return len(self.args)

    def argFunctionNodes(self):
        """Yield FunctionNode immediately below.

        Also handles args is None, so we don't have to check constantly

        """
        if self.args is not None:
            for n in self.args:
                if isFunctionNode(n):
                    yield n

    def argNonFunctionNodes(self):
        """Yield non-FunctionNode immediately below.

        Also handles args is None, so we don't have to check constantly

        """
        if self.args is not None:
            for n in self.args:
                if not isFunctionNode(n):
                    yield n

    def argStrings(self):
        """
        Yields strings below (e.g. non-FunctionNodes), handling None
        """
        if self.args is not None:
            for n in self.args:
                if isinstance(n, str):
                    yield n


    def argTypes(self):
        # A list of the strings or returntypes of by args
        # This should be equal to what my rule produced
        if self.args is None:
            return None
        else:
           return [a.returntype if isinstance(a, FunctionNode) else a for a in self.args]


    def is_terminal(self):
        """A FunctionNode is considered a "terminal" if it has no FunctionNodes below."""
        return self.args is None or len(list(filter(isFunctionNode, self.args))) == 0

    def __iter__(self):
        """Iterater for subnodes.

        Note
        ----
        * This will NOT work if you modify the tree. Then all goes to hell.
        * If the tree must be modified, use self.subnodes().

        """
        yield self

        for a in self.argFunctionNodes():
            for ssn in a:
                yield ssn

    def iterdepth(self):
        """Iterates subnodes, yielding node and depth."""
        yield (self, 0)

        if self.args is not None:
            for a in self.argFunctionNodes():
                for ssn, dd in a.iterdepth():
                    yield (ssn, dd+1)

    def all_leaves(self):
        """Returns a generator for all leaves of the subtree rooted at the instantiated FunctionNode."""
        if self.args is not None:
            for i in range(len(self.args)):  # loop through kids
                if isFunctionNode(self.args[i]):
                    for ssn in self.args[i].all_leaves():
                        yield ssn
                else:
                    yield self.args[i]

    def string_below(self, sep=" "):
        """The string of terminals (leaves) below the current FunctionNode in the parse tree.

        Arguments
        ---------
        sep : str
            is the delimiter between terminals. E.g. sep="," => "the,fuzzy,cat"

        """
        return sep.join(map(str, self.all_leaves()))

    # --------------------------------------------------------------------------------------------------------
    #  Derived functions that build on the above core

    def contains_function(self, x):
        """Checks if the FunctionNode contains x as function below."""
        for n in self:
            if n.name == x:
                return True
        return False
            
    def up_to(self, to=None):
        """Yield all nodes going up to "to". If "to" is None, we go until the root (default)."""
        ptr = self
        while (ptr is not to) and (ptr is not None):
            yield ptr
            ptr = ptr.parent

    def count_nodes(self, **kwargs):
        """Returns the subnode count."""
        return self.count_subnodes(**kwargs)

    def count_subnodes(self, predicate=lambdaTrue):
        """Returns the subnode count."""
        return len(list(filter(predicate, self)))

    def depth(self):
        """Returns the depth of the tree (how many embeddings below)."""
        depths = [a.depth() for a in self.argFunctionNodes()]
        depths.append(-1)  # for no function nodes (+1=0)
        return max(depths)+1

    def sample_node_normalizer(self, resampleProbability=lambdaOne):
        """
        Compute Z to be the sum of all subnodes' value from resampleProbability.
        * resampleProbability -- a function that gives the resample probability (NOT log prob.) of each node.
        NOTE: We allow resampleProbability to return a boolean, for 0/1 probability.
        """
        return sum([ 1.0*resampleProbability(x) for x in self])

    def sampling_log_probability(self,node,resampleProbability=lambdaOne):
        return nicelog(1.0*resampleProbability(node)) - nicelog(self.sample_node_normalizer(resampleProbability=resampleProbability))

    def sample_subnode(self, resampleProbability=lambdaOne):
        """Sample a subnode at random.

        We return a sampled tree and the log probability of sampling it

        """
        Z = self.sample_node_normalizer(resampleProbability=resampleProbability) # the total probability
        if not (Z > 0.0):
            raise NodeSamplingException

        r = random() * Z # now select a random number (giving a random node)

        for t in self:
            trp = float(resampleProbability(t))
            r -= trp
            if r <= 0:
                return [t, log(trp) - log(Z)]

        assert False, "Should not get here"

    # get a description of the input and output types
    # if collapse_terminal then we just map non-FunctionNodes to "TERMINAL"
    def type(self):
        """The type of a FunctionNode is defined to be its returntype if it's not a lambda, or is defined
        to be the correct (recursive) lambda structure if it is a lambda.

        For instance (lambda x. lambda y . (and (empty? x) y))
        is a (SET (BOOL BOOL)), where in types, (A B) is something that takes an A and returns a B

        Note
        ----
        If we don't have a function call (as in START) (i.e. self.name == ''), just use the type of
        what's below

        """
        if self.name == '':
            assert self.nargs() == 1, "**** Nameless calls must have exactly 1 arg"
            return self.args[0].type()
        if not (isinstance(self, BVAddFunctionNode) and self.added_rule is not None):
            return self.returntype
        else:
            # figure out what kind of lambda
            t = []
            if getattr(self, 'added_rule', None) is not None and self.added_rule.to is not None:
                t = tuple( [self.added_rule.nt,] + copy(self.added_rule.to) )
            else:
                t = self.added_rule.nt

            return (self.args[0].type(), t)

    def is_canonical_order(self, symmetric_ops):
        """Take a set of symmetric (commutative) ops (plus, minus, times, etc, not divide) and asserts that
            the LHS ordering is less than the right (to prevent)

        This is useful for removing duplicates of nodes. For instance,

                AND(X, OR(Y,Z))

        is logically the same as

                AND(OR(Y,Z), X)

        This function essentially checks if the tree is in sorted (alphbetical) order, but only for
        functions whose name is in symmetric_ops.

        """
        if self.nargs() < 1: # None or zero args
            return True

        if self.name in symmetric_ops:
            # Then we must check children
            if self.args is not None:
                for i in range(self.nargs()-1):
                    if self.args[i].name > self.args[i+1].name:
                        return False

        # Now check the children, whether or not we are symmetrical
        return all([x.is_canonical_order(symmetric_ops) for x in self.argFunctionNodes() ])

    def replace_subnodes(self, predicate, replace):
        """Set all nodes satifying predicate to a copy of replace.

        Note: we must fix probabilities after this since they may not be right--we can copy into a place
            where a lambda is defined.

        """
        # now go through and modify
        for n in filter(predicate, self.subnodes()):  # NOTE: must use subnodes since we are modfiying
            n.setto(copy(replace))

    def partial_subtree_root_match(self, y):
        """Does *y* match from my root?

        A partial tree here is one with some nonterminals (see random_partial_subtree) that
        are not expanded

        """
        if isFunctionNode(y):
            if (y.returntype != self.returntype) or \
               (y.name != self.name) or \
               (y.nargs() != self.nargs()):
                return False
            if y.args is None:
                return self.args is None

            for a, b in zip(self.args, y.args):
                if isFunctionNode(a):
                    if not a.partial_subtree_root_match(b):
                        return False
                else:
                    if isFunctionNode(b) or \
                            (a != b):
                        return False  # cannot work!
            return True
        else:
            # else y is a string and we match if y is our returntype
            assert isinstance(y, str)
            return y == self.returntype

    def partial_subtree_match(self, y):
        """Does `y` match a subtree anywhere?"""
        for x in self:
            if x.partial_subtree_root_match(y):
                return True

        return False

    def random_partial_subtree(self, p=0.5):
        """Generate a random partial subtree of me.

        We do this because there are waay too many unique subtrees to enumerate, and this allows a nice
        variety of structures

        Example
        -------
        >> prev_((seven_ if cardinality1_(x) else next_(next_(L_(x)))))
        prev_(WORD)
        prev_(WORD)
        prev_((seven_ if cardinality1_(x) else WORD))
        prev_(WORD)
        prev_((seven_ if BOOL else next_(next_(L_(SET)))))
        prev_(WORD)
        prev_((seven_ if cardinality1_(SET) else next_(WORD)))
        prev_(WORD)
        prev_((seven_ if BOOL else next_(WORD)))
        ...

        Note
        ----
        Partial here means that we include nonterminals with probability p

        """
        if self.args is None:
            return copy(self)

        newargs = []
        for a in self.args:
            if isFunctionNode(a):
                if random() < p:
                    newargs.append(a.returntype)
                else:
                    newargs.append(a.random_partial_subtree(p=p))
            else:
                newargs.append(a)  # string or something else

        ret = self.__copy__(shallow=True)  # don't copy kids
        ret.args = newargs

        return ret

    def is_complete_tree(self, grammar):
        """
        Check if this tree has any nonterminals in args, according to the grammar
        """
        for fn in self:
            for a in fn.argStrings():
                if grammar.is_nonterminal(a):
                    return False

        return True

    def uniquify_bv(self, remap=None):
        """
        Go through and make each of my uuids on BVUseFunctionNodes unique

        """
        from uuid import uuid4

        if remap is None:
            remap = dict()

        if isinstance(self, BVAddFunctionNode):
            # TODO: MAKE THIS THE SAME FUNCTION AS USED IN GRAMMAR_RULE
            newbv = 'bv__'+uuid4().hex
            if self.added_rule is not None:
                remap[self.added_rule.name] = newbv
                self.added_rule.name = newbv
        elif isinstance(self, BVUseFunctionNode):
            self.name = remap.get(self.name, self.name)

        for a in self.argFunctionNodes():
            a.uniquify_bv(remap)

    def iterate_subnodes(self, grammar, t=None, d=0, predicate=lambdaTrue, yield_depth=False, recurse_up=False):
        """Iterate through all subnodes of node *t*, while updating the added rules (bound variables)
        so that at each subnode, the grammar is accurate to what it was.

        Arguments
        ---------
        grammar : LOTlib3.Grammar
            This is the grammar we're iterating through
        t : FunctionNode
            The tree we will iterate over
        yield_depth : bool
            If True, we return (node, depth) instead of node.
        predicate : function
            Filter only the nodes that match this function (i.e. eval (function(fn) == True) on each fn).
        recurse_up : bool
            Do we recurse all the way up and add all above nodes too?
        """
        if not t:
            t = self
        if predicate(t):
            yield (t, d) if yield_depth else t

        # Define a new context that is the grammar with the rule added.
        # Then, when we exit, it's still right.
        with BVRuleContextManager(grammar, t, recurse_up=recurse_up):
            for a in t.argFunctionNodes():
                # Pass up anything from below
                for g in self.iterate_subnodes(grammar, a, d=d+1, yield_depth=yield_depth,
                                               predicate=predicate, recurse_up=False): # we never have to recurse up
                    yield g





# ============================================================================================================
# Other classes
# ============================================================================================================

class BVAddFunctionNode(FunctionNode):
    """
    A type of FunctionNode that adds a bound variable, namely a lambda.

    This should almost never need to be called, as it is defaultly handled by LOTlib3.Grammar
    """
    def __init__(self, parent, returntype, name, args,  added_rule=None):
        FunctionNode.__init__(self, parent, returntype, name, args)
        self.added_rule = added_rule
        assert added_rule is not None, "*** Cannot use BVAddFunctionNode if added_rule is None!"

    def uses_bv(self):
        """ Is my rule used below? """
        for a in self.argFunctionNodes():
            for n in a:
                if n.name == self.added_rule.name:
                    return True
        return False

    def __copy__(self, shallow=False):
        """Copy a function node.
                
        Note
        ----
        The rule is NOT deeply copied (regardless of shallow)

        Arguments
        ---------
        shallow: if True, this does not copy the children (self.to points to the same as what we return)

        """
        fn = BVAddFunctionNode(self.parent, self.returntype, self.name, None,
            added_rule=copy(self.added_rule)) ## TODO: We should not need to copy added_rule

        if (not shallow) and self.args is not None:
            fn.args = list(map(copy, self.args))
        else:
            fn.args = self.args

        for a in fn.argFunctionNodes():
            a.parent = fn

        return fn

    def as_list(self, d=0, bv_names=None):
        """Returns a list representation of the FunctionNode with function/self.name as the first element.

        Arguments
        ---------
        d : int
            An optional argument that keeps track of how far down the tree we are.
        bv_names : dict
            A dictionary keeping track of the names of bound variables (keys = UUIDs, values = names).

        """
        # initialize the bv_names variable if it's not defined
        if bv_names is None:
            bv_names = dict()    
        
        # Since this is a lambda, we should add an item to the bv_names dictionary
        # print "We are a lambda node...", self.name
        bvn = ''
        if self.added_rule is not None:
            bvn = self.added_rule.bv_prefix+str(d)
            bv_names[self.added_rule.name] = bvn
        
        # Call super now that bv_names has been defined
        x = FunctionNode.as_list(self, d, bv_names)
        
        # afterwards, we should remove the BV name from the bv_names dictionary
        # TODO: do we really need this?
        if self.added_rule is not None:
            del bv_names[self.added_rule.name]
 
        # print "\tand dictionary ", bv_names, " returns: ", x
        return x


class BVUseFunctionNode(FunctionNode):
    """
    A FunctionNode that uses a bound variable. As in, the use of "x" in lambda x: x+1
    """
    def __init__(self, parent, returntype, name, args, bv_prefix=None):
        FunctionNode.__init__(self, parent, returntype, name, args)
        self.bv_prefix = bv_prefix

    def as_list(self, d=0, bv_names=None):
        """Returns a list representation of the FunctionNode with function/self.name as the first element.

        Arguments
            d: An optional argument that keeps track of how far down the tree we are
            bv_names: A dictionary keeping track of the names of bound variables (keys = UUIDs,
            values = names)

        """
        # the tree should be represented as the empty set if the function node has no name
        assert self.name is not None
        assert self.name in bv_names
        x = [bv_names[self.name]]

        # and we're now ready to loop over the function node's arguments
        if self.args is not None:
            x.extend([a.as_list(d=d+1, bv_names=bv_names) if isFunctionNode(a) else a for a in self.args])
 
        return x

    def __copy__(self, shallow=False):
        """Copy a function node.
                
        Note:
            The rule is NOT deeply copied (regardless of shallow)

        Arguments
            shallow: if True, this does not copy the children (self.to points to the same as what we return)

        """
        fn = BVUseFunctionNode(self.parent, self.returntype, self.name, None, bv_prefix=self.bv_prefix)
        
        if (not shallow) and self.args is not None:
            fn.args = list(map(copy, self.args))
        else:
            fn.args = self.args

        for a in fn.argFunctionNodes():
            a.parent = fn

        return fn




# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
#
#    Functions for mappings FunctionNodes to strings
#
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------

import re
percent_s_regex = re.compile(r"%s")
bv_regex = re.compile(r"\<BV\>")

def schemestring(x, d=0, bv_names=None):
    """Outputs a scheme string in (lambda (x) (+ x 3)) format.

    Arguments:
        x: We return the string for this FunctionNode.
        bv_names: A dictionary from the uuids to nicer names.

    """
    if isinstance(x, str):
        return x
    elif isFunctionNode(x):

        if bv_names is None:
            bv_names = dict()

        name = x.name
        if isinstance(x, BVUseFunctionNode):
            name = bv_names.get(x.name, x.name)

        if x.args is None:
            return name
        else:
            if x.args is None:
                return name
            elif isinstance(x, BVAddFunctionNode):
                assert name is 'lambda'
                return "(%s (%s) %s)" % (name, x.added_rule.name,
                                         [schemestring(a, d+1, bv_names=bv_names) for a in x.args])
            else:
                return "(%s %s)" % (name, [schemestring(a,d+1, bv_names=bv_names) for a in x.args])


def fullstring(x, d=0, bv_names=None):
    """
    A string mapping function that is for equality checking. This is necessary because pystring silently ignores
    FunctionNode.names that are ''. Here, we print out everything, including returntypes
    :param x:
    :param d:
    :param bv_names:
    :return:
    """

    if isinstance(x, str):
        return x
    elif isFunctionNode(x):

        if bv_names is None:
            bv_names = dict()


        if isinstance(x, BVAddFunctionNode):
            # On a lambda, we must add the introduced bv, and then remove it again afterwards

            bvn = x.added_rule.bv_prefix+str(d)
            bv_names[x.added_rule.name] = bvn

            ret = '%s<%s> %s: %s' % ( x.name, x.returntype, bvn, [fullstring(xi, d=d+1, bv_names=bv_names) for xi in x.args] )

            del bv_names[x.added_rule.name]

            return ret
        else:

            name = x.name
            if isinstance(x, BVUseFunctionNode):
                name = bv_names.get(x.name, x.name)

            if x.args is None:
                return "%s<%s>"%(name, x.returntype)
            else:
                return "%s<%s>(%s)" % (name,
                                       x.returntype,
                                       ', '.join([fullstring(a, d=d+1, bv_names=bv_names) for a in x.args]))




def pystring(x, d=0, bv_names=None):
    """Output a string that can be evaluated by python; gives bound variables names based on their depth.

    Args:
        bv_names: A dictionary from the uuids to nicer names.

    """
    if isinstance(x, str):
        return x
    elif isFunctionNode(x):

        if bv_names is None:
            bv_names = dict()

        bvn = '' # used when lambda but not BVAddFunctionNode
        if isinstance(x, BVAddFunctionNode):
            bvn = x.added_rule.bv_prefix+str(d)
            bv_names[x.added_rule.name] = bvn
            # assert len(x.args) == 1


        # Now handle the name special cases
        if x.args is None: # terminal
            if isinstance(x, BVUseFunctionNode):
                ret = bv_names.get(x.name, x.name)
            else:
                ret = x.name
        elif x.name == '':
            assert len(x.args) == 1, "Null names must have exactly 1 argument"
            ret = pystring(x.args[0], d=d+1, bv_names=bv_names)

        elif percent_s_regex.search(x.name): # If we match the python string substitution character %s, then format
            ret = x.name % tuple([pystring(a, d=d+1, bv_names=bv_names) for a in x.args])

        elif x.name == 'lambda': # we are a lambda but NOT a BVAddFunctionNode -- a lambda thunk!
                assert len(x.args) == 1
                ret = 'lambda %s: %s' % (bvn, pystring(x.args[0], d=d+1, bv_names=bv_names))
        else:

            name = x.name
            if isinstance(x, BVUseFunctionNode): # handle bv functions
                name = bv_names.get(x.name, x.name)

            ret = name+'('+', '.join([pystring(a, d=d+1, bv_names=bv_names) for a in x.args])+')'

        # and if we have any bv matches, then insert the bv we introduce
        if bv_regex.search(ret):
            ret = bv_regex.sub(bvn, ret)

        # On a lambda, we must add the introduced bv, and then remove it again afterwards
        if isinstance(x, BVAddFunctionNode):
            del bv_names[x.added_rule.name]

        return ret





