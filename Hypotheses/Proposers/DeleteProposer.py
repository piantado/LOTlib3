"""
    Delete Proposer - promote an existing subtree and delete the
    subtree in which it is nested

    NOTE 0: NOT ERGODIC!

    NOTE 1: This is actually a specific form of the copy proposal, in
    which copies are required to move upward toward the root.
"""

from LOTlib3.BVRuleContextManager import BVRuleContextManager
from LOTlib3.FunctionNode import *
from LOTlib3.GrammarRule import *
from LOTlib3.Hypotheses.Proposers.Proposer import *
from LOTlib3.Hypotheses.Proposers.Utilities import *
from LOTlib3.Miscellaneous import Infinity, nicelog, None2Empty, sample1
from LOTlib3.Subtrees import least_common_difference

class DeleteProposer(Proposer):
    def propose_tree(self,grammar,tree,resampleProbability=lambdaOne):
        new_t = copy(tree)

        try: # to choose a node to delete
            n, lp = new_t.sample_subnode(lambda t: can_delete_FunctionNode(t)*resampleProbability(t))
        except NodeSamplingException:
            raise ProposalFailedException

        # Figure out which of my children have the same type as me
        replicating_children = list_replicating_children(n)
        if not replicating_children:
            raise ProposalFailedException

        # who to promote; NOTE: not done via any weighting
        chosen_child = sample1(replicating_children)

        # perform the deletion
        n.setto(chosen_child)

        return new_t

    def compute_proposal_probability(self,grammar,t1,t2,resampleProbability=lambdaOne):
        node_1,node_2 = least_common_difference(t1,t2)

        if (node_1 and node_2 and
            any([nodes_are_roughly_equal(arg,node_2) for arg in
                 None2Empty(node_1.args)])):

            lp_choosing_node_1 = t1.sampling_log_probability(node_1,lambda t: can_delete_FunctionNode(t)*resampleProbability(t))
            lp_choosing_child = -nicelog(len(list_replicating_children(node_1)))
            return lp_choosing_node_1 + lp_choosing_child

        else: # no possible deletion
            return -Infinity

if __name__ == "__main__": # test code
    test_proposer(DeleteProposer)
