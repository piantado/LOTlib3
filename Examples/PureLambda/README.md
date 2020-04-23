Introduction
============

This example provides a demonstration of some forthcoming work learning concepts without semantically meaningful primitives. Instead, concepts are learned as *pure* lambda calculus expressions that obey the appropriate composition laws. This provides a sense in which concepts could be learned without having any of their component pieces "built in." In the default example, pure lambda calculus expressions are learned for "true", "false", "and", "or", and "not" such that they compose in the required ways. 

This implementation in LOTlib with sampling is different from the soon-to-be-released backtracking algorithm that seems to go much faster. 