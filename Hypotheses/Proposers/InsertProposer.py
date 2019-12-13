"""
    Insert Proposer - wrap an existing subtree inside a new subtree

    NOTE: NOT ERGODIC!
"""

from LOTlib3.BVRuleContextManager import BVRuleContextManager
from LOTlib3.FunctionNode import *
from LOTlib3.GrammarRule import *
from LOTlib3.Hypotheses.Proposers.Proposer import *
from LOTlib3.Hypotheses.Proposers.Utilities import *
from LOTlib3.Miscellaneous import Infinity, nicelog, None2Empty, sample1
from LOTlib3.Subtrees import least_common_difference

class InsertProposer(Proposer):
    def propose_tree(self,grammar,tree,resampleProbability=lambdaOne):
        new_t = copy(tree)

        try: # to choose a node to insert on
            ni, lp = new_t.sample_subnode(lambda t: can_insert_FunctionNode(t, grammar)*resampleProbability(t) )
        except NodeSamplingException:
            raise ProposalFailedException

        # is there a rule that expands from ni.returntype to some ni.returntype?
        replicating_rules = list(filter(can_insert_GrammarRule, grammar.rules[ni.returntype]))
        if len(replicating_rules) == 0:
            raise ProposalFailedException

        # sample a rule
        r = sample1(replicating_rules)

        # the functionNode we are building
        fn = r.make_FunctionNodeStub(grammar, ni.parent)

        # figure out which arg will be the existing ni
        replicatingindices = [i for i in range(len(fn.args)) if fn.args[i] == ni.returntype]
        if len(replicatingindices) <= 0: # should never happen
            raise ProposalFailedException

        # choose the one to replace
        replace_i = sample1(replicatingindices)

        ## Now expand the other args, with the right rules in the grammar
        with BVRuleContextManager(grammar, fn, recurse_up=True):
            for i,a in enumerate(fn.args):
                fn.args[i] = copy(ni) if (i == replace_i) else grammar.generate(a)

        # perform the insertion
        ni.setto(fn)

        return new_t

    def compute_proposal_probability(self,grammar,t1,t2,resampleProbability=lambdaOne):
        node_1,node_2 = least_common_difference(t1,t2)

        if (node_1 and node_2 and any([nodes_are_roughly_equal(arg,node_1) for arg in None2Empty(node_2.args)])):

            lp_choosing_node_1 =  t1.sampling_log_probability(node_1,resampleProbability=lambda t: can_insert_FunctionNode(t, grammar)*resampleProbability(t))

            lp_choosing_rule = -nicelog(len(list(filter(can_insert_GrammarRule, grammar.rules[node_1.returntype]))))
            lp_choosing_replacement = -nicelog(len([i for i in range(len(node_2.args)) if node_2.args[i].returntype == node_1.returntype]))

            lp_generation = []
            for arg in node_2.args:
                if not (arg.name == node_1.name and
                        arg.returntype == node_1.returntype and
                        arg.args == node_1.args): # if the nodes are significantly different
                    with BVRuleContextManager(grammar, node_2, recurse_up=True):
                        lp_generation += [grammar.log_probability(arg)]

            lp_copy_making_node_2 = lp_choosing_rule + lp_choosing_replacement + sum(lp_generation)

            return lp_choosing_node_1 + lp_copy_making_node_2
        else:
            return -Infinity # the trees cannot be identical if we performed an insertion

if __name__ == "__main__": # test code
    test_proposer(InsertProposer)
