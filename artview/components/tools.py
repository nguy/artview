"""
tools.py

Routines and class instances to create tools for the ToolBox in Display.
"""
        
# Load the needed packages
from PyQt4 import QtGui, QtCore
import numpy as np
import warnings
import csv

from . import limits
from ..core import common

from matplotlib.lines import Line2D
from matplotlib.path import Path


# The following line is used to suppress NaN warnings thrown by Numpy 
# when using some tools
warnings.filterwarnings('ignore', category=UserWarning, append=True)
###############################
# Restore the default Display #
###############################
def restore_default_display(tooldict, field, scan_type):
    '''Restore the Display defaults.
    
    Parameters
    ----------
    zoompan - ZoomPan class instance
        A ZoomPan class instance.
    field - string
        Name of field to display.
    scan_type - "ppi", "rhi", "airborne" or None
        Scan type for radar file.
        
    Notes
    -----
    Returns updated zoompan class instance, limits dictionary, and colormap.
    '''
    # ****Need to check if this would work****
    for tool in tooldict:
        if tooldict[tool] is not None:
            tooldict[tool].disconnect()
            tooldict[tool] = None

    display_limits, CMAP = limits._default_limits(field, scan_type)
    
    return tooldict, display_limits, CMAP
##################################
# Mouse Click Value Class Method #
##################################
class ValueClick(QtGui.QMainWindow):
    '''
    Class for retrieving value by mouse click on display.
    '''
    def __init__(self, Vradar, Vtilt, Vfield, units, ax, statusbar, name="ValueClick", parent=None):
        '''
        Initialize the class to display mouse click value data on display.
    
        Parameters::
        ----------
        Vradar - Variable instance
            Radar signal variable to be used.
        Vtilt - Variable instance
            Tilt signal variable to be used.
        Vfield - Variable instance
            Field signal variable to be used.
        units - string
            Units of field variable.
        ax - Matplotlib axis instance
            Axis instance to use.
        statusbar - Qt StatusBar() instance
            Display point value message via this interface.
    
        [Optional]
        name - string
            Field Radiobutton window name.
        parent - PyQt instance
            Parent instance to associate to ZoomPan instance.
            If None, then Qt owns, otherwise associated with parent PyQt instance.
        
        Notes::
        -----
        This class records the values at the point selected by mouse click and 
        displays in the statusbar.
        '''
        super(ValueClick, self).__init__(parent)
        self.parent = parent
        self.name = name
        self.Vradar = Vradar
        self.Vtilt = Vtilt
        self.Vfield = Vfield
        self.units = units
        self.ax = ax
        self.statusbar = statusbar
        self.fig = ax.get_figure()
        QtCore.QObject.connect(Vradar, QtCore.SIGNAL("ValueChanged"), self.NewRadar)

        self.msg = "Click to display value"

    def connect(self):
        '''Connect the ValueClick instance'''
        self.pickPointID = self.fig.canvas.mpl_connect('button_press_event', self.onPick)

    def onPick(self, event):
        '''Get value at the point selected by mouse click.'''
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        if (xdata is None) or (ydata is None):
            self.msg = "Please choose point inside plot area"
        else:
            az = np.arctan2(xdata, ydata)*180./np.pi
            radar = self.Vradar.value #keep equantions clean
            if az < 0:
                az = az + 360.
            rng = np.sqrt(xdata*xdata + ydata*ydata)
 
            azindex = np.argmin(np.abs(radar.azimuth['data'][radar.sweep_start_ray_index['data'][self.Vtilt.value]:radar.sweep_end_ray_index['data'][self.Vtilt.value]+1]-az))+radar.sweep_start_ray_index['data'][self.Vtilt.value]
            if azindex == radar.sweep_end_ray_index['data'][self.Vtilt.value]:
                if az < 10:
                    az = az + 360.
                if np.abs(radar.azimuth['data'][radar.sweep_start_ray_index['data'][self.Vtilt.value]]+360.-az) < np.abs(radar.azimuth['data'][radar.sweep_end_ray_index['data'][self.Vtilt.value]]-az):
                    azindex = radar.sweep_start_ray_index['data'][self.Vtilt.value]
                else:
                    azindex = radar.sweep_end_ray_index['data'][self.Vtilt.value]

            rngindex = np.argmin(np.abs(radar.range['data']-rng*1000.))
            self.msg = 'x = %4.2f, y = %4.2f, Azimuth = %4.2f deg., Range = %4.3f km, %s = %4.2f %s'\
                        %(xdata, ydata, radar.azimuth['data'][azindex], \
                        radar.range['data'][rngindex]/1000., self.Vfield.value, \
                        radar.fields[self.Vfield.value]['data'][azindex][rngindex], self.units)
        self.statusbar.showMessage(self.msg)

    def disconnect(self):
        '''Disconnect the ZoomPan instance'''
        self.fig.canvas.mpl_disconnect(self.pickPointID)

    def NewRadar(self, variable, value, False):
        '''Update the display list when radar variable is changed.'''
        print "In NewRadar"

