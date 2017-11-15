# coding: utf-8

# The MIT License (MIT)

# Copyright (c) 2016-2017 Masamitsu MURASE

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the "Software"), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, merge, publish, distribute, 
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from .testrunner import TestRunner
from .testcase import TestCase
from .basepauser import BasePauser

__version__ = "1.3.0"

def main(pauser, filename="teststate.bin", command_after_test=None,
         log_filename=None, loglevel=None, assertion_log=False,
         options=None):
    import unittest
    suite = unittest.TestLoader().loadTestsFromModule(__import__("__main__"))
    TestRunner().run(suite, pauser, filename=filename,
                     command_after_test=command_after_test,
                     log_filename=log_filename, loglevel=loglevel,
                     assertion_log=assertion_log, options=options)

