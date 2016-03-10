
Installing ARTview
==================

## Install

The easiest method for installing ARTview is to use the conda packages from
the latest release.  To do this you must download and install
`Anaconda <http://continuum.io/downloads>`_ or
`Miniconda <http://continuum.io/downloads>`_.
Then use the following command in a terminal or command prompt to install
the latest version of ARTview::

    conda install -c jjhelmus artivew

To update an older version of ARTview to the latest release use::

    conda update -c jjhelmus ARTview

If you do not wish to use Anaconda or Miniconda as a Python environment or want
to use the latest, unreleased version of ARTview see the section below on
**Installing from source**.

## Installing from source

Installing ARTview from source is the only way to get the latest updates and
enhancement to the software that have not yet made it into a release.
The latest source code for ARTview can be obtained from the GitHub repository,
https://github.com/nguy/ARTview.  Either download and unpack the
`zip file <https://github.com/nguy/ARTview/archive/master.zip>`_ of
the source code or use git to checkout the repository::

    git clone https://github.com/nguy/ARTview.git

To install in your home directory, use::

    python setup.py install --user

To install for all users on Unix/Linux::

    python setup.py build
    sudo python setup.py install

If you prefer to use ARTview without installing, simply add the this path to
your PYTHONPATH (directory or with a .pth file) and compile the extension
in-place.

    python setup.py build_ext -i

## Dependencies
[Py-ART](https://github.com/ARM-DOE/pyart) >= 1.6

[matplotlib](http://matplotlib.org) >= 1.1.0

[Basemap](http://matplotlib.org/basemap) >= 0.99

[PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/intro) >= 4.6

Make sure that `matplotlib` is loading `PyQt4` as backend, for testing that execute `python test/qt.py`.

It is recommended to keep your Py-ART package updated, as new features may rely
upon new code in Py-ART.

Also for a more smooth user experience we recomend to [configure pyart](http://arm-doe.github.io/pyart-docs-travis/user_reference/generated/pyart.load_config.html#pyart.load_config)
to match the kind of files used as well as persornal preferences.

Developed on Python 2.7.7 and 2.7.9 :: Anaconda 2.0.1 and 2.1.0

ARTview has been tested on:
MacOSX 10.9.4, 10.10.2, 10.10.4
Linux Debian (Jessie)
Linux Red Hat (RHEL6)