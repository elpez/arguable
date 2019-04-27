import sys
import argparse
import contextlib
import io
import re


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, pattern, *args, **kwargs):
        """Create an argparse.ArgumentParser object from the argument pattern. The pattern argument
           should be a string of whitespace-separated tokens, where each token is one of:

             - one or more flags, e.g. "-vfq". Each flag is added as a separate, optional argument.
               You can specify long aliases in brackets after the flag, e.g. "-v[verbose]fq", and
               repeatable flags by repeating the letter, e.g. "-fvv[verbose]q"
             - a long option, e.g. "--verbose".
             - a positional argument, e.g. "infile". If it is followed by "?", then it is optional 
               (otherwise it is required). 

           The arity of positional arguments and long options can be set with:
             - "..." to consume all remaining command line arguments, requiring at least one
             - "...?" to consume all remaining command line arguments, requiring none
             - "...n" where n is a positive integer, to consume n arguments
        """
        super().__init__(*args, **kwargs)
        for token in yield_tokens(pattern):
            self._add_argument_from_token(token)

    def set_help(self, argname, helpstr):
        """Set the help string on the argument given by argname."""
        for action in self._actions:
            if action.dest == argname:
                action.help = helpstr

    def _add_argument_from_token(self, token):
        """Add an argument based on the token. The token should not be a combined short flag token 
           like "-vfg", i.e. it should be something yielded from yield_tokens.
        """
        if len(token) >= 2 and token[0] == "-" and token[1] != "-":
            token, long_name = determine_long_name(token)
            # a repeated flag
            if len(token) == 3:
                token = token[:-1]
                kwargs = {"action": "count", "default": 0}
            else:
                kwargs = {"action": "store_true"}
            if long_name:
                self.add_argument(token, "--" + long_name, **kwargs)
            else:
                self.add_argument(token, **kwargs)
        else:
            token, nargs = determine_nargs(token)
            token, typ = determine_type(token)
            if token.startswith("--"):
                # long flags default to being optional
                if (nargs is None or nargs == "?") and typ is None:
                    self.add_argument(token, action="store_true")
                else:
                    self.add_argument(token, nargs=nargs, type=typ)
            else:
                self.add_argument(token, nargs=nargs, type=typ)

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
            if hasattr(val, "__exit__"):
                exit_val = val.__exit__(*args)
                if exit_val is True:
                    ret = True
        return ret


def parse_args(pattern, args=None, exit_on_error=None, **kwargs):
    """Shortcut for calling parse_args on an ArgumentParser."""
    return ArgumentParser(pattern, **kwargs).parse_args(
        args, exit_on_error=exit_on_error
    )


def yield_tokens(pattern):
    """Yield successive tokens from the pattern.

       The main purpose of this function is to split combined flag arguments like "-vfg" into
       separate flags like "-v", "-f" and "-g".
    """
    for token in pattern.split():
        if len(token) >= 2 and token[0] == "-" and token[1] != "-":
            i = 1
            while i < len(token):
                if i < len(token) - 1:
                    # a flag (repeated or not) with a verbose name in brackets
                    # ex. "o[object]", "vv[verbose]"
                    if token[i + 1] == "[" or (
                        token[i] == token[i + 1]
                        and i < len(token) - 2
                        and token[i + 2] == "["
                    ):
                        end = token.find("]", i + 2)
                        if end == -1:
                            raise SyntaxError(
                                '"[" in {} needs a closing "]"'.format(token)
                            )
                        yield "-" + token[i : end + 1]
                        i = end + 1
                    # a repeated flag, ex. "vv"
                    elif token[i] == token[i + 1]:
                        yield "-" + token[i : i + 2]
                        i += 2
                    # a normal flag
                    else:
                        yield "-" + token[i]
                        i += 1
                else:
                    yield "-" + token[i]
                    i += 1
        else:
            yield token


def determine_long_name(token):
    """Return (token, long_name)"""
    try:
        token, long_name = token.split("[", maxsplit=1)
        long_name = long_name.rstrip("]")
    # the split failed
    except ValueError:
        return (token, "")
    # the split succeeded (a verbose name was provided)
    else:
        return (token, long_name)


def determine_nargs(token):
    """Return (token, nargs)"""
    try:
        token, end = token.split("...", maxsplit=1)
    # the split failed
    except ValueError:
        if token.endswith("?"):
            return (token[:-1], "?")
        else:
            return (token, None)
    # the split succeeded
    else:
        if end == "?":
            # foo...? gathers all remaining positional arguments, but doesn't complain if none are
            # left
            return (token, "*")
        elif end == "":
            # foo... gathers all remaining positional arguments, requiring at least one
            return (token, "+")
        else:
            # foo...n gathers n remaining positional arguments
            try:
                return (token, int(end))
            except ValueError:
                msg = '"..." must be followed by nothing, "?" or an integer, not {}'.format(
                    end
                )
                raise SyntaxError(msg)


_type_map = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "rfile": argparse.FileType("r"),
    "wfile": argparse.FileType("w"),
}


def determine_type(token):
    """Return (token, type)"""
    try:
        token, type_str = token.split(":", maxsplit=1)
    # the split failed
    except ValueError:
        return (token, None)
    # the split succeeded (a type was specified)
    else:
        try:
            return (token, _type_map[type_str])
        except KeyError:
            raise SyntaxError('unrecognized type specifier "{}"'.format(type_str))


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
