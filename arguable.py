import sys
import argparse

def parse_args(pattern, args=None):
    """Shortcut for calling parse_args on the object returned by make_parser."""
    args = args if args is not None else sys.argv
    return make_parser(pattern).parse_args(args)

def make_parser(pattern):
    """Create an argparse.ArgumentParser object from the argument pattern. The pattern argument
       should be a string of whitespace-separated tokens, where each token is one of:

         - one or more flags, e.g. "-vfq". Each flag is added as a separate, optional argument.
         - a long option, e.g. "--verbose".
         - a required positional argument, e.g. "infile"
         - an optional positional argument, e.g. "outfile?"
    """
    parser = argparse.ArgumentParser()
    for token in pattern.split():
        if token.startswith('--'):
            parser.add_argument(token, action='store_true')
        elif token.startswith('-'):
            for flag in token[1:]:
                parser.add_argument('-' + flag, action='store_true')
        elif token.endswith('?'):
            parser.add_argument(token[:-1], nargs='?')
        else:
            parser.add_argument(token)
    return parser
