from typing import Any

__all__ = ['NdArray']


class NdArray_:
    def __getitem__(self, key: Any) -> Any:
        pass

    def __delitem__(self, key: Any) -> None:
        pass

    def __setitem__(self, key: Any, other: Any) -> None:
        pass


NdArray = NdArray_()
