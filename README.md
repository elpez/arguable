# Blargparse

A command line argument parsing library for Python that isn't completely insane.

## Usage

```python
>>> parser = blargparse.Parser(description='Process some files')
>>> parser.add_arg('infile')
>>> parser.add_optional_arg('outfile', default='out.xml')
>>> parser.add_flag('-v', repeat=True, dest='verbosity')
>>> args = parser.parse_args(['-vvv', 'input.xml'])
>>> args.verbosity
3
>>> args.infile
'input.xml'
>>> args.outfile
'out.xml'
```

## Documentation

### Installation

Just drop in the `blargparse.py` file into your project; it is completely self-contained.