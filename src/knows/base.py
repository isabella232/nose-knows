import logging
import os
import sys

from collections import defaultdict


class Knows(object):
    def __init__(
        self,
        knows_filename,
        output=True,
        knows_directory='',
        logger=None,
        exclude=None,
    ):
        self.test_map = defaultdict(set)
        self.output = output
        self.knows_dir = knows_directory.rstrip('/')
        self.test_name = ''
        self.logger = logger or logging.getLogger('nose.plugins.knows')
        self.exclude = exclude or []
        self.knows_filename = knows_filename
        self.knows_dir_length = len(self.knows_dir) + 1

    def get_tests_to_run(self, input_files):
        tests_to_run = []
        match = False
        inputs = set()
        for fname in input_files:
            abs_fname = os.path.abspath(fname)
            if os.path.exists(abs_fname) and self.knows_dir in abs_fname:
                start_pos = abs_fname.index(self.knows_dir)
                length = len(self.knows_dir) + 1
                fname = abs_fname[start_pos + length:]
            # Try to add the path regardless. It may or may not exist in the
            # output file.
            inputs.add(fname)
        with open(self.knows_filename) as fh:
            for line in fh:
                if line.strip(':\n') in inputs:
                    match = True
                elif line.startswith('\t') and match:
                    tests_to_run.append(line.strip())
                else:
                    match = False

        if not tests_to_run:
            self.logger.error(
                '## Found no tests to run, consider adding some? Files: %s ##',
                ','.join(input_files),
            )
            # Return the tests to run to the previous state.
            tests_to_run = input_files

        return tests_to_run

    def begin(self):
        if self.output:
            sys.setprofile(self.tracer)

    def tracer(self, frame, event, arg):
        filename = frame.f_code.co_filename
        if self.test_name and filename.startswith(self.knows_dir):
            filename = filename[self.knows_dir_length:]
            self.test_map[filename].add(self.test_name)

    def start_test(self, test):
        self.test_name = test

    def stop_test(self, test):
        self.test_name = ''

    def finalize(self):
        if self.output:
            with open(self.knows_filename, 'w') as output_fh:
                for fname, tests in self.test_map.iteritems():
                    output_fh.write('%s:\n' % (fname,))
                    for t in tests:
                        output_fh.write('\t%s\n' % (t,))
