#!/usr/bin/env python
# vim: set ts=4 sw=4 et sts=4 ai:
#
# Test some basic functionality.
#

import os
import re
import sys
import unittest

qpath = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
sys.path.insert(0, qpath)


class TestQBasic(unittest.TestCase):

    def setUp(self):
        if os.path.exists('/tmp/q'):
            os.remove('/tmp/q')

    def tearDown(self):
        self.setUp()

    def assertInQLog(self, string):
        # Check the log file exists.
        self.assertTrue(os.path.exists('/tmp/q'))

        # Read in the data.
        f = open('/tmp/q', 'r')
        logdata = f.read()
        f.close()

        # Check the string is found in the log file.
        # We can't use self.assertRegexpMatches as we need re.DOTALL
        expected_regexp = re.compile('.*%s.*' % string, re.DOTALL)
        if not expected_regexp.search(logdata):
            msg = '%s: %r not found in\n%s\n%s\n%s' % (
                "Regexp didn't match",
                expected_regexp.pattern,
                "-"*75,
                logdata,
                "-"*75,
                )
            raise self.failureException(msg)

    def test_q_log_message(self):
        import q
        q.q('Test message')
        self.assertInQLog('Test message')

    def test_q_function_call(self):
        import q

        @q.t
        def test(arg):
            return 'RetVal'

        self.assertEqual('RetVal', test('ArgVal'))

        self.assertInQLog('ArgVal')
        self.assertInQLog('RetVal')

    def test_q_argument_order_arguments(self):
        import q
        q.writer.color = False

        class A:
            def __init__(self, two, three, four):
                q(two, three, four)

        A("ArgVal1", "ArgVal2", "ArgVal3")
        self.assertInQLog(".*".join([
            "__init__:",
            "two='ArgVal1'",
            "three='ArgVal2'",
            "four='ArgVal3'",
            ]))

    def test_q_argument_order_attributes(self):
        import q
        q.writer.color = False

        class A:
            def __init__(self, two, three, four):
                self.attrib1 = 'Attrib1'
                self.attrib2 = 'Attrib2'
                q(self.attrib1, self.attrib2)

        A("ArgVal1", "ArgVal2", "ArgVal3")
        self.assertInQLog(".*".join([
            "__init__:",
            "self.attrib1='Attrib1',",
            "self.attrib2='Attrib2'",
            ]))

    def test_q_argument_order_attributes_and_arguments(self):
        import q
        q.writer.color = False

        class A:
            def __init__(self, two, three, four):
                self.attrib1 = 'Attrib1'
                self.attrib2 = 'Attrib2'
                q(two, three, self.attrib1, four, self.attrib2)

        A("ArgVal1", "ArgVal2", "ArgVal3")
        self.assertInQLog(".*".join([
            "__init__:",
            "two='ArgVal1'",
            "three='ArgVal2'",
            "self.attrib1='Attrib1'",
            "four='ArgVal3'",
            "self.attrib2='Attrib2'",
            ]))


unittest.main()
