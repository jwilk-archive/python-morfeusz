# encoding=UTF-8

# Copyright © 2007, 2008, 2010 Jakub Wilk <jwilk@jwilk.net>
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
Bindings for Morfeusz_ SIaT, a Polish morphological analyser.

.. _Morfeusz:
   http://nlp.ipipan.waw.pl/~wolinski/morfeusz/
'''

from __future__ import with_statement

import sys
py3k = sys.version_info >= (3, 0)

from collections import defaultdict
if py3k:
    from _thread import allocate_lock
else:
    from thread import allocate_lock
if not py3k:
    from itertools import izip as zip
import ctypes

if py3k:
    unicode = str

__author__ = 'Jakub Wilk <jwilk@jwilk.net>'
__version__ = '0.3001'
__all__ = ['analyse', 'about', 'expand_tags', 'ATTRIBUTES', 'VALUES']

ATTRIBUTES = '''
subst=number case gender
depr=number case gender
adj=number case gender degree
adja=
adjp=
adv=degree
num=number case gender accommodability
ppron12=number case gender person accentability
ppron3=number case gender person accentability post_prepositionality
siebie=case
fin=number person aspect
bedzie=number person aspect
aglt=number person aspect vocalicity
praet=number gender aspect agglutination
impt=number person aspect
imps=aspect
inf=aspect
pcon=aspect
pant=aspect
ger=number case gender aspect negation
pact=number case gender aspect negation
ppas=number case gender aspect negation
winien=number gender aspect
pred=
prep=case vocalicity
conj=
qub=vocalicity
xxs=number case gender
xxx=
interp=
ign=
'''
ATTRIBUTES = \
dict(
    (key, tuple(values.split()))
    for line in ATTRIBUTES.splitlines() if line
    for (key, values) in (line.split('=', 1),)
)

VALUES = '''
number=sg pl
case=nom gen dat acc inst loc voc
gender=m1 m2 m3 f n1 n2 p1 p2 p3
person=pri sec ter
degree=pos comp sup
aspect=imperf perf
negation=aff neg
accentability=akc nakc
post_prepositionality=npraep praep
accommodability=congr rec
agglutination=agl nagl
vocalicity=nwok wok
'''
VALUES = \
dict(
    (key, tuple(values.split()))
    for line in VALUES.splitlines() if line
    for (key, values) in (line.split('=', 1),)
)


libmorfeusz = ctypes.CDLL('libmorfeusz.so.0')

MORFOPT_ENCODING = 1
MORFEUSZ_UTF_8 = 8

libmorfeusz.morfeusz_set_option(MORFOPT_ENCODING, MORFEUSZ_UTF_8)
libmorfeusz_lock = allocate_lock()

class InterpEdge(ctypes.Structure):
    _fields_ = \
    (
        ('i', ctypes.c_int),
        ('j', ctypes.c_int),
        ('_orth', ctypes.c_char_p),
        ('_base', ctypes.c_char_p),
        ('_tags', ctypes.c_char_p)
    )

    if py3k:
        @property
        def tags(self):
            if self._tags is not None:
                return self._tags.decode('UTF-8')
    else:
        @property
        def tags(self):
            return self._tags

    @property
    def orth(self):
        if self._orth is not None:
            return self._orth.decode('UTF-8')

    @property
    def base(self):
        if self._base is not None:
            return self._base.decode('UTF-8')

libmorfeusz_analyse = libmorfeusz.morfeusz_analyse
libmorfeusz_analyse.restype = ctypes.POINTER(InterpEdge)
libmorfeusz_about = libmorfeusz.morfeusz_about
libmorfeusz_about.restype = ctypes.c_char_p

def expand_tags(tags, expand_dot = True, expand_underscore = True):
    r'''
    >>> from pprint import pprint

    >>> tags = 'adj:sg:nom:m1.m2.m3:pos|adj:sg:acc:m3:pos'
    >>> xtags = expand_tags(tags)
    >>> pprint(list(xtags))
    ['adj:sg:nom:m1:pos',
     'adj:sg:nom:m2:pos',
     'adj:sg:nom:m3:pos',
     'adj:sg:acc:m3:pos']
    >>> xtags = expand_tags(tags, expand_dot=False)
    >>> pprint(list(xtags))
    ['adj:sg:nom:m1.m2.m3:pos', 'adj:sg:acc:m3:pos']

    >>> tags = 'ppron3:sg:acc:f:ter:_:npraep'
    >>> xtags = expand_tags(tags)
    >>> pprint(list(xtags))
    ['ppron3:sg:acc:f:ter:akc:npraep', 'ppron3:sg:acc:f:ter:nakc:npraep']
    >>> xtags = expand_tags(tags, expand_dot = False)
    >>> pprint(list(xtags))
    ['ppron3:sg:acc:f:ter:akc.nakc:npraep']
    >>> xtags = expand_tags(tags, expand_underscore = False)
    >>> pprint(list(xtags))
    ['ppron3:sg:acc:f:ter:_:npraep']
    '''

    if tags is None:
        yield
        return
    tags = str(tags)
    for tag in tags.split('|'):
        tag = tag.split(':')
        pos = tag.pop(0)
        chunks = [(pos,)]
        chunks += \
        (
            VALUES[attribute] if chunk == '_' and expand_underscore
            else chunk.split('.')
            for chunk, attribute in zip(tag, ATTRIBUTES[pos])
        )

        if not expand_dot:
            yield ':'.join('.'.join(values) for values in chunks)
            continue

        def expand_chunks(i):
            if i >= len(chunks):
                yield ()
            else:
                tail = tuple(expand_chunks(i + 1))
                for chunk_variant in chunks[i]:
                    for tail_variant in tail:
                        yield (chunk_variant,) + tail_variant

        for x in expand_chunks(0):
            yield ':'.join(x)

_expand_tags = expand_tags

def _dont_expand_tags(s, **kwargs):
    return (s,)

def analyse(text, expand_tags = True, expand_dot = True, expand_underscore = True):
    r'''
    Analyse the text.

    >>> from pprint import pprint
    >>> pprint(analyse('Mama ma.'))
    [((u'Mama', u'mama', 'subst:sg:nom:f'),
      (u'ma', u'mie\u0107', 'fin:sg:ter:imperf'),
      (u'.', u'.', 'interp')),
     ((u'Mama', u'mama', 'subst:sg:nom:f'),
      (u'ma', u'm\xf3j', 'adj:sg:nom:f:pos'),
      (u'.', u'.', 'interp'))]
    '''

    expand_tags = _expand_tags if expand_tags else _dont_expand_tags
    text = unicode(text)
    text = text.encode('UTF-8')
    dag = defaultdict(list)
    with libmorfeusz_lock:
        for edge in libmorfeusz_analyse(text):
            if edge.i == -1:
                break
            for tag in expand_tags(edge.tags, expand_dot = expand_dot, expand_underscore = expand_underscore):
                dag[edge.i] += ((edge.orth, edge.base, tag), edge.j),

    def expand_dag(i):
        nexts = dag[i]
        if not nexts:
            yield ()
        else:
            for head, j in nexts:
                for tail in expand_dag(j):
                    yield (head,) + tail

    return list(expand_dag(0))

def about():
    '''
    Return a string containing information on authors and version of the
    underlying library.
    '''
    about = libmorfeusz_about()
    try:
        return about.decode('UTF-8')
    except UnicodeError:
        return about.decode('ISO-8859-2')
    return about

if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim:ts=4 sw=4 et
