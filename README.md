K2fov
======
Check whether targets are in the field of view of K2

install with
```bash
pip install K2fov
```
if you have a previous version you will need to use
```bash
pip install K2fov --upgrade
```

You'll need a modern version of Python (I've only tested this on 2.7.5) and a relatively new version of numpy (I've tested this on 1.8).

The simplist thing to do is to have a CSV file with
RA_degrees, Dec_degrees, Kepmag
Do not use a header. For example

```bash
178.19284, 1.01924, 13.2
171.14213, 5.314616, 11.3
```

then you can do
```bash
python -c 'import K2fov; K2fov.K2onSilicon("mytargetlist.csv",1)'
```
Where mytargetlist.csv is your CSV file and 1 is the K2 Campaign number.
Campaign number must be 0 thru 7. Once we decide on Campaign 8+ pointing I'll update the code.

Running the code wil output a file with the three input columns and an additional column with either [0,1,2].<br>
0 = Not observable<br>
1 = Close to focal plane, worth including in a proposal<br>
2 = Target is in the K2 field of view<br>

The code will also make an image showing where the targets fall.

If you want to run simple script then you can run
```bash
python runK2onSilicon.py mytargetlist.csv campaignNumber
```
replace campaignNumber with 0, 1, 2 etc. You can also make the code executable and then just
```bash
./runK2onSilicon.py mtargetlist.csv campaignNumber
```

