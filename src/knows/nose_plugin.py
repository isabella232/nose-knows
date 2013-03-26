import logging
import os
import sys
import threading

from collections import defaultdict

import nose
from nose.plugins import Plugin


def parse_test_name(test_name):
    begin = test_name.index('<') + 1
    end = test_name.index('>')
    inside_brackets = test_name[begin:end]
    test_module_and_class, test_method = inside_brackets.split(' ', 1)
    if test_method.startswith('testMethod='):
        test_method = test_method[len('testMethod='):]
    test_module, test_class = test_module_and_class.rsplit('.', 1)
    return test_module + ':' + test_class + '.' + test_method


class Knows(Plugin):
    name = 'knows'

    def __init__(self, *args, **kwargs):
        self.test_map = defaultdict(set)
        self.output_filehandle = None
        self.output = True
        self.enableOpt = 'with-knows'
        self.test_name = ''
        self.logger = logging.getLogger('nose.plugins.knows')

    def options(self, parser, env=os.environ):
        parser.add_option(
            '--knows-file',
            type='string',
            dest='knows_file',
            default='.knows',
            help='Output file for knows plugin.',
        )
        parser.add_option(
            '--knows-out',
            action='store_true',
            dest='knows_out',
            help='Whether to output the mapping of files to unit tests.',
        )
        parser.add_option(
            '--knows-dir',
            type='string',
            dest='knows_dir',
            default='',
            help='Include only this given directory. This should be your '
                 'project directory name, and does not need to be an absolute '
                 'path.',

        )
        parser.add_option(
            '--knows-exclude',
            type='string',
            action='append',
            dest='knows_exclude',
            help='Exclude files having this string (can use multiple times).',
        )
        super(Knows, self).options(parser, env=env)

    def configure(self, options, config):
        self.enabled = getattr(options, self.enableOpt)
        if self.enabled:
            input_files = config.testNames
            self.knows_dir = options.knows_dir.rstrip('/')
            self.exclude = []
            if options.knows_exclude:
                self.exclude.extend(options.knows_exclude)
            if not options.knows_out:
                if input_files:
                    config.testNames = self.get_tests_to_run(
                        input_files,
                        options.knows_file,
                    )
                self.output = False
            self.output_filename = options.knows_file

        super(Knows, self).configure(options, config)

    def get_tests_to_run(self, input_files, knows_file):
        tests_to_run = []
        match = False
        inputs = set()
        for f in input_files:
            abs_f = os.path.abspath(f)
            if os.path.exists(abs_f) and self.knows_dir in abs_f:
                f = abs_f[f.index(self.knows_dir) + len(self.knows_dir) + 1:]
            inputs.add(f)
        with open(knows_file) as fh:
            for line in fh:
                if line.strip(':\n') in inputs:
                    match = True
                elif line.startswith('\t') and match:
                    tests_to_run.append(line.strip())
                else:
                    match = False

        return tests_to_run

    def begin(self):
        if self.output:
            self.output_filehandle = open(self.output_filename, 'w')
            threading.settrace(self.tracer)
            sys.settrace(self.tracer)

    def tracer(self, frame, event, arg):
        filename = frame.f_code.co_filename
        for exclude_string in self.exclude:
            if exclude_string in filename:
                break
        else:
            if self.test_name and self.knows_dir in filename:
                start_pos = filename.index(self.knows_dir)
                length = len(self.knows_dir) + 1
                filename = filename[start_pos + length:]

                if self.test_name not in self.test_map[filename]:
                    self.logger.info(
                        'Found file %s touched by test %s.',
                        filename,
                        self.test_name,
                    )
                    self.test_map[filename].add(self.test_name)

        return self.tracer

    def startTest(self, test):
        try:
            self.test_name = parse_test_name(repr(test))
        except Exception, e:
            self.logger.warning(
                'Could not figure out test name from %s.',
                repr(test),
            )
            self.test_name = ''

    def stopTest(self, test):
        self.test_name = ''

    def finalize(self, result):
        if self.output:
            for fname, tests in self.test_map.iteritems():
                self.output_filehandle.write('%s:\n' % (fname,))
                for t in tests:
                    self.output_filehandle.write('\t%s\n' % (t,))

            self.output_filehandle.close()
