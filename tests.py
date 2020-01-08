import unittest
import string

from ignore_optimize import randString, Rule

class TestRandString(unittest.TestCase):
    ALL = string.ascii_letters + string.digits + '_-.'

    def test_avoid(self):
        s = randString(100, string.ascii_letters)
        for c in s:
            self.assertIn(c, string.digits + '._-')

class TestRuleContains(unittest.TestCase):
    def test_simple(self):
        a,b,c = Rule('abc/d'), Rule('ab/cd'), Rule('ab/cd')
        self.assertFalse(a.contains(b))
        self.assertFalse(b.contains(a))
        self.assertTrue(b.contains(c))
        self.assertTrue(c.contains(b))
        
    def test_root(self):
        a,b,c,d = Rule('d'), Rule('/d'), Rule('/a/d'), Rule('a/d')
        self.assertTrue(a.contains(b))
        self.assertTrue(a.contains(c))
        self.assertFalse(b.contains(a))
        self.assertFalse(b.contains(c))
        self.assertFalse(c.contains(a))
        self.assertFalse(c.contains(b))
        self.assertTrue(c.contains(d))
        self.assertTrue(d.contains(c))
        
    def test_dir(self):
        a,b,c = Rule('d'), Rule('d/'), Rule('a/d')
        self.assertTrue(a.contains(b))
        self.assertTrue(a.contains(c))
        self.assertFalse(b.contains(a))
        self.assertFalse(b.contains(c))
        self.assertFalse(c.contains(a))
        self.assertFalse(c.contains(b))
    
    def test_star(self):
        a,b,c = Rule('d*'), Rule('dav'), Rule('d*v')
        self.assertTrue(a.contains(b))
        self.assertTrue(a.contains(c))
        self.assertFalse(b.contains(a))
        self.assertFalse(b.contains(c))
        self.assertFalse(c.contains(a))
        self.assertTrue(c.contains(b))
    
    def test_double(self):
        a,b,c = Rule('d/**'), Rule('d/abc/de/f/gh/'), Rule('d/abc/**/f')
        self.assertTrue(a.contains(b))
        self.assertTrue(a.contains(c))
        self.assertFalse(b.contains(a))
        self.assertFalse(b.contains(c))
        self.assertFalse(c.contains(a))
        self.assertTrue(c.contains(b))

    def test_other(self):
        a,b,c = Rule('a/b/*.txt'), Rule('/a/b/'), Rule('a/b/a.txtx')
        self.assertFalse(a.contains(b))
        self.assertFalse(a.contains(c))
        self.assertTrue(b.contains(a))
        self.assertTrue(b.contains(c))
        self.assertFalse(c.contains(a))
        self.assertFalse(c.contains(b))

    def test_specific(self):
        a,b,c = Rule('a/**'), Rule('a/**/'), Rule('a/b.txt')
        self.assertTrue(a.contains(b))
        self.assertTrue(a.contains(c))
        self.assertFalse(b.contains(a))
        self.assertTrue(b.contains(c))


if __name__ == '__main__':
    unittest.main()
