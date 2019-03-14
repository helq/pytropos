# Pytropos #

Experimental python linter/interpreter intended to check tensor/matrix/arrays operations
using NumPy.

Currently, it only supports a selected subset of Python and NumPy. Check it out and report
any issues or ideas you may have :)

## Intallation ##

Easy installation with `pip`:

    pip install git+https://github.com/helq/pytropos

## Execute ##

To analyse a python file run:

    pytropos <file>

(In development mode run `paver run <file>`, it doesn't require to run pip everytime).

Or if you want to try to run a statement at the time run the Repl:

    pytropos -r

## Examples of execution ##

The following piece of code is warrantied to fail in Python 3:

~~~python
i = 3
x = 0.0
y = i / x  # division by zero
x += y - i
print(x)
~~~

Running the code in Pytropos gives us:

    > pytropos excode.py
    excode.py:3:4: E001 ZeroDivisionError: float division by zero

A more complex example:

~~~python
import numpy as np

a = np.zeros( (10,6) )

m = 4 + 1
n = 0 + 2

if m == 5:
    n = 1
else:
    m = 6

b = np.ones( (m,n) )
res = np.dot(a, b)  # fails here

print(res)

var = True

if var:
    b = np.zeros( (3, 11) )
    res = np.dot(b, a)  # fails here

print(res)
~~~

and pytropos detects there's an error in the shape of some `numpy` arrays and informs us.

    > pytropos excode2.py
    excode2.py:14:6: W503 ValueError: shapes (10, 6) and (5, 1) not aligned: 6 (dim 1) != 5 (dim 0)
    excode2.py:22:10: W503 ValueError: shapes (3, 11) and (10, 6) not aligned: 11 (dim 1) != 10 (dim 0)

One last example using Pytropos type hints to indicate the expected shapes of the arrays
to define:

~~~python
import numpy as np
from somelib import data
from pytropos.hints.numpy import NdArray

A: NdArray[2, 3] = np.array(data)  # Helping Pytropos knowing the shape
x = np.array([1, 2, 0, 0])

y = A.dot(x)  # This fails!
~~~

Pytropos notifies us that the `dot` operation will fail:

    pytropos excode3.py
    excode3.py:7:4: W503 ValueError: shapes (2, 3) and (4,) not aligned: 3 (dim 1) != 4 (dim 0)

Note: Pytropos type hints do not carry any information when running them from the Python
interpreter, they only have meaning inside Pytropos and they may change the value as seen
in the example above.

## FAQ ##

- Q: What is Pytropos? What does Pytropos uses behind the scenes?

    A: Pytropos is a Python 3.6+ interpreter and Static Analyser based on Abstract
    Interpretation. Abstract Interpretation purpose is to "soundly" overapproximate the
    results of computing a piece of code, that means, it intends to tells you what are all
    the possible results of executing a piece of code as precisely as it can.

<!-- An in depth explanation on how Pytropos works can be found at <urltomasterthesis> -->

- Q: I run `pytropos <file>` but I see no output from `print(expr)` statements

    A: Pytropos cares only about the result of executing a statement and doesn't care
    about the side effects the statements may throw. Python's `print` function call
    "side effect" is to output to the screen but this side effect is never executed as
    Pytropos does not handle them. If Pytropos detects that a piece of code will fail to
    run it will print a warning on the screen.

- Q: It says that Pytropos can be used as a linter. How do I do that in my IDE?

    A: Althought running Pytropos as a Linter isn't a big deal as it outputs all warnings
    in the same format (`file:col:line <Warning message>`), it requires a specific
    configuration dependending on the IDE being used. I use the following configuration
    for Neomake for (neo)vim:

    ~~~vim
    function! PostProcessingPytropos(entry)
        " Pytropos uses 0-indexed columns, and Neovim uses 1-indexed
        let a:entry.col += 1

        if a:entry.text =~# '^E'  ||  a:entry.text =~# '^SyntaxError'
            let a:entry.type = 'E'
        elseif a:entry.text =~# '^W'
            let a:entry.type = 'W'
        elseif a:entry.text =~# '^F'
            let a:entry.type = 'F'
        else
            let a:entry.type = 'A'
        endif
    endfunction

    let g:neomake_python_pytropos_maker = {
       \ 'exe': 'pytropos',
       \ 'args': [],
       \ 'errorformat':
         \ '%f:%l:%c: %m',
      \ 'postprocess': [
         \ function('PostProcessingPytropos'),
         \ ]
      \ }

    let g:neomake_python_enabled_makers += ['pytropos']
    ~~~

## Supported Python Characteristics ##

- Builtin primitives: int, float, bool, list, and tuple value types
- Attribute Access
- Subscript Access (basic, no slices)
- If and While statements
- Type Hints (May change a value if used)
- Import (limited to NumPy)
- Basic operations and comparisons (`+`, `-`, ..., `<`, `>`, `<=`, `>=`)

### Not supported ###

- Function declarations, Classes declarations
- For statement
- Slices
- Exceptions Raising and Catching
- Dictionaries
- Type Comments
- Type Hints without defining a variable
- Import (analysis of multiple files at the same time)

## Why is this all written in python 3.6+? ##

Pytropos only works with Python 3.6 or newer. But, why not Python 2?

It's time people to move on! Python 2 is an amazing tool, but it was announced many years
now that the core team will stop supporting it. Now we have Python 3, but it seems that
too much code is still written to work in Python 2 too, which means that we cannot write
in the style of Python 3. Well, let's move on.

PS: supporting two Python versions is a lot of work! Python 2 and Python 3 differ in a lot
of subtle ways: scopes, primitive data types, behaviour of builtin functions, ...

## Development ##

Create and enter enviroment:

    python3 -m venv venv-env3
    source venv-env3/bin/activate

Install requirements and configure git hooks:

    pip install -r requirements-dev.txt
    git config --local core.hooksPath "git-hooks"

Pre- and post-commit hooks are in place to regenerate the documentation just before
commiting. If you want to disable temporarily the automatic regeneration create a file
named `no_docs_generation` on the root of the project:

    touch no_docs_generation

## Run tests ##

We have numerous unit and property-based tests (powered by [pytest][] and [hypothesis][]).
Additionally, [mypy][] and [flake8][] are run as tests too. To run them all:

    paver test_all

You can add pytest flags to a test with `paver test --flag`. As an example, you can look
at the statistics of the property-based tests with:

    paver test --hypothesis-show-statistics

You can limit the tests to check with the `-k`  flag:

    paver test -k test_main

[pytest]: https://pytest.org/
[hypothesis]: https://github.com/HypothesisWorks/hypothesis/
[mypy]: http://mypy-lang.org/
[flake8]: https://pypi.org/project/flake8/

To see test coverage of code:

    paver coverage

## Contributing ##

This project is part of my work for my master thesis and as such I'm a bit picky.

You're welcome to help. I'll be glad to hear some other voices about this.
