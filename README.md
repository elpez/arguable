# Arguable

A command line argument parsing library for Python that isn't completely insane.

## Usage

```python
>>> parser = arguable.make_parser('-vv infile outfile?')
>>> args = parser.parse_args(['-vvv', 'input.xml'])
>>> args.verbosity
3
>>> args.infile
'input.xml'
>>> args.outfile
None
```

## Documentation

### Installation

Just drop in the `arguable.py` file into your project; it is completely self-contained.
