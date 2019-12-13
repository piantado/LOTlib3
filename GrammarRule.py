from .FunctionNode import FunctionNode, BVAddFunctionNode, BVUseFunctionNode
from copy import copy
from LOTlib3.Miscellaneous import None2Empty,self_update
from uuid import uuid4

class GrammarRule(object):
    """Represent a rule in the grammar.

    Arguments
    ---------
    nt : str
        the nonterminal
    name : str
        the name of this function
    to : list<str>
        what you expand to (usually a FunctionNode).
    p : float
        unnormalized probability of expansion
    bv_prefix : ?
        may be needed for GrammarRules introduced *by* BVGrammarRules, so that when we
        display them we can map to bv_prefix+depth

    Examples
    --------
    # A rule where "expansion" is a nonempty list is a real expansion:
    >> GrammarRule( "EXPR", "plus", ["EXPR", "EXPR"], ...) -> plus(EXPR,EXPR)
    # A rule where "expansion" is [] is a thunk
    >> GrammarRule( "EXPR", "plus", [], ...) -> plus()
    # A rule where "expansion" is [] is a real terminal (non-thunk)
    >> GrammarRule( "EXPR", "five", None, ...) -> five
    # A rule where "name" is '' expands without parens:
    >> GrammarRule( "EXPR", '', "SUBEXPR", ...) -> EXPR->SUBEXPR

    Note
    ----
    The rule id (rid) is very important -- it's what we use expansion determine equality

    """
    def __init__(self, nt, name, to, p=1.0, bv_prefix=None):
        p = float(p)
        assert p>0.0, "*** p=0 in rule %s %s %s. What are you thinking?" %(nt,name,to)

        self_update(self, locals())

        assert to is None or isinstance(to, list) or isinstance(to, tuple), "*** 'to' in a GrammarRule must be a list!"

        for a in None2Empty(to):
            assert isinstance(a,str)
        if name == '':
            assert (to is None) or (len(to) == 1), \
                "*** GrammarRules with empty names must have only 1 argument"

    def __repr__(self):
        """Print string in format: 'NT -> [TO]   w/ p=1.0'."""
        return str(self.nt) + " -> " + self.name + (str(self.to) if self.to is not None else '') + \
            "\tw/ p=" + str(self.p)

    def __eq__(self, other):
        """Equality is determined through "is" so that we can remove a rule from lists via list.remove()."""
        return self.get_rule_signature() == other.get_rule_signature()

    def short_str(self):
        """Print string in format: 'NT -> [TO]'."""
        return str(self.nt) + " -> " + self.name + (str(self.to) if self.to is not None else '')

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_rule_signature(self):
        """ Return a unique identifier for this rule. This must match up with FunctionNode.get_rule_signature """
        sig = [self.nt, self.name]
        if self.to is not None:
            sig.extend(self.to)
        return tuple(sig)

    def make_FunctionNodeStub(self, grammar, parent):
        # NOTE: It is VERY important to copy to, or else we end up with big problems!
        fn = FunctionNode(parent, returntype=self.nt, name=self.name, args=copy(self.to))
        assert fn.get_rule_signature() == self.get_rule_signature() # potentially not needed
        return fn


class BVAddGrammarRule(GrammarRule):
    """
    A kind of GrammarRule that supports introduces a bound variable, as in at a lambda.

    Arguments
    ---------
    nt : str
        the nonterminal
    name : str
        the name of this function
    to : list<str>
        what you expand to (usually a FunctionNode).
    rid : ?
        the rule id number
    p : float
        unnormalized probability of expansion
    bv_type : str
        return type of the introduced bound variable
    bv_args : ?
        what are the args when we use a bv (None is terminals, else a type signature)

    Note
    ----
    If we use this, we should have BV (i.e. argument `bv_type` should be specified).

    """
    def __init__(self, nt, name, to, p=1.0, bv_prefix="y", bv_type=None, bv_args=None, bv_p=None):
        p = float(p)
        self_update(self, locals())
        assert bv_type is not None, "Did you mean to use a GrammarRule instead of a BVGrammarRule?"
        assert isinstance(bv_type, str), "bv_type must be a string! Make sure it's not a tuple or list."
        
    def __repr__(self):
        return str(self.nt) + " -> " + self.name + (str(self.to) if self.to is not None else '') + \
            "\tw/ p=" + str(self.p) + "," + \
            "\tBV:" + str(self.bv_type) + ";" + str(self.bv_args) + ";" + self.bv_prefix
    
    def make_bv_rule(self, grammar):
        """Construct the rule that we introduce at a given depth.

        Note:
            * This is a GrammarRule and NOT a BVGrammarRule because the introduced rules should *not*
                themselves introduce rules!
            * This is a little awkward because it must look back in grammar, but I don't see how to avoid that

        """
        bvp = self.bv_p
        if bvp is None:
            bvp = grammar.BV_P
        return BVUseGrammarRule(self.bv_type, self.bv_args, p=bvp, bv_prefix=self.bv_prefix)

    def make_FunctionNodeStub(self, grammar, parent):
        """Return a FunctionNode with none of the arguments realized. That's a "stub"

        Arguments
        ---------
        d : int
            the current depth
        parent : ?

        Note
        ----
        * The None's in the next line need to get set elsewhere, since they will depend on the depth and
        other rules
        * It is VERY important to copy to, or else we end up with garbage

        """
        fn = BVAddFunctionNode(parent, returntype=self.nt, name=self.name, args=copy(self.to), added_rule=self.make_bv_rule(grammar))
        assert fn.get_rule_signature() == self.get_rule_signature() # potentially not needed
        return fn


class BVUseGrammarRule(GrammarRule):
    """
    A Grammar rule that is the use of a bound variable. (e.g. in (lambda (y) ...), this rule is active in the ...
    and allows you to make y).

    Each of these has a unique name via uuid.

    """
    def __init__(self, nt, to, p=1.0, bv_prefix=None):
        GrammarRule.__init__(self, nt, 'bv__'+uuid4().hex, to, p, bv_prefix)

    def make_FunctionNodeStub(self, grammar, parent):
        fn = BVUseFunctionNode(parent, returntype=self.nt, name=self.name, args=copy(self.to))
        assert fn.get_rule_signature() == self.get_rule_signature() # potentially not needed
        return fn
