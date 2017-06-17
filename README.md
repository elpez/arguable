# Arguable

A simple, usable command line argument parsing library for Python.

## Features

- A concise but powerful syntax for specifying command line arguments
- Complete interoperability with the standard `argparse` library
- Context management for easy handling of file arguments
- More sensible error handling (unlike `argparse`, `arguable` can be configured to not exit the entire program when parsing fails)

## Usage

### A simple example

```python
>>> args = arguable.parse_args('-vv[verbosity]g infile:rfile outfile:wfile?', ['-vv', '-g', 'in.xml'])
>>> args.verbosity
2
>>> args.g
True
>>> args.infile
<_io.TextIOWrapper name='in.xml' mode='r' encoding='UTF-8'>
>>> args.outfile
None
```

To achieve this in `argparse` you'd have to do:

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('-v', action='count', default=0)
>>> parser.add_argument('-g', action='store_true')
>>> parser.add_argument('infile', type=argparse.FileType('r'))
>>> parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'))
>>> args = parser.parser_args(['-vvv', 'input.xml'])
```

### Managing files

The `Namespace` object returned by the `parse_args` method is a context manager, which makes it easy to process arguments as files:

```python
>>> with arguable.parse_args('infile:rfile', ['in.xml']) as args:
...     process_file(args.infile)
...     # args.infile is closed automatically at the end of the with statement
```

### Integration with argparse

Since the return value of `make_parser` is a subclass of `arguable.ArgumentParser`, you can do all the regular things, in case you need an advanced feature that `arguable` doesn't support.

```python
>>> parser = arguable.make_parser('infile:rfile -vv[verbosity]')
>>> parser.add_argument('--foo', action='append') # some advanced argparse functionality
>>> with parser.parse_args(['in.xml', '-vvvv', '--foo', '1', '--foo', '2']) as args:
...     # do whatever
```

## Documentation

### Installation

Just drop the `arguable.py` file into your project; it is completely self-contained.

### API

The public API of `arguable` consists of just two functions: `make_parser` to construct a parser, and `parse_args` as a shortcut for constructing a parser and then immediately parsing some arguments.

```python
make_parser(pattern, **kwargs)
```

Return an `arguable.ArgumentParser` object constructed from `pattern`.  The `pattern` argument should be a string consisting of whitespace-separated tokens, where each token is one of:

- A required positional argument, with no special syntax, e.g. `infile`. A type specificer can be given, preceded by a colon and *no whitespace*, e.g. `x:int`.
- An optional positional argument, specified by a trailing question mark, e.g. `outfile?`. Optional arguments can also take type specifiers, e.g. `x:int?`.
- A series of one-letter flags, e.g. `-vfo`. These are interpreted as optional flags that take no arguments. You can give them a long name by following the one-letter abbreviation with the full name in brackets, e.g. `-v[verbosity]`. By default, these flags are given the `store_true` action. If you want the number of occurences to be counted instead, simply repeat the one-letter abbreviation in the pattern string, e.g. `-vv`. All of these can be combined in a single string, so a moderately complex example might be `-vv[verbosity]fo`, which makes three flags: a repeatable `-v` flag aliased to `--verbosity`, and two optional flags `-f` and `-o`.
- A single long flag with no abbreviation, e.g. `--verbosity`.
- All positional arguments grouped into a list, requiring at least one, specified by a trailing `...`, e.g. `files...`
- All positional arguments grouped into a list, but without complaining if none are supplied, specified by a trailing `...?`, e.g. `files...?`
- A specific number of positional arguments, e.g. `foo...3`. This also works with long options: `--bar...2`.

The type specifiers are somewhat more restricted than in `argparse`. They must be one of the following: `int, bool, str, float, rfile, wfile`. The `rfile` and `wfile` specifiers correspond to `argparse.FileType('r')` and `argparse.FileType('w')` respectively.

All keyword arguments are forwarded to the `argparse.ArgumentParser` constructor.

Since the return value of `make_parser` is an `arguable.ArgumentParser` object, a subclass of `argparse.ArgumentParser`, you can add any additional arguments that could not be specified in the `arguable` syntax using the regular `argparse` methods.

```python
parse_args(pattern, args=None, exit_on_error=None, **kwargs)
```

Shortcut for calling `parse_args` on the object returned by `make_parser(pattern, **kwargs)`. Like its counterpart in `argparse`, the `args` argument defaults to `sys.argv` if it is not supplied. See the `arguable.ArgumentParser.parse_args` method for details.

### Modifications to argparse

The `arguable` library overrides two `argparse` classes for improved functionality.

#### ArgumentParser

This subclass of `argparse.ArgumentParser` overrides the `parse_args` method:

```python
arguable.ArgumentParser.parse_args(args=None, exit_on_error=None, **kwargs)
```

Identical to its `argparse` counterpart except for the `exit_on_error` argument, which lets you control how the parser deals with errors. When it is `False` (the default when `args` is explicitly given), the parser doesn't print anything to `stderr` and raises a `ValueError` instead of exiting. When it is `True` (the default when `args` is omitted and falls back to `sys.argv`), it behaves normally.

#### Namespace

The `argparse.Namespace` class is overrided to implement the `__enter__` and `__exit__` methods that make it a context manager. The `__exit__` method iterates over its attributes and calls `__exit__` on each of them that are themselves context managers.