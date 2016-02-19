"""
select_region.py

Class to select a Region of interest in Display.
"""
# Load the needed packages
import numpy as np
import pyart
import os

from matplotlib.path import Path
from matplotlib.lines import Line2D
import csv

from ..core import (Variable, Component, common, VariableChoose,
                    componentsList, QtGui, QtCore)
from ..core.points import Points


class SelectRegion(Component):
    '''
    Select a Region of Interest.

    This tool allows the user to draw a path in the display window using
    the mouse. The primary mouse button (often the left button) is used
    to select a point. The secondary mouse button (often the right button)
    is used to close the path of interest.

    A straight-sided polygon may be selected by clicking and releasing
    the primary mouse button.
    A curved shape (free-hand drawing) may be drawn by holding down
    the primary mouse button.

    One caveat found is that other tools may interfere with the curved
    shape drawing. If this is the case select the reset file defaults in
    toolbox menu.

    The code modified from:

    https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg00661.html
    '''

    Vpoints = None  #: see :ref:`shared_variable`
    VplotAxes = None  #: see :ref:`shared_variable`
    VpathInteriorFunc = None  #: see :ref:`shared_variable`
    Vgatefilter = None  #: see :ref:`shared_variable`
    Vradar = None  #: see :ref:`shared_variable`
    Vfield = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        # args, independent = _SelectRegionStart().startDisplay()
        kwargs, independent = \
            common._SimplePluginStart("SelectRegion").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, VplotAxes=None, VpathInteriorFunc=None, Vfield=None,
                 name="SelectRegion", parent=None):
        '''
        Initialize the class to select an Region of Interest on display.

        Parameters
        ----------
        VplotAxes : :py:class:`~artview.core.core.Variable` instance
            Plot axes signal variable. If None start new one with None.
        VpathInteriorFunc : :py:class:`~artview.core.core.Variable` instance
            py:func:`~artview.components.RadarDisplay.getPathInteriorValues`
            signal variable. If None start new one with None.
        Vfield : :py:class:`~artview.core.core.Variable` instance
            Field signal variable. If None start new one with empty string.
        name : string
            Window name.
        parent : PyQt instance
            Parent instance to associate to SelectRegion instance.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        Notes
        -----
        '''
        super(SelectRegion, self).__init__(name=name, parent=parent)
        self.Vpoints = Variable(None)
        self.Vgatefilter = Variable(None)
        self.Vradar = Variable(None)
        if VplotAxes is None:
            self.VplotAxes = Variable(None)
        else:
            self.VplotAxes = VplotAxes
        self.fig = None
        if VpathInteriorFunc is None:
            self.VpathInteriorFunc = Variable(None)
        else:
            self.VpathInteriorFunc = VpathInteriorFunc
        if Vfield is None:
            self.Vfield = Variable("")
        else:
            self.Vfield = Vfield
        self.sharedVariables = {
            "VplotAxes": self.NewPlotAxes,
            "Vgatefilter": None,
            "Vradar": None,
            "VpathInteriorFunc": None,
            "Vfield": None,
            "Vpoints": None}
        # Connect the components
        self.connectAllVariables()

#        self.statusbar = display.getStatusBar()
        self.columns = ("X", "Y", "Azimuth", "Range", "Value",
                        "Az Index", "R Index")
