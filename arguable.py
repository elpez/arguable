import sys
import argparse
import contextlib
import io
import re


class ArgumentParser(argparse.ArgumentParser):
    def parse_args(self, args=None, namespace=None, exit_on_error=None, **kwargs):
        # set a reasonable default for exit_on_error if not provided
        if exit_on_error is None:
            exit_on_error = bool(args is None)
        # use the arguable.Namespace class if no namespace is provided
        if namespace is None:
            namespace = Namespace()
        if exit_on_error:
            return super().parse_args(args, namespace=namespace, **kwargs)
        else:
            with suppress_stderr():
                try:
                    return super().parse_args(args, namespace=namespace, **kwargs)
                except SystemExit as e:
                    raise ValueError

class Namespace(argparse.Namespace):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        ret = False
        for val in self.__dict__.values():
            if hasattr(val, '__exit__'):
                exit_val = val.__exit__(*args)
                if exit_val is True:
                    ret = True
        return ret


def parse_args(pattern, args=None, exit_on_error=None, **kwargs):
    """Shortcut for calling parse_args on the object returned by make_parser."""
    return make_parser(pattern, **kwargs).parse_args(args, exit_on_error=exit_on_error)


def make_parser(pattern, **kwargs):
    """Create an argparse.ArgumentParser object from the argument pattern. The pattern argument
       should be a string of whitespace-separated tokens, where each token is one of:

         - one or more flags, e.g. "-vfq". Each flag is added as a separate, optional argument.
           You can specify long aliases in brackets after the flag, e.g. "-v[verbose]fq", and
           repeatable flags by repeating the letter, e.g. "-fvv[verbose]q"
         - a long option, e.g. "--verbose".
         - a positional argument, e.g. "infile". If it is followed by "?", then it is optional 
           (otherwise it is required). 

       The arity of positional arguments and long options can be modified by following them with:
         - "..." to consume all remaining command line arguments, requiring at least one
         - "...?" to consume all remaining command line arguments, requiring none
         - "...n" where n is a positive integer, to consume n arguments
    """
    parser = ArgumentParser(**kwargs)
    for token in pattern.split():
        add_argument_from_token(parser, token)
    return parser

_type_map = {
    'int':int,
    'bool':bool,
    'str':str,
    'float':float,
    'rfile':argparse.FileType('r'),
    'wfile':argparse.FileType('w'),
}
_pattern = re.compile(r'\.\.\.[0-9]+$')
def add_argument_from_token(parser, token):
    if token.startswith('--'):
        if _pattern.search(token):
            token, arity = token.split('...', maxsplit=1)
            parser.add_argument(token, nargs=int(arity))
        else:
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
    # foo... gathers all remaining positional arguments, requiring at least one
    elif token.endswith('...'):
        parser.add_argument(token[:-3], nargs='+')
    # foo...n gathers n remaining positional arguments
    elif _pattern.search(token):
        token, arity = token.split('...', maxsplit=1)
        parser.add_argument(token, nargs=int(arity))
    else:
        optional = False
        if token.endswith('?'):
            token = token[:-1]
            optional = True
        try:
            token, type_str = token.split(':', maxsplit=1)
        except ValueError:
            typ = None
        else:
            # a type was specified
            try:
                typ = _type_map[type_str]
            except KeyError:
                raise SyntaxError('unrecognized type specifier "{}"'.format(type_str))
        if optional:
            parser.add_argument(token, nargs='?', type=typ)
        else:
            parser.add_argument(token, type=typ)


@contextlib.contextmanager
def suppress_stderr():
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    yield
    sys.stderr = old_stderr

class MyContextManager:
    """Used to test context management on Namespace objects"""
    def __init__(self):
        self.has_exited = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.has_exited = True
        return False
