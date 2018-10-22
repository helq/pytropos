# ignoring some files when testing

from glob import glob

collect_ignore = ['tests/example_code']

# Neomake (vim plugin) generates sometimes files that should be ignored
for file in glob('tests/**/.*@neomake_*.py', recursive=True):
    collect_ignore.append(file)

for file in glob('tests/**/tools.py'):
    collect_ignore.append(file)
