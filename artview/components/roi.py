"""
roi.py

Class to select a Region of interest in Display.
"""
# Load the needed packages
import numpy as np

from PyQt4 import QtGui, QtCore
from matplotlib.path import Path
from matplotlib.lines import Line2D
import csv

from ..core import Variable, Component, common, VariableChoose


class ROI(Component):
    '''
    Select a Region of Interest: The code modified from
https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg00661.html
    '''

    VroiData = None #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        args, independent = _RoiStart().startDisplay()
        return self(**args), independent

    def __init__(self, display, name="ROI", parent=None):
        '''
        Initialize the class to select an ROI on display.

        Parameters::
        ----------
        display - ARTView Display
            Display instance to associate ROI. Must have following elements:
                * getPlotAxis() - Matplotlib axis instance
                * getStatusBar() - QtGui.QStatusBar
                * getField() - string
                * getPathInteriorValues(Path) - see
                  :py:func:`~artview.components.Display.getPathInteriorValues`

        [Optional]
        name - string
            Window name.
        parent - PyQt instance
            Parent instance to associate to ROI instance.
            If None, then Qt owns, otherwise associated w/ parent PyQt instance

        Notes::
        -----
        '''
        print display, name
        super(ROI, self).__init__(name=name, parent=parent)
        self.VroiData = Variable(None)
        self.sharedVariables = {"VroiData": None}

        # Connect the components
        self.connectAllVariables()

        self.ax = display.getPlotAxis()
        self.statusbar = display.getStatusBar()
        self.fig = self.ax.get_figure()
        self.getPathInteriorValues = display.getPathInteriorValues
        self.getField = display.getField
#        self.display = display
        self.columns = ("X", "Y", "Azimuth", "Range", "Value",
                        "Az Index", "R Index")
        self.statusbar.showMessage("Select Region with Mouse")

        self._initialize_ROI_vars()
#        self._setup_ROI_vars()
        self.CreateROIWidget()
        self.connect()
        self.show()

    def _initialize_ROI_vars(self):
        '''Initialize variables to be used in ROI selection'''
        self.previous_point = []
        self.start_point = []
        self.end_point = []
        self.line = None
        self.verts = []
        self.poly = []

    def _setup_ROI_vars(self):
        '''Setup variables from radar instance for ROI selection'''
        radar = self.Vradar.value  # keep equations clean
        self.az = radar.azimuth['data'][
            radar.sweep_start_ray_index['data'][self.Vtilt.value]:
            radar.sweep_end_ray_index['data'][self.Vtilt.value]+1]
        self.r = radar.range['data']/1000.
        self.big = np.ones(shape=(self.az.size, self.r.size))
        self.xys = np.empty(shape=(self.az.size*self.r.size, 2))
        self.rbig = self.big*self.r
        self.azbig = self.big*self.az.reshape(self.az.size, 1)
        x = self.rbig * np.sin(self.azbig*np.pi/180.)
        y = self.rbig * np.cos(self.azbig*np.pi/180.)
        self.xys[:, 0] = x.flatten()
        self.xys[:, 1] = y.flatten()

    def motion_notify_callback(self, event):
        '''Create the shape in plot area'''
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
                self.statusbar.showMessage("Closed Region")

                # Create arrays for indices/data
                data = self.getPathInteriorValues(path)
                if data is not None:
                    data = np.concatenate(data).reshape(7, -1).transpose()
                    self.VroiData.change(data)

    def connect(self):
        '''Connect the ROI instance'''
        self.motionID = self.fig.canvas.mpl_connect(
            'motion_notify_event', self.motion_notify_callback)
        self.buttonID = self.fig.canvas.mpl_connect(
            'button_press_event', self.button_press_callback)

    def disconnect(self):
        '''Disconnect the ROI instance'''
        self.fig.canvas.mpl_disconnect(self.motionID)
        self.fig.canvas.mpl_disconnect(self.buttonID)

    def CreateROIWidget(self):
        '''Create a widget to access ROI tools.
        Open and Save Table methods borrowed from:
http://stackoverflow.com/questions/12608835/writing-a-qtablewidget-to-a-csv-or-xls
        '''
        self.ROIbox = QtGui.QGroupBox("Region of Interest Selection",
                                      parent=self)
        self.rBox_layout = QtGui.QVBoxLayout(self.ROIbox)
        self.ROIbox.setLayout(self.rBox_layout)
        self.setCentralWidget(self.ROIbox)

        # Add buttons for functionality
        self.buttonViewTable = QtGui.QPushButton('View Tabular Data', self)
        self.buttonOpenTable = QtGui.QPushButton('Open Tabular Data', self)
        self.buttonSaveTable = QtGui.QPushButton('Save Tabular Data', self)
        self.buttonResetROI = QtGui.QPushButton('Reset ROI', self)
        self.buttonViewTable.clicked.connect(self.viewTable)
        self.buttonOpenTable.clicked.connect(self.openTable)
        self.buttonSaveTable.clicked.connect(self.saveTable)
        self.buttonResetROI.clicked.connect(self.resetROI)

        # Create functionality buttons
        self.rBox_layout.addWidget(self.buttonViewTable)
        self.rBox_layout.addWidget(self.buttonOpenTable)
        self.rBox_layout.addWidget(self.buttonSaveTable)
        self.rBox_layout.addWidget(self.buttonResetROI)

    def viewTable(self):
        '''View a Table of ROI points'''
        # Instantiate Table
        self.table = common.CreateTable(self.columns)
        self.table.display_data(self.VroiData.value)

        # Show the table
        self.table.show()

    def saveTable(self):
        '''Save a Table of ROI points to a CSV file'''
        data = self.VroiData.value
        fsuggest = 'ROI_' + self.getField() + '_' + \
            str(data[:, 0].mean()) + '_' + \
            str(data[:, 1].mean())+'.csv'
        path = QtGui.QFileDialog.getSaveFileName(
                self, 'Save CSV Table File', fsuggest, 'CSV(*.csv)')
        if not path.isEmpty():
            with open(unicode(path), 'wb') as stream:
                writer = csv.writer(stream)
                for row in range(data.shape[0]):
                    rowdata = []
                    for column in range(data.shape[1]):
                        item = data[row][column]
                        if item is not None:
                            rowdata.append(
                                unicode(item).encode('utf8'))
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
        # Commented out below is alternative ascii output (needs reformating)
