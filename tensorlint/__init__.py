# -*- coding: utf-8 -*-
"""Can check for correctness of tensor operations in numpy"""

from tensorlint import metadata

__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright

from tensorlint.internals import *  # noqa: F403, F401
