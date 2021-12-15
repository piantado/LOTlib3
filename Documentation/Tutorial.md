

# Introduction

LOTlib3 is a library for inferring compositions of functions from observations of their inputs and outputs or simply their outputs if there is no input. This tutorial will introduce a very simple problem and how it can be solved in LOTlib3. 

Suppose that you know basic arithmetic operations (called "primitives") like addition (+), subtraction (-), multiplication (*) and division (/). You observe a number which has been constructed using these operations, and wish to infer which operations were used. We'll assume that you observe the single number `12` and then do Bayesian inference in order to discover which operations occurred. For instance, 12 may be written as `(1+1) * 6`, involving an addition, a multiplication, two uses of 1, and one use of 6. Or it may have been written as ` 1 + 11`, or `2 * 3 * 2`, etc. There are lots of other ways.  Which one is correct?  Well any composition of addition, subtraction, multiplication, etc... that outputs a 12 would be consistent with the data.  However, some might seem more plausible than others.  For instance it might be unlikely the 12 was generated as 12+(1-1+1-1+1-1+1-1+1-1+1-1+1-1+1-1) as it seems a rather obtuse way to have arrived as 12.  LOTLib3 is designed to help you make sensible decisions about which compositions of functions likely explain a particular set of outputs or input-output pairs.

## Grammars

