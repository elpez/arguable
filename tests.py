#!/usr/bin/env python3

import unittest

import arguable


class ParserTests(unittest.TestCase):
    def test_long_option(self):
        parser = arguable.make_parser('--verbose')
        args = parser.parse_args(['--verbose'])
        self.assertEqual(args.verbose, True)

    def test_full(self):
        parser = arguable.make_parser('-v infile outfile?')
        args = parser.parse_args(['test.xml'])
        self.assertEqual(args.v, False)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, None)

        args = parser.parse_args(['test.xml', '-v'])
        self.assertEqual(args.v, True)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, None)

        args = parser.parse_args(['-v', 'test.xml', 'out.html'])
        self.assertEqual(args.v, True)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, 'out.html')

if __name__ == '__main__':
    unittest.main()
