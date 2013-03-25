==========
nose-knows
==========

**nose-knows** is a nose plugin for figuring out which unit tests you should
run after modifying code. It works by tracing your code during unit tests while
given the ``--knows-out`` command, and creating an output file that can then be
used to figure out which unit tests to run for each file. That file is used
when provided with ``--knows-in``, passing in a list of filenames, and the
appropriate set of unit tests is run.

The likely best practice here is to have a system like Jenkins run the unit
test suite once in a while to create this map, and then incorporating
downloading the knows output file from Jenkins.

**nose-knows** is copyright 2013 Eventbrite and Contributors, and is made
available under BSD-style license; see LICENSE for details.
