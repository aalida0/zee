#!/usr/bin/env python3
"""Run focused no-scan tests with stdlib unittest, including plain test functions."""
import importlib
import inspect
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'tests')]


def main():
    with tempfile.TemporaryDirectory(prefix='d14-test-mpl-') as tmp:
        os.environ['MPLCONFIGDIR'] = tmp
        suite = unittest.TestSuite()
        for path in sorted((ROOT/'tests').glob('test_module14_*.py')):
            module = importlib.import_module(path.stem)
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
            for name, function in inspect.getmembers(module, inspect.isfunction):
                if name.startswith('test_') and function.__module__ == module.__name__:
                    suite.addTest(unittest.FunctionTestCase(function))
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__ == '__main__': raise SystemExit(main())
