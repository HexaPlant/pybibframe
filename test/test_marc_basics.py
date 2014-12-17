'''

Requires http://pytest.org/ e.g.:

pip install pytest

----
'''

import sys
import logging
import asyncio
import unittest
import difflib
from io import StringIO

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader.marcxml import bfconvert

#Move to a test utils module
import os, inspect
def module_path(local_function):
   ''' returns the module path without the use of __file__.  Requires a function defined 
   locally in the module.
   from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
   return os.path.abspath(inspect.getsourcefile(local_function))

#hack to locate test resource (data) files regardless of from where nose was run
RESOURCEPATH = os.path.normpath(os.path.join(module_path(lambda _: None), '../resource/'))

def verify_conversion(name, entbase=None, config=None, loop=None, canonical=True):
    m = memory.connection()
    m_expected = memory.connection()
    s = StringIO()
    with open(os.path.join(RESOURCEPATH, name+'.mrx')) as indoc:
        bfconvert(indoc, model=m, out=s, config=config, canonical=canonical, loop=loop)
        s.seek(0)
        jsonload(m, s)

    with open(os.path.join(RESOURCEPATH, name+'.versa')) as indoc:
        jsonload(m_expected, indoc)

    assert m == m_expected, "Discrepancies found for {0}:\n{1}".format(name, file_diff(repr(m), repr(m_expected)))

def file_diff(s_orig, s_new):
    diff = difflib.unified_diff(s_orig.split('\n'), s_new.split('\n'))
    return '\n'.join(list(diff))

class BasicTest(unittest.TestCase):
    '''
    Use a new event loop per test, and so one call of bfconvert per test
    '''

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def test_model_consumed(self):
        m = memory.connection()
        with open(os.path.join(RESOURCEPATH, 'multiple-authlinks.xml')) as indoc:
            bfconvert([indoc], entbase='http://example.org/', model=m, config=None, verbose=False, loop=self.loop)

        assert m.size() == 0, 'Model not consumed:\n'+repr(m)

    def test_simple_verify(self):
        verify_conversion('gunslinger', loop=self.loop)
        pass

    def test_simple_verify2(self):
        verify_conversion('egyptskulls', loop=self.loop)
        pass

    def test_simple_verify3(self):
        verify_conversion('kford-holdings1', loop=self.loop)
        pass

if __name__ == '__main__':
    raise SystemExit("use py.test")
