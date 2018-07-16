# Code taken from: https://github.com/helq/mlclass_homework_2_SVMs
# mlclass_homework_2_SVMs/01/01_cross_validation.py

from sklearn.model_selection import cross_validate
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.decomposition import KernelPCA

import numpy as np
import pickle
from multiprocessing import Pool

# getting data
xs_all_ = np.array( [[float(xi) for xi in x.split()] for x in open("xtrain.txt").readlines()] )
ys_all_ = np.array( [int(float(y)) for y in open("ytrain.txt").readlines()] )
n_all = len(xs_all_)

test_size = 300

## preprocessing
### KPCA
kpca = KernelPCA(kernel="poly", gamma=2.2, degree=2, fit_inverse_transform=True, max_iter=1000000)
xs_train_, xs_test_, ys_train_, ys_test_ = train_test_split(xs_all_, ys_all_, test_size=test_size, random_state=123)
xs_train_kpca = kpca.fit_transform(xs_train_)
xs_test_kpca = kpca.transform(xs_test_)

## Autoencoder
xs_all_autoencoder = np.array( [[float(xi) for xi in x.split()] for x in open("xtrain_encoded.txt").readlines()] )

# search grid parameters
grids_params = [
    {
        'preprocessing': 'no-preprocessing_variable-gamma',
        'kernel_params': {'kernel': 'poly', 'max_iter': 1000000},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            #gamma = 1./15 # this is the value by default
            'gamma': [1./450000 * 1.8**i for i in range(20)],
            'degree': list(range(1, 8))
        },
        'xs_all': xs_all_,
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'no-preprocessing',
        'kernel_params': {'kernel': 'poly', 'gamma': 1., 'max_iter': 1000000},#, 'verbose': True},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'degree': list(range(1, 8))
        },
        'xs_all': xs_all_,
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'scaling',
        'kernel_params': {'kernel': 'poly', 'gamma': 1., 'max_iter': 1000000},#, 'verbose': True},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'degree': list(range(1, 8))
        },
        'xs_all': (xs_all_ - xs_all_.mean( (0,) )) / xs_all_.std( (0,) ), # scaling and centering
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'robust-scaling',
        'kernel_params': {'kernel': 'poly', 'gamma': 1., 'max_iter': 1000000},#, 'verbose': True},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'degree': list(range(1, 8))
        },
        'xs_all': preprocessing.robust_scale(xs_all_, axis=0),
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'normalization',
        'kernel_params': {'kernel': 'poly', 'gamma': 1., 'max_iter': 1000000},#, 'verbose': True},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'degree': list(range(1, 8))
        },
        'xs_all': preprocessing.normalize(xs_all_, norm='l2'),
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'kernelPCA_gamma1_poly1',
        'kernel_params': {'kernel': 'poly', 'gamma': 1., 'max_iter': 1000000},#, 'verbose': True},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'degree': list(range(1, 8))
        },
        'xs_train': xs_train_kpca,
        'xs_test': xs_test_kpca,
        'ys_train': ys_train_,
        'ys_test': ys_test_
    },
    {
        'preprocessing': 'autoencoder',
        'kernel_params': {'kernel': 'poly', 'gamma': 1., 'max_iter': 1000000},#, 'verbose': True},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'degree': list(range(1, 8))
        },
        'xs_all': xs_all_autoencoder,
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'no-preprocessing',
        'kernel_params': {'kernel': 'rbf'},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            #gamma = 1./15 # this is the value by default
            'gamma': [1./450000 * 1.8**i for i in range(20)]
        },
        'xs_all': xs_all_,
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'scaling',
        'kernel_params': {'kernel': 'rbf'},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'gamma': [1./45000 * 1.8**i for i in range(20)]
        },
        'xs_all': (xs_all_ - xs_all_.mean( (0,) )) / xs_all_.std( (0,) ), # scaling and centering
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'robust-scaling',
        'kernel_params': {'kernel': 'rbf'},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'gamma': [1./90000 * 1.8**i for i in range(20)]
        },
        'xs_all': preprocessing.robust_scale(xs_all_, axis=0),
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'normalization',
        'kernel_params': {'kernel': 'rbf'},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'gamma': [1./90000 * 2.2**i for i in range(20)]
        },
        'xs_all': preprocessing.normalize(xs_all_, norm='l2'),
        'ys_all': ys_all_
    },
    {
        'preprocessing': 'kernelPCA_gamma1_poly1',
        'kernel_params': {'kernel': 'rbf'},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'gamma': [1./90000 * 2.2**i for i in range(20)]
        },
        'xs_train': xs_train_kpca,
        'xs_test': xs_test_kpca,
        'ys_train': ys_train_,
        'ys_test': ys_test_
    },
    {
        'preprocessing': 'autoencoder',
        'kernel_params': {'kernel': 'rbf'},
        'axes': {
            'nu': np.arange(.02,.8,.02),
            'gamma': [1./90000 * 2.2**i for i in range(20)]
        },
        'xs_all': xs_all_autoencoder,
        'ys_all': ys_all_
    },
]

