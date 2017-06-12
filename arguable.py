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
         - a repeatable flag, e.g. "-vv".
         - a long option, e.g. "--verbose".
         - a required positional argument, e.g. "infile"
         - an optional positional argument, e.g. "outfile?"
    """
    parser = argparse.ArgumentParser()
    for token in pattern.split():
        if token.startswith('--'):
            parser.add_argument(token, action='store_true')
        elif token.startswith('-'):
            # -xx... where x is the same character is a repeatable option
            if len(token) > 2 and len(set(token[1:])) == 1:
                parser.add_argument('-' + token[1], action='count', default=0)
            # -ofv[verbose]... is a series of optional flags, -o -f and -v, where -v has a long
            # counterpart --verbose
            else:
                i = 1
                while i < len(token):
                    flag = token[i]
                    # handle long names
                    if i < len(token) - 1 and token[i+1] == '[':
                        end = token.find(']', i + 2)
                        if end != -1:
                            long_name = token[i+2:end]
                            parser.add_argument('-' + flag, '--' + long_name, action='store_true')
                            i = end + 1
                        else:
                            msg = 'long name "{}" needs a terminating "]"'.format(token[i+1:])
                            raise SyntaxError(msg)
                    else:
                        parser.add_argument('-' + flag, action='store_true')
                        i += 1
        # foo? is an optional positional argument
        elif token.endswith('?'):
            parser.add_argument(token[:-1], nargs='?')
        # anything else is interpreted as a required positional argument
        else:
            parser.add_argument(token)
    return parser
