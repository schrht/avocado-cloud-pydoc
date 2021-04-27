#!/usr/bin/env python
"""
Dump the information of the avocado-cloud testcases.
"""

import argparse
import logging
import yaml
import os
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


def parse_py_files(pypath):
    """Parse the test_*.py files.

    Input:
        - pypath: the path of test_*.py files.
    Return:
        - dict: information of the testcases.
    """

    with open(pypath, 'r') as f:
        lines = f.readlines()

    # class_name
    # function_names
    for line in lines:
        print(line)



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
    parse_py_files(ARGS.pypath + '/test_functional_checkup.py')

exit(0)
