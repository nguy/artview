#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
backgroud.py
"""

# Load the needed packages

import pyart
import numpy as np
from netCDF4 import Dataset
from matplotlib.colors import LightSource
from mpl_toolkits.basemap import shiftgrid, cm

import sys
import os

from ..core import Component, Variable, common, QtGui, QtCore, componentsList


class TopographyBackground(Component):
    '''
    add TopograpyBackground to Display
    '''

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("TopographyBackground").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, VpyartDisplay=None, name="TopographyBackground", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        VpyartDisplay : :py:class:`~artview.core.core.Variable` instance
            pyart Display signal variable. If None start new one with None.
        name : string
            Component name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(TopographyBackground, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        self.layout.addWidget(QtGui.QLabel("Etopo file:"), 0, 0)

        self.lineEdit = QtGui.QLineEdit(
            "http://ferret.pmel.noaa.gov/thredds/dodsC/data/PMEL/etopo5.nc",
            self)
        self.layout.addWidget(self.lineEdit, 0, 1)

        self.searchButton = QtGui.QPushButton("Search")
        self.searchButton.clicked.connect(self.search)
        self.layout.addWidget(self.searchButton, 0, 2)
        self.applyButton = QtGui.QPushButton("Apply")
        self.applyButton.clicked.connect(self.apply)
        self.layout.addWidget(self.applyButton, 0, 3)
        self.current_open = None

        if VpyartDisplay is None:
            self.VpyartDisplay = Variable(None)
        else:
            self.VpyartDisplay = VpyartDisplay

        self.sharedVariables = {"VpyartDisplay": None}

        self.show()

    def search(self):
        '''Open a dialog box to choose file.'''

        filename = QtGui.QFileDialog.getOpenFileName(
            self, 'Choose file', os.getcwd())
        filename = str(filename)
        if filename == '':
            return
        else:
            self.lineEdit.setText(filename)

    def apply(self):
        common.ShowQuestion
        display = self.VpyartDisplay.value
        if (isinstance(display, pyart.graph.RadarMapDisplay) or
            isinstance(display, pyart.graph.GridMapDisplay)):
            pass
        elif (isinstance(display, pyart.graph.RadarDisplay) or
              isinstance(display, pyart.graph.AirborneRadarDisplay)):
            common.ShowWarning(
                "Topography require a MapDisplay, be sure to "
                "check the 'use MapDisplay' box in the 'Display Options' Menu")
            return
        else:
            common.ShowWarning(
                "Need a pyart display instance, be sure to "
                "link this components (%s), to a radar or grid display" %
                self.name)
            return

        filename = str(self.lineEdit.text())
        if filename != self.current_open:
            if filename.startswith("http"):
                resp = common.ShowQuestion(
                    "Loading a file from the internet may take long." + 
                    " Are you sure you want to continue?")
                if resp != QtGui.QMessageBox.Ok:
                    return
            self.etopodata = Dataset(filename)
            self.current_open = filename

        topoin = np.maximum(0, self.etopodata.variables['ROSE'][:])
        lons = self.etopodata.variables['ETOPO05_X'][:]
        lats = self.etopodata.variables['ETOPO05_Y'][:]
        # shift data so lons go from -180 to 180 instead of 20 to 380.
        topoin,lons = shiftgrid(180.,topoin,lons,start=False)

        # plot topography/bathymetry as an image.

        # create the figure and axes instances.
        # setup of basemap ('lcc' = lambert conformal conic).
        # use major and minor sphere radii from WGS84 ellipsoid.
        m = self.VpyartDisplay.value.basemap
        # transform to nx x ny regularly spaced 5km native projection grid
        nx = int((m.xmax-m.xmin)/500.)+1; ny = int((m.ymax-m.ymin)/500.)+1
        topodat = m.transform_scalar(topoin,lons,lats,nx,ny)
        # plot image over map with imshow.

        # draw coastlines and political boundaries.

        ls = LightSource(azdeg = 90, altdeg = 20)
        # convert data to rgb array including shading from light source.
        # (must specify color map)
        rgb = ls.shade(topodat, cm.GMT_relief)
        im = m.imshow(rgb)

        self.VpyartDisplay.update(strong=False)


class ImageBackground(Component):
    '''
    add TopograpyBackground to Display
    '''

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("ImageBackground").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, VpyartDisplay=None, name="ImageBackground", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        VpyartDisplay : :py:class:`~artview.core.core.Variable` instance
            pyart Display signal variable. If None start new one with None.
        name : string
            Component name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(ImageBackground, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        self.layout.addWidget(QtGui.QLabel("Image file:"), 0, 0)

        self.lineEdit = QtGui.QLineEdit("", self)
        self.layout.addWidget(self.lineEdit, 0, 1, 1, 3)

        self.searchButton = QtGui.QPushButton("Search")
        self.searchButton.clicked.connect(self.search)
        self.layout.addWidget(self.searchButton, 0, 4)
        self.applyButton = QtGui.QPushButton("Apply")
        self.applyButton.clicked.connect(self.apply)
        self.layout.addWidget(self.applyButton, 0, 5)

        self.layout.addWidget(QtGui.QLabel(u"Center (°):"), 1, 0)
        self.x0_lineEdit = QtGui.QLineEdit("",self)
        self.layout.addWidget(self.x0_lineEdit, 1, 1)
        self.y0_lineEdit = QtGui.QLineEdit("",self)
        self.layout.addWidget(self.y0_lineEdit, 1, 2)

        self.layout.addWidget(QtGui.QLabel("Size (km):"), 1, 3)
        self.dx_lineEdit = QtGui.QLineEdit("",self)
        self.layout.addWidget(self.dx_lineEdit, 1, 4)
        self.dy_lineEdit = QtGui.QLineEdit("",self)
        self.layout.addWidget(self.dy_lineEdit, 1, 5)

        if VpyartDisplay is None:
            self.VpyartDisplay = Variable(None)
        else:
            self.VpyartDisplay = VpyartDisplay

        self.VplotAxes = Variable(None)
        self.Vradar = Variable(None)
        self.Vgrid = Variable(None)

        self.sharedVariables = {"VpyartDisplay": None,
                                "VplotAxes": None,
                                "Vradar": self.NewRadar,
                                "Vgrid": self.NewGrid,}

        self.show()

    def search(self):
        '''Open a dialog box to choose file.'''

        filename = QtGui.QFileDialog.getOpenFileName(
            self, 'Choose file', os.getcwd())
        filename = str(filename)
        if filename == '':
            return
        else:
            self.lineEdit.setText(filename)

    def NewRadar(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vradar <artview.core.core.Variable>`.
        '''
        # test for None
        radar = self.Vradar.value
        if radar is not None:
            lat_radar = float(radar.latitude['data'][0])
            lon_radar = float(radar.longitude['data'][0])
            rng = float(radar.range['data'][-1])/1000
            self.x0_lineEdit.setText("%.6f" % lon_radar)
            self.y0_lineEdit.setText("%.6f" % lat_radar)
            self.dx_lineEdit.setText("%.3f" % (2 * rng))
            self.dy_lineEdit.setText("%.3f" % (2 * rng))

    def NewGrid(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vgrid <artview.core.core.Variable>`.
        '''
        # test for None
        grid = self.Vgrid.value
        if grid is not None:
            x = grid.x['data']
            y = grid.y['data']
            projparams = grid.get_projparams()
            lon,lat = pyart.core.cartesian_vectors_to_geographic(
                (x[-1]+x[0])/2, (y[-1]+y[0])/2, projparams)
            self.x0_lineEdit.setText("%.6f" % lon)
            self.y0_lineEdit.setText("%.6f" % lat)
            self.dx_lineEdit.setText("%.3f" % ((x[-1] - x[0])/1000))
            self.dy_lineEdit.setText("%.3f" % ((y[-1] - y[0])/1000))

    def apply(self):
        display = self.VpyartDisplay.value
        if display is None:
            common.ShowWarning(
                "Need a pyart display instance, be sure to "
                "link this components (%s), to a radar or grid display" %
                self.name)
            return
        elif (isinstance(display, pyart.graph.RadarMapDisplay) or
            isinstance(display, pyart.graph.GridMapDisplay) or
            isinstance(display, pyart.graph.RadarDisplay)):
            pass
        else:
            common.ShowWarning(
                "Need a pyart display instance, be sure to "
                "link this components (%s), to a radar or grid display" %
                self.name)
            return

        ax = self.VplotAxes.value
        if ax is None:
            common.ShowWarning(
                "Need a axes instance, be sure to "
                "link this components (%s), to the plot axes a display" %
                self.name)
        import matplotlib.image as mpimg

        img=mpimg.imread(str(self.lineEdit.text()))

        x0 = float(str(self.x0_lineEdit.text()))
        y0 = float(str(self.y0_lineEdit.text()))
        dx = float(str(self.dx_lineEdit.text()))
        dy = float(str(self.dy_lineEdit.text()))
        aspect = ax.get_aspect()
        if isinstance(display, pyart.graph.RadarMapDisplay):
            m = self.VpyartDisplay.value.basemap
            x0, y0 = m(x0,y0)
            dx *= 1000
            dy *= 1000
            im = ax.imshow(img, extent=(x0-dx/2, x0+dx/2, y0-dy/2, y0+dy/2),
                           aspect=aspect)
        elif isinstance(display, pyart.graph.RadarDisplay):
            radar = self.Vradar.value
            lat_radar = float(radar.latitude['data'][0])
            lon_radar = float(radar.longitude['data'][0])
            x0, y0 = pyart.core.geographic_to_cartesian(
                x0, y0, {'proj': 'pyart_aeqd',
                         'lon_0': lon_radar, 'lat_0': lat_radar})
            x0 = x0[0]
            y0 = y0[0]
            im = ax.imshow(img, extent=(x0-dx/2, x0+dx/2, y0-dy/2, y0+dy/2),
                           aspect=aspect)
        elif isinstance(display, pyart.graph.GridMapDisplay):
            m = self.VpyartDisplay.value.basemap
            x0, y0 = m(x0,y0)
            dx *= 1000
            dy *= 1000
            im = ax.imshow(img, extent=(x0-dx/2, x0+dx/2, y0-dy/2, y0+dy/2),
                           aspect=aspect)


        self.VpyartDisplay.update(strong=False)



_plugins = [TopographyBackground, ImageBackground]
