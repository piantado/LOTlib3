from random import random
from math import log
from collections import defaultdict

from LOTlib3.Miscellaneous import sample1, lambdaOne, dropfirst, self_update
from LOTlib3.GrammarRule import *
from LOTlib3.Hypotheses.Proposers import ProposalFailedException
from LOTlib3.FunctionNode import NodeSamplingException


def lp_sample_equal_to(n, x, resampleProbability=lambdaOne):
    """
        What is the log probability of sampling x or something equal to it from n?
    """
    assert x in n, str(x)+"\t\t"+str(n)

    Z = n.sample_node_normalizer(resampleProbability=resampleProbability)
    return log(sum([resampleProbability(t) if (t==x) else 0.0 for t in n])) - log(Z)

class InverseInlineProposer(object):
    """
        Inverse inlinling proposals.
    """

    def __init__(self, grammar):
        """
            This takes a grammar and a regex to match variable names
        """
        self_update(self,locals())
        LOTProposer.__init__(self, grammar)

        # check that we used "apply_" instead of "apply"
        for r in self.grammar:
            assert r.name is not "apply", "*** Need to use 'apply_' instead of 'apply' "
            assert r.name is not "lambda_", "*** Need to use 'lambda' instead of 'lambda' "
            # the asymmetry here is disturbing, but lambda is a keyword and apply is a function

        self.insertable_rules = defaultdict(list) # Hash each nonterminal to (a,l) where a and l are the apply and lambda rules you need
        for nt in list(self.grammar.rules.keys()):
            for a in [r for r in self.grammar if (r.name=="apply_") and (r.nt == nt)]:
                for l in [r for r in self.grammar if isinstance(r, BVAddGrammarRule) and (r.nt == a.to[0]) and (r.bv_args is None) and (r.bv_type==a.to[1])]: # For each lambda whose "below" is the right type. bv_args are not implemented yet
                    self.insertable_rules[nt].append( (a,l) )

        # print "# Insertable rules:"
        # for k,v in self.insertable_rules.items():
        #     print k
        #     for a,l in v:
        #         print "\t", a, "----------", l



    def can_abstract_at(self, x):
        """
            Can I put a lambda at x?
        """
        return len(self.insertable_rules[x.returntype]) > 0

    def is_valid_argument(self, n, x):
        """
            The only valid arguments that can be extracted contain lambdas defined above n OR below t
        """
        allowed_bvs = set()
        for t in dropfirst(n.up_to(to=None)):  # don't count n in the bvs we allow!
            if isinstance(t, BVAddFunctionNode):
                allowed_bvs.add(t.added_rule.name)

        for t in x:
            # we also allow bvs of things defined in t
            if isinstance(t, BVAddFunctionNode)  and t is not x:
                allowed_bvs.add(t.added_rule.name)
            elif isinstance(t, BVUseFunctionNode) and (t.name not in allowed_bvs):
                return False

        return True



    def can_inline_at(self, n):
        """
            Can we inline this? Only if its an apply whose lambda bv takes no args. ALSO, the argument must occur in the lambda, or else this could not have been created via inlining
        """

        if n.name != "apply_":
            return False

        assert len(n.args) == 2
        l, a = n.args

        assert (not isinstance(l.added_rule, BVUseFunctionNode)) or l.added_rule.bv_args is None # NOTE: l.added_rule.name checks if the bound variable is actually used, but only works for bv_args=None

        return (l.rule.bv_args is None or len(l.rule.bv_args) == 0) and l.args[0].contains_function(l.added_rule.name) and (l.args[0].returntype == n.returntype) and self.is_valid_argument(l.args[0], a) and self.can_abstract_at(l.args[0])


    def propose_tree(self, t):
        """
            Delete:
                - find an apply
                - take the interior of the lambdathunk and sub it in for the lambdaarg everywhere, remove the apply
            Insert:
                - Find a node
                - Find a subnode s
                - Remove all repetitions of s, create a lambda
                - and add an apply
        """

        newt = copy(t)
        f,b = 0.0, 0.0

        # ------------------
        if random() < 0.5: # Am inverse-inlining move

            # where the lambda goes
            try:
                n, np = newt.sample_subnode(resampleProbability=self.can_abstract_at)
            except NodeSamplingException:
                raise ProposalFailedException

            # print "# INVERSE-INLINE"

            # Pick the rule we will use
            ir = self.insertable_rules[n.returntype]
            ar, lr = sample1(ir) # the apply and lambda rules
            assert ar.nt == n.returntype
            assert lr.nt == ar.to[0]

            # what the argument is. Must have a returntype equal to the second apply type
            arg_predicate = lambda z: z.returntype == ar.to[1] and self.is_valid_argument(n, z) #how do we choose args?
            try:
                argval, _ = n.sample_subnode(resampleProbability=arg_predicate )
            except NodeSamplingException:
                raise ProposalFailedException

            argval = copy(argval) # necessary since the argval in the tree gets overwritten
            below = copy(n) # necessary since n gets setto the new apply rule

            # now make the function nodes.
            n.setto(ar.make_FunctionNodeStub(self.grammar, None)) # n's parent is preserved

            lambdafn = lr.make_FunctionNodeStub(self.grammar, n) ## this must be n, not applyfn, since n will eventually be setto applyfn
            bvfn = lambdafn.added_rule.make_FunctionNodeStub(self.grammar,  None) # this takes the place of argval everywhere below
            below.replace_subnodes(lambda x:x==argval, bvfn) # substitute below the lambda
            lambdafn.args[0] = below

            below.parent = lambdafn
            argval.parent = n

            # build our little structure
            n.args = lambdafn, argval

            assert self.can_inline_at(n) # this had better be true

            # to go forward, you choose a node, a rule, and an argument
            f = np + (-log(len(ir))) + lp_sample_equal_to(n, argval, resampleProbability=arg_predicate)
            newZ = newt.sample_node_normalizer(self.can_inline_at)
            b = (log(self.can_inline_at(n)*1.0) - log(newZ))

        else: # An inlining move
            try:
                n, np = newt.sample_subnode(resampleProbability=self.can_inline_at)
            except NodeSamplingException:
                raise ProposalFailedException

            # print "# INLINE"

            # Replace the subnodes
            newn = n.args[0].args[0] # what's below the lambda
            argval = n.args[1]
            bvn = n.args[0].added_rule.name # the name of the added variable

            newn.replace_subnodes(lambda x: isinstance(x,BVUseFunctionNode) and x.name == bvn, argval)

            n.setto(newn)
            assert self.can_abstract_at(n) # this had better be true

            # figure out which rule we are supposed to use
            possible_rules = [r for r in self.grammar.rules[n.returntype] if r.name==n.name and tuple(r.to) == tuple(n.argTypes()) ]
            assert len(possible_rules) == 1 # for now?

            n.rule = possible_rules[0]

            ir = self.insertable_rules[n.returntype] # for the backward probability
            f = np # just the probability of choosing this apply

            # choose n, choose a, choose the rule
            arg_predicate = lambda z: (z.returntype == argval.returntype) and self.is_valid_argument(newn, z)
            new_nZ = newt.sample_node_normalizer(self.can_abstract_at) # prob of choosing n
            argvalp = lp_sample_equal_to(newn, argval, resampleProbability=arg_predicate)
            assert len(ir)>0
            b = (log(self.can_abstract_at(newn)) - log(new_nZ)) + argvalp + (-log(len(ir)))

        assert newt.check_parent_refs() # Can comment out -- here for debugging

        return [newt, f-b]



