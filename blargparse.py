import sys
import argparse

class Parser(argparse.ArgumentParser):
    def add_required_arg(self, name):
        self.add_argument(name)

    def add_optional_arg(self, name, default=None):
        self.add_argument(name, nargs='?', default=default)

    def add_flag(self, name, repeat=False, dest=None):
        if repeat:
            self.add_argument(name, action='count', dest=dest)
        else:
            self.add_argument(name, action='store_true', dest=dest)
