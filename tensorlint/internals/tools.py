import typing as ty
from typing import Dict, List, Tuple, Type  # noqa: F401

__all__ = ['NonImplementedTL', 'Singleton', 'Pos']

Pos = ty.Tuple[int, int]


class NonImplementedTL(Exception):
    pass


# taken from: https://stackoverflow.com/a/6798042
class Singleton(type):
    _instances = {}  # type: Dict[Type, ty.Any]

    def __call__(cls, *args, **kwargs):  # type: ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def clean_sing(cls) -> None:
        if cls in cls._instances:
            del cls._instances[cls]
