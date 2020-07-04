# Pytropos #

Experimental Python linter/interpreter intended to check NumPy array operations.

Currently, it only supports a selected subset of Python and NumPy.

## Installation ##

Easy installation with `pip`:

    pip install git+https://github.com/helq/pytropos

## Execution ##

### Standalone / Checking file ###

To analyse a python file run:

    pytropos <file>

In "development mode", run using `paver run <file>`. (The development mode doesn't require
to execute pip every single time a change is made into the code. _Development mode_ means
that you download the repository to make changes to the code. See how to do so in
"Development" section below.)

### REPL ###

If you want to play with Pytropos as if it was a regular REPL for Python:

    pytropos -r

## File Examples ##

1. The following piece of code is warrantied to fail in Python:

    ~~~python
    i = 3
    x = 0.0
    y = i / x  # division by zero
    x += y - i
    print(x)
    ~~~

    Running the code in Pytropos will show the error the code will produce:

        > pytropos excode.py
        excode.py:3:4: E001 ZeroDivisionError: float division by zero

2. A more complex example:

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

    Pytropos detects an error in the shape of some NumPy arrays:

        > pytropos excode2.py
        excode2.py:14:6: W503 ValueError: shapes (10, 6) and (5, 1) not aligned: 6 (dim 1) != 5 (dim 0)
        excode2.py:22:10: W503 ValueError: shapes (3, 11) and (10, 6) not aligned: 11 (dim 1) != 10 (dim 0)

3. On some cases Pytropos cannot infer the shape of an array. If you want to tell Pytropos
    the shape, you can type hint the code:

    ~~~python
    import numpy as np
    from somelib import data
    from pytropos.hints.numpy import NdArray  # Won't import anything at runtime

    A: NdArray[2, 3] = np.array(data)  # Helping Pytropos knowing the shape
    x = np.array([1, 2, 0, 0])

    y = A.dot(x)  # This fails!
    ~~~

    Pytropos notifies us that the `dot` operation will fail:

        pytropos excode3.py
        excode3.py:7:4: W503 ValueError: shapes (2, 3) and (4,) not aligned: 3 (dim 1) != 4 (dim 0)

**Note:** Pytropos' type hints do not change the behaviour of the code in the regular Python interpreter.
They only have a meaning inside Pytropos, otherwise they are empty statements.

## FAQ ##

- Q: What is Pytropos? What does Pytropos uses behind the scenes?

    A: Pytropos is a Python 3.6+ interpreter and Static Analyser based on Abstract
    Interpretation. The purpose of Abstract Interpretation is to "soundly" overapproximate the
    results of computing a piece of code, that means, it intends to tells you what are all
    the possible results of executing a piece of code as precisely as it can.

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

## Development ##

Download the repository, then create and _source_ an enviroment:

    python3 -m venv venv-env3
    source venv-env3/bin/activate

Install requirements and configure git hooks:

    pip install -r requirements-dev.txt
    git config --local core.hooksPath "git-hooks"

Pre- and post-commit hooks are in place to regenerate the documentation just before
commiting. If you want to temporarily disable the documentation regeneration---it might be
a tad slow---, create a file named `no_docs_generation` on the root of the project:

    touch no_docs_generation

## Testing ##

There are a total of four kinds of tests: unit tests (using [pytest][]), property-based
tests (pytest + [hypothesis][]), [mypy][] type checking and [flake8][] linting. To run
them all:

    paver test_all

To only run Pytest type:

    paver test

Any argument passed to `paver test` will be redirected to Pytest. Two useful Pytest
arguments are:

    paver test --hypothesis-show-statistics

which will show the statistics of running `hypothesis`, and

    paver test -k word

which only runs tests containing the word `word` (e.g, `test_main`).

[pytest]: https://pytest.org/
[hypothesis]: https://github.com/HypothesisWorks/hypothesis/
[mypy]: http://mypy-lang.org/
[flake8]: https://pypi.org/project/flake8/

To see test coverage of code:

    paver coverage

## Citing ##

~~~bibtex
@MastersThesis{cruzPytropos2019,
  title = {Static Analysis of Python Programs using Abstract Interpretation: An Application to Tensor Shape Analysis},
 school = {Universidad Nacional de Colombia - Sede Bogot{\'a}},
 author = {Elkin Cruz-Camacho},
   year = {2019},
    url = {http://bdigital.unal.edu.co/72620/}
}
~~~

## Contributing ##

Write an issue or create a pull request!

This project was part of my work for my Master Thesis. I don't work on it anymore. It's
unmaintained. Nonetheless, I am happy to hear about ideas and pull requests :)
