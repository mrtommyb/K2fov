# K2fov [![PyPI](http://img.shields.io/pypi/v/K2fov.svg)](https://pypi.python.org/pypi/K2fov/)  [![PyPI](http://img.shields.io/pypi/dm/K2fov.svg)](https://pypi.python.org/pypi/K2fov/) [![Travis status](https://travis-ci.org/KeplerGO/K2fov.svg)](https://travis-ci.org/KeplerGO/K2fov)
***Check whether targets are in the field of view of NASA's K2 mission.***

The `K2fov` package allows users to check whether a target is in the field of view of K2. 
In particular, the package adds a `K2onSilicon` to the command line
which allows a target list in csv format to be checked.

### Installation

You can install `K2fov` using `pip`:
```bash
pip install K2fov
```
if you have a previous version installed, please upgrade to the
latest version using:
```bash
pip install K2fov --upgrade
```
You'll need a modern version of Python and a relatively new version of numpy.

### Usage

The simplest thing to do is to have a CSV file with columns
"RA_degrees, Dec_degrees, Kepmag".
Do not use a header.

For example, create a file called `mytargetlist.csv` containing
the following rows:
```bash
178.19284, 1.01924, 13.2
171.14213, 5.314616, 11.3
```

You can then check whether each object in the file falls on silicon
by calling `K2onSilicon` from the command line:
```bash
K2onSilicon mytargetlist.csv 1
```

Where `mytargetlist.csv` is your CSV file and `1` is the K2 Campaign number.

Running the code will output a file with the three input columns and an additional column with either [0,2].<br>
0 = Not observable<br>
2 = Target is in the K2 field of view<br>

The code will also make an image showing where the targets fall.