#        self.statusbar.showMessage("Select Region with Mouse")

        # Initialize the variables and GUI
        self._initialize_SelectRegion_vars()
        self.CreateSelectRegionWidget()
        self.NewPlotAxes(None, False)
        self.show()

    def _initialize_SelectRegion_vars(self):
        '''Initialize variables to be used in SelectRegion selection.'''
        self.previous_point = []
        self.start_point = []
        self.end_point = []
        self.line = None
        self.verts = [[]]
        self.polys = [[]]
        self.paths = []

    def motion_notify_callback(self, event):
        '''Create the shape in plot area.'''
        if event.inaxes:
            ax = event.inaxes
            x, y = event.xdata, event.ydata
            if event.button is None and self.line is not None:
                # Move line around
                self.line.set_data([self.previous_point[0], x],
                                   [self.previous_point[1], y])
                self.fig.canvas.draw()
            elif event.button == 1:  # Free Hand Drawing
                line = Line2D([self.previous_point[0], x],
                              [self.previous_point[1], y])
                self.previous_point = [x, y]
                self.verts[-1].append([x, y])
                self.polys[-1].append(ax.add_line(line))
                self.fig.canvas.draw()

    def button_press_callback(self, event):
        '''
        Grab the data when line is drawn.
        If shape is closed, then compile points within.
        '''
        # test for double click support (matplotlib > 1.2)
        db_support = 'dblclick' in dir(event)
        if event.inaxes:
            x, y = event.xdata, event.ydata
            ax = event.inaxes
            # If you press the right button (single)
            if event.button == 1 and (not db_support or not event.dblclick):
                if self.line is None:  # if there is no line, create a line
                    self.line = Line2D([x, x], [y, y], marker='o')
                    self.start_point = [x, y]
                    self.previous_point = self.start_point
                    self.verts[-1].append([x, y])
                    self.polys[-1].append(ax.add_line(self.line))
                    self.fig.canvas.draw()
                # add a segment
                else:  # if there is a line, create a segment
                    self.line = Line2D([self.previous_point[0], x],
                                       [self.previous_point[1], y],
                                       marker='o')
                    self.previous_point = [x, y]
                    self.verts[-1].append([x, y])
                    self.polys[-1].append(event.inaxes.add_line(self.line))
                    self.fig.canvas.draw()

            # Close the loop by double clicking and create a table
            # (or single right click)
            elif ((event.button == 1 and db_support and event.dblclick) or
                  event.button == 3 and self.line is not None):
                # close the loop
                self.line.set_data(
                    [self.previous_point[0], self.start_point[0]],
                    [self.previous_point[1], self.start_point[1]])
                self.verts[-1].append(self.start_point)
                self.fig.canvas.draw()
                self.line = None
                path = Path(self.verts[-1])
                self.paths.append(path)
                self.verts.append([])
                self.polys.append([])

                # Inform via status bar
                # self.statusbar.showMessage("Closed Region")

                # Create Points object
                self.update_points()

    def update_points(self):
        '''Create points object from paths list.'''
        func = self.VpathInteriorFunc.value
        if func is not None:
            points = func(self.paths)
            if points is not None:
                self.Vpoints.change(points)

    def connect(self):
        '''Connect the SelectRegion instance.'''
        if self.fig is not None:
            self.motionID = self.fig.canvas.mpl_connect(
                'motion_notify_event', self.motion_notify_callback)
            self.buttonID = self.fig.canvas.mpl_connect(
                'button_press_event', self.button_press_callback)

    def disconnect(self):
        '''Disconnect the SelectRegion instance.'''
        if self.fig is not None:
            self.fig.canvas.mpl_disconnect(self.motionID)
            self.fig.canvas.mpl_disconnect(self.buttonID)

    def CreateSelectRegionWidget(self):
        '''Create a widget to access SelectRegion tools.
        Open and Save Table methods borrowed from:
        http://stackoverflow.com/questions/12608835/writing-a-qtablewidget-to-a-csv-or-xls
        '''
        self.SelectRegionbox = QtGui.QGroupBox("Region of Interest Selection")
        self.rBox_layout = QtGui.QVBoxLayout(self.SelectRegionbox)
        self.SelectRegionbox.setLayout(self.rBox_layout)
        self.setCentralWidget(self.SelectRegionbox)

        # Add buttons for functionality
        self.buttonResetSelectRegion = QtGui.QPushButton('Reset Region', self)
        self.buttonResetSelectRegion.setToolTip("Clear the Region")
        self.buttonHelp = QtGui.QPushButton('Help', self)
        self.buttonHelp.setToolTip("About using SelectRegion")
        self.buttonRemovePoly = QtGui.QPushButton('Remove Polygon', self)
        self.buttonRemovePoly.setToolTip("Remove last Polygon")
        self.buttonRemoveVertex = QtGui.QPushButton('Remove Vertex', self)
        self.buttonRemoveVertex.setToolTip("Remove last Vertex")
        self.buttonResetSelectRegion.clicked.connect(self.resetSelectRegion)
        self.buttonHelp.clicked.connect(self._displayHelp)
        self.buttonRemovePoly.clicked.connect(self.removePolygon)
        self.buttonRemoveVertex.clicked.connect(self.removeVertex)

        # Create functionality buttons
        self.rBox_layout.addWidget(self.buttonResetSelectRegion)
        self.rBox_layout.addWidget(self.buttonHelp)
        self.rBox_layout.addWidget(self.buttonRemovePoly)
        self.rBox_layout.addWidget(self.buttonRemoveVertex)

    def removePolygon(self):
        '''remove last polygon from the list if not drawing. if drawing
        remove current draw.'''
        if self.line is None:
            if self.paths:
                self.paths.pop()
            poly = self.polys.pop(-2)
            self.verts.pop(-2)
            for line in poly:
                line.remove()
        else:
            self.line = None
            self.verts[-1] = []
            poly = self.polys.pop()
            for line in poly:
                line.remove()
            self.polys.append([])

        self.fig.canvas.draw()
        self.update_points()

    def removeVertex(self):
        '''remove last vertex from the list.'''
        if self.line is None:
            if self.paths:
                self.paths.pop()
                self.polys.pop()
                self.verts.pop()
                self.verts[-1].pop()
                self.line = self.polys[-1][-1]
                self.previous_point = self.verts[-1][-1]
                self.start_point = self.verts[-1][0]
        else:
            self.verts[-1].pop()
            self.polys[-1].pop().remove()
            if self.polys[-1]:
                self.line = self.polys[-1][-1]
                self.previous_point = self.verts[-1][-1]
            else:
                self.removePolygon()
        self.fig.canvas.draw()
        self.update_points()

    def _displayHelp(self):
        ''' Launch pop-up help window.'''
        text = (
            "<b>Using the Region of Interest (SelectRegion) Tool</b><br><br>"
            "<i>Purpose</i>:<br>"
            "Draw a path in the display window using the Mouse.<br><br>"
            "<i>Functions</i>:<br>"
            " Primary Mouse Button (e.g. left button)- add vertex<br>"
            " Hold button to draw free-hand path<br>"
            " Secondary Button (e.g. right button)- close path<br><br>"
            "A message 'Closed Region' appears in status bar when "
            "boundary is properly closed.<br><br>"
            "On the basic workings of the selection, a "
            "<a href='https://youtu.be/Hcz2YtpXBdM'>Video Tutorial</a> "
            "has been created.<br>"
            "For changing which display the SelectRegion is linked to, a "
            "<a href='https://youtu.be/cd4_OBJ6HnA'>Video Tutorial</a> "
            "has been created.<br>"
            "If using SelectRegion in 'extract_points' mode, a "
            "<a href='https://youtu.be/iWBFSN6Thbw'>Video Tutorial</a> "
            "has been created.<br>"
            )
        common.ShowLongTextHyperlinked(text)

    def resetSelectRegion(self):
        '''Clear the SelectRegion lines from plot and reset things.'''
        if self.polys:
            for poly in self.polys:
                for i in xrange(len(poly)):
                    try:
                        poly[i].remove()
                    except:
                        pass

            # Redraw to remove the lines and reinitialize variable
            self.fig.canvas.draw()

            # Renew region variables, etc.
            self._initialize_SelectRegion_vars()
        # self.statusbar.showMessage("Select Region with Mouse")
        else:
            print("No Region Selection to clear")
        self.Vpoints.change(None)

    def closeEvent(self, QCloseEvent):
        '''Reimplementations to remove from components list.'''
        try:
            self.resetSelectRegion()
        except:
            import warnings
            import traceback
            error = traceback.format_exc()
            warnings.warn(
                "Reseting SelectRegion fails with following error\n" + error)
        self.disconnect()
        super(SelectRegion, self).closeEvent(QCloseEvent)

    def NewPlotAxes(self, variable, strong):
        self.disconnect()
        if self.VplotAxes.value is not None:
            self.fig = self.VplotAxes.value.get_figure()
        self.connect()

        if self.VplotAxes.value is not None:
            for poly in self.polys:
                for line in poly:
                    self.VplotAxes.value.add_line(line)
                self.fig.canvas.draw()
