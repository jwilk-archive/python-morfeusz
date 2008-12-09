# encoding=UTF-8

# Copyright © 2007, 2008 Jakub Wilk <ubanus@users.sf.net>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License, version 2, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <http://www.gnu.org/licenses>.
# 
# Linking python-morfeusz with other modules is making a combined work based on
# python-morfeusz. Thus, the terms and conditions of the GNU General Public
# License cover the whole combination.
#
# In addition, as a special exception, the copyright holder of python-morfeusz
# give you permission to combine python-morfeusz with the Morfeusz SIAT
# morphological analyser <http://nlp.ipipan.waw.pl/~wolinski/morfeusz/>. You
# may copy and distribute such a system following the terms of the GNU GPL for
# python-morfeusz and the license of Morfeusz SIAT.
#
# Note that people who make modified versions of python-morfeusz are not
# obligated to grant this special exception for their modified versions; it is
# their choice whether to do so. The GNU General Public License gives
# permission to release a modified version without this exception; this
# exception also makes it possible to release a modified version which carries
# forward this exception.

'''
Python bindings to Morfeusz.
'''

from collections import defaultdict
from _thread import allocate_lock
import ctypes
from ctypes import c_int, c_char_p

__author__ = 'Jakub Wilk <ubanus@users.sf.net>'
__version__ = '0.2403'
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
        ('i', c_int),
        ('j', c_int),
        ('_orth', c_char_p),
        ('_base', c_char_p),
        ('tags', c_char_p)
    )

    @property
    def orth(self):
        if self._orth is not None:
            return self._orth

    @property
    def base(self):
        if self._base is not None:
            return self._base

libmorfeusz_analyse = libmorfeusz.morfeusz_analyse
libmorfeusz_analyse.restype = ctypes.POINTER(InterpEdge)
libmorfeusz_about = libmorfeusz.morfeusz_about
libmorfeusz_about.restype = c_char_p

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
    [(('Mama', 'mama', 'subst:sg:nom:f'),
      ('ma', 'mieć', 'fin:sg:ter:imperf'),
      ('.', '.', 'interp')),
     (('Mama', 'mama', 'subst:sg:nom:f'),
      ('ma', 'mój', 'adj:sg:nom:f:pos'),
      ('.', '.', 'interp'))]
    '''

    expand_tags = _expand_tags if expand_tags else _dont_expand_tags
    text = str(text)
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
    return libmorfeusz_about().decode('ISO-8859-2')

if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim:ts=4 sw=4 et
