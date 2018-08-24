from .values.value import Value, Any

__all__ = [
    'congruent', 'unite'
]


# I don't consider subtying in this work, for simplicity purposes, no tensor derives from
# other classes (only from `object`)
def congruent(x: Value, y: Value) -> bool:
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


def unite(x: Value, y: Value) -> Value:
    """
    Implements unite basic rule of the type system:
    unite(?, x) = ?
    unite(x, ?) = ?
    unite(x, x) = x
    unite(x, y) = ?
    unite(W(a), W(b)) = W(unite(a,b))

    NOTE: This function doesn't assume subtyping!!!
    """
    if isinstance(x, Any) or isinstance(y, Any):
        return Any()
    if type(x) is not type(y):  # inhibiting subtyping!!
        return Any()

    return x.unite_inside(y)
