# encoding=UTF-8

import sys
py3k = sys.version_info >= (3, 0)

if py3k:
    import unittest
else:
    import unittest2 as unittest

import morfeusz

if py3k:
    def u(s):
        return s
else:
    def u(s):
        return s.decode('UTF-8')

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

class test_about(unittest.TestCase):

    def test_type(self):
        self.assertEqual(
            type(morfeusz.about()),
            type(u(''))
        )

if __name__ == '__main__':
    unittest.main()

# vim:ts=4 sw=4 et
