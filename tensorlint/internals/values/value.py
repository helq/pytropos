import typing as ty

__all__ = ['Value', 'Any']


# TODO(helq): make Value an abstract class, no value should be constructible from Value
# TODO(helq): add `get` method to simulate access to member values like, num.some.var
class Value(object):
    """
    All variables in tensorlint must derivate from `Value`. `Value` is just like `object`
    for all objects in python.
    """

    def unite_inside(self, other: 'Value') -> 'Value':
        raise NotImplementedError

    def congruent_inside(self, other: 'Value') -> bool:
        raise NotImplementedError

    @property
    def python_name(self) -> str:
        raise NotImplementedError

    @property
    def python_repr(self) -> str:
        raise NotImplementedError

    def call(self, *args: ty.Any, **kargs: ty.Any) -> ty.Any:
        raise NotImplementedError

    @property
    def get(self) -> ty.Any:
        raise NotImplementedError


# TODO(helq): Implement all methods special method names
# https://docs.python.org/3/reference/datamodel.html#special-method-names
class Any(Value):
    error_when_used = False

    @property
    def python_repr(self) -> str:
        return "any?"

    def checkErrorIfUsed(self) -> None:
        if Any.error_when_used:
            raise Exception("Trying to use Any value")

    def call(self, *args: ty.Any, **kargs: ty.Any) -> 'Any':
        return Any()

    @property
    def get(self) -> 'Any':
        return Any()

    def __init__(self, *args: ty.Any, **kargs: ty.Any) -> None:
        if len(args) > 0:
            if Any.error_when_used:
                raise Exception("Trying to construct Any value (with parms: {})".format(repr(args)))
        if Any.error_when_used:
            raise Exception("Trying to construct Any value")

    def __repr__(self) -> str:
        return "Any()"

    def __call__(self, *args, **kargs) -> 'Any':  # type: ignore
        raise NotImplementedError

    def __getattr__(self, name: str) -> 'Any':
        return Any()

    def __getitem__(self, key: ty.Any) -> 'Any':
        return Any()

    def __setitem__(self, key: ty.Any, val: ty.Any) -> None:
        pass

    def __delitem__(self, key: ty.Any) -> None:
        pass
