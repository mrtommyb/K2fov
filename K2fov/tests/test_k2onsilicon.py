"""Test whether the K2onSilicon command-line tool works."""
import tempfile

from ..K2onSilicon import K2onSilicon_main


def test_K2onSilicon():
    """Test the basics: does K2onSilicon run without error on a dummy file?"""
    csv = '0, 0, 0\n'
    with tempfile.NamedTemporaryFile() as temp:
        try:
            # Python 3
            temp.write(bytes(csv, 'utf-8'))
        except TypeError:
            # Legacy Python
            temp.write(csv)
        temp.flush()
        K2onSilicon_main(args=[temp.name, "1"])