def cross_validate_with_params( params ):
    """Uses global variables: xs_train, ys_train, axes_keys"""

    axes_coord, kernel_params = params

    clf = svm.NuSVC(**kernel_params)
    scores = cross_validate(clf, xs_train, ys_train, cv=5, return_train_score=True)#, n_jobs=-1)

    clfmdl = clf.fit(xs_train, ys_train)

    for axis_k in axes_keys:
        print("{}: {:<9.3g}".format(axis_k, kernel_params[axis_k]), end=" ")

    print("Accuracy: {:.5g} (+/- {:.5g}) Num support: {:d}"
          .format(scores["test_score"].mean(),
                  scores["test_score"].std() * 2,
                  clfmdl.support_.shape[0]))

    return (scores, clfmdl.support_.shape[0])

if __name__ == '__main__':
    for params in grids_params:
        if "xs_all" in params:
            # partitioning
            xs_train, xs_test, ys_train, ys_test = \
                    train_test_split(params['xs_all'], params['ys_all'], test_size=test_size, random_state=123)
        elif "xs_train" in params:
            xs_train = params['xs_train']
            xs_test  = params['xs_test']
            ys_train = params['ys_train']
            ys_test  = params['ys_test']
        else:
            raise "there is no data, neither `xs_train` nor `xs_all`"

        # Cross-validation
        print("Cross-validation processing")

        axes = params['axes']
        axes_keys = list(axes.keys())
        axes_values = [axes[k] for k in axes_keys]

        grid_size = 1
        axes_sizes = []
        for axis_v in axes.values():
            axis_size = len(axis_v)
            grid_size *= axis_size
            axes_sizes.append( axis_size )

        kernels_params = []
        for idx in range(grid_size):
            kernel_params = params['kernel_params'].copy()
            axes_coord = []
            for i in range(len(axes)-1, -1, -1):
                axis_size = axes_sizes[i]
                axis_idx = idx%axis_size
                idx = int(idx/axis_size)

                axis_value = axes_values[i][axis_idx]

                axes_coord.append(axis_value)
                kernel_params[axes_keys[i]] = axis_value

            axes_coord = tuple(reversed(axes_coord))
            kernels_params.append( (axes_coord, kernel_params) )

            #cross_results[axes_coord] = None # initializing value to prevent weird behaivor when running the code in parallel
            #print(axes_coord)
            #print(kernel_params)

        pool = Pool(processes=10)
        grid_results = pool.map( cross_validate_with_params, kernels_params )
        cross_results = { kernels_params[i][0]:grid_results[i] for i in range(grid_size) }

        with open("cross_validation/cross_validation-{}-{}.dat"
                  .format(params['kernel_params']['kernel'], params['preprocessing']), "wb") as f:
            pickle.dump( tuple(axes_keys), f )
            pickle.dump( cross_results, f )
