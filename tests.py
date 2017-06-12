#!/usr/bin/env python3

import unittest

import arguable


class ParserTests(unittest.TestCase):
    def test_parse_args(self):
        parser = arguable.make_parser('-v infile outfile?')
        args = parser.parse_args(['test.xml', '-v'])
        self.assertEqual(args.v, True)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, None)

if __name__ == '__main__':
    unittest.main()