# +                outfile = open(fsuggest,'w')
# +                outfile.write(
# "     X        Y    Azimuth   Range     Value   Az Index  R Index\n")
# +                    outfile.write(
# "%8.2f %8.2f %8.2f %8.3f %8.2f %8d %8d\n" %(self.xys[self.ind[i],0],
# self.xys[self.ind[i],1], self.az[self.ind[i]/self.r.size],
# self.r[self.ind[i]%self.r.size],
# self.Vradar.fields[self.Vfield.value][
# 'data'][self.Vradar.sweep_start_ray_index['data'][
# self.Vtilt]+self.ind[i]/self.r.size,self.ind[i] \
# % self.r.size],self.Vradar.sweep_start_ray_index['data'][self.Vtilt]+\
# self.ind[i]/self.r.size,self.ind[i]%self.r.size))
# +                outfile.close()
#  msg = "     X        Y    Azimuth   Range     Value   Az Index  R Index\n"
#                for i in range(self.ind.size):
#                warn = common.ShowWarning(msg)
#                    print "%8.2f %8.2f %8.2f %8.3f %8.2f %8d %8d" %\

    def openTable(self):
        path = QtGui.QFileDialog.getOpenFileName(
                self, 'Open File', '', 'CSV(*.csv)')
        data = []
        if not path.isEmpty():
            with open(unicode(path), 'rb') as stream:
                for rowdata in csv.reader(stream):
                    row = [None]*7
                    for column, item in enumerate(rowdata):
                        row[column] = float(item.decode('utf8'))
                    data.append(row)
        data = np.array(data)
        self.VroiData.change(data)

    def resetROI(self):
        '''Clear the ROI lines from plot and reset things'''
        for i in xrange(len(self.poly)):
            self.poly[i].remove()

        # Redraw to remove the lines and reinitialize variable
        self.fig.canvas.draw()
        self._initialize_ROI_vars()
#        self._setup_ROI_vars()
        self.statusbar.showMessage("Select Region with Mouse")

    def closeEvent(self, QCloseEvent):
        '''Reimplementations to remove from components list'''
        self.resetROI()
        self.disconnect()
        super(ROI, self).closeEvent(QCloseEvent)

#    def NewRadar(self, variable, value, False):
#        '''Update the display list when radar variable is changed.'''
#        print "In NewRadar"


class _RoiStart(QtGui.QDialog):
    '''
    Dialog Class for graphical Start of Roi, to be used in guiStart
    '''

    def __init__(self):
        '''Initialize the class to create the interface'''
        super(_RoiStart, self).__init__()
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

        self.displayButton = QtGui.QPushButton("Find Component")
        self.displayButton.clicked.connect(self.chooseDisplay)
        self.layout.addWidget(QtGui.QLabel("display"), 0, 0)
        self.layout.addWidget(self.displayButton, 0, 1, 1, 3)

        self.name = QtGui.QLineEdit("Roi")
        self.layout.addWidget(QtGui.QLabel("name"), 1, 0)
        self.layout.addWidget(self.name, 1, 1, 1, 3)

        self.independent = QtGui.QCheckBox("Independent Window")
        self.independent.setChecked(True)
        self.layout.addWidget(self.independent, 2, 1, 1, 1)

        self.closeButton = QtGui.QPushButton("Start")
        self.closeButton.clicked.connect(self.closeDialog)
        self.layout.addWidget(self.closeButton, 3, 0, 1, 5)

    def closeDialog(self):
        if self.result["display"] is not None:
            self.done(QtGui.QDialog.Accepted)
        else:
            warn = common.ShowWarning("Must Select Display")

    def startDisplay(self):
        self.exec_()

        self.result['name'] = str(self.name.text())
        print self.result['name']

        return self.result, self.independent.isChecked()
