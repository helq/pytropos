# -*- coding: utf-8 -*-
# Taken from https://gitlab.com/homochirality/listanalchem
# listanalchem/listanalchem/tools.py
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
import sys
import numpy as np

## Type imports for type checking with MYPY
#if 'typing' in sys.modules.keys():
#    from typing import (
#        List,
#    )

from functools import reduce
#from sympy.parsing.sympy_parser import parse_expr
import listanalchem.reduce_cas as redcas

def extreme_currents(SC_, verbose=False):
    Tiny = 1e-10
    Nr = SC_.shape[1] # number of reactions
    Ra = np.linalg.matrix_rank( SC_ )

    #SC_singular = False
    # Checking if stoichiometric matrix is singular
    # if it is, some repeated rows are eliminated from the matrix
    if Ra < SC_.shape[0]:
        #SC_singular = True
        non_singular_rows, removed_rows = __rows_to_keep(SC_)
        SC = SC_[ non_singular_rows ]
        if verbose:
            print("NOTE!: Extreme currents of stoichiometric matrix will be computed from reduced stoichiometric matrix")
            eliminated_rows = SC_.shape[0] - SC.shape[0]
            print("Stoichiometric matrix reduced to ({} row{} eliminated):".format(eliminated_rows, 's' if eliminated_rows!=1 else ''))
            print(SC)
            print()
            if len(removed_rows) > 0: # This should always, always happen. If it doesn't happen it should probably raise an Exception.
                print("Rows eliminated ({}):".format(removed_rows))
                print(SC_[removed_rows])
                print()
    else:
        SC = SC_

    if Ra == SC.shape[1]: # SC is a non-singular square matrix
        return None

    N1 = Nr-SC.shape[0]-1

    B = np.zeros( (Nr, 1) )
    B[-1] = 1
    Nsol = 0
    E = []
    # searching for all extreme currents
    for N1_ones_array in __unique_permutations( [0]*(Nr-N1) + [1]*N1 ):
        # k = reduce( lambda acc, bit: 2*acc+bit, N1_ones_array, 0 ) # number represented by N1_ones_array
        indeces = [i for (i, num) in enumerate(N1_ones_array) if num == 1]

        A1 = np.zeros( (N1, Nr) )
        for i in range(N1):
            A1[i, indeces[i]] = 1

        found = False
        A2 = np.zeros( (1,Nr) )
        for colA in range(Nr):
            A2[0,colA] = 1
            A = np.concatenate( (SC,A1,A2), axis=0 )
            if not found and np.linalg.matrix_rank(A)==Nr:
                Ej = np.linalg.solve(A, B)
                #print(A)
                #print()
                found = True
                if np.amin(Ej) > -Tiny:
                    #print(A)
                    #print()
                    to_add = True
                    for colE in range(Nsol):
                        if ( Ej - E[colE] < Tiny*np.ones( (Nr,1) ) ).all():
                            to_add = False # solution already in the list of solutions
                    if to_add:
                        E.append( Ej )
                        # print("K =", k, " \tSolution #", Nsol+1)
                        Nsol += 1

    # Scaling each extreme current to integer numbers
    for i in range(Nsol-1):
        # first, find the smallest number in each column of E that is not zero (bigger than Tiny)
        # then, divide each column by the smallest number found
        E[i] /= min( [Eij for Eij in E[i].T.tolist()[0] if Eij > Tiny] )
        # TODO: dividing by the smallest doesn't necessary gives all numbers as reals
        # possible better approach, divide by all numbers smaller than one, and divide by gcd of them all

    # creating np.array from list of E[i] np.arrays (of sizes (1,Nr))
    #return {
    #    'E': np.concatenate(E, axis=1).round(),
    #    'SC_singular': SC_singular
    #}
    null_array = np.array([]).reshape( (Nr, 0) )
    return np.concatenate(E + [null_array], axis=1).round()

## From https://stackoverflow.com/a/30558049
def __unique_permutations(elements):
    if len(elements) == 1:
        yield (elements[0],)
    else:
        unique_elements = set(elements)
        for first_element in unique_elements:
            remaining_elements = list(elements)
            remaining_elements.remove(first_element)
            for sub_permutation in __unique_permutations(remaining_elements):
                yield (first_element,) + sub_permutation

def __rows_to_keep(A_):
    """
    Using gaussian elimination to know which columns to keep to make Ran(A_) == A_.shape[0],
    ie. which columns to preserve to make the matrix A_ non-singular
    A_ is a np.array
    """
    n, m = A_.shape
    A = A_.copy() # .astype( np.float64 ) # we only work with integers in this project
    indeces = np.array(range(n))

    # print(indeces)
    l = -1
    k = 0
    while k < n and l < m-1:
        l += 1
        maxindex = abs(A[k:, l]).argmax() + k
        # print("1")
        # print(A)
        if A[maxindex, l] == 0: # the whole column is zero
            continue
        # Swap rows
        if maxindex != k:
            temp = A[maxindex, :].copy()
            A[maxindex, :] = A[k, :]
            A[k, :] = temp
            # print(indeces[k])
            # print(indeces[maxindex])
            indeces[k], indeces[maxindex] = indeces[maxindex], indeces[k]
            # print("2")
            # print(indeces)
            # print(A)
            # exit(0)
        # Deleting k row (dependency) from all the other below
        for row in range(k+1, n):
            multiplier = A[row,l]/A[k,l] # A[k,l] is non zero
            A[row,:]  -= ( multiplier*A[k,:] ).astype( np.int64 )
        # print("3")
        # print(A)

        k += 1

    #print(k, l)

    # If the loop above finished with this condition, then some rows (n-k) are dependent of the rest
    if l==m-1:
        kept    = sorted(indeces[:k])
        removed = sorted(indeces[k:])
    # There is no row to remove, all rows are independent of each other
    else:
        kept    = sorted(indeces)
        removed = np.array([])

    #print(A)
    #print(indeces)

    return kept, removed#, A

