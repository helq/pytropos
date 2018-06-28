from mypy import fastparse
from mypy import nodes as mn
# import mypy.types
from typing import Union, Any, Dict, Set

# Trying to get hash of element, if it fails it will try to get a hash result
# of combining hashes from elems
def special_hash( e : Any ) -> int:
    try:
        return hash(e)
    except Exception:
        return hash( tuple([special_hash(ee) for ee in dir(e) if ee[0] != '_']) )

def todict(mypyobj : mn.MypyFile) -> Union[Dict[str, Any], str, None, int, float, list, tuple]:
    """
    Extracts the parsed and (optionally) analysed AST represented inside a mypy.nodes.MyPyFile object.

    Parsing the code and printing it on the screen:

    > from mypy import fastparse
    > file_name = 'file_example.py'
    > ff = open(file_name, 'r').read()
    > mypyfile = fastparse.parse(ff, file_name, None)
    > print( json.dumps(todict(mypyfile), indent=1) )

    Parsing the code, analysing it with mypy, and printing it:

    > from mypy import build, main
    > import os, glob
    >
    > sources, options = main.process_options(['file_example.py'])
    >
    > b = build.build(sources, options)
    > messages = b.errors
    > d = todict( b.files['file_example'] )
    >
    > print( json.dumps(d, indent=1) ) # the AST
    > print( messages ) # typing errors found by mypy

    """
    visited : Set[int] = set()

    # The use of Dict[str, Any] is unavoidable, if Any is changed to any other
    # type the
    #def helper(mypyobj : Union[mn.Context, dict, str, None, int, float, list, tuple]) -> Union[Dict[str, Any], str, None, int, float, list, tuple]:
    def helper(mypyobj : Any) -> Union[Dict[str, Any], str, None, int, float, list, tuple]:
        # print(type(mypyobj).__name__, " ->")
        # toret = None
        if mypyobj is None:
            # print("<- None")
            return None

        if isinstance(mypyobj, int) or isinstance(mypyobj, float): # this captures booleans too
            return mypyobj

        if isinstance(mypyobj, list):
            return [helper(obj) for obj in mypyobj]

        if isinstance(mypyobj, tuple):
            return tuple(helper(obj) for obj in mypyobj)

        if isinstance(mypyobj, set):
            return list(mypyobj)

        # Only used in MyPyFile objects which have an element (called alias_deps) of type dict
        if isinstance(mypyobj, dict):
            return { str(i) : helper(x) for i,x in mypyobj.items() }

        # print( type(mypyobj) )
        # print( mypyobj )
        if isinstance(mypyobj, mn.Context) and special_hash(mypyobj) not in visited:
            visited.add( special_hash(mypyobj) )

            obj_vars = [v for v in dir(mypyobj)
                          if v[:1] != '_'
                         and not callable( getattr(mypyobj, v) ) ]

            # if I don't put the type here, mypy will infer that the type is Dict[str, str] :S
            contents : Dict[str, Any] = {
                'type_name_mypy': "{}.{}".format(type(mypyobj).__module__ ,type(mypyobj).__name__)
            }

            methods = ['name', 'fullname'] # methods to call if they exist

            contents.update({
                v: getattr(mypyobj, v)() for v in methods
                if v in dir(mypyobj) and callable( getattr(mypyobj, v) )
            })

            ignore = ['FLAGS', # Additional uncessary info from functions
                      'imports', # MypyFile have a separate list for imports, but it isn't that necessary
                      'definition', # recursive reference from mypy.types.CallableType to Node :S
                      # we don't need to save this, this carries the same
                      # information as type, the difference lies that `type` may
                      # change depending on what the mypy inference algorithm does
                      #'unanalyzed_type',
                      'mro' # a variable used in type inference
                      ]

            # print(type(mypyobj).__name__, obj_vars)
            # for v in obj_vars:
            #     if not v in ignore:
            #         var = getattr(mypyobj, v)
            #         # print("var: '{}' of type: '{}'".format(v, type(var).__name__))
            #         d = helper( var )
            #         contents[v] = d
            contents.update({
                v: helper( getattr(mypyobj, v) ) for v in obj_vars
                if not v in ignore
            })

            return contents

        return str(mypyobj)

    return helper(mypyobj)

__all__ = ['todict']