###############################
# Use a custom Method #
###############################
def custom_tool(tooldict):
    '''Allow user to activate self-defined tool.
    
    Parameters::
    ----------
        
    Notes::
    -----
    '''
    if tooldict['zoompan'] is not None:
        tooldict['zoompan'].disconnect()
        tooldict['zoompan'] = None
    msg = "This feature is inactive at present"
    warn = common.ShowWarning(msg)

##########################
# Zoom/Pan Class Methods #
##########################
class ZoomPan(QtGui.QMainWindow):
    '''
    Class for Zoom and Pan of display.
    
    Modified an original answer found here: 
    http://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
    '''
    def __init__(self, Vlims, ax, display_limits, base_scale = 2., \
                 name="ZoomPan", parent=None):
        '''
        Initialize the class to create the interface.
    
        Parameters::
        ----------
        Vlims - Variable instance
            Limits signal variable to be used.
        ax - Matplotlib axis instance
            Axis instance to use.
        limits - dict
            Display limits dictionary.
    
        [Optional]
        base_scale - float
            Scaling factor to use fo Zoom/Pan
        name - string
            Field Radiobutton window name.
        parent - PyQt instance
            Parent instance to associate to ZoomPan instance.
            If None, then Qt owns, otherwise associated with parent PyQt instance.
        
        Notes::
        -----
        This class records the selected button and passes the
        change value back to variable.
        '''
        super(ZoomPan, self).__init__(parent)
        self.parent = parent
        self.name = name

        # Set up signal, so that DISPLAY can react to external 
        # (or internal) changes in limits (Core.Variable instances expected)
        # Send the new limits back to the main window
        self.Vlims = Vlims
        QtCore.QObject.connect(Vlims, QtCore.SIGNAL("ValueChanged"), self.NewLimits)

        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None
        self.entry = {}
        self.entry['dmin'] = None
        self.entry['dmax'] = None
        #self.connect()
        self.ax = ax
        self.limits = display_limits
        self.base_scale = base_scale
        self.fig = ax.get_figure() # get the figure of interest

    def connect(self):
        '''Connect the ZoomPan instance'''
        self.scrollID = self.fig.canvas.mpl_connect('scroll_event', self.onZoom)
        self.pressID = self.fig.canvas.mpl_connect('button_press_event',self.onPress)
        self.releaseID = self.fig.canvas.mpl_connect('button_release_event',self.onRelease)
        self.motionID = self.fig.canvas.mpl_connect('motion_notify_event',self.onMotion)

    def onZoom(self, event):
        '''Recalculate limits when zoomed'''
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location

        if event.button == 'down':
            # deal with zoom in
            scale_factor = 1 / self.base_scale
        elif event.button == 'up':
            # deal with zoom out
            scale_factor = self.base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print event.button

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
        self.ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
        self.ax.figure.canvas.draw()

        # Record the new limits and pass them to main window
        self.limits['xmin'] = xdata - new_width * (1-relx)
        self.limits['xmax'] = xdata + new_width * (relx)
        self.limits['ymin'] = ydata - new_height * (1-rely)
        self.limits['ymax'] = ydata + new_height * (rely)

    def onPress(self, event):
        '''Get the current event parameters'''
        if event.inaxes != self.ax: return
        self.cur_xlim = self.ax.get_xlim()
        self.cur_ylim = self.ax.get_ylim()
        self.press = self.x0, self.y0, event.xdata, event.ydata
        self.x0, self.y0, self.xpress, self.ypress = self.press

    def onRelease(self, event):
        self.press = None
        self.ax.figure.canvas.draw()

    def onMotion(self, event):
        '''Redraw the plot when panned'''
        if self.press is None: return
        if event.inaxes != self.ax: return
        dx = event.xdata - self.xpress
        dy = event.ydata - self.ypress
        self.cur_xlim -= dx
        self.cur_ylim -= dy
        self.ax.set_xlim(self.cur_xlim)
        self.ax.set_ylim(self.cur_ylim)

        self.ax.figure.canvas.draw()

        # Record the new limits and pass them to main window
        self.limits['xmin'], self.limits['xmax'] = self.cur_xlim[0], self.cur_xlim[1]
        self.limits['ymin'], self.limits['ymax'] = self.cur_ylim[0], self.cur_ylim[1]

    def disconnect(self):
        '''Disconnect the ZoomPan instance'''
        self.fig.canvas.mpl_disconnect(self.scrollID)
        self.fig.canvas.mpl_disconnect(self.pressID)
        self.fig.canvas.mpl_disconnect(self.releaseID)
        self.fig.canvas.mpl_disconnect(self.motionID)

        #self.LimsDialog.accept()
        self.Vlims.change(self.limits)

    def NewLimits(self, variable, value, strong):
        '''Record the new display limits.'''
        '''Retrieve new limits input'''
        print "In NewLims"

