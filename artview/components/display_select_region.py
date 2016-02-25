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
from ..core.points import Points, write_points_csv, read_points_csv


class DisplaySelectRegion(Component):
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
        #args, independent = _SelectRegionStart().startDisplay()
        # XXX _SelectRegionStart need updating
        return self(parent=parent), False

    def __init__(self, VplotAxes=None, VpathInteriorFunc=None, Vfield=None,
                 name="DisplaySelectRegion", parent=None):
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
            Parent instance to associate to DisplaySelectRegion instance.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        Notes
        -----
        '''
        super(DisplaySelectRegion, self).__init__(name=name, parent=parent)
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

#        self.ax = display.getPlotAxis()
#        self.statusbar = display.getStatusBar()
#        self.fig = self.ax.get_figure()
#        self.getPathInteriorValues = display.getPathInteriorValues
#        self.getField = display.getField
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
        self.verts = []
        self.poly = []

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
                self.poly.append(ax.add_line(line))
                self.previous_point = [x, y]
                self.verts.append([x, y])
                self.fig.canvas.draw()

    def button_press_callback(self, event):
        '''
        Grab the data when line is drawn.
        If shape is closed, then compile points within.
        '''
        if event.inaxes:
            x, y = event.xdata, event.ydata
            ax = event.inaxes
            if event.button == 1:  # If you press the right button
                if self.line is None:  # if there is no line, create a line
                    self.line = Line2D([x, x], [y, y], marker='o')
                    self.start_point = [x, y]
                    self.previous_point = self.start_point
                    self.verts.append([x, y])
                    self.poly.append(ax.add_line(self.line))
                    self.fig.canvas.draw()
                # add a segment
                else:  # if there is a line, create a segment
                    self.line = Line2D([self.previous_point[0], x],
                                       [self.previous_point[1], y],
                                       marker='o')
                    self.previous_point = [x, y]
                    self.verts.append([x, y])
                    self.poly.append(event.inaxes.add_line(self.line))
                    self.fig.canvas.draw()

            # Close the loop by double clicking and create a table
            elif event.button == 3 and self.line is not None:
                # close the loop
                self.line.set_data(
                    [self.previous_point[0], self.start_point[0]],
                    [self.previous_point[1], self.start_point[1]])
                self.poly.append(ax.add_line(self.line))
                self.fig.canvas.draw()
                self.line = None
                path = Path(self.verts)

                # Inform via status bar
                #self.statusbar.showMessage("Closed Region")

                # Create Points object
                func = self.VpathInteriorFunc.value
                if func is not None:
                    points = func(path)
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
        self.buttonViewTable = QtGui.QPushButton('View Tabular Data', self)
        self.buttonViewTable.setToolTip("View Region Data in popup window")
        self.buttonOpenTable = QtGui.QPushButton('Open Tabular Data', self)
        self.buttonOpenTable.setToolTip("Open a Region Data CSV file")
        self.buttonSaveTable = QtGui.QPushButton('Save Tabular Data', self)
        self.buttonSaveTable.setToolTip("Save a Region Data CSV file")
        self.buttonStats = QtGui.QPushButton('Stats', self)
        self.buttonStats.setToolTip("Show basic statistics of selected Region")
        self.buttonHist = QtGui.QPushButton('Plot Histogram', self)
        self.buttonHist.setToolTip("Plot histogram of selected Region")
        self.buttonApplyMask = QtGui.QPushButton('Mask Region', self)
        self.buttonApplyMask.setToolTip("Apply filter mask to selected Region")
        self.buttonRestoreMask = QtGui.QPushButton('Restore Mask', self)
        self.buttonRestoreMask.setToolTip("Restore the original data mask")
        self.buttonResetSelectRegion = QtGui.QPushButton('Reset Region', self)
        self.buttonResetSelectRegion.setToolTip("Clear the Region")
        self.saveButton = QtGui.QPushButton("Save File", self)
        self.saveButton.setToolTip("Save modified radar instance to cfradial file")
        self.buttonHelp = QtGui.QPushButton('Help', self)
        self.buttonHelp.setToolTip("About using DisplaySelectRegion")
        self.buttonViewTable.clicked.connect(self.viewTable)
        self.buttonOpenTable.clicked.connect(self.openTable)
        self.buttonSaveTable.clicked.connect(self.saveTable)
        self.buttonStats.clicked.connect(self.displayStats)
        self.buttonHist.clicked.connect(self.showHist)
        self.buttonApplyMask.clicked.connect(self.applyMask)
        self.buttonRestoreMask.clicked.connect(self.restoreMask)
        self.buttonResetSelectRegion.clicked.connect(self.resetSelectRegion)
        self.saveButton.clicked.connect(self.saveRadar)
        self.buttonHelp.clicked.connect(self._displayHelp)

        # Create functionality buttons
        self.rBox_layout.addWidget(self.buttonViewTable)
        self.rBox_layout.addWidget(self.buttonOpenTable)
        self.rBox_layout.addWidget(self.buttonSaveTable)
        self.rBox_layout.addWidget(self.buttonStats)
        self.rBox_layout.addWidget(self.buttonHist)
        self.rBox_layout.addWidget(self.buttonApplyMask)
        self.rBox_layout.addWidget(self.buttonRestoreMask)
        self.rBox_layout.addWidget(self.buttonResetSelectRegion)
        self.rBox_layout.addWidget(self.saveButton)
        self.rBox_layout.addWidget(self.buttonHelp)

    def _displayHelp(self):
        ''' Launch pop-up help window.'''
        text = (
            "<b>Using the Display Region of Interest (DisplaySelectRegion) Tool</b><br><br>"
            "<i>Purpose</i>:<br>"
            "Draw a path in the display window using the Mouse.<br><br>"
            "<i>Functions</i>:<br>"
            " Primary Mouse Button (e.g. left button)- add vertex<br>"
            " Hold button to draw free-hand path<br>"
            " Secondary Button (e.g. right button)- close path<br><br>"
            "A message 'Closed Region' appears in status bar when "
            "boundary is properly closed.<br><br>"
            "WARNING: By saving the file, the mask associated with the data "
            "values may be modfidied. The data itself does not change.<br>"
            )
        common.ShowLongText(text)

    def viewTable(self):
        '''View a Table of Region points.'''
        # Check that data has been selected or loaded
        if self.Vpoints.value is not None:
            # Instantiate Table
            self.table = common.CreateTable(self.Vpoints.value)
            self.table.display()
            # Show the table
            self.table.show()
        else:
            common.ShowWarning("Please select or open Region first")

    def saveTable(self):
        '''Save a Table of SelectRegion points to a CSV file.'''
        points = self.Vpoints.value
        if points is not None:
            fsuggest = ('SelectRegion_' + self.Vfield.value + '_' +
                str(points.axes['x_disp']['data'][:].mean()) + '_' +
                str(points.axes['y_disp']['data'][:].mean())+'.csv')
            path = QtGui.QFileDialog.getSaveFileName(
                self, 'Save CSV Table File', fsuggest, 'CSV(*.csv)')
            if not path.isEmpty():
                write_points_csv(path, points)
        else:
            common.ShowWarning("No gate selected, no data to save!")

    def openTable(self):
        '''Open a saved table of SelectRegion points from a CSV file.'''
        path = QtGui.QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV(*.csv)')
        if path == '':
            return
        points = read_points_csv(path)
        self.Vpoints.change(points)

    def resetSelectRegion(self):
        '''Clear the SelectRegion lines from plot and reset things.'''
        if self.poly:
            for i in xrange(len(self.poly)):
                try:
                    self.poly[i].remove()
                except:
                    pass

            # Redraw to remove the lines and reinitialize variable
            self.fig.canvas.draw()

            # Renew region variables, etc.
            self._initialize_SelectRegion_vars()
        #self.statusbar.showMessage("Select Region with Mouse")
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

    def displayStats(self):
        '''Calculate basic statistics of the SelectRegion list.'''
        from ..core import common
        if self.Vpoints.value is None:
            common.ShowWarning("Please select Region first")
        else:
            points = self.Vpoints.value
            field = list(points.fields.keys())[0]
            SelectRegionstats = common._array_stats(
                points.fields[field]['data'])
            text = "<b>Basic statistics for the selected Region</b><br><br>"
            for stat in SelectRegionstats:
                text += ("<i>%s</i>: %5.2f<br>" %
                         (stat, SelectRegionstats[stat]))
            self.statdialog, self.stattext = common.ShowLongText(text,
                                                                 modal=False)

    def showHist(self):
        '''Show a histogram plot of the SelectRegion list.'''
        from ..components.plot_simple import PlotDisplay
        if self.Vpoints.value is None:
            common.ShowWarning("Please select Region first")
        else:
            points = self.Vpoints.value
            field = list(points.fields.keys())[0]
            plot = PlotDisplay(
                points.fields[field]['data'], plot_type="hist",
                name="Select Region Histogram")

    def NewPlotAxes(self, variable, strong):
        self.disconnect()
        if self.VplotAxes.value is not None:
            self.fig = self.VplotAxes.value.get_figure()
        self.connect()

    def saveRadar(self):
        '''Open a dialog box to save radar file.'''
        dirIn, fname = os.path.split(self.Vradar.value.filename)
        filename = QtGui.QFileDialog.getSaveFileName(
            self, 'Save Radar File', dirIn)
        filename = str(filename)
        if filename == '' or self.Vradar.value is None:
            print("Vradar is None!")
        else:
            radar = self.Vradar.value
            if self.Vgatefilter.value is not None:
                radar = radar.extract_sweeps(range(radar.nsweeps))
                for field in radar.fields.keys():
                    radar.fields[field]['data'].mask = np.logical_or(
                        self.Vgatefilter.value._gate_excluded,
                        radar.fields[field]['data'].mask)
            #self.Vradar.update(True)
            pyart.io.write_cfradial(filename, radar)
            print("Saved %s" % (filename))

    ######################
    #   Filter Methods   #
    ######################

    def restoreMask(self):
        '''Remove applied filter by restoring original mask'''
        if self.Vgatefilter.value is not None:
            self.Vgatefilter.value.include_all()
            self.Vgatefilter.update(True)
            print(np.sum(self.Vgatefilter.value._gate_excluded))

    def applyMask(self):
        '''Mount Options and execute
        :py:func:`~pyart.filters.GateFilter`.
        Mask the selected points.
        Vgatefilter is updated, strong or weak depending on overwriting old fields.
        '''
        mask_ray = self.Vpoints.value.axes['ray_index']['data'][:]
        mask_range = self.Vpoints.value.axes['range_index']['data'][:]

        if self.Vgatefilter.value is None:
            if self.Vradar.value is None:
                print("Error can not creat mask from none radar")
                return
            gatefilter = pyart.filters.GateFilter(self.Vradar.value)
            mask = gatefilter.gate_excluded
            mask[mask_ray, mask_range] = True
            gatefilter._merge(mask, 'or', True)
            self.Vgatefilter.change(gatefilter)
        else:
            mask = self.Vgatefilter.value.gate_excluded
            mask[mask_ray, mask_range] = True
            self.Vgatefilter.value._merge(mask, 'or', True)
            self.Vgatefilter.update()

        print(np.sum(mask))
        print(np.sum(self.Vgatefilter.value._gate_excluded))

class _SelectRegionStart(QtGui.QDialog):
    '''
    Dialog Class for graphical start of SelectRegion, to be used in guiStart.
    '''

    def __init__(self):
        '''Initialize the class to create the interface.'''
        super(_SelectRegionStart, self).__init__()
        self.result = {"display": None}
        self.layout = QtGui.QGridLayout(self)
        # set window as modal
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.setupUi()

    def chooseDisplay(self):
        item = VariableChoose(
            compSelect=True, varSelect=False).chooseVariable()
        if item is None:
            return
        else:
            self.result["display"] = item[1]

    def setupUi(self):

        self.displayCombo = QtGui.QComboBox()
        self.layout.addWidget(QtGui.QLabel("Select display"), 0, 0)
        self.layout.addWidget(self.displayCombo, 0, 1, 1, 3)
        self.fillCombo()

        self.name = QtGui.QLineEdit("SelectRegion")
        self.layout.addWidget(QtGui.QLabel("name"), 1, 0)
        self.layout.addWidget(self.name, 1, 1, 1, 3)

        self.independent = QtGui.QCheckBox("Independent Window")
        self.independent.setChecked(True)
        self.layout.addWidget(self.independent, 2, 1, 1, 1)

        self.closeButton = QtGui.QPushButton("Start")
        self.closeButton.clicked.connect(self.closeDialog)
        self.layout.addWidget(self.closeButton, 3, 0, 1, 5)

    def fillCombo(self):
        self.displays = []

        for component in componentsList:
            if self._isDisplay(component):
                self.displayCombo.addItem(component.name)
                self.displays.append(component)

    def _isDisplay(self, comp):
        ''' Test if a component is a valid display to be used. '''
        if (hasattr(comp, 'getPlotAxis') and
            hasattr(comp, 'getStatusBar') and
            hasattr(comp, 'getField') and
            hasattr(comp, 'getRadar') and
            hasattr(comp, 'getPathInteriorValues')
            ):
            return True
        else:
            return False

    def closeDialog(self):
        self.done(QtGui.QDialog.Accepted)

    def startDisplay(self):
        self.exec_()

        self.result['name'] = str(self.name.text())
        self.result["display"] = self.displays[
            self.displayCombo.currentIndex()]
        print((self.result['name']))

        return self.result, self.independent.isChecked()
