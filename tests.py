#!/usr/bin/env python3

import unittest
import contextlib
import io
import sys
import os

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
            # forgot the ending ']'
            arguable.ArgumentParser('-fov[verbose')

        # with repeated options
        args = arguable.parse_args('-fvv[verbose]o', ['-vvvv', '-f'])
        self.assertEqual(args.verbose, 4)
        self.assertEqual(args.f, True)
        self.assertEqual(args.o, False)


    def test_repeatable(self):
        parser = arguable.ArgumentParser('-vv')
        args = parser.parse_args([])
        self.assertEqual(args.v, 0)

        args = parser.parse_args(['-v'])
        self.assertEqual(args.v, 1)

        args = parser.parse_args(['-vvvvv'])
        self.assertEqual(args.v, 5)


    def test_gathering(self):
        parser = arguable.ArgumentParser('-v x y...')
        args = parser.parse_args(['foo', 'bar', 'baz', '-v'])
        self.assertEqual(args.x, 'foo')
        self.assertEqual(args.y, ['bar', 'baz'])
        self.assertEqual(args.v, True)
        with self.assertRaises(ValueError):
            # y requires at least one argument
            parser.parse_args(['1'])

        parser = arguable.ArgumentParser('-v x y...?')
        args = parser.parse_args(['foo', 'bar', 'baz', '-v'])
        self.assertEqual(args.x, 'foo')
        self.assertEqual(args.y, ['bar', 'baz'])
        self.assertEqual(args.v, True)
        # not supplying any arguments for y is just fine
        args = parser.parse_args(['foo', '-v'])
        self.assertEqual(args.x, 'foo')
        self.assertEqual(args.y, [])
        self.assertEqual(args.v, True)


    def test_type(self):
        parser = arguable.ArgumentParser('x:int y:int?')
        args = parser.parse_args(['10', '7'])
        self.assertEqual(args.x, 10)
        self.assertEqual(args.y, 7)
        # make sure that y is really optional
        args = parser.parse_args(['10'])

        args = arguable.parse_args('x:float', ['7.8'])
        self.assertEqual(args.x, 7.8)

        args = arguable.parse_args('x:wfile', ['tmpfile'])
        self.assertIsInstance(args.x, io.IOBase)
        args.x.close()

        args = arguable.parse_args('x:rfile', ['tmpfile'])
        self.assertIsInstance(args.x, io.IOBase)
        args.x.close()
        os.remove(args.x.name)


    def test_context_management(self):
        manager = arguable.MyContextManager()
        with arguable.parse_args('x', ['whatever']) as args:
            # add a new argument that is a context manager
            args.y = manager
            self.assertFalse(manager.has_exited)
        # make sure __exit__ is called on the manager
        self.assertTrue(manager.has_exited)


    def test_kwargs(self):
        parser = arguable.ArgumentParser('', prog='bar', description='foo')
        self.assertEqual(parser.description, 'foo')
        self.assertEqual(parser.prog, 'bar')

    
    def test_arbitrary_arity(self):
        parser = arguable.ArgumentParser('foo...3 bar...2 --baz...1')
        args = parser.parse_args(['1', '2', '3', '4', '5', '--baz', '6'])
        self.assertEqual(args.foo, ['1', '2', '3'])
        self.assertEqual(args.bar, ['4', '5'])
        self.assertEqual(args.baz, ['6'])


    def test_full(self):
        parser = arguable.ArgumentParser('-vv[verbosity]g infile outfile? foo:int...?')
        args = parser.parse_args(['test.xml'])
        self.assertEqual(args.verbosity, 0)
        self.assertEqual(args.g, False)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, None)
        self.assertEqual(args.foo, [])

        args = parser.parse_args(['test.xml', '-v'])
        self.assertEqual(args.verbosity, 1)
        self.assertEqual(args.g, False)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, None)
        self.assertEqual(args.foo, [])

        args = parser.parse_args(['-vv', '-g', 'test.xml', 'out.html'])
        self.assertEqual(args.verbosity, 2)
        self.assertEqual(args.g, True)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, 'out.html')
        self.assertEqual(args.foo, [])

        args = parser.parse_args(['-vv', '-g', 'test.xml', 'out.html', '1', '2', '3'])
        self.assertEqual(args.verbosity, 2)
        self.assertEqual(args.g, True)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, 'out.html')
        self.assertEqual(args.foo, [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
