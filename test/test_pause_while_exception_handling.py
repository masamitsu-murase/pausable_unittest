# -*- coding: utf-8 -*-

import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import testpauser
import pausable_unittest.dummypauser

import time
import re

class PauseWhileExceptionHandlingTest(pausable_unittest.TestCase):
    def raise_exception_while_file_accessing(self, skip=False):
        if True:
            return
        with open(__file__, "r") as file:
            raise Exception("test")

    def test_pause_while_exception_handling_try_finally(self):
        result = False
        try:
            try:
                self.raise_exception_while_file_accessing("__pypy__" in sys.builtin_module_names)
            finally:
                self.reboot()
                result = True
        except:
            pass
        self.assertEqual(result, True, "Reboot succeeded.")

    def test_pause_while_exception_handling_try_except(self):
        result = False
        try:
            self.raise_exception_while_file_accessing()
        except Exception as e:
            self.reboot()
            result = True
        self.assertEqual(result, True, "Reboot succeeded.")


if __name__ == "__main__":
    dummy = pausable_unittest.dummypauser.Pauser()
    pausable_unittest.main(dummy)
