#!/usr/bin/env python
"""
Dump the information of the avocado-cloud testcases.
"""

import argparse
import logging
import sys
import os
import importlib
import inspect
import pandas as pd

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

ARG_PARSER = argparse.ArgumentParser(
    description="Dump the information of the avocado-cloud testcases.")
ARG_PARSER.add_argument('--product',
                        dest='product',
                        action='store',
                        help='The product name.',
                        choices=('AWS', 'Aliyun'),
                        required=True)
ARG_PARSER.add_argument('--pypath',
                        dest='pypath',
                        action='store',
                        help='The path of test_*.py files.',
                        required=True)
ARG_PARSER.add_argument('--output-format',
                        dest='output_format',
                        action='store',
                        choices=('csv', 'html'),
                        help='The output file format.',
                        default='csv',
                        required=False)
ARG_PARSER.add_argument('--output',
                        dest='output',
                        action='store',
                        help='The file to store testcase information.',
                        default='testcases.csv',
                        required=False)


def load_pydoc(pypath):
    """Load pydoc for each testcases from the *.py files.

    Input:
        - pypath: the py file or the folder container multiple py files.
    Return:
        - testcases: a list of dict contains testcase names and their pydoc.
    """

    # Init data
    testcases = []

    # TODO: Create testcode.py from py file(s)
    os.system('cp -f {} /tmp/testcode.py'.format(pypath))

    # Remove class inheritance
    os.system('sed -i "/^from .* import/d" /tmp/testcode.py')
    os.system('sed -i "/^import /d" /tmp/testcode.py')
    os.system('sed -i "s/\\(^class .*\\)(Test):/\\1():/" /tmp/testcode.py')

    # Load modules from testcode
    sys.path.append('/tmp')
    testcode = importlib.import_module('testcode')

    # Extarct the func and pydoc
    clsmembers = inspect.getmembers(testcode, inspect.isclass)
    for clsmember in clsmembers:
        funcmembers = inspect.getmembers(clsmember[1], inspect.isfunction)
        for funcmember in funcmembers:
            # Filter out the testcases
            if funcmember[0].startswith('test_'):
                name = clsmember[0] + '.' + funcmember[0]
                doc = funcmember[1].__doc__
                testcases.append({'func': name, 'pydoc': doc})

    return testcases


def dump_dataframe(dataframe, output_format='csv', filename='file.csv'):
    """Dump the testcase information to a file.

    Input:
        - dataframe: information of the testcases.
    """
    if output_format == 'csv':
        with open(filename, 'w') as f:
            f.write(dataframe.to_csv())
    else:
        with open(filename, 'w') as f:
            f.write(dataframe.to_html())


if __name__ == '__main__':
    # Parse args
    ARGS = ARG_PARSER.parse_args()

    # Parse testcases
    testcases = load_pydoc(ARGS.pypath + '/test_functional_checkup.py')
    print(testcases)

exit(0)
