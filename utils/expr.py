import sympy as sp
from sympy import Expr, Poly

def asExpr(string : str) -> Expr:
    try:
        return Poly(string).as_expr()
    except Exception:
        return Poly(string, gens = sp.symbols("_")).as_expr()