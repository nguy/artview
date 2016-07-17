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


        etopodata = Dataset(str(self.lineEdit.text()))

        topoin = np.maximum(0, etopodata.variables['ROSE'][:])
        lons = etopodata.variables['ETOPO05_X'][:]
        lats = etopodata.variables['ETOPO05_Y'][:]
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



_plugins = [TopographyBackground]
