import sys
import argparse
import contextlib
import io


class ArgumentParser(argparse.ArgumentParser):
    def parse_args(self, args=None, exit_on_error=None, **kwargs):
        # set a reasonable default for exit_on_error if not provided
        if exit_on_error is None:
            exit_on_error = bool(args is None)
        if exit_on_error:
            return super().parse_args(args, **kwargs)
        else:
            with suppress_stderr():
                try:
                    return super().parse_args(args, **kwargs)
                except SystemExit as e:
                    raise ValueError


def parse_args(pattern, args=None, exit_on_error=None):
    """Shortcut for calling parse_args on the object returned by make_parser."""
    return make_parser(pattern).parse_args(args, exit_on_error=exit_on_error)


def make_parser(pattern):
    """Create an argparse.ArgumentParser object from the argument pattern. The pattern argument
       should be a string of whitespace-separated tokens, where each token is one of:

         - one or more flags, e.g. "-vfq". Each flag is added as a separate, optional argument.
             You can specify long aliases in brackets after the flag, e.g. "-v[verbose]fq"
         - a repeatable flag, e.g. "-vv".
         - a long option, e.g. "--verbose".
         - a required positional argument, e.g. "infile"
         - an optional positional argument, e.g. "outfile?"
    """
    parser = ArgumentParser()
    for token in pattern.split():
        add_argument_from_token(parser, token)
    return parser

def add_argument_from_token(parser, token):
    if token.startswith('--'):
        parser.add_argument(token, action='store_true')
    elif token.startswith('-'):
        # -ofv[verbose]... is a series of optional flags, -o -f and -v, where -v has a long
        # counterpart --verbose
        i = 1
        doing_repeat = False
        while i < len(token):
            flag = token[i]
            # handle long names
            if i < len(token) - 1 and token[i+1] == '[':
                end = token.find(']', i + 2)
                if end != -1:
                    long_name = token[i+2:end]
                    if doing_repeat:
                        parser.add_argument('-'+flag, '--'+long_name, action='count', default=0)
                        doing_repeat = False
                    else:
                        parser.add_argument('-'+flag, '--'+long_name, action='store_true')
                    i = end + 1
                else:
                    msg = 'long name "{}" needs a terminating "]"'.format(token[i+1:])
                    raise SyntaxError(msg)
            # handle repeated flags, e.g. -vv
            elif i < len(token) - 1 and token[i+1] == flag:
                doing_repeat = True
                i += 1
            else:
                if doing_repeat:
                    parser.add_argument('-'+flag, action='count', default=0)
                else:
                    parser.add_argument('-'+flag, action='store_true')
                i += 1
    # foo...? gather all remaining positional arguments, but doesn't complain if none are left
    elif token.endswith('...?'):
        parser.add_argument(token[:-4], nargs='*')
    # foo? is an optional positional argument
    elif token.endswith('?'):
        parser.add_argument(token[:-1], nargs='?')
    # foo... gathers all remaining positional arguments, requiring at least one
    elif token.endswith('...'):
        parser.add_argument(token[:-3], nargs='+')
    # anything else is interpreted as a required positional argument
    else:
        parser.add_argument(token)


@contextlib.contextmanager
def suppress_stderr():
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    yield
    sys.stderr = old_stderr
