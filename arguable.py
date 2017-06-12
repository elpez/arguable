import sys
import argparse

class ArgumentParser(argparse.ArgumentParser):
    def add_required_arg(self, name):
        self.add_argument(name)

    def add_optional_arg(self, name, default=None):
        self.add_argument(name, nargs='?', default=default)

    def add_flag(self, name, repeat=False, dest=None):
        if repeat:
            self.add_argument(name, action='count', dest=dest)
        else:
            self.add_argument(name, action='store_true', dest=dest)

def parse_args(pattern, args=None):
    args = args if args is not None else sys.argv
    return make_parser(pattern).parse_args(args)

def make_parser(pattern):
    parser = argparse.ArgumentParser()
    for token in pattern.split():
        if token.startswith('-'):
            for flag in token[1:]:
                parser.add_argument('-' + flag, action='store_true')
        elif token.startswith('--'):
            parser.add_argument(token, action='store_true')
        elif token.endswith('?'):
            parser.add_argument(token[:-1], nargs='?')
        else:
            parser.add_argument(token)
    return parser
