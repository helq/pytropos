__all__ = ['new_id']

__current_id = 0


def new_id() -> int:
    """Returns a new id everytime it is called"""
    global __current_id

    toret = __current_id
    __current_id += 1

    return toret
