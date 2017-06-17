# Arguable

A simple, easy-to-use command line argument parsing library for Python.

## Features

- A concise but powerful syntax for specifying command line arguments
- Context management for easy handling of file arguments
- Drop-in replacement for `argparse`
- More sensible error handling (unlike `argparse`, `arguable` can be configured to not exit the entire program when parsing fails)

## Usage

### A full example

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

Compare this to the equivalent `argparse` code (it's six times longer!):

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('-v', action='count', default=0)
>>> parser.add_argument('-g', action='store_true')
>>> parser.add_argument('infile', type=argparse.FileType('r'))
>>> parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'))
>>> args = parser.parser_args(['-vvv', 'input.xml'])
```

### Managing files

The `Namespace` object returned by `parse_args` is a context manager, which makes it easy to process arguments as files:

```python
>>> with arguable.parse_args('infile:rfile', ['in.xml']) as args:
...     process_file(args.infile)
...     # args.infile is closed automatically at the end of the with statement
```

### Another example

It's easy to specify the exact number and type of command line arguments that should be consumed:

```python
>>> args = arguable.parse_args('foo:int...3  bar:float...2', ['1', '2', '3', '4', '5'])
>>> args.foo
[1, 2, 3]
>>> args.bar
[4.0, 5.0]
```

### Integration with argparse

You can still do all the regular `argparse` things, in case you need an advanced feature that `arguable` doesn't support.

```python
>>> parser = arguable.ArgumentParser('infile:rfile -vv[verbosity]')
>>> parser.add_argument('--foo', action='append') # some advanced argparse functionality
>>> with parser.parse_args(['in.xml', '-vvvv', '--foo', '1', '--foo', '2']) as args:
...     # do whatever
```

## Documentation

### Installation

Just drop the `arguable.py` file into your project; it is completely self-contained.

### API

`arguable` defines a single public method, `parse_args`, and two classes that override their `argparse` counterparts, `ArgumentParser` and `Namespace`.

```python
parse_args(pattern, args=None, exit_on_error=None, **kwargs)
```

Shortcut for calling `ArgumentParser(pattern, **kwargs).parse_args(args=args, exit_on_error=exit_on_error)`. Useful if you have no need for the underlying `ArgumentParser` object.

#### ArgumentParser

```python
def __init__(self, pattern, *args, **kwargs)
```

Construct a parser from `pattern`.  The `pattern` argument should be a string consisting of whitespace-separated tokens, where each token is either:

- A positional argument or long flag, e.g. `infile` or `--verbose`. 
  - These can be given a type specifier (one of `int`, `bool`, `str`, `float`, `rfile`, `wfile`) preceded by a colon, e.g. `infile:rfile`. The `rfile` and `wfile` specifiers correspond to `argparse.FileType('r')` and `argparse.FileType('w')` respectively.
  - They can have a specified arity (one of `?`, `...`,  `...?`, `...n` where `n` is a positive integer) after the type specifier. `?` means "optionally consume one argument if present," `...` means "consume all remaining positional arguments, requiring at least one", `...?` means "consume all remaining positional arguments but don't complain if none are left", and `...n` means "consume exactly `n` of the remaining positional arguments."
  - The only difference between a positional argument and a long flag is that by default the former is required and consume one argument, while the latter is optional and consume no arguments. If either type or arity is specified for a long flag, it behaves exactly the same as a positional argument.
  - A full example: `summands:int...7` means "consume 7 of the remaining positional arguments, convert each of them into a integer and store them in a list called `summands`."
- A short flag, e.g. `-v`
  - If the flag name is repeated (e.g., `-vv`), then the flag is treated as repeatable.
  - The flag name may be succeeded by a verbose name in brackets, e.g. `-v[verbose]`. This can be combined with the syntax for repeated flags, e.g. `-vv[verbose]`.
  - Multiple flags can be combined in a single token, e.g. `-fovv[verbose]g[debug]`.

All the other positional and keyword arguments are forwarded to the `argparse.ArgumentParser` constructor.

```python
def parse_args(self, args=None, exit_on_error=None, **kwargs)
```

Identical to its `argparse` counterpart except for the `exit_on_error` argument, which lets you control how the parser deals with errors. When it is `False` (the default when `args` is explicitly given), the parser doesn't print anything to `stderr` and raises a `ValueError` instead of exiting. When it is `True` (the default when `args` is omitted and falls back to `sys.argv`), it behaves normally.

#### Namespace

The `argparse.Namespace` class is overrided to implement the `__enter__` and `__exit__` methods that make it a context manager. The `__exit__` method iterates over its attributes and calls `__exit__` on each of them that are themselves context managers.