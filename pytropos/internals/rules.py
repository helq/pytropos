from .values.base import AbstractValue, Any

__all__ = [
    'congruent', 'unite'
]


# I don't consider subtying in this work, for simplicity purposes, no tensor derives from
# other classes (only from `object`)
def congruent(x: AbstractValue, y: AbstractValue) -> bool:
    """
    Implements rules:
    x ~ ?
    ? ~ x
    x ~ x
    x ≁ y
    """
    if isinstance(x, Any) or isinstance(y, Any):
        return True

    return type(x) is type(y) and x.congruent_inside(y)


def unite(x: AbstractValue, y: AbstractValue) -> AbstractValue:
    """
    Implements unite basic rule of the type system:
    unite(?, x) = ?
    unite(x, ?) = ?
    unite(x, x) = x
    unite(x, y) = ?
    unite(W(a), W(b)) = W(unite(a,b))

    NOTE: This function ignores subtyping!!!, if A <: B then unite(A, B) will return ? (if
    it took care of subtyping it should return B)
    """
    if isinstance(x, Any) or isinstance(y, Any):
        return Any()
    if type(x) is not type(y):  # inhibiting subtyping!!
        return Any()

    return x.join(y)  # type: ignore
