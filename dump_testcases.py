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
import json
import pandas as pd

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

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
                        help='The path of test_*.py file or its directory.',
                        required=True)
ARG_PARSER.add_argument('--output-format',
                        dest='output_format',
                        action='store',
                        choices=('json', 'json-polarion', 'csv', 'html'),
                        help='The output file format.',
                        default='json',
                        required=False)
ARG_PARSER.add_argument('--output',
                        dest='output',
                        action='store',
                        help='The file to store testcase information.',
                        default='testcases.json',
                        required=False)


class TestDocGenerator():
    def __init__(self, product, pypath):
        self.product = product
        self.pypath = pypath

        self.pydocs = []
        self.polarion_data = []

        self.load_pydoc()

    def load_pydoc(self):
        """Load pydoc for each testcase from the test_*.py files.

        Input:
            - self.pypath: the py file or the folder with multiple py files.
        Update:
            - self.pydocs: list of func name and the pydoc.
        """

        # Create testcode.py from py file(s)
        tmppath = '/tmp/{}'.format(os.getpid())
        os.system('mkdir -p {}'.format(tmppath))

        if os.path.isfile(self.pypath):
            os.system('cp -f {} {}/testcode.py'.format(self.pypath, tmppath))
        elif os.path.isdir(self.pypath):
            os.system('cat {}/test_*.py > {}/testcode.py'.format(
                self.pypath, tmppath))
        else:
            logging.error('Invalid path {}'.format(self.pypath))
            exit(1)

        # Remove class inheritance
        os.system('sed -i "/^from .* import/d" {}/testcode.py'.format(tmppath))
        os.system('sed -i "/^import /d" {}/testcode.py'.format(tmppath))
        os.system(
            'sed -i "s/\\(^class .*\\)(Test):/\\1():/" {}/testcode.py'.format(tmppath))

        # Load modules from testcode
        sys.path.append(tmppath)
        testcode = importlib.import_module('testcode')

        # Extarct the func and pydoc
        clsmembers = inspect.getmembers(testcode, inspect.isclass)
        for clsmember in clsmembers:
            logging.debug('Class Name: {}'.format(clsmember[1]))
            if sys.version_info.major == 2:
                funcmembers = inspect.getmembers(clsmember[1],
                                                 inspect.ismethod)
            else:
                funcmembers = inspect.getmembers(clsmember[1],
                                                 inspect.isfunction)
            for funcmember in funcmembers:
                # Filter out the testcases
                logging.debug('Function Name: {}'.format(funcmember[1]))
                if funcmember[0].startswith('test_'):
                    name = clsmember[0] + '.' + funcmember[0]
                    docstr = funcmember[1].__doc__
                    doc = None if not docstr else [
                        x.strip() for x in docstr.split('\n')
                        if x.strip() != ''
                    ]
                    self.pydocs.append({
                        'func': name,
                        'pydoc_str': docstr,
                        'pydoc': doc
                    })

        return 0

    def _query_pydoc(self, name, pydoc, none_for_na=True):
        """Query the value of specified field name from pydoc.

        Input:
            - name: the field name.
            - pydoc: the list of a pydoc lines.
        Return:
            - string: value of the specified field name.
        """
        if pydoc is None:
            return None
        if '{}:'.format(name) not in pydoc:
            return None

        idx = pydoc.index('{}:'.format(name))
        cnt = []
        for line in pydoc[idx + 1:]:
            if line.endswith(':'):
                break
            cnt.append(line)
        value = '\n'.join(cnt)

        if none_for_na and value.lower() in ('', 'n/a', 'na'):
            return None
        else:
            return value

    def parse_pydoc_polarion(self):
        """Parse pydoc for polarion usage.

        Update:
            - self.polarion_data: the data for polarion usage.
        """
        for case in self.pydocs:
            func = case.get('func')
            pydoc = case.get('pydoc')

            data = {}
            data['Title'] = '[{}]{}'.format(self.product, func)
            data['TCMS Bug'] = self._query_pydoc('bugzilla_id', pydoc)

            if self._query_pydoc('customer_case_id', pydoc):
                data['Customer Scenario'] = True
            else:
                data['Customer Scenario'] = False

            author = self._query_pydoc('maintainer', pydoc)
            if author and author.endswith('@redhat.com'):
                author = author.replace('@redhat.com', '')
            data['Author'] = author

            importance = self._query_pydoc('case_priority', pydoc)
            if importance is None:
                data['Importance'] = None
            elif importance.lower in ('critical', 'high', 'medium', 'low'):
                data['Importance'] = importance.lower
            else:
                data['Importance'] = {
                    '0': 'critical',
                    '1': 'high',
                    '2': 'medium',
                    '3': 'low'
                }.get(importance)

            step = self._query_pydoc('key_steps', pydoc)
            if isinstance(step, str):
                step = step.replace('\n', '<br/>')
            data['Step'] = step

            data['Expected Result'] = self._query_pydoc('pass_criteria', pydoc)

            if pydoc:
                data['Description'] = '<br/>'.join(pydoc)
            else:
                data['Description'] = None

            self.polarion_data.append(data)

        return 0

    def _dump_json(self, data, path):
        """Dump the data to a json file.

        Input:
            - data: a json list.
            - path: the output file.
        """
        with open(path, 'w') as f:
            json.dump(data, f, indent=3, sort_keys=False)

    def _dump_csv(self, path):
        """Dump the information to a csv file.

        Input:
            - path: the output file.
        """
        dataframe = pd()
        with open(path, 'w') as f:
            f.write(dataframe.to_csv())

    def dump_polarion_json(self, path):
        """Dump polarion data to a json file.

        Input:
            - path: the output file.
        """
        self._dump_json(self.polarion_data, path)


if __name__ == '__main__':
    # Parse args
    ARGS = ARG_PARSER.parse_args()

    # Parse testcases
    tdg = TestDocGenerator(ARGS.product, ARGS.pypath)
    if ARGS.output_format == 'json-polarion':
        tdg.parse_pydoc_polarion()
        tdg.dump_polarion_json(ARGS.output)

exit(0)
