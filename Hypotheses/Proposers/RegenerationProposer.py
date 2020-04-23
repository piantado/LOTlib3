"""
    Regeneration Proposer - choose a node of type X and replace it with
    a newly sampled value of type X.
"""

from LOTlib3.BVRuleContextManager import BVRuleContextManager
from LOTlib3.FunctionNode import NodeSamplingException
from LOTlib3.Hypotheses.Proposers.Proposer import *
from LOTlib3.Miscellaneous import lambdaOne, logsumexp
from LOTlib3.Subtrees import least_common_difference
from copy import copy
from math import log

class RegenerationProposer(Proposer):

    def propose_tree(self, grammar, t, resampleProbability=lambdaOne):
        """Propose, returning the new tree"""
        new_t = copy(t)
    
        try: # to sample a subnode
            n, lp = new_t.sample_subnode(resampleProbability=resampleProbability)
        except NodeSamplingException: # when no nodes can be sampled
            raise ProposalFailedException
    
        # In the context of the parent, resample n according to the
        # grammar. recurse_up in order to add all the parent's rules
        with BVRuleContextManager(grammar, n.parent, recurse_up=True):
            n.setto(grammar.generate(n.returntype))
        return new_t
    
    def compute_proposal_probability(self, grammar, t1, t2, resampleProbability=lambdaOne, recurse=True):
        # NOTE: This is not strictly necessary since we don't actually have to sum over trees
        # if we use an auxiliary variable argument. But this fits nicely with the other proposers
        # and is not much slower.

        chosen_node1 , chosen_node2 = least_common_difference(t1,t2)

        lps = []
        if chosen_node1 is None: # any node in the tree could have been regenerated
            for node in t1:
                lp_of_choosing_node = t1.sampling_log_probability(node,resampleProbability=resampleProbability)
                with BVRuleContextManager(grammar, node.parent, recurse_up=True):
                    lp_of_generating_tree = grammar.log_probability(node)
                lps += [lp_of_choosing_node + lp_of_generating_tree]
        else: # we have a specific path up the tree
            while chosen_node1:
                lp_of_choosing_node = t1.sampling_log_probability(chosen_node1,resampleProbability=resampleProbability)
                with BVRuleContextManager(grammar, chosen_node2.parent, recurse_up=True):
                    lp_of_generating_tree = grammar.log_probability(chosen_node2)
                lps += [lp_of_choosing_node + lp_of_generating_tree]
                if recurse:
                    chosen_node1 = chosen_node1.parent
                    chosen_node2 = chosen_node2.parent
                else:
                    chosen_node1 = None

        return logsumexp(lps)
