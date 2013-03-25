==========
nose-knows
==========

**nose-knows** is a nose plugin for figuring out which unit tests you should
run after modifying code. It works by tracing your code during unit tests while
given the ``--knows-out`` command, and creating an output file that can then be
used to figure out which unit tests to run for each file modified. You can then
pass in a list of files and only run the appropriate unit tests.

Examples::

    (risk)eyal-01575:src eyal$ nosetests --with-knows --knows-dir=$RISK_DIR --knows-out
    .....................................................................
    ----------------------------------------------------------------------
    Ran 69 tests in 0.444s

    OK

The ``.knows`` file now contains the following::

    warehouse/src/transform_data/transformers/__init__.py:
        tests.test_transformers.test_std_data
        tests.test_transformers.test_join
        tests.test_transformers.test_min_data
        tests.test_transformers.test_json_data
        tests.test_transformers.test_count
        tests.test_transformers.test_sum_data
        tests.test_transformers.test_avg_data
        tests.test_transform_data_table_follower

and you can pass in ``transform_data/transformers/__init__.py`` to nose::

    (risk)eyal-01575:src eyal$ nosetests --with-knows --knows-dir=$RISK_DIR transform_data/transformers/__init__.py
    .....................................
    ----------------------------------------------------------------------
    Ran 37 tests in 0.019s

    OK

The best practice here is to have a system like Jenkins run the unit test suite
once in a while to create this map, and then creating a bash function/script to
downloadthe knows output file from Jenkins and run it against the set of
changed files from a commit.

**nose-knows** is copyright 2013 Eventbrite and Contributors, and is made
available under BSD-style license; see LICENSE for details.
