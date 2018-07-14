from tensorlint.internals import Any

__all__ = ['dummy']

# dummy is quite interesting. It is used in the following way:
# > from tensorlint.libs.dummy import dummy as lib
# > lib.addition( Int(5), Float(), Any() )
# Any()
#
# Dummy acquires its power form Any. Any is an object that can do anything but
# always returns Any for all its operations
dummy = Any()
