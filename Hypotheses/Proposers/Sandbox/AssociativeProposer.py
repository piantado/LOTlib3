
from LOTlib3.Hypotheses.Proposers import ProposalFailedException
from LOTlib3.FunctionNode import *
from LOTProposer import LOTProposer
from LOTlib3.GrammarRule import *
from LOTlib3.FunctionNode import NodeSamplingException


class AssociativeProposal(LOTProposer):
    """
        This is a proposer that takes associative FunctionNodes and re-associates
        x(x(Y, Z),W) --> x(Y,x(Z,W))
        and vice versa.

        This could help us get out of stuck places where we can't propose to the right subset
        of nodes.

        target_name is the name of the fn that associate.
        For now, we only allow binary nodes

        TODO: EXCLUDE LAMBDAS, check returntypes, check forward/back counts

    """
    def __init__(self, target_name, grammar):
        self.__dict__.update(locals())


    def can_associate_here(self, fn):
        if fn.name != self.target_name or len(fn.args) != 2:
            return False
        else:
            r = fn.args[0]
            return isFunctionNode(r) and \
                   r.name == self.target_name and \
                   len(r.args) == 2

    def can_inverse_associate_here(self, fn):
        if fn.name != self.target_name or len(fn.args) != 2:
            return False
        else:
            r = fn.args[1]
            return isFunctionNode(r) and \
                   r.name == self.target_name and \
                   len(r.args) == 2

    def propose_tree(self, t):

        newt = copy(t)
        fb = 0.0 # the forward/backward prob we return

        if random() < 0.5:
            try:
                ni, lp = newt.sample_subnode(self.can_associate_here)
            except NodeSamplingException:
                raise ProposalFailedException

            y, z, w = ni.args[0].args[0], ni.args[0].args[1], ni.args[1]

            a = ni.args[0]
            a.args = [z,w]

            ni.args = [y, a]
            f,b = 0.0, 0.0 ## TODO: FIX FORWARD/BACK

        else: # A delete move!
            try:
                ni, lp = newt.sample_subnode(self.can_inverse_associate_here)
            except NodeSamplingException:
                raise ProposalFailedException

            y, z, w = ni.args[0], ni.args[1].args[0], ni.args[1].args[1]

            a = ni.args[1]
            a.args = [y,z]

            ni.args = [a, w]
            f,b = 0.0, 0.0 ## TODO: FIX FORWARD/BACK

        return [newt, f-b]

if __name__ == "__main__":

    from LOTlib3.Grammar import Grammar

    grammar = Grammar(start='EXPR')
    grammar.add_rule('EXPR', '(%s %s)', ['EXPR', 'EXPR'], 1.0)
    for a in 'abcdefg':
        grammar.add_rule('EXPR', a, None, 1.0)

    proposer = AssociativeProposal('(%s %s)', grammar)

    for _ in range(1000):
        t = grammar.generate()

        print(t)

        for _ in range(10):
            try:
                v = proposer.propose_tree(t)
                print("\t", v)
            except ProposalFailedException:
                pass



