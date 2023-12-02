# *- coding: utf-8 -*-

#try: import numpy as np
#except ImportError: import numpypy as np

from copy import copy
from collections import defaultdict
import itertools

from LOTlib3.Miscellaneous import *
from LOTlib3.GrammarRule import GrammarRule, BVAddGrammarRule
from LOTlib3.BVRuleContextManager import BVRuleContextManager
from LOTlib3.FunctionNode import FunctionNode, BVAddFunctionNode


# when we pack, we are allowed to use these characters, in this order
import string
pack_string = '0123456789'+string.ascii_lowercase+string.ascii_uppercase


class Grammar(CommonEqualityMixin):
    """
    A PCFG-ish class that can handle rules that introduce bound variables
    """
    def __init__(self, BV_P=10.0, start='START'):
        self_update(self,locals())
        self.rules = defaultdict(list)  # A dict from nonterminals to lists of GrammarRules.
        self.rule_count = 0
        self.bv_count = 0   # How many rules in the grammar introduce bound variables?

    def __str__(self):
        """Display a grammar."""
        return '\n'.join([str(r) for r in itertools.chain(*[self.rules[nt] for nt in list(self.rules.keys())])])

    def nrules(self):
        """ Total number of rules
        """
        return sum([len(self.rules[nt]) for nt in list(self.rules.keys())])

    def get_rules(self, nt):
        """
        The possible rules for any nonterminal
        """
        return self.rules[nt]

    def get_all_rules(self):
        """
        A list of all rules
        """
        for nt in self.nonterminals():
            for r in self.get_rules(nt):
                yield r

    def is_nonterminal(self, x):
        """A nonterminal is just something that is a key for self.rules"""
        # if x is a string  &&  if x is a key
        return isinstance(x, str) and (x in self.rules)

    def display_rules(self):
        """Prints all the rules to the console."""
        for rule in self:
            print(rule)

    def __iter__(self):
        """Define an iterator over all rules so we can say 'for rule in grammar...'."""
        for k in list(self.rules.keys()):
            for r in self.rules[k]:
                yield r

    def nonterminals(self):
        """Returns all non-terminals."""
        return list(self.rules.keys())

    def get_rule_by_name(self, n, nt=None):
        if nt is None:
            matches = [r for r in self.get_all_rules() if r.name == n]
        else:
            matches = [r for r in self.get_rules(nt) if r.name == n]
        assert len(matches)==1, "%s %s %s" % (n, nt, str(matches))
        return matches[0]

    def get_matching_rule(self, t):
        """
        Get the rule matching t's signature. Note: We could probably speed this up with a hash table if need be.
        """
        rules = self.get_rules(t.returntype)
        matching_rules = [r for r in rules if (r.get_rule_signature() == t.get_rule_signature())]
        assert len(matching_rules) == 1, \
            "Grammar Error: " + str(len(matching_rules)) + " matching rules for this FunctionNode! %s %s %s" % (t.get_rule_signature(), str(t), matching_rules)
        return matching_rules[0]

    def single_probability(self, t):
        # in this tree, in its context (recursing up), what is the probability of this single expansion?

        with BVRuleContextManager(self, t, recurse_up=True):
            z = log(sum([ r.p for r in self.get_rules(t.returntype) ]))
            r = self.get_matching_rule(t)
            return log(r.p)-z

    def log_probability(self, t):
        """
        Returns the log probability of t, recomputing everything (as we do now)

        This is overall about half as fast, but it means we don't have to store generation_probability
        """
        assert isinstance(t, FunctionNode)

        z = log(sum([ r.p for r in self.get_rules(t.returntype) ]))

        # Find the one that matches. While it may seem like we should store this, that is hard to make work
        # with multiple grammar objects across loading/saving, because the objects will change. This way,
        # we always look it up.
        lp = -Infinity
        r = self.get_matching_rule(t)
        assert r is not None, "Failed to find matching rule at %s %s" % (t, r)

        lp = log(r.p) - z

        with BVRuleContextManager(self, t):
            for a in t.argFunctionNodes():
                lp += self.log_probability(a)

        return lp

    def add_rule(self, nt, name, to, p, bv_type=None, bv_args=None, bv_prefix='y', bv_p=None):
        """Adds a rule and returns the added rule.

        Arguments
            nt (str): The Nonterminal. e.g. S in "S -> NP VP"
            name (str): The name of this function.
            to (list<str>): What you expand to (usually a FunctionNode).
            p (float): Unnormalized probability of expansion
            bv_type (str): What bound variable was introduced
            bv_args (list): What are the args when we use a bv (None is terminals, else a type signature)

        """
        self.rule_count += 1
        assert name is not None, "To use null names, use an empty string ('') as the name."
        if bv_type is not None:
            newrule = BVAddGrammarRule(nt, name,to, p=p, bv_type=bv_type, bv_args=bv_args, bv_prefix=bv_prefix, bv_p=bv_p)
        else:
            newrule = GrammarRule(nt, name, to, p=p)

        self.rules[nt].append(newrule)
        return newrule
    
    def is_terminal_rule(self, r):
        """
        Check if a rule is "terminal" - meaning that it doesn't contain any nonterminals in its expansion.
        """ 
        return not any([self.is_nonterminal(a) for a in None2Empty(r.to)])  


    # --------------------------------------------------------------------------------------------------------
    # Generation
    # --------------------------------------------------------------------------------------------------------

    def generate(self, x=None):
        """Generate from the grammar

        Arguments:
            x (string): What we start from -- can be None and then we use Grammar.start.

        """
        # print "# Calling Grammar.generate", type(x), x

        # Decide what to start from based on the default if start is not specified
        if x is None:
            x = self.start
            assert self.start in self.nonterminals(), \
                "The default start symbol %s is not a defined nonterminal" % self.start

        # Dispatch different kinds of generation
        if isinstance(x,list):            
            return [self.generate(x=xi) for xi in x]             # If we get a list, just map along it to generate.
        elif self.is_nonterminal(x):

            # sample a grammar rule
            rules = self.get_rules(x)
            assert len(rules) > 0, "*** No rules in x=%s"%x

            # sample the rule
            r = weighted_sample(rules, probs=lambda x: x.p, log=False)

            # Make a stub for this functionNode 
            fn = r.make_FunctionNodeStub(self, None)

            # Define a new context that is the grammar with the rule added
            # Then, when we exit, it's still right.
            with BVRuleContextManager(self, fn, recurse_up=False):      # not sure why we can't use with/as:
                # Can't recurse on None or else we genreate from self.start
                if fn.args is not None:
                    # and generate below *in* this context (e.g. with the new rules added)
                    try:
                        fn.args = self.generate(fn.args)
                    except RuntimeError as e:
                        print("*** Runtime error in %s" % fn)
                        raise e

                # and set the parents
                for a in fn.argFunctionNodes():
                    a.parent = fn

            return fn
        elif isinstance(x, FunctionNode): # this will let us finish generation of a partial tree

            x.args = [ self.generate(a) for a in x.args]

            for a in x.argFunctionNodes():
                a.parent = x

            return x

        else:  # must be a terminal
            assert isinstance(x, str), ("*** Terminal must be a string! x="+x)
            return x

    def enumerate(self, d=20, nt=None, leaves=True):
        """Enumerate all trees up to depth n.

        Parameters:
            d (int): how deep to go? (defaults to 20 -- if Infinity, enumerate() runs forever)
            nt (str): the nonterminal type
            leaves (bool): do we put terminals in the leaves or leave nonterminal types? This is useful in
              PartitionMCMC

        """
        for i in infrange(d):
            for t in self.enumerate_at_depth(i, nt=nt, leaves=leaves):
                yield t

    def enumerate_at_depth(self, d, nt=None, leaves=True):
        """Generate trees at depth d, no deeper or shallower.

        Parameters
            d (int): the depth of trees you want to generate
            nt (str): the type of the nonterminal you want to return (None reverts to self.start)
            leaves (bool): do we put terminals in the leaves or leave nonterminal types? This is useful in
              PartitionMCMC. This returns trees of depth d-1!

        Return:
            yields the ...

        """
        if nt is None:
            nt = self.start

        # handle garbage that may be passed in here
        if not self.is_nonterminal(nt):
            yield nt
        else:
            # raise StopIteration

            if d == 0:
                if leaves:
                    # Note: can NOT use filter here, or else it doesn't include added rules
                    for r in self.rules[nt]:
                        if self.is_terminal_rule(r):
                            yield r.make_FunctionNodeStub(self, None)
                else:
                    # If not leaves, we just put the nonterminal type in the leaves
                    yield nt
            else:
                # Note: can NOT use filter here, or else it doesn't include added rules. No sorting either!
                for r in self.rules[nt]:

                    # No good since it won't be deep enough
                    if self.is_terminal_rule(r):
                        continue

                    fn = r.make_FunctionNodeStub(self, None)

                    # The possible depths for the i'th child
                    # Here we just ensure that nonterminals vary up to d, and otherwise
                    child_i_depths = lambda i: range(d) if self.is_nonterminal(fn.args[i]) else [0]

                    # The depths of each kid
                    for cd in lazyproduct(list(map(child_i_depths, range(len(fn.args)))), child_i_depths):

                        # One must be equal to d-1
                        # TODO: can be made more efficient via permutations. Also can skip terminals in args.
                        if max(cd) < d-1:
                            continue
                        assert max(cd) == d-1

                        myiter = lazyproduct(
                            [self.enumerate_at_depth(di, nt=a, leaves=leaves) for di, a in zip(cd, fn.args)],
                            lambda i: self.enumerate_at_depth(cd[i], nt=fn.args[i], leaves=leaves))
                        try:
                            while True:
                                # Make a copy so we don't modify anything
                                yieldfn = copy(fn)

                                # BVRuleContextManager here makes us remove the rule BEFORE yielding,
                                # or else this will be incorrect. Wasteful but necessary.
                                with BVRuleContextManager(self, fn, recurse_up=False):
                                    yieldfn.args = next(myiter)
                                    for a in yieldfn.argFunctionNodes():
                                        # Update parents
                                        a.parent = yieldfn

                                yield copy(yieldfn)

                        except StopIteration:
                            # Catch this here so we continue in this loop over rules
                            pass

    def depth_to_terminal(self, x, openset=None, current_d=None):
        """
        Return a dictionary that maps both this grammar's rules and its nonterminals to a number,
        giving how quickly we can go from that nonterminal or rule to a terminal.

        Arguments:
            openset(doc?): stores the set of things we're currently trying to compute for. We must skip rules
              that contain anything in there, since they have to be defined still, and so we want to avoid
              a loop.

        """
        if current_d is None: 
            current_d = dict()
            
        if openset is None:
            openset = set()
            
        openset.add(x)
        
        if isinstance(x, GrammarRule):
            if x.to is None or len(x.to) == 0:
                current_d[x] = 0 # we are a terminal
            else:
                current_d[x] = 1 + max([(self.depth_to_terminal(a, openset=openset, current_d=current_d)
                                        if a not in openset else 0) for a in x.to])
        elif isinstance(x, str):
            if x not in self.rules:
                current_d[x] = 0    # A terminal
            else:
                current_d[x] = min([(self.depth_to_terminal(r, openset=openset, current_d=current_d)
                                    if r not in openset else Infinity) for r in self.rules[x]])
        else:
            assert False, "Shouldn't get here!"

        openset.remove(x)
        return current_d[x]

    def renormalize(self):
        """ go through each rule in each nonterminal, and renormalize the probabilities """

        for nt in self.nonterminals():
            z = sum([r.p for r in self.get_rules(nt)])
            for r in self.get_rules(nt):
                r.p = r.p / z


    # --------------------------------------------------------------------------------------------------------
    # Packing and unpacking trees
    # This is useful for storing trees in a more concise, ascii format. Much smaller size than
    # pickling hypotheses
    # --------------------------------------------------------------------------------------------------------

    def sig2idx(self):
        """
        Compute a dictionary from signatures to rule indices
        this is so that when we add rules for bound variables, we don't
        change all the rule indices.
        NOTE: This step is slow and should be cached for a grammar
        """
        d = dict()
        idx = 0 # store the rule index, making each unique. NOTE: we could make it unique for each nt, but that may mess with LZPrior

        for nt in self.nonterminals():
            for r in self.get_rules(nt):
                d[r.get_rule_signature()] = idx
                idx += 1

        return d

    def idx2rule(self):
        """
        Compute a dictionary from idx to rules that matches sig2idx
        """
        d = dict()
        idx = 0 # store the rule index, making each unique. NOTE: we could make it unique for each nt, but that may mess with LZPrior

        for nt in self.nonterminals():
            for r in self.get_rules(nt):
                d[idx] = r
                idx += 1

        return d

    def pack_ascii(self, t, sig2idx=None):
        """
        Pack a tree into a simple ascii string, using grammar.
        Not particularly optimized, but simple
        """

        if sig2idx is None:
            sig2idx = self.sig2idx()


        # the output string (starts empty)
        s = ''

        # compute the node's index (i.e. packed name)
        # pack_string is a string, not a function
        s = s + pack_string[sig2idx[t.get_rule_signature()]]

        # add rule if we're adding a bound variable (i.e. a lambda)
        if isinstance(t, BVAddFunctionNode):
            r = t.added_rule
            idx =  max(sig2idx.values())+1
            sig2idx[r.get_rule_signature()] = idx

        # recurse
        for a in t.argFunctionNodes():
            s = s+self.pack_ascii(a, sig2idx=sig2idx)

        # remove bound variable rule after recursing
        if isinstance(t, BVAddFunctionNode):
            r = t.added_rule
            del sig2idx[r.get_rule_signature()]
            
        return s

    def unpack_ascii(self, s):
        # we must convert to list(s) so that it will support pop, delete
        s = list(s)

        return self.unpack_ascii_rec(s, self.start, self.idx2rule())

    def unpack_ascii_rec(self, s, x, idx2rule):
        """
        Unpack a string into a tree. Follows the format of Grammar.generate, but indexes
        the choices with s
        """
        assert x is not None  # should have been given by unpack_ascii

        # Dispatch different kinds of generation
        if isinstance(x, list):
            return [self.unpack_ascii_rec(s, xi, idx2rule) for xi in x]

        elif self.is_nonterminal(x):
            
            rules = self.get_rules(x)

            # index
            # instead of sampling a rule, get it from the string
            i = pack_string.index(s[0])
            del s[0]  # remove (works since s is a list)
            r = idx2rule[i]

            # Make a stub for this functionNode
            fn = r.make_FunctionNodeStub(self, None)
            with BVRuleContextManager(self, fn, recurse_up=False):

                # add rule (to idx2rule)
                if isinstance(r, BVAddGrammarRule):
                    idx = max(idx2rule.keys()) + 1
                    idx2rule[idx] = fn.added_rule

                # recurse
                if fn.args is not None:
                    fn.args = self.unpack_ascii_rec(s, fn.args, idx2rule)

                # remove rule (as we now do in packing, too)
                if isinstance(r, BVAddGrammarRule):
                    idx = max(idx2rule.keys())
                    del idx2rule[idx]
            
                for a in fn.argFunctionNodes():
                    a.parent = fn

            return fn

        else: # must be a terminal
            return x

    #def pack_test(self,n=1000):
    #    """a quick test for packing and unpacking"""
    #    one_test = lambda x: x == self.unpack_ascii(self.pack_ascii(x))
    #    return all([one_test(self.generate()) for _ in xrange(n)])
