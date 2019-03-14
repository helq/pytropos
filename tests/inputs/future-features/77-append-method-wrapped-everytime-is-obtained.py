lst = []

hipths1 = lst.append.__self__ is lst                    # This is True
hipths2 = lst.append.__self__.append is not lst.append  # This is True
hipths3 = lst.append.__func__  # Fails :S, append here is returned as a builtin method not a wrapper around a builtin method

class A:
    def fun(self) -> None:
        pass

a = A()
hipths4 = a.fun.__self__ is a                            # This is True
hipths5 = a.fun.__self__.fun is not a.fun                # This is True
hipths6 = a.fun.__self__.fun.__func__ is a.fun.__func__  # This is True
