__all__ = ['NonImplementedTL', 'Singleton']

class NonImplementedTL(Exception):
    pass

# Singleton class taken from: https://stackoverflow.com/a/6798042
class Singleton(type):
    _instances = {} # type: ignore
    def __call__(cls, *args, **kwargs): # type: ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
