#!/usr/bin/env python3

import unittest

import arguable


class ParserTests(unittest.TestCase):
    def test_long_option(self):
        args = arguable.parse_args('--verbose', ['--verbose'])
        self.assertEqual(args.verbose, True)


    def test_long_option_syntax(self):
        args = arguable.parse_args('-v[verbose]fo', ['-v', '-f'])
        self.assertEqual(args.verbose, True)
        self.assertEqual(args.f, True)
        self.assertEqual(args.o, False)

        args = arguable.parse_args('-fv[verbose]o', ['-v', '-f'])
        self.assertEqual(args.verbose, True)
        self.assertEqual(args.f, True)
        self.assertEqual(args.o, False)

        args = arguable.parse_args('-fov[verbose]', ['-v', '-f'])
        self.assertEqual(args.verbose, True)
        self.assertEqual(args.f, True)
        self.assertEqual(args.o, False)

        with self.assertRaises(SyntaxError):
            # forget the ending ']'
            arguable.make_parser('-fov[verbose')


    def test_repeatable(self):
        parser = arguable.make_parser('-vv')
        args = parser.parse_args([])
        self.assertEqual(args.v, 0)

        args = parser.parse_args(['-v'])
        self.assertEqual(args.v, 1)

        args = parser.parse_args(['-vvvvv'])
        self.assertEqual(args.v, 5)


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
