ARTview
=======

ARM Radar Toolkit Viewer

ARTview is an interactive viewing browser that uses the PyArt toolkit.  
It allows one to easily scroll through a directory of weather radar data files 
and visualize the data.  All file types available in PyArt can be opened with
the ARTview browser.

With ARTview you can:

<<<<<<< HEAD
	Dynamically switch fields (variables) and tilt angles via drop down menu.
	
    Dynamically switch fields (variables) and tilt angles via drop down menu.
    
    Dynamically switch tilt angle by button selection.
    
    Browse a directory by advancing with drop down "Next" and "Previous" menus or by arrow key.
    
    View ground-based or airborne radar.
    
=======
    Dynamically switch fields (variables) and tilt angles via drop down menu.
    Dynamically switch tilt angle by button selection.
    Browse a directory by advancing with drop down "Next" and "Previous" menus or by arrowkey.
    View ground-based or airborne radar.
>>>>>>> 01d2b2eded95a12cc8006b2954136cdc78b5f16a
    View PPI, sector, or RHI scans
  
## Installation
Currently it is a standalone executable python script, but may eventually be wrapped into PyArt after maturation.
No specific installation is required.

## Usage
```python
artview.py /some/directory/you/want/to/point/to
```
To see the command line options:
```python
artview.py -h
```

## Dependencies
[Py-Art](https://github.com/ARM-DOE/pyart)

[matplotlib](http://matplotlib.org)

[TkInter](https://wiki.python.org/moin/TkInter)

Developed on Python 2.7.7 :: Anaconda 2.0.1 
MacOSX 10.9.4

Author: Nick Guy (nick.guy@noaa.gov)

NOTE:: This is open source software.  Contributions are very welcome, though this is not my primary project.  In addition it needs to be state that no responsibility is taken by the author for any adverse effects.
