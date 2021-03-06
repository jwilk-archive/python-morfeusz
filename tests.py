# encoding=UTF-8

# Copyright © 2007-2017 Jakub Wilk <jwilk@jwilk.net>
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

import sys

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest

import morfeusz

if str is bytes:
    def u(s):
        return s.decode('UTF-8')
else:
    def u(s):
        return s

sgjp = 'SGJP' in morfeusz.about()

class test_expand_tags(unittest.TestCase):

    def test1(self):
        tags = 'adj:sg:nom:m1.m2.m3:pos|adj:sg:acc:m3:pos'
        xtags = morfeusz.expand_tags(tags)
        self.assertEqual(list(xtags), [
            'adj:sg:nom:m1:pos',
            'adj:sg:nom:m2:pos',
            'adj:sg:nom:m3:pos',
            'adj:sg:acc:m3:pos',
        ])

    def test2(self):
        tags = 'adj:sg:nom:m1.m2.m3:pos|adj:sg:acc:m3:pos'
        xtags = morfeusz.expand_tags(tags, expand_dot=False)
        self.assertEqual(list(xtags), [
            'adj:sg:nom:m1.m2.m3:pos',
            'adj:sg:acc:m3:pos'
        ])

    def test3(self):
        tags = 'ppron3:sg:acc:f:ter:_:npraep'
        xtags = morfeusz.expand_tags(tags)
        self.assertEqual(list(xtags), [
            'ppron3:sg:acc:f:ter:akc:npraep',
            'ppron3:sg:acc:f:ter:nakc:npraep'
        ])

    def test4(self):
        tags = 'ppron3:sg:acc:f:ter:_:npraep'
        xtags = morfeusz.expand_tags(tags, expand_dot=False)
        self.assertEqual(list(xtags), [
            'ppron3:sg:acc:f:ter:akc.nakc:npraep'
        ])

    def test5(self):
        tags = 'ppron3:sg:acc:f:ter:_:npraep'
        xtags = morfeusz.expand_tags(tags, expand_underscore=False)
        self.assertEqual(list(xtags), [
            'ppron3:sg:acc:f:ter:_:npraep'
        ])

class test_analyse(unittest.TestCase):

    def test1(self):
        text = 'Mama ma.'
        interps = morfeusz.analyse(text)
        if sgjp:
            self.assertEqual(interps.pop(),
                [(u('Mama'), u('mama'), 'subst:sg:nom:f'), (u('ma'), u('mój'), 'adj:sg:voc:f:pos'), (u('.'), u('.'), 'interp')]
            )
        self.assertEqual(interps, [
            [(u('Mama'), u('mama'), 'subst:sg:nom:f'), (u('ma'), u('mieć'), 'fin:sg:ter:imperf'), (u('.'), u('.'), 'interp')],
            [(u('Mama'), u('mama'), 'subst:sg:nom:f'), (u('ma'), u('mój'), 'adj:sg:nom:f:pos'), (u('.'), u('.'), 'interp')]
        ])

    def test2(self):
        text = u('Miałem miał.')
        interps = morfeusz.analyse(text, dag=True)
        self.assertEqual(interps, [
            (0, 1, (u('Miał'), u('mieć'), u('praet:sg:m1:imperf'))),
            (0, 1, (u('Miał'), u('mieć'), u('praet:sg:m2:imperf'))),
            (0, 1, (u('Miał'), u('mieć'), u('praet:sg:m3:imperf'))),
            (1, 2, (u('em'), u('być'), u('aglt:sg:pri:imperf:wok'))),
            (0, 2, (u('Miałem'), u('miał'), u('subst:sg:inst:m3'))),
            (2, 3, (u('miał'), u('miał'), u('subst:sg:nom:m3'))),
            (2, 3, (u('miał'), u('miał'), u('subst:sg:acc:m3'))),
            (2, 3, (u('miał'), u('mieć'), u('praet:sg:m1:imperf'))),
            (2, 3, (u('miał'), u('mieć'), u('praet:sg:m2:imperf'))),
            (2, 3, (u('miał'), u('mieć'), u('praet:sg:m3:imperf'))),
            (3, 4, (u('.'), u('.'), u('interp'))),
        ])

class test_about(unittest.TestCase):

    def test_type(self):
        self.assertEqual(
            type(morfeusz.about()),
            type(u(''))
        )

if __name__ == '__main__':
    unittest.main()

# vim:ts=4 sts=4 sw=4 et