##################################
# Select Area (Polygon) Class Method #
##################################
class ROI(QtGui.QMainWindow):
    '''
    Select a Region of Interest: The code modified from
    https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg00661.html
    '''

    def __init__(self, Vradar, Vtilt, Vfield, statusbar, ax, display, name="ROI", parent=None):
        '''
        Initialize the class to select an ROI on display.
    
        Parameters::
        ----------
        Vradar - Variable instance
            Radar signal variable to be used.
        Vtilt - Variable instance
            Tilt signal variable to be used.
        Vfield - Variable instance
            Field signal variable to be used.
        statusbar - Qt StatusBar() instance
            Display point value message via this interface.
        ax - Matplotlib axis instance
            Axis instance to use.
        display - ARTView Display
        	Display instance to associate ROI.

        [Optional]
        name - string
            Field Radiobutton window name.
        parent - PyQt instance
            Parent instance to associate to ROI instance.
            If None, then Qt owns, otherwise associated with parent PyQt instance.
        
        Notes::
        -----
        '''
        super(ROI, self).__init__(parent)
        self.parent = parent
        self.name = name
        self.Vradar = Vradar
        self.Vtilt = Vtilt
        self.Vfield = Vfield
        QtCore.QObject.connect(Vradar, QtCore.SIGNAL("ValueChanged"), self.NewRadar)

        self.ax = ax
        self.statusbar = statusbar
        self.fig = ax.get_figure()
        self.display = display
        self.columns = ["X", "Y", "Azimuth", "Range", "Value", "Az Index", "R Index"]
        self.statusbar.showMessage("Select Region with Mouse")

        self._initialize_ROI_vars()
        self._setup_ROI_vars()
        self.CreateROIWidget()
        self.show()

    def _initialize_ROI_vars(self):
        '''Initialize variables to be used in ROI selection'''
        self.previous_point = []
        self.start_point = []
        self.end_point = []
        self.line = None
        self.verts = []
        self.ind = []
        self.poly = []
 
    def _setup_ROI_vars(self):
        '''Setup variables from radar instance for ROI selection'''
        radar = self.Vradar.value #keep equantions clean
        self.az = radar.azimuth['data'][radar.sweep_start_ray_index['data'][self.Vtilt.value]:radar.sweep_end_ray_index['data'][self.Vtilt.value]+1]
        self.r =  radar.range['data']/1000.
        self.big=np.ones(shape=(self.az.size, self.r.size))
        self.xys=np.empty(shape=(self.az.size*self.r.size,2))
        self.rbig = self.big*self.r
        self.azbig = self.big*self.az.reshape(self.az.size,1)
        x = self.rbig*np.sin(self.azbig*np.pi/180.)
        y = self.rbig*np.cos(self.azbig*np.pi/180.)
        self.xys[:,0] = x.flatten()
        self.xys[:,1] = y.flatten()

    def motion_notify_callback(self, event):
        '''Create the shape in plot area'''
        if event.inaxes:
            ax = event.inaxes
            x, y = event.xdata, event.ydata
            if event.button == None and self.line != None: # Move line around 
                self.line.set_data([self.previous_point[0], x],
                                   [self.previous_point[1], y])
                self.fig.canvas.draw()
            elif event.button == 1: # Free Hand Drawing
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
            radar = self.Vradar.value
            if event.button == 1:  # If you press the right button
                if self.line == None: # if there is no line, create a line
                    self.line = Line2D([x, x], [y, y], marker = 'o')
                    self.start_point = [x,y]
                    self.previous_point =  self.start_point
                    self.verts.append([x, y])
                    self.poly.append(ax.add_line(self.line))
                    self.fig.canvas.draw()
                # add a segment
                else: # if there is a line, create a segment
                    self.line = Line2D([self.previous_point[0], x],
                                       [self.previous_point[1], y],
                                       marker = 'o')
                    self.previous_point = [x,y]
                    self.verts.append([x, y])
                    self.poly.append(event.inaxes.add_line(self.line))
                    self.fig.canvas.draw()

            # Close the loop by double clicking and create a table
            elif event.button == 3 and self.line != None: # close the loop
                self.line.set_data([self.previous_point[0], self.start_point[0]],
                                 [self.previous_point[1], self.start_point[1]])
                self.poly.append(ax.add_line(self.line))
                self.fig.canvas.draw()
                self.line = None
                path = Path(self.verts)
 
                # Inform via status bar
                self.statusbar.showMessage("Closed Region")
 
                # Create arrays for indices/data
                self.ind = np.nonzero([path.contains_point(xy) for xy in self.xys])[0]
                self.data = np.empty([len(self.ind), len(self.columns)])

                for i in range(self.ind.size):
                    X, Y = self.xys[self.ind[i],0], self.xys[self.ind[i],1]
                    Azimuth, Range = self.az[self.ind[i]/self.r.size], self.r[self.ind[i]%self.r.size]
                    Value = radar.fields[self.Vfield.value]['data'][radar.sweep_start_ray_index['data'][self.Vtilt.value]+self.ind[i]/self.r.size,self.ind[i]%self.r.size]
                    Az_Index = radar.sweep_start_ray_index['data'][self.Vtilt.value] + self.ind[i]/self.r.size
                    Rng_Index = self.ind[i]%self.r.size
                    self.data[i,:] = (X, Y, Azimuth, Range, Value, Az_Index, Rng_Index)

                # Instantiate Table
                self.table = common.CreateTable(self.columns)

    def connect(self):
        '''Connect the ROI instance'''
        self.motionID = self.fig.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.buttonID = self.fig.canvas.mpl_connect('button_press_event', self.button_press_callback)

    def disconnect(self):
        '''Disconnect the ROI instance'''
        self.fig.canvas.mpl_disconnect(self.motionID)
        self.fig.canvas.mpl_disconnect(self.buttonID)

    def CreateROIWidget(self):
        '''Create a widget to access ROI tools.
        Open and Save Table methods borrowed from:
        http://stackoverflow.com/questions/12608835/writing-a-qtablewidget-to-a-csv-or-xls
        '''
        self.ROIbox = QtGui.QGroupBox("Region of Interest Selection", parent=self)
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
        self.table.display_data(self.data)

        # Show the table
        self.table.show()

    def saveTable(self):
        '''Save a Table of ROI points to a CSV file'''
        fsuggest = 'ROI_'+self.Vfield.value+'_'+str(self.xys[self.ind,0].mean())+'_'+str(self.xys[self.ind,1].mean())+'.csv'
        path = QtGui.QFileDialog.getSaveFileName(
                self, 'Save CSV Table File', fsuggest, 'CSV(*.csv)')
        if not path.isEmpty():
            with open(unicode(path), 'wb') as stream:
                writer = csv.writer(stream)
                for row in range(self.table.rowCount()):
                    rowdata = []
                    for column in range(self.table.columnCount()):
                        item = self.table.item(row, column)
                        if item is not None:
                            rowdata.append(
                                unicode(item.text()).encode('utf8'))
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
        # Commented out below is an alternative ascii output (needs reformating)
