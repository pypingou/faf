import sys
from StringIO import StringIO
from contextlib import contextmanager


@contextmanager
def captured_output():
    """
    Capture stdout and stderr output of the executed block

    Example:

    with captured_output() as (out, err):
        foo()
    """

    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
