"""
        This folder defines a bunch of "standard" grammars.

        In each, we do NOT specify the terminals, which typically expand the nonterminal PREDICATE->...

"""

from LOTlib3.Grammar import Grammar

DEFAULT_FEATURE_WEIGHT = 5.0

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SimpleBoolean_noTF = Grammar()
SimpleBoolean_noTF.add_rule('START', '', ['BOOL'], 1.0)

SimpleBoolean_noTF.add_rule('BOOL', 'and_', ['BOOL', 'BOOL'], 1.0)
SimpleBoolean_noTF.add_rule('BOOL', 'or_', ['BOOL', 'BOOL'], 1.0)
SimpleBoolean_noTF.add_rule('BOOL', 'not_', ['BOOL'], 1.0)

SimpleBoolean_noTF.add_rule('BOOL', '', ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SimpleBoolean = Grammar()
SimpleBoolean.add_rule('START', 'False', None, 1.0)
SimpleBoolean.add_rule('START', 'True', None, 1.0)
SimpleBoolean.add_rule('START', '', ['BOOL'], 1.0)

SimpleBoolean.add_rule('BOOL', 'and_', ['BOOL', 'BOOL'], 1.0)
SimpleBoolean.add_rule('BOOL', 'or_', ['BOOL', 'BOOL'], 1.0)
SimpleBoolean.add_rule('BOOL', 'not_', ['BOOL'], 1.0)

SimpleBoolean.add_rule('BOOL', '', ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Logical connectives with NO logical compositionality
# (e.g. one-level recursion)

AndOr = Grammar()
AndOr.add_rule('START', '', ['BOOL'], 1.0)
AndOr.add_rule('START', '', ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)
AndOr.add_rule('START', 'False', None, DEFAULT_FEATURE_WEIGHT)
AndOr.add_rule('START', 'True', None, DEFAULT_FEATURE_WEIGHT)

AndOr.add_rule('BOOL', 'and_', ['PREDICATE', 'PREDICATE'], 1.0)
AndOr.add_rule('BOOL', 'or_', ['PREDICATE', 'PREDICATE'], 1.0)
AndOr.add_rule('BOOL', 'not_', ['PREDICATE'], 1.0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CNF = Grammar()
CNF.add_rule('START', '', ['CONJ'], 1.0)
CNF.add_rule('START', '', ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
CNF.add_rule('START', 'True', None, DEFAULT_FEATURE_WEIGHT)
CNF.add_rule('START', 'False', None, DEFAULT_FEATURE_WEIGHT)

CNF.add_rule('CONJ', '',     ['DISJ'], 1.0)
CNF.add_rule('CONJ', '',     ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
CNF.add_rule('CONJ', 'and_', ['PRE-PREDICATE', 'CONJ'], 1.0)

CNF.add_rule('DISJ', '',     ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
CNF.add_rule('DISJ', 'or_',  ['PRE-PREDICATE', 'DISJ'], 1.0)

# A pre-predicate is how we treat negation
CNF.add_rule('PRE-PREDICATE', 'not_', ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)
CNF.add_rule('PRE-PREDICATE', '',     ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DNF = Grammar()
DNF.add_rule('START', '', ['DISJ'], 1.0)
DNF.add_rule('START', '', ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
DNF.add_rule('START', 'True', None, DEFAULT_FEATURE_WEIGHT)
DNF.add_rule('START', 'False', None, DEFAULT_FEATURE_WEIGHT)

DNF.add_rule('DISJ', '',     ['CONJ'], 1.0)
DNF.add_rule('DISJ', '',     ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
DNF.add_rule('DISJ', 'or_',  ['PRE-PREDICATE', 'DISJ'], 1.0)

DNF.add_rule('CONJ', '',     ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
DNF.add_rule('CONJ', 'and_', ['PRE-PREDICATE', 'CONJ'], 1.0)

# A pre-predicate is how we treat negation
DNF.add_rule('PRE-PREDICATE', 'not_', ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)
DNF.add_rule('PRE-PREDICATE', '',     ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CNF_noTF = Grammar()
CNF_noTF.add_rule('START', '', ['CONJ'], 1.0)
CNF_noTF.add_rule('START', '', ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)

CNF_noTF.add_rule('CONJ', '',     ['DISJ'], 1.0)
CNF_noTF.add_rule('CONJ', '',     ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
CNF_noTF.add_rule('CONJ', 'and_', ['PRE-PREDICATE', 'CONJ'], 1.0)

CNF_noTF.add_rule('DISJ', '',     ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
CNF_noTF.add_rule('DISJ', 'or_',  ['PRE-PREDICATE', 'DISJ'], 1.0)

# A pre-predicate is how we treat negation
CNF_noTF.add_rule('PRE-PREDICATE', 'not_', ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)
CNF_noTF.add_rule('PRE-PREDICATE', '',     ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DNF_noTF = Grammar()
DNF_noTF.add_rule('START', '', ['DISJ'], 1.0)
DNF_noTF.add_rule('START', '', ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)

DNF_noTF.add_rule('DISJ', '',     ['CONJ'], 1.0)
DNF_noTF.add_rule('DISJ', '',     ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
DNF_noTF.add_rule('DISJ', 'or_',  ['PRE-PREDICATE', 'DISJ'], 1.0)

DNF_noTF.add_rule('CONJ', '',     ['PRE-PREDICATE'], DEFAULT_FEATURE_WEIGHT)
DNF_noTF.add_rule('CONJ', 'and_', ['PRE-PREDICATE', 'CONJ'], 1.0)

# A pre-predicate is how we treat negation
DNF_noTF.add_rule('PRE-PREDICATE', 'not_', ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)
DNF_noTF.add_rule('PRE-PREDICATE', '',     ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# A NAND grammar. We get a crazy explosion in rules if
# we allowed BOOl->True and BOOL->False, so we simply write these in as
# separate NAND expansions


#NOTE: Inference in this grammar is *very* heavily dependent on DEFAULT_FEATURE_WEIGHT
Nand = Grammar()
Nand.add_rule('START', '', ['BOOL'], 1.0)

Nand.add_rule('BOOL', 'nand_', ['BOOL', 'BOOL'], 1.0)
Nand.add_rule('BOOL', 'nand_', ['True', 'BOOL'], 1.0)
Nand.add_rule('BOOL', 'nand_', ['False', 'BOOL'], 1.0)
Nand.add_rule('BOOL', '', ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NoLogic = Grammar()
NoLogic.add_rule('START', 'False', [], DEFAULT_FEATURE_WEIGHT)
NoLogic.add_rule('START', 'True', [], DEFAULT_FEATURE_WEIGHT)
NoLogic.add_rule('START', '', ['PREDICATE'], DEFAULT_FEATURE_WEIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TF = Grammar()
TF.add_rule('START', 'False', None, DEFAULT_FEATURE_WEIGHT)
TF.add_rule('START', 'True', None, DEFAULT_FEATURE_WEIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Default grammars for testing


finiteTestGrammar = Grammar(start='MYSTART')

finiteTestGrammar.add_rule('MYSTART', '', ['A0'], 1.0)

finiteTestGrammar.add_rule('A0', 'A0_', ['A1', 'a'], 0.1)
finiteTestGrammar.add_rule('A0', 'A0_', ['b'], 0.6)

finiteTestGrammar.add_rule('A1', 'A1_', ['A2', 'c'], 0.2)
finiteTestGrammar.add_rule('A1', 'A1_', ['d'], 0.8)

finiteTestGrammar.add_rule('A2', 'A2_', ['e'], 1.0)

# NOTE: we give these different names so we can't derive identical trees multiple ways
# (by, e.g., not using a lambda)
finiteTestGrammar.add_rule('A0', 'apply_', ['L0', 'A1'], 0.20)
finiteTestGrammar.add_rule('L0', 'lambda', ['B0'], 0.11, bv_p=0.07, bv_type='B1')

finiteTestGrammar.add_rule('A0', 'apply2_', ['L1', 'A1'], 0.20)
finiteTestGrammar.add_rule('L1', 'lambda', ['B0'], 0.12, bv_p=0.08, bv_type='B1', bv_args=['B2'])

finiteTestGrammar.add_rule('A0', 'apply3_', ['L2', 'A1'], 0.20)
finiteTestGrammar.add_rule('L2', 'lambda', ['B0'], 0.13, bv_p=0.09, bv_type='B1', bv_args=[])

finiteTestGrammar.add_rule('B0', 'B0_', ['f', 'B1'], 0.89)
finiteTestGrammar.add_rule('B0', 'B0_', ['g'],       0.77)

finiteTestGrammar.add_rule('B1', 'B1_', ['h', 'B2'], 0.84)
finiteTestGrammar.add_rule('B1', 'B1_', ['i'],       0.16)

finiteTestGrammar.add_rule('B2', 'B2_', ['o'], 1.0)



infiniteTestGrammar = Grammar()

infiniteTestGrammar.add_rule('START', '', ['A'], 1.0)

infiniteTestGrammar.add_rule('A', 'A', ['A', 'A'], 0.2)
infiniteTestGrammar.add_rule('A', 'A', ['a'], 0.7)

infiniteTestGrammar.add_rule('A', 'apply_', ['L', 'A'], 0.10)
infiniteTestGrammar.add_rule('L', 'lambda', ['A'], 0.11, bv_p=0.07, bv_type='A')

infiniteTestGrammar.add_rule('A', 'apply_', ['LF', 'A'], 0.10)
infiniteTestGrammar.add_rule('LF', 'lambda', ['A'], 0.11, bv_p=0.07, bv_type='A', bv_args=['A'], bv_prefix='F')

