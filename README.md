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
    
    Change scaling interactively.  Both by limits popup window or by using the
    the mouse to zoom in/out or pan image.
    
    Modify title and units, and save image easily via drop down menu.
    
  
## Installation
Currently it is a standalone executable python script, but may eventually be wrapped into PyArt after maturation.
See dependencies below.

## Usage

```python
python artview.py -d /some/directory/you/want/to/point/to
```

The file can also be made executable by
```python
chmod +x artview.py
```

Then it can be run by calling :
```python
artview.py -d /some/directory/you/want/to/point/to
```

To see the command line options:
```python
artview.py -h
```

To plot an RHI formatted file, you can use the --rhi flag:
```python
artview.py --rhi -d /some/directory/with/RHI/files
```

To plot airborne sweep data, you can use the --airborne flag:
```python
artview.py --airborne -d /some/directory/with/airbrone/sweep/files
```

ARTview should be able to recognize RHI and airborne files, though switching 
between scan types has not been fully worked out yet.

The default startup uses radar reflectivity and checks for a few common names.
If you find a file with a field that does not load, let me know and I can add it
to the list.

You can make publication quality images.
Modify the title and/or units if you'd like:
![Screenshot2](https://github.com/nguy/artview/blob/master/ARTView_Screenshot_title_unit.png)

Now you can save the image simply from the menubar.

File -> Save Image (Or Ctrl+s on linux, Cmd+S on MacOS)

## Dependencies
[Py-Art](https://github.com/ARM-DOE/pyart)

[matplotlib](http://matplotlib.org)

[PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/intro) or [TkInter](https://wiki.python.org/moin/TkInter) 

Note that the TkInter version is an older deprecated version of the code.

Developed on Python 2.7.7 and 2.7.9 :: Anaconda 2.0.1 and 2.1.0
MacOSX 10.9.4 and 10.10.2

##Author list

Nick Guy (nick.guy@uwyo.edu)

Timothy Lang 

Paul Hein

NOTE:: This is open source software.  Contributions are very welcome, though this is not my primary project.  In addition it needs to be stated that no responsibility is taken by the author for any adverse effects.

## Caveats
There has not been extensive testing, but seems reasonably stable.

The data structure used to load can cause lag time, please be patient.


