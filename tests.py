#!/usr/bin/env python3

import unittest

import arguable


class ParserTests(unittest.TestCase):
    def test_basic(self):
        parser = arguable.ArgumentParser(description='Process some files')
        parser.add_required_arg('infile')
        parser.add_optional_arg('outfile', default='out.xml')
        parser.add_flag('-v', repeat=True, dest='verbosity')
        args = parser.parse_args(['-vvv', 'input.xml'])
        self.assertEqual(args.verbosity, 3)
        self.assertEqual(args.infile, 'input.xml')
        self.assertEqual(args.outfile, 'out.xml')

    def test_parse_args(self):
        parser = arguable.make_parser('-v infile outfile?')
        args = parser.parse_args(['test.xml', '-v'])
        self.assertEqual(args.v, True)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, None)

if __name__ == '__main__':
    unittest.main()
