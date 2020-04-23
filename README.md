LOTlib3
-------

LOTlib3 is a Python 3 library for implementing "language of thought" models. A LOTlib3 model specifies a set of primitives and captures learning as inference over compositions of those primitives in order to express complex concepts. LOTlib3 permits lambda expressions, meaning that learners can come up with abstractions over compositions and define new primitives. Frequently, models use sampling in order to determine likely compositional hypotheses given some observed data. This library is an updated version of LOTlib, which was Python 2 and now deprecated.

The best way to use this library is to read and modify the examples. 

LOTlib3 currently uses tree-regeneration Metropolis-Hastings (from the "rational rules" model of Goodman et al. 2008).

REQUIREMENTS
------------

- numpy

INSTALLATION
------------

Put this library somewhere - e.g. ~/Libraries/LOTlib3/
	
Set the PYTHONPATH environment variable to point to LOTlib3/:
	
	$ export PYTHONPATH=$PYTHONPATH:~/Libraries/LOTlib3
	
You can put this into your .bashrc file to make it loaded automatically when you open a terminal. On ubuntu and most linux, this is:
	
	$ echo 'export PYTHONPATH=\$PYTHONPATH:~/Libraries/LOTlib3' >> ~/.bashrc

And you should be ready to use the library via:
	
	import LOTlib3
	
EXAMPLES and TUTORIAL
---------------------

A tutorial can be found in the "Documentation" folder above. 

A good starting place is the FOL folder, which contains a simple example to generate first-order logical expressions. These have simple boolean functions as well as lambda expressions. 

More examples are provided in the "Examples" folder. These include: simple symbolic regression, and a recursive number learning model.

Citation:
---------

This software may be cited as:

	@misc{piantadosi2014lotlib,
            author={Steven T. Piantadosi},
            title={{LOTlib: Learning and Inference in the Language of Thought}},
            year={2014},
            howpublished={available from https://github.com/piantado/LOTlib}
	}