#+                outfile = open(fsuggest,'w')
#+                outfile.write("     X        Y    Azimuth   Range     Value   Az Index  R Index\n")
#+                    outfile.write("%8.2f %8.2f %8.2f %8.3f %8.2f %8d %8d\n" %(self.xys[self.ind[i],0], self.xys[self.ind[i],1], self.az[self.ind[i]/self.r.size], self.r[self.ind[i]%self.r.size], self.Vradar.fields[self.Vfield.value]['data'][self.Vradar.sweep_start_ray_index['data'][self.Vtilt]+self.ind[i]/self.r.size,self.ind[i]%self.r.size],self.Vradar.sweep_start_ray_index['data'][self.Vtilt]+self.ind[i]/self.r.size,self.ind[i]%self.r.size))
#+                outfile.close()
#                msg = "     X        Y    Azimuth   Range     Value   Az Index  R Index\n"
#                for i in range(self.ind.size):
#                warn = common.ShowWarning(msg)
#                    print "%8.2f %8.2f %8.2f %8.3f %8.2f %8d %8d" %\

    def openTable(self):
        path = QtGui.QFileDialog.getOpenFileName(
                self, 'Open File', '', 'CSV(*.csv)')
        if not path.isEmpty():
            with open(unicode(path), 'rb') as stream:
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
                for rowdata in csv.reader(stream):
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setColumnCount(len(rowdata))
                    for column, data in enumerate(rowdata):
                        item = QtGui.QTableWidgetItem(data.decode('utf8'))
                        self.table.setItem(row, column, item)

    def resetROI(self):
        '''Clear the ROI lines from plot and reset things'''
        for i in xrange(len(self.poly)):
            self.poly[i].remove()

        # Redraw to remove the lines and reinitialize variable
        self.fig.canvas.draw()
        self._initialize_ROI_vars()
        self._setup_ROI_vars()
        self.statusbar.showMessage("Select Region with Mouse")

    def NewRadar(self, variable, value, False):
        '''Update the display list when radar variable is changed.'''
        print "In NewRadar"
