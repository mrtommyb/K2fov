# K2fov [![PyPI](http://img.shields.io/pypi/v/K2fov.svg)](https://pypi.python.org/pypi/K2fov/)  [![PyPI](http://img.shields.io/pypi/dm/K2fov.svg)](https://pypi.python.org/pypi/K2fov/) [![Travis status](https://travis-ci.org/KeplerGO/K2fov.svg)](https://travis-ci.org/KeplerGO/K2fov) [![DOI](https://zenodo.org/badge/10301/KeplerGO/K2fov.svg)](https://zenodo.org/badge/latestdoi/10301/KeplerGO/K2fov)
***Check whether targets are in the field of view of NASA's K2 mission.***

The `K2fov` Python package allows users to check whether a target is in the field of view of K2. 
In particular, the package adds the `k2onsilicon` and `k2findcampaigns` tools
to the command line, which allow the visibility of targets to be checked
during one (`k2onsilicon`) or all (`k2findcampaigns`) campaigns, respectively.
The usage of these tools is explained below.

## Installation

You will need a modern version of Python 2 or 3 on your system.
If this requirement is met, you can install `K2fov` using `pip`:
```bash
pip install K2fov
```
if you have a previous version installed, please make sure you upgrade to the
latest version using:
```bash
pip install K2fov --upgrade
```
It is important to upgrade frequently to ensure that you are using the most
up to date K2 field parameters.

## Usage

### k2onsilicon

Installing `K2fov` will automatically add a command line tool 
to your path called `k2onsilicon`, which takes a list of targets
as input and writes a new list that indicates the "silicon status"
of each target, i.e. whether or not it falls on one of the
detectors of the spacecraft's focal plane.

**Example**

The simplest thing to do is to have a CSV file with columns
"RA_degrees, Dec_degrees, Kepmag".
Do not use a header.

For example, create a file called `mytargetlist.csv` containing
the following rows:
```bash
178.19284, 1.01924, 13.2
171.14213, 5.314616, 11.3
```
The format for the target list is very strict -- you need three
columns: RA in degrees, Declination in degrees and Kepler
magnitude. Headers or other additional columns will cause an execution
failure.

You can then check whether each object in the file falls on silicon
by calling `k2onsilicon` from the command line:
```bash
k2onsilicon mytargetlist.csv 1
```
Where `mytargetlist.csv` is your CSV file and `1` is the K2 Campaign number.

Running the code will output an updated target list containing the three input columns and an extra column containing either a "0" or "2".<br>
0 = Not observable<br>
2 = Target is in the K2 field of view and on silicon<br>

The code will also write an image, called `targets_fov.png`, showing where the targets fall.

Execute `k2onsilicon --help` to be reminded of its usage:
```
$ k2onsilicon --help
usage: k2onsilicon [-h] csv_file campaign

Run k2onsilicon to find which targets in a list call on active silicon for a
given K2 campaign.

positional arguments:
  csv_file    Name of input csv file with targets, column are Ra_degrees,
              Dec_degrees, Kepmag
  campaign    K2 Campaign number

optional arguments:
  -h, --help  show this help message and exit
```


### k2findcampaigns

If instead of checking the targets in a single campaign,
you want to understand whether a target is visible in *any* past or
future K2 Campaign, you can use a different tool called `k2findcampaigns`.

**Example**

For example, to verify whether J2000 coordinate
(ra, dec) = (269.5, -28.5) degrees is visible at any point
during the K2 mission, type:
```
$ k2findcampaigns 269.5 -28.5
Success! The target is on silicon during K2 campaigns [9].
```

You can also search by name.
For example, to check whether *T Tauri* is visible, type:
```
$ k2findcampaigns-byname "T Tauri"
Success! T Tauri is on silicon during K2 campaigns [4].
```

Finally, you can check a list of targets (either using their coordinates or names), using `k2findcampaigns-csv`.
For example:
```
$ k2findcampaigns-csv targets.csv
Writing targets.csv-k2findcampaigns.csv.
```

**More information**

Execute `k2findcampaigns --help`, `k2findcampaigns-byname --help` or `k2findcampaigns-csv --help` to be reminded of the use:
```
$ k2findcampaigns --help
usage: k2findcampaigns [-h] ra dec

Check if a celestial coordinate is (or was) observable by any past or future
observing campaign of NASA's K2 mission.

positional arguments:
  ra          Right Ascension in decimal degrees (J2000).
  dec         Declination in decimal degrees (J2000).

optional arguments:
  -h, --help  show this help message and exit
```

```
k2findcampaigns-byname --help
usage: k2findcampaigns-byname [-h] name

Check if a target is (or was) observable by any past or future observing
campaign of NASA's K2 mission.

positional arguments:
  name        Name of the object. This will be passed on to the CDS name
              resolver to retrieve coordinate information.

optional arguments:
  -h, --help  show this help message and exit
```

```
$ k2findcampaigns-csv --help
usage: k2findcampaigns-csv [-h] input_filename

Check which objects listed in a CSV table are (or were) observable by NASA's
K2 mission.

positional arguments:
  input_filename  Path to a comma-separated table containing columns
                  'ra,dec,kepmag' (decimal degrees) or 'name'.

optional arguments:
  -h, --help      show this help message and exit
```


### K2inMicrolensRegion

Finally, this package adds the `K2inMicrolensRegion` tool to check if a
celestial coordinate is inside the 3-megapixel superstamp region
that has been allocated to the [Campaign 9 microlensing experiment](http://keplerscience.arc.nasa.gov/k2-c9.html).
The stamp covers a large, ~contiguous region towards the Galactic Bulge.
```
$ K2inMicrolensRegion --help
usage: K2inMicrolensRegion [-h] ra dec

Check if a celestial coordinate is inside the K2C9 microlensing superstamp.

positional arguments:
  ra          Right Ascension in decimal degrees (J2000).
  dec         Declination in decimal degrees (J2000).

optional arguments:
  -h, --help  show this help message and exit
```


## Attribution

`K2fov` was created by Fergal Mullally, Thomas Barclay, and Geert Barentsen
for NASA's Kepler/K2 Guest Observer Office.
If this tool aided your research, please cite it using the [DOI identifier](https://zenodo.org/record/44283) or the following BibTeX entry:
```
@misc{fergal_mullally_2016_44283,
  author       = {Fergal Mullally and
                  Thomas Barclay and
                  Geert Barentsen},
  title        = {v3.0.1},
  month        = jan,
  year         = 2016,
  doi          = {10.5281/zenodo.44283},
  url          = {http://dx.doi.org/10.5281/zenodo.44283}
}
```
