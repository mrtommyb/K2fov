#! /usr/bin/env python
# A simple script that will call the K2fov.K2onSilicon() function
import sys

try:
    from K2fov.K2onSilicon import K2onSilicon_main
except ImportError:
    print('You need K2fov installed: pip install K2fov')
    sys.exit(1)

if __name__ == '__main__':
    K2onSilicon_main()
