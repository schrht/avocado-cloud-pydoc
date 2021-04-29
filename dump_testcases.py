#!/usr/bin/env python
"""
Dump pydoc content from the avocado-cloud test code.
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
    description="Dump pydoc content from the avocado-cloud test code.")
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


class TestDocGenerator():
    def __init__(self, product, pypath):
        self.product = product
        self.pypath = pypath

        self.testcases = []

    def load_pydoc(self):
        """Load pydoc for each testcase from the *.py files.

        Input:
            - self.pypath: the py file or the folder with multiple py files.
        Update:
            - self.testcases: func name and the pydoc.
        """

        # TODO: Create testcode.py from py file(s)
        os.system('cp -f {} /tmp/testcode.py'.format(self.pypath))

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
                    self.testcases.append({'func': name, 'pydoc': doc})

    def analyse_pydoc(self):
        def _get_value(key):
            if pydoc is None:
                return None
            if '{}:'.format(key) not in pydoc:
                return None

            idx = pydoc.index('{}:'.format(key))
            ctx = []
            for line in pydoc[idx + 1:]:
                if line.endswith(':'):
                    break
                ctx.append(line)
            value = '\n'.join(ctx)

            if value in ('', 'n/a', 'N/A'):
                return None
            else:
                return value

        for testcase in self.testcases:
            if testcase['pydoc']:
                pydoc = testcase['pydoc'].split('\n')
                pydoc = [x.strip() for x in pydoc if x.strip() != '']
            else:
                pydoc = None

            testcase['Title'] = '[{}]{}'.format(self.product,
                                                testcase.get('func'))
            testcase['TCMS Bug'] = _get_value('bugzilla_id')

            if _get_value('customer_case_id'):
                testcase['Customer Scenario'] = True
            else:
                testcase['Customer Scenario'] = False

            testcase['Author'] = _get_value('maintainer')

            importance = _get_value('case_priority')
            if importance is None:
                testcase['Importance'] = None
            elif importance.lower in ('critical', 'high', 'medium', 'low'):
                testcase['Importance'] = importance.lower
            else:
                testcase['Importance'] = {
                    '0': 'critical',
                    '1': 'high',
                    '2': 'medium',
                    '3': 'low'
                }.get(importance)

            testcase['Step'] = _get_value('key_steps')
            testcase['Expected Result'] = _get_value('pass_criteria')

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
    tdg = TestDocGenerator(ARGS.product,
                           ARGS.pypath + '/test_functional_checkup.py')
    tdg.load_pydoc()
    tdg.analyse_pydoc()
    print(tdg.testcases)

exit(0)
