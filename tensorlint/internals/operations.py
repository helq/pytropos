import typing as ty
from .values import (
    Value, special_methods_implementations, Pos, Any, OperationFun
)

# These functions are created below with __create_opbin
__all__ = ['add', 'mul', 'eq']  # noqa: F822


def __create_opbin(name: str) -> OperationFun:
    def op(val: Value, other: Value, src_pos: ty.Optional[Pos] = None) -> Value:
        return __binop(name, val, other, src_pos, True)
    return op


for op in __all__:
    globals()[op] = __create_opbin(op)


# (Gradual) type rules (see paper) to operate two variables
def __binop(
        op: str,
        val: Value,
        other: Value,
        src_pos: ty.Optional[Pos] = None,
        rev: bool = False
) -> Value:
    # if any of the two values is any the end result will be any
    if isinstance(val, Any) or isinstance(other, Any):
        return Any()

    # checking if there is some rule two add the two values
    for type_l, type_r, fun in special_methods_implementations[op]:
        # print("vals: {}".format((type_l, type_r, fun)))
        # print("current types: {}  {}".format(type(val), type(other)))
        # print("evaluation: {}  {}".format(type(val), type(other)))
        if isinstance(val, type_l) and isinstance(other, type_r):
            res = fun(val, other, src_pos)
            if res != NotImplemented:
                return res
            else:
                # TODO(helq): show error of implementation. The function
                # `fun` should implement what it says it should implement,
                # ie, type_l and type_r
                print("Function operating between types `{}` and `{}`"
                      " didn't compute. This shouldn't happen!".format(type_l, type_r))

    # Try reverse operation if everything failed. So, if the call was:
    # `add(5,3)` try `add(3,5)`
    if rev:
        return __binop(op, other, val, src_pos, False)

    # TODO(helq): add typechecking error
    # print("The values couldn't be added")
    return Any()