def formula_with_quantifiers(num_species, num_reaction_speeds, dual_pairs, E_omega, R):
    atoms = ['x0 = x1']
    atoms.extend( 'x%d > 0' % i for i in range(num_species) )
    atoms.extend( 'k%d > 0' % i for i in range(num_reaction_speeds) )
    atoms.extend( 'k%d = k%d' % (a, b) for (a, b) in dual_pairs )
    atoms.extend( '%s = %s' % (str(E_omega[i,i]), str(R[i])) for i in range(num_reaction_speeds) )
    quantifiers_begining = []
    quantifiers_begining.extend( 'ex(x%d, ' % i for i in range(num_species) )
    quantifiers_begining.extend( 'ex(k%d, ' % i for i in range(num_reaction_speeds) )
    quantifiers_ending = ')'*(num_species+num_reaction_speeds)
    return ''.join(quantifiers_begining) + ' and '.join(atoms) + ' ' + quantifiers_ending

def eliminate_quantifiers(formula, verbose=False):
    """
    Using `reduce` computational algebra system to eliminate quantifiers from first order forumla
    """
    no_quantifiers = None
    with redcas.ReduceCAS(verbose=verbose) as red:
        no_quantifiers = red.eliminate_quantifiers(formula)
    return no_quantifiers

def formula_to_inequalities_list( string_formula ):
    """
    Takes a  string of the form "`ineq` and `ineq` and ..." (where `ineq` is
    either "`js` < `js`" or "`js` > `js` for some variables `js`")
    """
    #formula_list = []
    #for ineq in string_formula.replace(' < ',' <= ').replace(' > ',' >= ').split('and'):
    #    if ineq.find(' = ') != -1: # if ineq is an Eq
    #        ineq = 'Eq('+ ineq.replace(' = ',',') +')'
    #    formula_list.append( parse_expr(ineq) )
    #return formula_list
    return string_formula.replace(' < ',' <= ').replace(' > ',' >= ').split('and')

def sample_from_inequalities( ineqs_list, vars, verbose=False ):
    sample  = None
    if 'false' in ineqs_list: return None # system is inconsistent
    with redcas.ReduceCAS(verbose=verbose) as red:
        sample  = red.sample_from_inequalities( ineqs_list, vars )
    return sample

def get_ranges_for_inequalities( ineqs_list, verbose=False ):
    with redcas.ReduceCAS(verbose=verbose) as red:
        result = red.get_ranges_for_inequalities( ineqs_list )
    return result

def ranges_and_eqs_to_strs( eqs_and_ranges ):
    return [
        str(ks) + " = " + str(e)
        for ks, e in eqs_and_ranges
    ]

import listanalchem.mypprint as lpprint
import stopit

from distutils.version import LooseVersion
import sympy

# `error_when_incomplete` was added to sympy in commit 88bca19948a9f937be21de14e72069017ab5cec2,
# for more info look at https://github.com/sympy/sympy/commit/88bca19948a9f937be21de14e72069017ab5cec2
if LooseVersion(sympy.__version__) < LooseVersion("1.1.1"):
    eigen_kargs = {}
else:
    eigen_kargs = {"error_when_incomplete": False}

@stopit.threading_timeoutable(default=None)
def get_eigenvects(matrix):
    # TODO: add "try catch" block because for the version where `error_when_incomplete` is not defined can fail if it doesn't find all eigenvalues :(
    return matrix.eigenvects(**eigen_kargs)

@stopit.threading_timeoutable(default=None)
def get_eigenvals(matrix):
    # TODO: add "try catch" block because for the version where `error_when_incomplete` is not defined can fail if it doesn't find all eigenvalues :(
    return matrix.eigenvals(**eigen_kargs)

def get_and_print_eigenvects(matrix, output={'latex': False, 'no_pretty': False}, timeout=300):
    sympy_pprint = lpprint.get_sympy_pprint(latex=output['latex'], no_pretty=output['no_pretty'])

    # trying to get eigenvectors, if it fails (times out) it will try to find only the eigenvalues
    eigenvects_exception = False
    try:
        eigenvects = get_eigenvects(matrix, timeout=timeout)
    except Exception as e:
        print("Couldn't calculate eigenvectors. Some internal exception occurred :S", file=sys.stderr)
        print(e, file=sys.stderr)
        eigenvects = None
        eigenvects_exception = True

    if eigenvects is None:
        if not eigenvects_exception:
            print("Error: Eigenvectors calculation took more than {} secs!".format(timeout))
        print("Trying to calculate only eigenvalues now")
        eigenvals = get_eigenvals(matrix, timeout=timeout)
        if eigenvals is None:
            print("I'm really sorry, but I couldn't calculate the Eigenvectors")
            print()
            return
        else:
            eigenvects = [(eig, mul, None) for (eig, mul) in eigenvals.items()]
            print()

    # making sure the sum of all eigenvectors' algebraic_mul is the same as the size of the matrix
    if matrix.shape[0] != sum(e[1] for e in eigenvects):
        print("Warning: not all eigenvectors could be calculated :S\n")
    for i, (eigenvalue, algebraic_mul, eigenvector) in enumerate(eigenvects):
        print("Eigenvalue", i+1, end=" ")
        print("(with algebraic multiplicity of:", algebraic_mul, end=")\n")
        sympy_pprint(eigenvalue)
        if eigenvector is not None:
            print("Eigenvector of eigenvalue", i+1)
            sympy_pprint(eigenvector)
    print()
    return eigenvects
