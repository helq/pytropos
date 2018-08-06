from typed_ast import ast3

operations = {
    ast3.Add: '__add__',
    ast3.Sub: '__sub__',
    ast3.Mult: '__mul__',
    ast3.MatMult: '__matmul__',
    ast3.Div: '__truediv__',
    ast3.FloorDiv: '__floordiv__',
    ast3.Mod: '__mod__',
    # __divmod__ does exist but it is not an operation, it is called by a function (divmod)
    # ast3.DivMod: '__divmod__',
    ast3.Pow: '__pow__',
    ast3.LShift: '__lshift__',
    ast3.RShift: '__rshift__',
    ast3.BitAnd: '__and__',
    ast3.BitXor: '__xor__',
    ast3.BitOr: '__or__'
}
