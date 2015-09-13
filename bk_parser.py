"""
parser.py

Parse the input code from execution program.
"""

import argparse

# Get the version
f = open("version", "r")
NAME = f.readline().strip()
VERSION = f.readline().strip()
f.close()


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

    igroup = parser.add_argument_group(
        title="Set input platform, optional",
        description=("Ingest method for various platfoms can be chosen. "
                     "If not chosen, an assumption of a ground-based "
                     "platform is made. "
                     "The following flags may be used to display"
                     "RHI or airborne sweep data."
                     ))

    igroup.add_argument('--airborne', action='store_true',
                        help='Airborne radar file')

    igroup.add_argument('--rhi', action='store_true',
                        help='RHI scan')

    igroup.add_argument('-v', '--version', action='version',
                        version='ARTview version %s' % (VERSION))

    # Directory argument now optional
    igroup.add_argument('-d', '--directory', type=str,
                        help='directory to open', default='./')
    igroup.add_argument('-f', '--field', type=str,
                        help='field to show', default='reflectivity')

    # Parse the args
    args = parser.parse_args(argv[1::])
    # Check if there is an input directory
    if args.directory:
        fDirIn = args.directory
    else:
        fDirIn = "./"

    # Set airborne flag off and change if airborne called
    airborne, rhi = False, False
    if args.airborne:
        airborne = True
    if args.rhi:
        rhi = True

    return args.directory, args.field
