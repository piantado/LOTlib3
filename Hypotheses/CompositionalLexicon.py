from SimpleLexicon import SimpleLexicon

class CompositionalLexicon(SimpleLexicon):
    """
    A CompositionalLexicon is one where the in data points are "sentences", and they get mapped through the lexicon
    to meanings, which are then composed in some way.

    ['a', 'man'] -> [lexicon['a'], lexicon['man']]
    """

    raise NotImplementedError