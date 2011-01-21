'''
*python-morfeusz* is a set of bindings for Morfeusz_,
a Polish morphological analyser.

.. _Morfeusz:
   http://sgjp.pl/morfeusz/
'''

classifiers = '''
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Natural Language :: Polish
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Text Processing :: Linguistic
'''.strip().split('\n')

import os
import distutils.core

def get_version():
    file = open('morfeusz.py')
    try:
        for line in file:
            if line.startswith('__version__ ='):
                version = line.split('=', 1)[1]
                return eval(version, {}, {})
    finally:
        file.close()
    raise IOError('Unexpected end-of-file')

os.putenv('TAR_OPTIONS', '--owner root --group root --mode a+rX')

distutils.core.setup(
    name = 'python-morfeusz',
    version = get_version(),
    license = 'MIT',
    description = 'bindings for Morfeusz',
    long_description = __doc__.strip(),
    classifiers = classifiers,
    url = 'http://jwilk.net/software/python-morfeusz',
    author = 'Jakub Wilk',
    author_email = 'jwilk@jwilk.net',
    py_modules = ['morfeusz']
)

# vim:ts=4 sw=4 et
