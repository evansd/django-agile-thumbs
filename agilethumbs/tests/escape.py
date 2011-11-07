from django.test import TestCase

from agilethumbs.base import escape, unescape


STRINGS = [
    u'high unicode chars \xd1\x89\xc3\xab\xe0\xaa\x8b',
    u'naughty chars &"\' %$+={}()\\.:',
    u'/leading',
    u'trailing/',
    u'multiple///slashes',
]


class TestStringEscaping(TestCase):
    
    def testRoundTripEquivalent(self):
        for s in STRINGS:
            self.assertEqual(s, unescape(escape(s)))
    
    def testCleanOutput(self):
        for s in STRINGS:
            self.assertNotRegexpMatches(escape(s), r'[^\w\-\~/]')
    
    def testNoLeadingSlashes(self):
        for s in STRINGS:
            self.assertNotEqual('/', escape(s)[0])
    
    def testNoTrailingSlashes(self):
        for s in STRINGS:
            self.assertNotEqual('/', escape(s)[-1])
        
    def testNoMultipleSlashes(self):
        for s in STRINGS:
            self.assertNotIn('//', escape(s))
    
    def testCleanStringsUntouched(self):
        clean = u'this/is-1234/a_clean_string'
        self.assertEqual(clean, escape(clean))
