# -*- coding: utf-8 -*-
# Taken from https://gitlab.com/homochirality/listanalchem
# listanalchem/listanalchem/mypprint.py
# Minor modifications to the code

# Copyright 2018 Universidad Nacional de Colombia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function, division

import os, pprint, sympy
import numpy as np

def print_latex(x):
    if isinstance(x, np.ndarray):
        x = sympy.Matrix(x)
    print(sympy.latex(x))

def sympy_pprint(x):
    if isinstance(x, np.ndarray):
        print(x)
    else:
        sympy.pprint(x)

def get_sympy_pprint(latex=False, no_pretty=True):
    if   latex:           return print_latex
    elif no_pretty:       return lambda x: print(repr(x))
    elif os.name == 'nt': return pprint.pprint
    else:                 return sympy_pprint

def sympy_pretty(x):
    if isinstance(x, np.ndarray):
        return str(x)
    else:
        return sympy.pretty(x)

def get_sympy_pretty(latex=False, no_pretty=True):
    if   latex:           return sympy.latex
    elif no_pretty:       return repr
    elif os.name == 'nt': return pprint.pformat
    else:                 return sympy_pretty
