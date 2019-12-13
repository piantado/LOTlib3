from LOTlib3.FunctionNode import *
from LOTlib3.Miscellaneous import None2Empty

def can_delete_FunctionNode(x):
    """
    We can delete from functionNodes if they use a rule X -> f(..., X, ...).
    Then we can promote the inner X
    """
    return ((not (isinstance(x, BVAddFunctionNode) and x.uses_bv()))
            and any([ x.returntype == a.returntype for a in
                      x.argFunctionNodes() ]))

def can_insert_GrammarRule(r):
    return any([r.nt==a for a in None2Empty(r.to)])

def can_insert_FunctionNode(x, grammar):
    """
    We can insert ot a function node if the grammar contains a rule from its NT to itself
    """
    return any([can_insert_GrammarRule(r) for r in grammar.rules[x.returntype]])

def list_replicating_children(node):
    return [arg for arg in node.args if (isinstance(arg,FunctionNode)
                                         and arg.returntype == node.returntype)]

def nodes_are_roughly_equal(n1,n2):
    """ ignores placement in a larger tree and bound variables"""
    return (n1 and # nodes must exist
            n2 and
            n1.name == n2.name and # should be roughly equal
            n1.returntype == n2.returntype and
            n1.args == n2.args)

def give_grammar(grammar,node):
    # BVRuleContextManager gives the grammar used inside a node, not
    # at the node itself, so we consider the node's parent
    with BVRuleContextManager(grammar, node.parent, recurse_up=True):
        g = deepcopy(grammar)
    return g

def nodes_equal_except_parents(grammar,n1,n2):
    return ((n1.name == n2.name) and
            (n1.args == n2.args) and
            (n1.returntype == n2.returntype) and
            (give_grammar(grammar,n1) == give_grammar(grammar,n2)))
