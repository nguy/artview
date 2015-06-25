ARTview
=======

ARM Radar Toolkit Viewer

ARTview is an interactive viewing browser that uses the [PyArt](https://github.com/ARM-DOE/pyart) toolkit.  
It allows one to easily scroll through a directory of weather radar data files 
and visualize the data.  All file types available in PyArt can be opened with
the ARTview browser.

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
python -m artview
```

The above command will look in the current working directory. Command line options
just like the original exist to specify directory, field, etc.
```python
python -m artview -d /some/directory/you/want/to/point/to
```

To see the command line options:
```python
python -m artview -h
```

To plot an RHI formatted file, you can use the --rhi flag:
```python
python -m artview --rhi -d /some/directory/with/RHI/files
```

To plot airborne sweep data, you can use the --airborne flag:
```python
python -m artview --airborne -d /some/directory/with/airbrone/sweep/files
```

ARTview should be able to recognize RHI and airborne files, though switching 
between scan types has not been fully worked out yet.

The default startup uses radar reflectivity and checks for a few common names.
If you find a file with a field that does not load, let us know and we can add it
to the list.

## Dependencies
[Py-Art](https://github.com/ARM-DOE/pyart)

[matplotlib](http://matplotlib.org)

[PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/intro) or [TkInter](https://wiki.python.org/moin/TkInter) 

Note that the TkInter version is an older deprecated version of the code.

Developed on Python 2.7.7 and 2.7.9 :: Anaconda 2.0.1 and 2.1.0
MacOSX 10.9.4 and 10.10.2

##Contributors

Nick Guy (nick.guy@uwyo.edu)

Timothy Lang 

Paul Hein

Anderson Gama

NOTE:: This is open source software.  Contributions are very welcome, though this is not any of our primary project.  In addition it needs to be stated that no responsibility is taken by the author for any adverse effects.

## Caveats
There has not been extensive testing, but seems reasonably stable.
We are always looking for feedback.


