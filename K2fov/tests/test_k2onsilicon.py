"""Test whether the `K2onSilicon` command-line tool works."""
import tempfile
import numpy as np

from ..K2onSilicon import K2onSilicon_main


def test_K2onSilicon():
    """Test the basics: does K2onSilicon run without error on a dummy file?"""
    csv = '269.5, -28.5, 12\n0, 0, 20\n'
    with tempfile.NamedTemporaryFile() as temp:
        try:
            # Python 3
            temp.write(bytes(csv, 'utf-8'))
        except TypeError:
            # Legacy Python
            temp.write(csv)
        temp.flush()
        K2onSilicon_main(args=[temp.name, "9"])

    # Verify the output
    output_fn = "targets_siliconFlag.csv"
    ra, dec, mag, status = np.atleast_2d(
                    np.genfromtxt(
                                output_fn,
                                usecols=[0, 1, 2, 3],
                                delimiter=','
                                )
            ).T
    # The first target is one silicon in C9, the second is not
    assert(int(status[0]) == 2)
    assert(int(status[1]) == 0)
    # Sanity check of the other columns
    assert(ra[0] == 269.5)
    assert(dec[0] == -28.5)
    assert(mag[0] == 12)
    assert(ra[1] == 0)
    assert(dec[1] == 0)
    assert(mag[1] == 20)
