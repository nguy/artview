ARTview
=======

ARM Radar Toolkit Viewer

ARTview is an interactive viewing browser that uses the [Py-Art](https://github.com/ARM-DOE/pyart) toolkit.
It allows one to easily scroll through a directory of weather radar data files 
and visualize the data.  All file types available in PyArt can be opened with
the ARTview browser.

![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.27358.svg)](http://dx.doi.org/10.5281/zenodo.27358)

![Screenshot](https://github.com/nguy/artview/blob/master/ARTView_Screenshot.png)

With ARTview you can:

    Dynamically switch fields (variables) and tilt angles via drop down menu.

    Dynamically switch tilt angle via radio button selection.  Also easily change 
    by using the up/down arrow keys.

    Browse a directory by advancing with drop down "Next" and "Previous" menus or 
    by arrow left/right key.

    View ground-based or (some) airborne radar files.

    View PPI, sector or RHI type file scans.

    Change display parametets such as scaling, title, units labels, colormap,  
    and add range rings.

    Save output images from a drop-down menu (Or Ctrl+s on linux, Cmd+S on MacOS)

    A toolbox which allows Zooming/Paning, find point values, select regions,
    interface with PyArt routines and select a custom tools a user creates.

    The default two windows can be configured to share parameters or operate independently.

## Links
[Code repository](https://github.com/nguy/artview)

[Documentation](https://rawgit.com/nguy/artview/master/docs/build/html/index.html)

[Issues](https://github.com/nguy/artview/issues)

[Py-ART](https://github.com/ARM-DOE/pyart)

## News
ARTView has become and installable package!
It is still undergoing further functionality development, so keep an eye out for new
features.  It has performed well in internal testing, but we're sure there are bugs in
there and we appreciate your help in finding and addressing them.

The single stream, original version is still available in the scripts directory. It is 
much more limited in scope than the full version.
The other code should not have any effect on it's useage.

## Installation
```python
python setup.py install
```

or for a single user install
```python
python setup.py install --user
```

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

To see the command line options:
```python
artview -h
```

ARTview should be able to recognize and correctly handle PPI, RHI and airborne files.

The default startup uses radar reflectivity and checks for a few common names.
If you find a file with a field that does not load, let us know and we can add it
to the list.

## Dependencies
[Py-Art](https://github.com/ARM-DOE/pyart) >= 1.5

[matplotlib](http://matplotlib.org) >= 1.1.0

[Basemap](http://matplotlib.org/basemap) >= 0.99

[PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/intro) >= 4.6

An old unsupported and limited version can be found in the scripts directory and uses
[TkInter](https://wiki.python.org/moin/TkInter) .

Developed on Python 2.7.7 and 2.7.9 :: Anaconda 2.0.1 and 2.1.0

ARTView has been tested on:
MacOSX 10.9.4, 10.10.2, 10.10.4
Linux Debian (Jessie)
Linux Red Hat (RHEL6)

##Contributors

Anderson Gama

Nick Guy (nick.guy@uwyo.edu)

Paul Hein

Timothy Lang

NOTE:: This is open source software.  Contributions are very welcome, though this is not any of our primary project.  In addition it needs to be stated that no responsibility is taken by the author for any adverse effects.

## Caveats
There has not been extensive testing, but seems reasonably stable.
We are always looking for feedback.

It is  **strongly** encouraged to use Python 2.7 or above. There are minor issues with 
Python 2.6 operability. Some are taken care of with internal tests, however we do not
intend to continue support for 2.6 for long.

Please contact Nick Guy at above email or preferably open an [Issue](https://github.com/nguy/artview/issues) with any problems you encounter.
