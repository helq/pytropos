from typing import Dict, Type, Any  # noqa: F401
from typing import Tuple, Optional

__all__ = ['NonImplementedPT', 'Singleton', 'Pos']

Pos = Tuple[Optional[Tuple[int, int]], str]


class NonImplementedPT(Exception):
    pass


# taken from: https://stackoverflow.com/a/6798042
class Singleton(type):
    _instances = {}  # type: Dict[Type, Any]

    def __call__(cls, *args, **kwargs):  # type: ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def clean_sing(cls) -> None:
        if cls in cls._instances:
            del cls._instances[cls]
