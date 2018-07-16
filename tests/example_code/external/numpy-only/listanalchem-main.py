#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Taken from https://gitlab.com/homochirality/listanalchem
# listanalchem/listanalchem/__main__.py
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

def main(config, model_path):
    from listanalchem.reactions_parser import ReactionsDetails # , sna_matrices

    print("Welcome to Listanalchem!")
    print("Remember to check the model you're loading, it must:")
    print("* Have a name `modelname`")
    print("* Have a list of species `species` (note: the first two species will be considered enantiomers, all other species do not)")
    print("* Have a non-empty list of reactions")
    print()

    # Sympy pretty printing, used to print results in LaTeX format
    #from sympy import init_printing
    #init_printing(use_latex=True)

    modelname, species, reactions = load_model(model_path)

    if config['Andres&Carolina Analysis']['enable']:
        rd = ReactionsDetails( reactions, species, sort_by='andres&carolina' )

        reactions_andrescarolina = rd.get_reactions_andrescarolina()
        # detecting if reactions were all of the right type (synthesis, ...) and had dual pairs
        isAndresCarolina = len(reactions_andrescarolina['others']) == 0

        if isAndresCarolina:
            print("!! Attention! The order of the entered reactions has changed to follow the order:")
            print("!! synthesis, fo-decomposition, autocatalytic, so-decomposition,")
            print("!! no-enantioselective and inhibition")
        else:
            print("!! Attention! Algorithm Andres&Carolina will not be executed (look below for more info)")

        print()

    # creating matrices without andrescarolina analysis or the list of reactions doesn't fulfill an
    # andrescarolina chemical network
    if not config['Andres&Carolina Analysis']['enable'] or not isAndresCarolina:
        # creating all matrices, leaving reactions list in the same order it was entered
        #S, K, R, xs, ks = sna_matrices(reactions, species)
        rd = ReactionsDetails( reactions, species, sort_by=None )

    print_modelname(modelname)
    print()
    print_model_details(rd, config['output'])
    output = config['output']

    if config['Trace-Determinant Analysis']['enable']:
        print("\n============================= ( - 1 - ) =============================")
        import listanalchem.analyses._01_tracedeterminant as tracedeterminant
        jacobWithOnly2Species = config['Trace-Determinant Analysis']['only 2 species for jacobian']
        tracedeterminant.run_analysis(rd, jacobWithOnly2Species=jacobWithOnly2Species, output=output)

    if config['Belgian Analysis']['enable']:
        print("\n============================= ( - 2 - ) =============================")
        import listanalchem.analyses._02_belgian as belgian
        belgian.run_analysis(rd, output=output)

    if config['Andres&Carolina Analysis']['enable']:
        print("\n============================= ( - 3 - ) =============================")
        import listanalchem.analyses._03_andrescarolina as andrescarolina
        andrescarolina.run_analysis(rd, reactions_andrescarolina, output=output)

    if config['Andres&Carolina Analysis 2']['enable']:
        print("\n============================= ( - 4 - ) =============================")
        import listanalchem.analyses._04_andrescarolina2 as andrescarolina2
        andrescarolina2.run_analysis(rd, output=output)

    if config['Andres&Carolina Analysis 2 + SNA']['enable']:
        print("\n============================= ( - 5 - ) =============================")
        import listanalchem.analyses._05_andrescarolina2_sna as andrescarolina2_sna
        n_samples = config['Andres&Carolina Analysis 2 + SNA']['n_samples']
        m_samples = config['Andres&Carolina Analysis 2 + SNA']['m_samples']
        samples_folder = config['Andres&Carolina Analysis 2 + SNA']['samples_folder']
        andrescarolina2_sna.run_analysis(rd, n_samples, m_samples, samples_folder, modelname, output)

    print_modelname(modelname)


def load_model(model_file):
    # Opening file where the model is saved
    model_str = model_file.read()

    # Loading model
    try:
        model = {}
        exec(model_str, {}, model)
    except Exception as e:
        print("Model file is faulty, there may be a comma missing")
        print(e)
        exit(1)

    # Verifying model's consistency
    allstr = lambda l: all( isinstance(s, str) for s in l )
    assert "modelname" in model, "`modelname` is missing on the model file"
    assert "species"   in model, "`species` is missing on the model file"
    assert "reactions" in model, "`reactions` is missing on the model file"
    assert isinstance( model["modelname"], str ), "`modelname` must be a string"
    assert isinstance( model["species"], list )   and allstr( model["species"] ),   "`species` must be a list of strings"
    assert isinstance( model["reactions"], list ) and allstr( model["reactions"] ), "`reactions` must be a list of strings"

    # extracting model's data
    return (model["modelname"], model["species"], model["reactions"])

def print_modelname(modelname):
    print("*"*(len(modelname)+10))
    print("*** ", modelname, " ***")
    print("*"*(len(modelname)+10))

