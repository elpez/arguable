import io
import os

import pytest

from arguable import arguable


def test_long_option():
    args = arguable.parse_args("--verbose", ["--verbose"])
    assert args.verbose is True


def test_long_option_syntax():
    args = arguable.parse_args("-v[verbose]fo", ["-v", "-f"])
    assert args.verbose is True
    assert args.f is True
    assert args.o is False

    args = arguable.parse_args("-fv[verbose]o", ["-v", "-f"])
    assert args.verbose is True
    assert args.f is True
    assert args.o is False

    args = arguable.parse_args("-fov[verbose]", ["-v", "-f"])
    assert args.verbose is True
    assert args.f is True
    assert args.o is False

    with pytest.raises(SyntaxError):
        # Forgot the ending ']'.
        arguable.ArgumentParser("-fov[verbose")

    # With repeated options
    args = arguable.parse_args("-fvv[verbose]o", ["-vvvv", "-f"])
    assert args.verbose == 4
    assert args.f is True
    assert args.o is False


def test_repeatable():
    parser = arguable.ArgumentParser("-vv")
    args = parser.parse_args([])
    assert args.v == 0

    args = parser.parse_args(["-v"])
    assert args.v == 1

    args = parser.parse_args(["-vvvvv"])
    assert args.v == 5


def test_gathering():
    parser = arguable.ArgumentParser("-v x y...")
    args = parser.parse_args(["foo", "bar", "baz", "-v"])
    assert args.x == "foo"
    assert args.y == ["bar", "baz"]
    assert args.v is True

    with pytest.raises(ValueError):
        # y requires at least one argument.
        parser.parse_args(["1"])

    parser = arguable.ArgumentParser("-v x y...?")
    args = parser.parse_args(["foo", "bar", "baz", "-v"])
    assert args.x == "foo"
    assert args.y == ["bar", "baz"]
    assert args.v is True
    # Not supplying any arguments for y is just fine.
    args = parser.parse_args(["foo", "-v"])
    assert args.x == "foo"
    assert args.y == []
    assert args.v is True


def test_type():
    parser = arguable.ArgumentParser("x:int y:int?")
    args = parser.parse_args(["10", "7"])
    assert args.x == 10
    assert args.y == 7
    # Make sure that y is really optional.
    args = parser.parse_args(["10"])
    assert args.x == 10
    assert args.y is None

    args = arguable.parse_args("x:float", ["7.8"])
    assert args.x == 7.8

    args = arguable.parse_args("x:wfile", ["tmpfile"])
    assert isinstance(args.x, io.IOBase)
    args.x.close()

    args = arguable.parse_args("x:rfile", ["tmpfile"])
    assert isinstance(args.x, io.IOBase)
    args.x.close()
    os.remove(args.x.name)


def test_context_management():
    manager = arguable.MyContextManager()

    with arguable.parse_args("x", ["whatever"]) as args:
        # Add a new argument that is a context manager.
        args.y = manager
        assert not manager.has_exited

    # Make sure __exit__ is called on the manager.
    assert manager.has_exited


def test_kwargs():
    parser = arguable.ArgumentParser("", prog="bar", description="foo")
    assert parser.description == "foo"
    assert parser.prog == "bar"


def test_arbitrary_arity():
    parser = arguable.ArgumentParser("foo...3 bar...2 --baz...1")
    args = parser.parse_args(["1", "2", "3", "4", "5", "--baz", "6"])
    assert args.foo == ["1", "2", "3"]
    assert args.bar == ["4", "5"]
    assert args.baz == ["6"]


def test_full():
    parser = arguable.ArgumentParser("-vv[verbosity]g infile outfile? foo:int...?")
    args = parser.parse_args(["test.xml"])
    assert args.verbosity == 0
    assert args.g is False
    assert args.infile == "test.xml"
    assert args.outfile is None
    assert args.foo == []

    args = parser.parse_args(["test.xml", "-v"])
    assert args.verbosity == 1
    assert args.g is False
    assert args.infile == "test.xml"
    assert args.outfile is None
    assert args.foo == []

    args = parser.parse_args(["-vv", "-g", "test.xml", "out.html"])
    assert args.verbosity == 2
    assert args.g is True
    assert args.infile == "test.xml"
    assert args.outfile is "out.html"
    assert args.foo == []

    args = parser.parse_args(["-vv", "-g", "test.xml", "out.html", "1", "2", "3"])
    assert args.verbosity == 2
    assert args.g is True
    assert args.infile == "test.xml"
    assert args.outfile is "out.html"
    assert args.foo == [1, 2, 3]
