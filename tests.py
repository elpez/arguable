#!/usr/bin/env python3

import unittest

import blargparse


class ParserTests(unittest.TestCase):
    def test_basic(self):
        parser = blargparse.Parser(description='Process some files')
        parser.add_required_arg('infile')
        parser.add_optional_arg('outfile', default='out.xml')
        parser.add_flag('-v', repeat=True, dest='verbosity')
        args = parser.parse_args(['-vvv', 'input.xml'])
        self.assertEqual(args.verbosity, 3)
        self.assertEqual(args.infile, 'input.xml')
        self.assertEqual(args.outfile, 'out.xml')

if __name__ == '__main__':
    unittest.main()