The general strategy of LOTlib3 models is to specify a space of possible compositions using a grammar. The grammar is actually a probabilistic context free grammar (with one small modification described below) that specifies a prior distribution on trees, or equivalently compositional structures like (1+1)*6, 2+2+2+2+2+2, (1+1)+(2*5), etc. If this is unfamiliar, the wiki on [PCFGs](https://en.wikipedia.org/wiki/Stochastic_context-free_grammar) would be useful to read first. 

However, the best way to understand the grammar is as a way of specifying a program: any expansion of the grammar "renders" into a python program, whose code can then be evaluated. This will be made more concrete later.

For now, here is how we can construct a simple example grammar

```python
    from LOTlib3.Grammar import Grammar
    
    # Define a grammar object
    # Defaultly this has a start symbol called 'START' but we want to call 
    # it 'EXPR'
    grammar = Grammar(start='EXPR')
    
    # Define some operations
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(float(%s) / float(%s))', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(-%s)', ['EXPR'], 1.0)
    
    # And define some numbers. We'll give them a 1/(n^2) probability
    for n in range(1,10):
        grammar.add_rule('EXPR', str(n), None, 10.0/(n**2))
```
A few things to note here. The grammar rules have the format
```python
    grammar.add_rule( <NONTERMINAL>, <FUNCTION>, <ARGUMENTS>, <PROBABILITY>)
```
where <NONTERMINAL> says what nonterminal this rule is expanding. In this example, there is only one kind of nonterminal, an expression (denoted EXPR). The <FUNCTION> argument is the function that this rule represents. These are strings that name defined functions in LOTlib3, but they can also be strings (as here) where the <ARGUMENTS> get substituted in via string substitution (so for instance, "(%s+%s)" can be viewed as the function `lambda x,y: eval("(%s+%s)"%(x,y)))`. The arguments are a list of the arguments to the function. Note that the <FUNCTION> string can be pretty complex. For division, we have `(float(%s) / float(%s))`, which forces the function to use floating point division, not python's default. 

If the <FUNCTION> is a terminal that does not take arguments (as in the numbers 0..9), the <ARGUMENTS> part of a rule should be None. Note that None is very different from an empty list:
```python
    grammar.add_rule('EXPR', 'hello', None, 1.0)
```
renders into the program "hello" but 
```python
    grammar.add_rule('EXPR', 'hello', [], 1.0)
```
renders into "hello()". 


The production probabilities are, for now, fixed. Note that the numbers have probabilities proportional to 1/n**2.  This means that is prefers smaller numbers. But we also multiplied those values by 10, making them as a group much more likely than other operations. This is important because the PCFG has to define a proper probability distribution. This means that a nonterminal must have a probability of 1 of eventually leading to a terminal (a terminal is any rule with `None` as its <ARGUMENTS>). The easiest way to ensure this is to upweight the probabilities on terminals so they are more likely to be sampled.  We might have been ok in this simple case because we are only dealing with the numbers 1-9 but as the number of terminal possibilities increases eventually the probability of sampling one would become very small compared to repeatedly sampling the more complex expressions that have weight 1.0.
    
We can see some productions from this grammar if we call Grammar.generate. We will also show the probability of this tree according to the grammar, which is computed by renormalizing the <PROBABILITY> values of each rule when expanding each nonterminal:
```python
    for _ in xrange(100):
        t = grammar.generate()
        print grammar.log_probability(t), t 
```
As you can see, the longer/bigger trees have lower (more negative) probabilities, implementing essentially a simplicity bias. These PCFG probabilities will often be our prior for Bayesian inference. 

Note that even though each `t` is a tree (a hierarchy of LOTlib3.FunctionNodes), it renders nicely above as a string. This is defaultly how expressions are evaluated in python. But we can see more of the internal structure using `t.fullprint()`, which shows the nonterminals, functions, and arguments at each level:
```python
    t = grammar.generate()
    t.fullprint()
```

There is a column in this output that should say 'None' for each row of the output.  It is ok to ignore that for now.

## Hypotheses

The grammar nicely specifies a space of expressions, but LOTlib3 needs a "hypothesis" to perform inference. In LOTlib3, hypotheses must define functions for computing priors, computing the likelihood of data, and implementing proposals in order for MCMC to work. In most cases, a hypothesis will represent a single production from the grammar.

Fortunately, for our purposes, there is a simple hypothesis class that it built-in to LOTlib3 which defaultly implements these. Let's just use it here. 
```python
    from math import log
    from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis
    
    # define a 
    class MyHypothesis(LOTHypothesis):
        def __init__(self, **kwargs):
            LOTHypothesis.__init__(self, grammar=grammar, display="lambda: %s", **kwargs)
    
        def compute_single_likelihood(self, datum):
            if self(*datum.input) == datum.output:
                return log((1.0-datum.alpha)/100. + datum.alpha)
            else:
                return log((1.0-datum.alpha)/100.)
            
```
There are a few things going on here. First, we import LOTHypothesis and use that to define the new class `MyHypothesis`. LOTHypothesis defines `compute_prior()` and `compute_likelihood(data)`--more about these later. We define the initializer `__init__`. We overwrite the LOTHypothesis default and specify that the grammar we want is the one defined above. LOTHypotheses also defaultly take an argument called `x` (more on this later), but for now we want our hypothesis to be a function of no arguments. When we convert the value of the hypothesis into a string, it will get substituted into the `display` keyword. Here, `display="lambda: %s"` meaning that the hypothesis will be displayed and also evaled in python as appearing after a lambda.

Essentially, `compute_likelihood` maps `compute_single_likelihood` over a list of data (treating each as IID conditioned on the hypothesis). So when we want to define how the likelihood works, we typically want to overwrite `compute_single_likelihood` as we have above. In this function, we expect an input `datum` with attributes `input`, `output`, and `alpha`. The LOTHypothesis `self` can be viewed as a function (here, one with no arguments) and so it can be called on `datum.input`. The likelihood this defines is one in which we generate a random number from 1..100 with probability `1-datum.alpha` and the correct number with probability `datum.alpha`. Thus, when the hypothesis returns the correct value (e.g. `self(*datum.input) == datum.output`) we must add these quantities to get the total probability of producing the data. When it does not, we must return only the former. LOTlib3.Hypotheses.Likelihoods defines a number of other standard likelihoods, including the most commonly used  one, `BinaryLikelihood`. 

## Data

Given that our hypothesis wants those kinds of data, we can then create data as follows:
```python
    from LOTlib3.DataAndObjects import FunctionData
    data = [ FunctionData(input=[], output=12, alpha=0.95) ]
```
Note here that the most natural form of data is a list--even if it is only a single element--where each element, a datum, gets passed to `compute_single_likelihood`. The data here specifies the input, output, and noise value `alpha`. Note that even though `alpha` could live as an attribute of hypotheses, it makes most sense to view it as a known part of the data. Here input is a empty list because there is no input!  Remember the example we started with was explaining a single output (the number 12).  Keep reading to understand examples with an input below!

## Making hypotheses

We may now use our definition of a hypothesis to make one. If we call the initializer without a `value` keyword, LOTHypothesis just samples it from the given grammar: 
```python
    h = MyHypothesis()
    print(h.compute_prior(), h.compute_likelihood(data), h)
```
Even better, `MyHypothesis` also inherits a `compute_posterior` function:
```python
    print(h.compute_posterior(data), h.compute_prior(), h.compute_likelihood(data), h)
```
For convenience, when `compute_posterior` is called, it sets attributes on `h` for the prior, likelihood, and posterior (score):
```python
    h = MyHypothesis()
    h.compute_posterior(data)
    print(h.posterior_score, h.prior, h.likelihood, h)
```

## Running MCMC

We are almost there. We have define a grammar and a hypothesis which uses the grammar to define a prior, and custom code to define a likelihood. LOTlib3's main claim to fame is that we can simply import MCMC routines and do inference over the space defined by the grammar. It's very easy:
```python
    from LOTlib3.Samplers.MetropolisHastings import MetropolisHastingsSampler
    
    # define a "starting hypothesis". This one is essentially copied by 
    # all proposers, so the sampler doesn't need to know its type or anything. 
    h0 = MyHypothesis()
    
    # Now use the sampler like an iterator. In MetropolisHastingsSampler, compute_posterior gets called
    # so when we have an h, we can get its prior and likelihood
    for h in MetropolisHastingsSampler(h0, data, steps=100):
        print(h.posterior_score, h.prior, h.likelihood, h)
```
That probably went by pretty fast and also generated error messages! Here's another thing we can do:
```python
    h0 = MyHypothesis()
    
    from collections import Counter

    count = Counter()
    for h in MetropolisHastingsSampler(h0, data, steps=1000):
        count[h] += 1
    
    for h in sorted(count.keys(), key=lambda x: count[x]):
        print(count[h], h.posterior_score, h)
```
LOTlib3 hypotheses are required to hash nicely, meaning that they can be saved or put into dictionaries and sets like this. 

## Making our hypothesis class more robust

As you might have noticed we did not allow the number 0 as a terminal value in our grammar.  This is because it ran the risk of a divide by zero error.  However, we might like to include all the numbers between zero and nine.  So let's change that one part of our grammar definiton by replacing the lines like this:

```python
# And define some numbers. We'll give them a 1/((n+1)^2) probability
    for n in range(10):
        grammar.add_rule('EXPR', str(n), None, 10.0/((n+1)**2))
```

But how do we deal with the fact that we might get a expression with a zero in the demoninator?  This will generate a divide by zero error when evaluated by the Python interpreter.

Fortunately, we can hack our hypothesis class to address this by catching the exception. A smart way to do this is to override `__call__` and return an appropriate value when such an error occurs:
```python
    from math import log
    from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis

    class MyHypothesis(LOTHypothesis):
        def __init__(self, **kwargs):
            LOTHypothesis.__init__(self, grammar=grammar, display="lambda: %s", **kwargs)
            
        def __call__(self, *args):
            try:
                # try to do it from the superclass
                return LOTHypothesis.__call__(self, *args)
            except ZeroDivisionError:
                # and if we get an error, return nan
                return float("nan")
    
        def compute_single_likelihood(self, datum):
            if self(*datum.input) == datum.output:
                return log((1.0-datum.alpha)/100. + datum.alpha)
            else:
                return log((1.0-datum.alpha)/100.)
```

## Getting serious about running

Now with more robust code, we can run the `Counter` code above for longer and get a better picture of the posterior. 
```python
    h0 = MyHypothesis()
    
    from collections import Counter

    # run a bit, counting how often we get each hypothesis
    count = Counter()
    for h in MetropolisHastingsSampler(h0, data, steps=100000):
        count[h] += 1
    
    # print the counts and the posteriors
    for h in sorted(count.keys(), key=lambda x: count[x]):
        print(count[h], h.posterior_score, h)
```

If our sampler is working correctly, it should be the case that the time average of the sampler (the `h`es from the for loop) should approximate the posterior distribution (e.g. their re-normalized scores). Let's use this code to see if that's true

```python
    # Miscellaneous stores a number of useful functions. Here, we need logsumexp, which will
    # compute the normalizing constant for posterior_scores when they are in log space
    from LOTlib3.Miscellaneous import logsumexp 
    from numpy import exp # but things that are handy in numpy are not duplicated (usually)
    
    # get a list of all the hypotheses we found. This is necessary because we need a fixed order,
    # which count.keys() does not guarantee unless we make a new variable. 
    hypotheses = count.keys() 
    
    # first convert posterior_scores to probabilities. To this, we'll use a simple hack of 
    # renormalizing the psoterior_scores that we found. This is a better estimator of each hypothesis'
    # probability than the counts from the sampler
    z = logsumexp([h.posterior_score for h in hypotheses])
    
    posterior_probabilities = [ exp(h.posterior_score - z) for h in hypotheses ]
    
    # and compute the probabilities over the sampler run
    cntz = sum(count.values())    
    sampler_counts          = [ float(count[h])/cntz for h in hypotheses ] 
    
    ## and let's just make a simple plot
    import matplotlib.pyplot as pyplot
    fig = pyplot.figure()
    plt = fig.add_subplot(1,1,1)
    plt.scatter(posterior_probabilities, sampler_counts)
    plt.plot([0,1], [0,1], color='red')
    fig.show()
    
```
## Primitives

LOTlib3 also builds in a number of primitive operations, which live in LOTlib3.Primitives. When these are supplied as the <FUNCTION> in grammar rule, they act as functions that get called. **By convention, LOTlib3 internal primitives end in an underscore**. Here is an example equivalent to the grammar above, but using LOTlib3 function calls. 
```python 

    grammar.add_rule('EXPR', 'plus_', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', 'times_', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', 'divide_(float(%s),float(%s))', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', 'neg_', ['EXPR'], 1.0)
    
```
Note that when these are rendered into strings, they appear as function calls (and not just string substitutions to make python code) as in
```python
    times_(plus_(x,neg_(1)), plus_(1,1))
```
There are many functions built-in to python, including a number of operations for manipulating sets, numbers, and logic. The code for `divide_` shows that it does not cast its arguments to floats: here we have to do so using string substitution as above.  For simple thing it is up to you to decide if you like to use the built in python operators (e.g. '+') or the LOTLib3 primitive ('plus_') as they are basically the same.

You can also create new primitives which extends the functionality of LOTlib3 in many interesting way. To make a custom function accessible to LOTlib3's evaluator, use the `@primitive` decorator:
```python
    from LOTlib3.Eval import primitive
    
    @primitive
    def my_stupid_primitive_(x):
        return x+90253
```
Now if you use `my_stupid_primitive_` in a grammar rule, it can be "run" just like any normal python code
```python
    grammar.add_rule('EXPR', 'my_stupid_primitive_', ['EXPR'], 1.0)
```
It is generally more friendly to give it an underscore to make sure it's not confused for a normal python function.

## Nonterminals in the grammar

It may not have been obvious in the above examples, but the <NONTERMINAL> part of each grammar rule can be viewed as specifying the *return type* of the function that rule correspond to, while the <ARGUMENTS> can be viewed as the types of the arguments. Thus, what a grammar mainly does is ensure that the primitives all get arguments of the correct types. 

Let's see another example: suppose we had two kinds of things: booleans (BOOL) and numbers (EXPR). We might write a grammar like this
```python
    grammar.add_rule('EXPR', 'plus_', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', 'times_', ['EXPR', 'EXPR'], 1.0)
    
    # Use something that renders into if statements in real python
    grammar.add_rule('EXPR', '(%s if %s else %s)', ['EXPR', 'BOOL', 'EXPR'], 1.0)

    # Now how do we get a boolean?
    grammar.add_rule('BOOL', '(%s > %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('BOOL', '(%s >= %s)', ['EXPR', 'EXPR'], 1.0)

    # And a terminal
    grammar.add_rule('EXPR', '1', 10.0)
```
Here, the second argument to the `if` line must be a BOOL, and so we have given LOTlib3 a way to create code that returns BOOLs. It just happens that this code is a comparison of numbers, or EXPRs. 

## The best hypotheses

Very often, models in LOTlib3 approximate the full posterior distribution P(H|D) using the highest posterior hypotheses. There are two main ways to do this. One is a class named `LOTlib3.TopN` which acts like a set--you can add to it, but it keeps only the ones with highest posterior_score (or whatever "key" is set). It will return them to you in a sorted order:
```python
    from LOTlib3.TopN import TopN
    
    tn = TopN(N=10) # store the top N

    h0 = MyHypothesis()
    
    for h in MetropolisHastingsSampler(h0, data, steps=10000):
        tn.add(h)

    for h in tn.get_all(sorted=True):
        print(h.posterior_score, h)

```

There's also a friendly way to interface with `TopN`:

```python
    for h in MetropolisHastingsSampler(h0, data, steps=10000):
        tn << h
```

You might notice running this that productions the results in the output 12 are given high posterior scores.  However, it still might be the case that very simple and short programs like just a single number output (like 0) are still the "top" hypothesis.  This shows the importance of thinking about the nature of your prior and the likelihood function for your problem.

## Hypotheses as functions

Remember how we made `display="lambda: %s"` in the definition of MyHypothesis? That stated that a hypothesis was not a function of any arguments since the `lambda` has no arguments. You may have noticed that when a hypothesis is converting to a string (for printing or evaling) it acquires this additional `lambda` on the outside, indicating that the hypothesis was a function of no arguments, or a [thunk](https://en.wikipedia.org/wiki/Thunk). 

Here is a new listing where a class like MyHypothesis requires an argument. Now, when it renders, it comes with a `lambda x` in front, rather than just a `lambda`. There are two other primary changes: the grammar now has to allow the argument (`x`) to be produced in expressions, and the `datum.input` has to provide an argument, which gets bound to `x` when the function is evaluated. 
```python
    ######################################## 
    ## Define a grammar
    ######################################## 

    from LOTlib3.Grammar import Grammar
    grammar = Grammar(start='EXPR')
    
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(float(%s) / float(%s))', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(-%s)', ['EXPR'], 1.0)
    
    # Now define how the grammar uses x. The string 'x' must
    # be the same as used in the args below
    grammar.add_rule('EXPR', 'x', None, 1.0) 

    for n in range(0,10):
        grammar.add_rule('EXPR', str(n), None, 10.0/((n+1)**2))

    from math import log
    from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis

    ######################################## 
    ## Define the hypothesis
    ######################################## 
    
    # define a 
    class MyHypothesisX(LOTHypothesis):
        def __init__(self, **kwargs):
            LOTHypothesis.__init__(self, grammar=grammar, display="lambda x: %s", **kwargs)
        
        def __call__(self, *args):
            try:
                # try to do it from the superclass
                return LOTHypothesis.__call__(self, *args)
            except ZeroDivisionError:
                # and if we get an error, return nan
                return float("nan")
    
        def compute_single_likelihood(self, datum):
            if self(*datum.input) == datum.output:
                return log((1.0-datum.alpha)/100. + datum.alpha)
            else:
                return log((1.0-datum.alpha)/100.)

    ######################################## 
    ## Define the data
    ######################################## 

    from LOTlib3.DataAndObjects import FunctionData

    # Now our data takes input x=3 and maps it to 12
    # What could the function be?
    data = [ FunctionData(input=[3], output=12, alpha=0.95) ]

    ######################################## 
    ## Actually run
    ######################################## 
    from LOTlib3.Samplers.MetropolisHastings import MetropolisHastingsSampler
    from LOTlib3.TopN import TopN

    tn = TopN(N=10) 
    h0 = MyHypothesisX()

    for h in MetropolisHastingsSampler(h0, data, steps=10000):
        tn << h
```
Why does this matter? Well now instead of just explaining the data we saw, we can use the hypothesis to generalize to *new*, unseen data. For instance, we can take each hypothesis and see what it has to say about other numbers
```python

    tn = TopN(N=10) 
    h0 = MyHypothesisX()

    for h in MetropolisHastingsSampler(h0, data, steps=10000):
        tn << h
        
    # And now for each top N hypothesis, we'll see what it maps 0..9 to 
    for h in tn.get_all(sorted=True):
        print(h.posterior_score, h, list(map(h, range(0,10))))
```
Thus, we have taken a single data point and used it to infer a function that can *generalize* to new, unseen data or arguments. Note, though, that there is no requirement that `x` is used in each hypothesis. (If we wanted that, a LOTlib3ian way to do it would be to modify the prior to assign trees that don't use `x` to have `-Infinity` log prior). 

Just for fun here, let's take the posterior predictive and see how likely we are to generalize this function to each other number. 
```python
    
    ## First let's make a bunch of hypotheses
    from LOTlib3.TopN import TopN

    tn = TopN(1000) 

    h0 = MyHypothesisX()
    for h in MetropolisHastingsSampler(h0, data, steps=100000): # run more steps
        tn.add(h)

    # store these in a list (tn.get_all is defaultly a generator)
    hypotheses = list(tn.get_all())
    
    # Compute the normalizing constant
    from LOTlib3.Miscellaneous import logsumexp
    z = logsumexp([h.posterior_score for h in hypotheses])

    ## Now compute a matrix of how likely each input is to go
    ## to each output
    M = 20 # an MxM matrix of values
    import numpy

    # The probability of generalizing
    G = numpy.zeros((M,M))

    # Now add in each hypothesis' predictive
    for h in hypotheses:
        # the (normalized) posterior probability of this hypothesis
        p = numpy.exp(h.posterior_score - z)
        
        for x in range(M):
            output = int(h(x))
            
            # only keep those that are in the right range
            if 0 <= output < M:
                G[x][int(output)] += p

    # And show the output
    print(numpy.array_str(G, precision=3))
```
As you can see from the complexity of this array which shows the probabilities for different outputs given different inputs, observing that some (unseen) function maps 3->12 gives rise to nontrivial beliefs about the function underlying this transformation. 

# Lambdas

The power of this kind of representation comes not only from an ability to learn such simple functions, but to also learn functions with new kinds of abstractions. In programming languages, the simplest kind of abstraction is a variable--a value that is stored for later use. The variable `x` is created above on the level of a LOTHypothesis, but where things get more interesting is when the lower down values in a grammar can be used to define variables. Let's look at a grammar with two additional pieces
```python

    from LOTlib3.Grammar import Grammar
    grammar = Grammar(start='EXPR')
    
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(float(%s) / float(%s))', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(-%s)', ['EXPR'], 1.0)
    
    grammar.add_rule('EXPR', 'x', None, 1.0) 

    for n in range(1,10):
        # We'll make these lower probability so we can see more lambdas below
        grammar.add_rule('EXPR', str(n), None, 5.0/n**2)

    # And allow lambda abstraction
    # First we define the application of a new nonterminal, FUNC, to a term EXPR
    grammar.add_rule('EXPR', '(%s)(%s)', ['FUNC', 'EXPR'], 1.0)
    # Here, FUNC should be thought of as a function
    grammar.add_rule('FUNC', 'lambda', ['EXPR'], 1.0, bv_type='EXPR')

```
Here, `lambda` is a special LOTlib3 keyword that *introduces a bound variable* with a unique name in expanding the <ARGUMENT>s. In other words, when the grammar happens to sample a rule whose <FUNCTION> is `'lambda'`, it creates a new variable name, allows `bv_type` to expand to this variable, expands the <ARGUMENTS> to `lambda` (here, `EXPR`), and then removes the rule from the grammar. Let's look at some productions:
```python
    for _ in range(1000):
        print(grammar.generate())
```
Now some of the trees contain `lambda` expressions, which bind a variable (defaultly rendered as `y1`). The variable `y1` can only be used below its corresponding lambda, making the grammar in LOTlib3 technically not context-free, but very weakly context-sensitive. The variables like `y1` are called **bound variables** in LOTlib3. Note that they are numbered by their height in the tree, making them unique to the nodes below, but neither sequential, nor unique in the whole tree (underlyingly, they have unique names no matter what, but not when rendered into strings). 

These bound variables count towards the prior (when using `grammar.log_probability`) in exactly the way they should: when a nonterminal (specified in `bv_type`) can expand to a given bound variable, that costs probability, and other expansions must lose probability. The default in LOTlib3 is to always renormalize the probabilities specified. Note that in the `add_rule` command, we can change the probability that a EXPR->yi rule has by passing in a bv_p argument:
```python
    # make using yi 10x more likely than before
    grammar.add_rule('FUNC', 'lambda', ['EXPR'], 1.0, bv_type='EXPR', bv_p=10.0)
```

Lambdas like these play the role of variable declarations in a normal programming language. But note that the variables aren't guaranteed to be useful. In fact, very often variables are stupid, as in the expression
```python
    (lambda y1: y1)((1 * 1))
```
where the lambda defines a variable that is used immediately without modification. This expression is therefore equivalent to 
```python
    (1 * 1)
```
in terms of its function, but not in terms of its prior. 

We can also change the name that bound variables get by setting `bv_prefix`:
```python
    grammar.add_rule('FUNC', 'lambda', ['EXPR'], 1.0, bv_type='EXPR', bv_prefix='v')
```
will make bound variables named `v1`, `v2`, etc. 

## Here's where things get crazy

Of course, the true art of lambdas is not just that they can define variables, but that the variables themselves can be functions! This corresponds to *function declarations* in ordinary programming languages. If this is foreign or weird, I'd suggest reading [The Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sicp/). 

To define lambdas as functions, we only need to specify a `bv_args` list in the `lambda` declaration. `bv_args` is the type of arguments that are passed to each use of a bound variable each time it is used. But... then we have a problem of needing to bind that variable to something. If `yi` is itself a function of an EXPR, then its argument *also* has to be a function. That requires two lambdas. Here's how it works:
```python

    from LOTlib3.Grammar import Grammar
    grammar = Grammar(start='EXPR')
    
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(float(%s) / float(%s))', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(-%s)', ['EXPR'], 1.0)
    
    grammar.add_rule('EXPR', 'x', None, 1.0)  

    for n in xrange(1,10):
        grammar.add_rule('EXPR', str(n), None, 5.0/n**2)

    # Allow ourselves to define functions. This means creating a bound 
    # variable that can be bound to a FUNC. Where, the bound variable
    # is defined (here, FUNCDEF) we are allowed to use it. 
    grammar.add_rule('EXPR', '((%s)(%s))',  ['FUNCDEF', 'FUNC'], 1.0)

    # The function definition has a bound variable who can be applied as
    # a function, whose arguments are an EXPR (set by the type of the FUNC above)
    # and whose name is F, and who when applied to an EXPR returns an EXPR
    # We'll also set bv_p here. Feel free to play with it and see what that does. 
    grammar.add_rule('FUNCDEF', 'lambda', ['EXPR'], 1.0, bv_type='EXPR', bv_args=['EXPR'], bv_prefix='F')

    # and we have to say what a FUNC is. It's a function (lambda) from an EXPR to an EXPR
    grammar.add_rule('FUNC', 'lambda', ['EXPR'], 1.0, bv_type='EXPR')

```
Let's look at some hypotheses. Here, we'll show only those that use `F1` as a function (thus contain the string `"F1("`):
```python
    import re 

    for _ in xrange(50000):
        t = grammar.generate()
        if re.search(r"F1\(", str(t)):
            print t
```
For instance, this code might generate the following expression, which is obscure, though acceptable, python:
```python
    ((lambda F1: F1(x+1))(lambda y1: y1+3))
```
Here, we have define a variable `F1` that really represents the *function* `lambda y1: y1+3`. The value that is returned is the value of applying `F1` to the overall hypothesis value `x` plus `1`. Note that LOTlib3 here has correctly used `F1` in a context where an EXPR is needed (due to `bv_type='EXPR'` on `FUNCDEF`). It knows that the argument to `F1` is also an EXPR, which here happens to be expanded to `x+1`. It also knows that `F1` is itself a function, and it binds this function (through the outermost apply) to `lambda y1: y1+3`. LOTlib3 knows that `F1` can only be used in the left hand side of this apply, and `y1` can only be used on the right. This holds even if multiple bound variables of different types are generated. 

This ability to define functions provides some of the most interesting learning dynamics for the model. A nice example is provided in LOTlib3.Examples.Magnetism, where learners take data and learn predicates classifying observable objects into two kinds, as well as laws stated over those kinds.

## Recursive functions

Well that's wonderful, but what if we want a function to refer to *itself*? This is common in programming languages in the form of [recursive](https://en.wikipedia.org/wiki/Recursion_%28computer_science%29) definitions. This takes a little finagling in the LOTlib3 internals (through ambitious use of the [Y-combinator](https://en.wikipedia.org/wiki/Fixed-point_combinator#Fixed_point_combinators_in_lambda_calculus)) which you don't have to worry about. There is a class that implements recursion straightforwardly: `RecursiveLOTHypothesis`. Internally, hypothesis of this type always have an argument (defaultly called `recurse_`) which binds to themselves! 

Here is a simple example:
```python

    ######################################## 
    ## Define the grammar
    ######################################## 
    
    from LOTlib3.Grammar import Grammar
    grammar = Grammar(start='EXPR')
    
    # for simplicity, two operations
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    
    # we'll just allow two terminals for simplicity
    # We have to upweight them a little to keep things well-defined
    grammar.add_rule('EXPR', 'x', None, 10.0) 
    grammar.add_rule('EXPR', '1', None, 10.0) 
    
    # If we're going to allow recursion, we better have a base case
    # But this probably requires an "if" statement. LOTlib3's "if_" 
    # primitive will do the trick
    grammar.add_rule('EXPR', '(%s if %s else %s)', ['EXPR', 'BOOL', 'EXPR'], 1.0)
    
    # and we need to define a boolean. For now, let's just check
    # if x=1
    grammar.add_rule('BOOL', 'x==1', None, 1.0)
    
    # and the recursive operation -- I am myself a function
    # from EXPR to EXPR, so recurse should be as well
    grammar.add_rule('EXPR', 'recurse_', ['x-1'], 1.0) 
    
    ######################################## 
    ## Define the hypothesis
    ######################################## 
    from LOTlib3.Hypotheses.RecursiveLOTHypothesis import RecursiveLOTHypothesis
    
    class MyRecursiveHypothesis(RecursiveLOTHypothesis):
        def __init__(self, **kwargs):
            RecursiveLOTHypothesis.__init__(self, grammar=grammar, display="lambda recurse_, x: %s", **kwargs)
        
    ######################################## 
    ## Look at some examples
    ######################################## 
    import re
    from LOTlib3.Eval import RecursionDepthException
    
    for _ in range(50000):
        h = MyRecursiveHypothesis()
        
        # Now when we call h, something funny may happen: we may get
        # an exception for recursing too deep. If this happens for some 
        # reasonable xes, let's not print the hypothesis -- it must not 
        # be well-defined
        try:
            # try our function out
            values = map(h, range(1,10))
        except RecursionDepthException:
            continue
            
        # if we succeed, let's only show hypotheses that use recurse:
        if re.search(r"recurse_\(", str(h)):
            print(h) 
            print(values)
```
Note that there is nothing special about the `recurse_` name: it can be changed by setting `recurse=...` in `RecursiveLOTHypothesis.__init__`, but then the name should also be changed in the grammar. In this tutorial, we have only looked at defining the grammar, not in inferring recursive hypotheses. LOTlib3.Examples.Number is an example of learning a genuinely recursive function from data. 