def print_model_details(rd, output={'latex': False, 'no_pretty': False}):
    import pprint
    import sympy
    import numpy as np
    from listanalchem.mypprint import get_sympy_pprint

    sympy_pprint = get_sympy_pprint(latex=output['latex'], no_pretty=output['no_pretty'])

    S, K, R, species, reactions = rd.S, rd.K, rd.R, rd.species, rd.get_reactions()
    nS, nR = S.shape # number of species and number of reactions

    ### Printing model's details and matrices ###
    print("Species:")
    print(species)
    print("Reactions list:")
    pprint.pprint(reactions)

    print("\nStoichiometric Matrix:")
    sympy_pprint(S)
    print("\nReactions Order Matrix:")
    sympy_pprint(K)
    print("\nVelocity Function:")
    sympy_pprint(R)
    print()

    print("Differential equations functions (polynomials) vector:")
    sympy_pprint(S*R)
    print()

    if S.shape[0] != np.linalg.matrix_rank(S):
        print("Warning: Stoichiometric Matrix is SINGULAR!")
        print()

# code to use with args parser, gotten from https://stackoverflow.com/a/43357954
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == '__main__':
    import argparse
    from argparse import FileType
    import os
    if os.name == 'posix':
        _, columns_console = os.popen('stty size', 'r').read().split()
    else:
        columns_console = 80

    parser = argparse.ArgumentParser(
        description='Execute a stability analysis on a chemical network.'
                   +' Used principally for research in homochirality.',
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40, width=int(columns_console)) )

    parser.add_argument('--model',
                        type=FileType('r'),
                        default='models/Kondepudi-Nelson-Strecker-Amino-acids-Production-Limited-Enantio-Selectivity-KNS-AP-LES-Model-2.py',
                        help='Location of file holding chemical network model'
                            +' (default: models/Kondepudi-Nelson-Strecker-Amino-acids-Production-Limited-Enantio-Selectivity-KNS-AP-LES-Model-2.py)',
                        metavar='file')
    parser.add_argument('--tracedeterminant',
                        type=str2bool,
                        default=True,
                        help='Enable|Disable (first) Trace-Determinant Analysis (default: true)',
                        metavar='(t|f)')
    parser.add_argument('--tracedeterminant-jacob-2',
                        type=str2bool,
                        default=True,
                        help='Enable|Disable usage of a reduced jacobian matrix'
                            +' (2x2, left- and uppermost) for Trace-Determinant Analysis (default: true)',
                        metavar='(t|f)')
    parser.add_argument('--belgian',
                        type=str2bool,
                        default=True,
                        help='Enable|Disable (second) Belgian-Serbian Analysis (default: true)',
                        metavar='(t|f)')
    parser.add_argument('--andrescarolina',
                        type=str2bool,
                        default=True,
                        help='Enable|Disable (third) Andres&Carolina Analysis (default: true).'
                            +' Caution: Activating this modifies the order of the reactions'
                            +' for all other analysis',
                        metavar='(t|f)')
    parser.add_argument('--andrescarolina2',
                        type=str2bool,
                        default=True,
                        help='Enable|Disable (fourth) Andres&Carolina 2 Analysis (default: true).',
                        metavar='(t|f)')
    parser.add_argument('--andrescarolina2-sna',
                        type=str2bool,
                        default=True,
                        help='Enable|Disable (fifth) SNA + Andres&Carolina Criterion Analysis with sampling (default: true).',
                        metavar='(t|f)')
    parser.add_argument('--n_samples',
                        type=int,
                        default=1,
                        help='Number of samples to take (used only with --andrescarolina2-sna option) (default: 1).',
                        metavar='INT')
    parser.add_argument('--m_samples',
                        type=int,
                        default=1000,
                        help='Number of samples to when calculating proportion of frank states (used only with --andrescarolina2-sna option) (default: 1000).',
                        metavar='INT')
    parser.add_argument('--samples_folder',
                        type=str,
                        default=None,
                        help="Place to save samples (samples are save in chemulator's `simu.json' format) (used only with --andrescarolina2-sna option) (default: None).",
                        metavar='dir')
    parser.add_argument('--latex',
                        type=str2bool,
                        default=False,
                        help='Enable|Disable LaTeX output of formulas and matrices (default: false).',
                        metavar='(t|f)')
    parser.add_argument('--no-pretty',
                        type=str2bool,
                        default=False,
                        help='Enable|Disable Pretty output (it is overrided by LaTeX output) (default: false).',
                        metavar='(t|f)')
    args = parser.parse_args()
    #print(args)

    config = {
        'Trace-Determinant Analysis': {
            'enable': args.tracedeterminant,
            'only 2 species for jacobian': args.tracedeterminant_jacob_2
        },
        'Belgian Analysis': {
            'enable': args.belgian
        },
        'Andres&Carolina Analysis': {
            'enable': args.andrescarolina
        },
        'Andres&Carolina Analysis 2': {
            'enable': args.andrescarolina2
        },
        'Andres&Carolina Analysis 2 + SNA': {
            'enable': args.andrescarolina2_sna,
            'n_samples': args.n_samples,
            'm_samples': args.m_samples,
            'samples_folder': args.samples_folder
        },
        'output': {
            'latex': args.latex,
            'no_pretty': args.no_pretty
        }
    }

    try:
        main(config, args.model)
    except Exception as msg:
        print("An unexpected error occurred when running an analysis", file=sys.stderr)
        print("  Please open an issue in https://gitlab.com/homochirality/listanalchem, include", file=sys.stderr)
        print("  the model you are using that is causing trouble.", file=sys.stderr)
        print(file=sys.stderr)
        print("  The error message return by the program was:", file=sys.stderr)
        print("   ", msg, file=sys.stderr)
        print(file=sys.stderr)
        raise msg
