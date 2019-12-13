from LOTlib3.Miscellaneous import self_update
class BVRuleContextManager(object):

    def __init__(self, grammar, fn, recurse_up=False):
        """
            This manages rules that we add and subtract in the context of grammar generation. This is a class that is somewhat
            in between Grammar and GrammarRule. It manages creating, adding, and subtracting the bound variable rule via "with" clause in Grammar.

            NOTE: The "rule" here is the added rule, not the "bound variable" one (that adds the rule)
            NOTE: If rule is None, then nothing happens

            This actually could go in FunctionNode, *except* that it needs to know the grammar, which FunctionNodes do not
        """
        self_update(self, locals())
        self.added_rules = [] # all of the rules we added -- may be more than one from recurse_up=True

    def __str__(self):
        return "<Managing context for %s>"%str(self.fn)

    def __enter__(self):
        if self.fn is None: # skip these
            return

        assert len(self.added_rules) == 0, "Error, __enter__ called twice on BVRuleContextManager"

        for x in self.fn.up_to(to=None) if self.recurse_up else [self.fn]:
            if x.added_rule is not None:
                #print "# Adding rule ", x.added_rule
                r = x.added_rule
                self.added_rules.append(r)
                self.grammar.rules[r.nt].append(r)

    def __exit__(self, t, value, traceback):

        if self.fn is None: # skip these
            return

        #print "# Removing rule", r
        for r in self.added_rules:
            self.grammar.rules[r.nt].remove(r)

        # reset
        self.added_rules = []

        return False #re-raise exceptions

