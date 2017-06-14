# Arguable

A command line argument parsing library for Python that isn't completely insane.

## Features

- A concise but powerful syntax for specifying command line arguments
- Complete interoperability with the standard `argparse` library
- More sensible error handling (unlike `argparse`, `arguable` can be configured to not exit the entire program when parsing fails)

## Usage

```python
>>> args = arguable.parse_args('-vv[verbosity]g infile outfile?', ['-vv', '-g', 'in.xml'])
>>> args.verbosity
2
>>> args.g
True
>>> args.infile
'in.xml'
>>> args.outfile
None
```

The preceding example is exactly equivalent (albeit six times shorter!) to this `argparse` code:

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('-v', action='count', default=0)
>>> parser.add_argument('-g', action='store_true')
>>> parser.add_argument('infile')
>>> parser.add_argument('outfile', nargs='?')
>>> args = parser.parser_args(['-vvv', 'input.xml'])
```

## Documentation

### Installation

Just drop the `arguable.py` file into your project; it is completely self-contained.

### API

The public API of `arguable` consists of just two functions: `make_parser` to construct a parser, and `parse_args` as a shortcut for constructing a parser and then immediately parsing some arguments.

```python
make_parser(pattern)
```

Return an `arguable.ArgumentParser` object constructed from `pattern`.  The `pattern` argument should be a string consisting of whitespace-separated tokens, where each token is one of:

- A required positional argument, with no special syntax, e.g. `infile`. A type specificer can be given, preceded by a colon and *no whitespace*, e.g. `x:int`.
- An optional positional argument, specified by a trailing question mark, e.g. `outfile?`. Optional arguments can also take type specifiers, e.g. `x:int?`.
- A series of one-letter flags, e.g. `-vfo`. These are interpreted as optional flags that take no arguments. You can give them a long name by following the one-letter abbreviation with the full name in brackets, e.g. `-v[verbosity]`. By default, these flags are given the `store_true` action. If you want the number of occurences to be counted instead, simply repeat the one-letter abbreviation in the pattern string, e.g. `-vv`. All of these can be combined in a single string, so a moderately complex example might be `-vv[verbosity]fo`, which makes three flags: a repeatable `-v` flag aliased to `--verbosity`, and two optional flags `-f` and `-o`.
- A single long flag with no abbreviation, e.g. `--verbosity`.
- All positional arguments grouped into a list, requiring at least one, specified by a trailing `...`, e.g. `files...`
- All positional arguments grouped into a list, but without complaining if none are supplied, specificed by a trailing `...?`, e.g. `files...?`

The type specifiers are somewhat more restricted than in `argparse`. They must be one of the following: `int, bool, str, float, rfile, wfile`. The `rfile` and `wfile` specifiers correspond to `argparse.FileType('r')` and `argparse.FileType('w')` respectively.

Since the return value of `make_parser` is an `arguable.ArgumentParser` object, a subclass of `argparse.ArgumentParser`, you can add any additional arguments that could not be specified in the `arguable` syntax using the regular `argparse` methods.

```python
parse_args(pattern, args=None, exit_on_error=None)
```

Shortcut for calling `parse_args` on the object returned by `make_parser(pattern)`. Like its counterpart in `argparse`, the `args` argument defaults to `sys.argv` if it is not supplied. See the `arguable.ArgumentParser.parse_args` method for details.

```python
class arguable.ArgumentParser
```

A subclass of `argparse.ArgumentParser` that overrides the `parse_args` method.

```python
arguable.ArgumentParser.parse_args(args=None, exit_on_error=None, **kwargs)
```

Identical to its `argparse` counterpart except for the `exit_on_error` argument, which lets you control how the parser deals with errors. When it is `False` (the default when `args` is explicitly given), the parser doesn't print anything to `stderr` and raises a `ValueError` instead of exiting. When it is `True` (the default when `args` is omitted and falls back to `sys.argv`), it behaves normally.