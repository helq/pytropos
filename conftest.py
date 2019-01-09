# Pytest "configuration" file

import glob
import os
import re

# ignoring some files when testing
collect_ignore = ['tests/inputs']


# Neomake (vim plugin) generates sometimes trash files
for file in glob.glob(r'tests/**/.*@neomake_.*\.py', recursive=True):
    collect_ignore.append(file)


# Any file that doesn't start by 'test_' is ignored
not_a_test_file = re.compile(r'/(?!test_)[^/]*\.py$')

for root, _, files in os.walk('tests/'):
    for file in [os.path.join(root, f) for f in files]:
        if not_a_test_file.search(file):
            collect_ignore.append(file)
