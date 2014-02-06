K2fov
======
Check whether targets are in the field of view of K2

install with
```bash
pip install K2fov
```

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
Campaign number must be either 0 or 1. Once we decide on Campaign 2+ pointing I'll update the code.
