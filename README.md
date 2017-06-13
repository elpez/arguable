# Arguable

A command line argument parsing library for Python that isn't completely insane.

## Features

- A concise but powerful syntax for specifying command line arguments
- Complete interoperability with the standard `argparse` library

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

The equivalent `argparse` code would be:

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

Return an `argparse.ArgumentParser` object constructed from `pattern`.  The `pattern` argument should be a string consisting of whitespace-separated tokens, where each token is one of:

- A required positional argument, with no special syntax, e.g. `infile`
- An optional positional argument, specified by a trailing question mark, e.g. `outfile?`
- A series of one-letter flags, e.g. `-vfo`. These are interpreted as optional flags that take no arguments. You can give them a long name by following the one-letter abbreviation with the full name in brackets, e.g. `-v[verbosity]`. By default, these flags are given the `store_true` action. If you want the number of occurences to be counted instead, simply repeat the one-letter abbreviation in the pattern string, e.g. `-vv`. All of these can be combined in a single string, so a moderately complex example might be `-vv[verbosity]fo`, which makes three flags: a repeatable `-v` flag aliased to `--verbosity`, and two optional flags `-f` and `-o`.
- A single long flag with no abbreviation, e.g. `--verbosity`.
- All positional arguments grouped into a list, requiring at least one, specified by a trailing `...`, e.g. `files...`
- All positional arguments grouped into a list, but without complaining if none are supplied, specificed by a trailing `...?`, e.g. `files...?`

Since the return value of `make_parser` is an actual `argparse.ArgumentParser` object, you can add any additional arguments that could not be specified in the `arguable` syntax.

```python
parse_args(pattern, args=None)
```

Shortcut for calling `parse_args` on the object returned by `make_parser(pattern)`. Like its counterpart in `argparse`, the `args` argument defaults to `sys.argv` if it is not supplied. The return value is the same as in [argparse](https://docs.python.org/3.4/library/argparse.html#the-parse-args-method): a namespace object with values for each of the expected arguments.