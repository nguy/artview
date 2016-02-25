ARTview
=======

ARM Radar Toolkit Viewer

ARTview is an interactive GUI viewer that is built on top of the
[Py-ART](https://github.com/ARM-DOE/pyart) toolkit.
It allows one to easily scroll through a directory of weather radar data files
and visualize the data.  All file types available in Py-ART can be opened with
the ARTview browser.

You can interact with data files through "Plugins". Many functions from the Py-ART
package can be selected. In addition, ARTview plugins allow querying data by
selecting regions or points visually.

![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.27358.svg)](http://dx.doi.org/10.5281/zenodo.27358)

![Screenshot](https://github.com/nguy/artview/blob/master/ARTView_Screenshot.png)

ARTview highlights:

    Dynamically switch fields (variables) and tilt angles via drop down menu.

    Dynamically switch tilt angle via radio button selection.  Also easily change
    by using the up/down arrow keys.

    Browse a directory using the FileNavigator menu or left/right arrow keys.

    View surface-based or (some) airborne radar files.

    View (and switch between) PPI, sector or RHI type file scans.

    Change display parametets such as scaling, title, units labels, colormap,
    and add range rings.

    Save output images from a drop-down menu (Or Ctrl+s on linux, Cmd+S on MacOS).

    Use Py-ART auxilary file readers by right clicking a file in the FileList.

    Display toolbox which allows Zooming/Panning, find point values, select regions.

    The default two windows can be configured to share parameters or operate independently.

    Run automated correction routines.

    Hand-edit data files.

    Write your own plugins to use.

## Links
[Code repository](https://github.com/nguy/artview)

[Documentation](https://rawgit.com/nguy/artview/master/docs/build/html/index.html)

[User Forum](https://groups.google.com/forum/#!forum/artview-users)

[Issues](https://github.com/nguy/artview/issues)

[Py-ART](https://github.com/ARM-DOE/pyart)

## News
Some minor bugs have been addressed to improve performance of plugins.
The menu has undergone a facelift to make it easier to understand the tools
in ARTview. More user-friendly interfaces have been deployed to improve the
experience.

A number of editing tools have now been linked (from Py-ART) and developed
internally. There remains further functionality development, so keep an eye
out for new features.
It has performed well in internal testing, but if you find bugs in
there, we appreciate your help in finding and addressing them.

## Tutorials
Paul Hein has put together a [brief introduction](http://radarmet.atmos.colostate.edu/software/artview/).
Anderson Gama has made a [video introduction](https://www.youtube.com/watch?v=iaNoGZTUhg4) to ARTView 1.0
as well as [video tutorials](https://www.youtube.com/watch?v=B_BmYV7GdCA&list=PLCmWx9EHGvfIrvrYSTpHrEqdVVjvKi4SF)
to ARTView 1.2.

## Install

The easiest method for installing ARTView is to use the conda packages from
the latest release.  To do this you must download and install
`Anaconda <http://continuum.io/downloads>`_ or
`Miniconda <http://continuum.io/downloads>`_.
Then use the following command in a terminal or command prompt to install
the latest version of ARTView::

    conda install -c jjhelmus artivew

To update an older version of ARTView to the latest release use::

    conda update -c jjhelmus artview

If you do not wish to use Anaconda or Miniconda as a Python environment or want
to use the latest, unreleased version of ARTView see the section below on
**Installing from source**.

## Installing from source

Installing ARTView from source is the only way to get the latest updates and
enhancement to the software that have not yet made it into a release.
The latest source code for ARTView can be obtained from the GitHub repository,
https://github.com/nguy/artview.  Either download and unpack the
`zip file <https://github.com/nguy/artview/archive/master.zip>`_ of
the source code or use git to checkout the repository::

    git clone https://github.com/nguy/artview.git

To install in your home directory, use::

    python setup.py install --user

To install for all users on Unix/Linux::

    python setup.py build
    sudo python setup.py install


## Usage
Either cd into the installed folder and run:

```python
python artview -d /some/directory/you/want/to/point/to
```

Or it can be run from anywhere with the following:

```python
artview
```

A specific file can be loaded:
```python
artview -F /some/directory/you/want/to/point/to/filename
```

A specific field (e.g. reflectivity) can be loaded:
```python
artview -f 'reflectivity'
```

Use a different start-up script with -s
```python
artview -s radar
```
There are several [predefined scripts](SCRIPTS.md) that you can use, but you
can also [write your own](https://rawgit.com/nguy/artview/master/docs/build/html/script_tutorial.html).

To see other command line options:
```python
artview -h
```

ARTview should be able to recognize and correctly handle PPI, RHI and airborne files.

The default startup uses radar reflectivity and checks for a few common names.
If you find a file with a field that does not load, let us know and we can add it
to the list.


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

ARTView has been tested on:
MacOSX 10.9.4, 10.10.2, 10.10.4
Linux Debian (Jessie)
Linux Red Hat (RHEL6)

It is  **strongly** encouraged to use Python 2.7 or above. There are minor issues with
Python 2.6 operability that keep popping up. We make no guarantees that 2.6 will
work properly.

## User Forum

For questions on the use of ARTView please write in the [mailing list](https://groups.google.com/forum/#!forum/artview-users),
if you found any bug please report in the [Issue](https://github.com/nguy/artview/issues). We are thankful for all feedback.

## Contributors

[Anderson Gama](https://github.com/gamaanderson)

[Nick Guy](https://github.com/nguy)

Paul Hein

Timothy Lang

Jonathan Helmus

## Disclaimer
This is open source software and contributions are very welcome!
This is not a primary project for any of the contributors, so please be patient
if you have questions/suggestions.  In addition it needs to be stated that no
responsibility is taken by the authors for any adverse effects.

## Special Note
Icons used in ```FileNavigator``` were created by oxygenicons (http://www.oxygen-icons.org/)
and distributed at the IconArchive (http://www.iconarchive.com) under
the GNU Lesser General Public License.
