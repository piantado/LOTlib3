import math
"""
    Some simple nan-wrapped arithemtic primitives (for old testing on GPUropolis)
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assembly arithmetic
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def assembly_primitive(fn):
    def inside(*args):
        try:
            v = fn(*args)
            return v
        except ZeroDivisionError: return float("nan")
        except ValueError: return float("nan")
        except OverflowError: return float("nan")
        
    return inside



# For assembly 
@assembly_primitive
def ADD(x,y): return x+y

@assembly_primitive
def SUB(x,y): return x-y

@assembly_primitive
def MUL(x,y): return x*y

@assembly_primitive
def DIV(x,y): return x/y

@assembly_primitive
def LOG(x): return math.log(x)

@assembly_primitive
def POW(x,y):return pow(x,y)

@assembly_primitive
def EXP(x): return math.exp(x)

@assembly_primitive
def NEG(x): return -x

@assembly_primitive
def SIN(x): return math.sin(x)

@assembly_primitive
def ASIN(x): return math.asin(x)