if __name__ == "__main__":
        from LOTlib import break_ctrlc
        #from LOTlib3.Examples.Magnetism.SimpleMagnetism import data, grammar,  make_h0  DOES NOT WORK FOR BV ARGS
        from LOTlib3.Examples.Number.Model.Utilities import grammar, make_h0, generate_data, get_knower_pattern

        grammar.add_rule('LAMBDA_WORD', 'lambda', ['WORD'], 1.0, bv_type='WORD')
        grammar.add_rule('WORD', 'apply_', ['LAMBDA_WORD', 'WORD'], 1.0)

        p = InverseInlineProposer(grammar)

        """
        # Just look at some proposals
        for _ in xrange(200):
            t = grammar.generate()
            print ">>", t
            #assert t.check_parent_refs()

            for _ in xrange(10):
                t =  p.propose_tree(t)[0]
                print "\t", t

        """
        # Run MCMC -- more informative about f-b errors
        from LOTlib3.Inference.Samplers.MetropolisHastings import MHSampler

        from LOTlib3.Inference.Proposals.MixtureProposal import MixtureProposal
        from LOTlib3.Inference.Proposals.RegenerationProposal import RegenerationProposal

        h = make_h0(proposal_function=MixtureProposal([InverseInlineProposer(grammar), RegenerationProposal(grammar)] ))
        data = generate_data(100)
        for h in break_ctrlc(MHSampler(h, data)):
            print(h.posterior_score, h.prior, h.likelihood, get_knower_pattern(h), h)


