from LOTlib3.Eval import primitive
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Access arbitrary features
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Some of our own primitivesS
@primitive
def is_color_(x,y): return (x.color == y)

@primitive
def is_shape_(x,y): return (x.shape == y)

@primitive
def is_pattern_(x,y): return (x.pattern == y)

@primitive
def is_size_(x,y): return (x.size == y)

@primitive
def isattr_(x,a,y):
    return getattr(x,a) == y

@primitive
def switch_(i,*ar):
    """
        Index into an array. NOTE: with run-time priors, the *entire* array gets evaluated.
        If you want to avoid this, use switchf_, which requires lambdas
    """
    return ar[i]

@primitive
def switchf_(i,x,*ar):
    return ar[i](x)
