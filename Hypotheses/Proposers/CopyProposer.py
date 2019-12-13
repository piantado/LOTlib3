"""
    Copy proposal - choose two nodes of type X and copy one to the other

    NOTE: NOT ERGODIC!
"""

from LOTlib3.BVRuleContextManager import BVRuleContextManager
from LOTlib3.FunctionNode import NodeSamplingException
from LOTlib3.Hypotheses.Proposers.Proposer import *
from LOTlib3.Hypotheses.Proposers.Utilities import *
from LOTlib3.Miscellaneous import Infinity, lambdaOne, logsumexp, nicelog
from LOTlib3.Subtrees import least_common_difference
from copy import copy, deepcopy

class CopyProposer(Proposer):
    def propose_tree(self,grammar,tree,resampleProbability=lambdaOne):
        new_t = copy(tree)
    
        # sample a source and (possibly identical) target with the same grammar.
        try:
            src, lp_choosing_src_in_old_tree = new_t.sample_subnode(resampleProbability)
            src_grammar = give_grammar(grammar,src)
            good_choice = lambda x: 1.0 if ((give_grammar(grammar,x) == src_grammar) and
                                            (x.returntype == src.returntype)) else 0.0
            target, lp_choosing_target_in_old_tree = new_t.sample_subnode(good_choice)
        except NodeSamplingException:
            raise ProposalFailedException
        
        new_src = deepcopy(src)
        new_src.parent = target.parent
        target.setto(new_src)
        
        return new_t
    
    def compute_proposal_probability(self,grammar, t1, t2, resampleProbability=lambdaOne, recurse=True):
        chosen_node1 , chosen_node2 = least_common_difference(t1,t2)
    
        lps = []
        if chosen_node1 is None: # any node in the tree could have been copied
            for node in t1:
                could_be_source = lambda x: 1.0 * nodes_equal_except_parents(grammar,x,node) * resampleProbability(x)
                lp_of_choosing_source = (nicelog(t1.sample_node_normalizer(could_be_source) - could_be_source(node)) - nicelog(t1.sample_node_normalizer(resampleProbability)))
                lp_of_choosing_target = t1.sampling_log_probability(chosen_node1,resampleProbability=resampleProbability)
                lps += [lp_of_choosing_source + lp_of_choosing_target]
        else: # we have a specific path up the tree
            while chosen_node1:
                could_be_source = lambda x: 1.0 * nodes_equal_except_parents(grammar,x,chosen_node2) * resampleProbability(x)
    
                lp_of_choosing_source = nicelog(t1.sample_node_normalizer(could_be_source)) - nicelog(t1.sample_node_normalizer(resampleProbability))
                lp_of_choosing_target = t1.sampling_log_probability(chosen_node1,resampleProbability=resampleProbability)
                lps += [lp_of_choosing_source + lp_of_choosing_target]
    
                if recurse:
                    chosen_node1 = chosen_node1.parent
                    chosen_node2 = chosen_node2.parent
                else:
                    chosen_node1 = None
    
        return logsumexp(lps)

if __name__ == "__main__": # test code
    test_proposer(CopyProposer)
