# encoding=UTF-8

# Copyright © 2010-2017 Jakub Wilk <jwilk@jwilk.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
*python-morfeusz* is a set of bindings for Morfeusz_,
a Polish morphological analyser.

.. _Morfeusz:
   http://sgjp.pl/morfeusz/
'''

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
'''.strip().splitlines()

distutils.core.setup(
    name='python-morfeusz',
    version=get_version(),
    license='MIT',
    description='bindings for Morfeusz',
    long_description=__doc__.strip(),
    classifiers=classifiers,
    url='http://jwilk.net/software/python-morfeusz',
    author='Jakub Wilk',
    author_email='jwilk@jwilk.net',
    py_modules=['morfeusz']
)

# vim:ts=4 sts=4 sw=4 et
