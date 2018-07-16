# -*- coding: utf-8 -*-
# Taken from https://gitlab.com/homochirality/listanalchem
# listanalchem/listanalchem/analyses/_02_belgian.py
# Minor modifications to the code

# Copyright 2017-2018 Universidad Nacional de Colombia
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

import numpy as np
import sympy
import pprint
import os
from functools import reduce
import listanalchem.mypprint as lpprint

if os.name == 'posix':
    _, columns_console = map(int, os.popen('stty size', 'r').read().split())
else:
    columns_console = 80

from listanalchem.tools import extreme_currents, get_and_print_eigenvects

from itertools import combinations
def mineurs(VJ, limit=0):
    sizeVJ = VJ.shape[0]
    if limit<1:
        limit = sizeVJ
    mineurs = []
    # searching in determinants of principal matrices for negative terms
    for n in range(1, min(limit, sizeVJ)+1):
        for index in combinations( range(sizeVJ), n ):
            mineur_ = VJ[index, index].det(method='berkowitz').expand()
            if mineur_ == 0:
                continue # don't even waste your time trying to find any negative coefficients on this mineur
            mineur = mineur_.as_poly()
            # print(mineur)
            negative_coefficients = { gens: coeff for gens, coeff in mineur.terms() if coeff < 0}
            if len(negative_coefficients) > 0: # there is at least a term with a negative coefficient
                # showResults(mineur, index, -1 * negative_coefficients, save_to_file)
                mineurs.append({
                    'mineur': mineur,
                    #'negative coefficients': negative_coefficients,
                    'index': index
                })
    return mineurs

import operator
def mul(xs, unity=1):
    return reduce(operator.mul, xs, unity)

def mineur_to_inequality(mineur):
    """Recives a sympy polynomial and creates a unequality from it"""
    nGens = len(mineur.gens)
    negative, positive = [], [] # negative and positive expressions of mineur (a principal determinant of VJ)
    for exps, coeff in mineur.terms():
        # mineur.gens contains all Js, e.g., (J1, J2, J3)
        # exps contains the exponents for each Jn
        term = abs(coeff) * mul([ mineur.gens[j]**exps[j] for j in range(nGens) ])
        (negative if coeff < 0 else positive).append(term) # if term is negative, then add it to negative terms, otherwise to positive
    return sum(negative) - sum(positive) > 0

def run_analysis(rd, output={'latex': False, 'no_pretty': False}):
    S, K, R, xs, ks = rd.S, rd.K, rd.R, rd.xs, rd.ks
    nS, nR = S.shape # number of species and number of reactions

    latex = output['latex']
    sympy_pprint = lpprint.get_sympy_pprint(latex=latex, no_pretty=output['no_pretty'])

    print("*** Stoichiometric Network Analysis using the algorithm from reference [3] in README.md ***")
    print()

    E = extreme_currents(S, verbose=True)
    if E is None:
        print("*******")
        print("Stoichiometric Matrix is square, therefore there are no extreme currents for this system")
        print("*******")
        return

    E = E.astype('int32')
    nE = E.shape[1] # number of extreme currents

    print("Extreme Currents Matrix")
    sympy_pprint(E)
    print()

    J =  sympy.symbols( 'j0:%d' % nE ) # convex parameters
    # E_omega = sum([sympy.diag(*E.T[i])*J[i] for i in range(nE)], sympy.zeros( nR, nR ))
    E_omega_prim = sum([E[:,i].reshape(nR,1)*J[i] for i in range(nE)], sympy.zeros( nR, 1 ))

    print("E_omega_prim matrix")
    sympy_pprint(E_omega_prim)
    print()

    # VJ_ = S * E_omega * K.T
    VJ = S * sympy.diag(*E_omega_prim) * K.T

    print("V(J) Matrix")
    sympy_pprint(VJ)
    print()

    print("\n==== Mineur Analysis ====")

    limit = 6 # limit to search for mineurs
    print("Limiting mineur analysis to mineurs of size smaller or equal to", limit)
    print()

    # TODO: Check if VJ must be multiplied by -1 or it shouldn't
    ms = mineurs(-VJ, limit)

    if len(ms) == 0:
        print("There are no negative terms in the determinant of any mineur of size <=", limit)
        #exit(0)

    for mineur in ms:
        print("Mineur:")
        sympy_pprint(mineur["mineur"])
        #print("Negative coefficients in mineur:")
        #sympy.pprint(mineur["negative coefficients"])
        print("Compounds number:", mineur["index"])
        print()

    serbs_inequalities = [sympy.sympify("j{} > 0".format(i)) for i in range(nE)] + [mineur_to_inequality(mineur["mineur"]) for mineur in ms]
    print("Serb's inequalities")
    if latex:
        serbs_inequalities = sympy.Matrix(serbs_inequalities)
        sympy_pprint(serbs_inequalities)
    else:
        pprint.pprint(serbs_inequalities)

    print("\n==== Matrix V(J) ====")
    print(" *** Trace-Determinant plane. See references [1] and [2] in README.md *** ")
    print()

    print("Trace of the V(J) matrix")
    sympy_pprint(VJ.trace().expand())
    print()
    print("Determinant of the V(J) matrix")
    determinant = VJ.det(method='berkowitz').expand()
    sympy_pprint(determinant)
    print()

    #if determinant < 0:
    #    print("*** You have saddle points ***")

    Discriminant = VJ.trace()**2 - 4*determinant
    print("Discriminant")
    sympy_pprint(Discriminant)
    print()

    #if Discriminant > 0:
    #    print("Only real roots: Node attractors or saddle points.")

    print(" ** Eigenvalues and eigenvectors of the VJ matrix **\n")
    get_and_print_eigenvects(VJ, output)
