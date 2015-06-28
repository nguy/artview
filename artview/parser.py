"""
parser.py

Parse the input code from execution program.
"""

import argparse

# Get the version
import version
NAME = 'ARTview'
VERSION = version.version


def parse(argv):
    '''
    Parse the input command line.

    Parameters::
    ----------
    argv - string
        Input command line string.

    Notes::
    -----
    Returns directory and field for initialization.
    '''
    parser = argparse.ArgumentParser(
              description="Start ARTview - the ARM Radar Toolkit Viewer.")

    parser.add_argument('-v', '--version', action='version',
                         version='ARTview version %s' % (VERSION))

    #Directory argument now optional
    parser.add_argument('-d', '--directory', type=str, help='directory to open', default='./')
    parser.add_argument('-f', '--field', type=str, help='field to show', default='reflectivity')

    # Parse the args
    args = parser.parse_args(argv[1::])
    # Check if there is an input directory
    if args.directory:
        fDirIn = args.directory
    else: 
        fDirIn = "./"

    return args.directory, args.field

