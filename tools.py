"""
tools.py

Routines and class instances to create tools for the ToolBox in Display.
"""
        
# Load the needed packages
from PyQt4 import QtGui, QtCore
import numpy as np

import limits
import common

from matplotlib.lines import Line2D
from matplotlib.path import Path

###############################
# Restore the default Display #
###############################
def restore_default_display(tooldict, field, airborne, rhi):
    '''Restore the Display defaults.
    
    Parameters::
    ----------
    zoompan - ZoomPan class instance
        A ZoomPan class instance.
    field - string
        Name of field to display.
    airborne - boolean
        True for airborne-type radar file.
    rhi - boolean
        True for RHI-type radar file.
        
    Notes::
    -----
    Returns updated zoompan class instance, limits dictionary, and colormap.
    '''
    # ****Need to check if this would work****
#    if zoompan != None:
#        zoompan.disconnect()
#        zoompan = None
    if tooldict['zoompan'] != None:
        tooldict['zoompan'].disconnect()
        tooldict['zoompan'] = None
    display_limits, CMAP = limits.initialize_limits(field, airborne, rhi)
    
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
        self.pickPointID = self.fig.canvas.mpl_connect('button_press_event', self.onPick)
        
    def onPick(self, event):
        '''Get value at the point selected by mouse click.'''
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        az = np.arctan2(xdata, ydata)*180./np.pi
        radar = self.Vradar.value #keep equantions clean
        if az < 0:
            az = az + 360.
        rng = np.sqrt(xdata*xdata+ydata*ydata)
        azindex = np.argmin(np.abs(radar.azimuth['data'][radar.sweep_start_ray_index['data'][self.Vtilt.value]:radar.sweep_end_ray_index['data'][self.Vtilt.value]]-az))+radar.sweep_start_ray_index['data'][self.Vtilt.value]
        rngindex = np.argmin(np.abs(radar.range['data']-rng*1000.))
        self.msg = 'x = %4.2f, y = %4.2f, Azimuth = %4.2f deg., Range = %4.2f km, %s = %4.2f %s'\
                    %(xdata, ydata, radar.azimuth['data'][azindex], \
                    radar.range['data'][rngindex]/1000., self.Vfield.value, \
                    radar.fields[self.Vfield.value]['data'][azindex][rngindex], self.units)
        self.statusbar.showMessage(self.msg)
            
    def disconnect(self):
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
    if tooldict['zoompan'] != None:
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
        self.scrollID = self.fig.canvas.mpl_connect('scroll_event', self.onZoom)
        self.pressID = self.fig.canvas.mpl_connect('button_press_event',self.onPress)
        self.releaseID = self.fig.canvas.mpl_connect('button_release_event',self.onRelease)
        self.motionID = self.fig.canvas.mpl_connect('motion_notify_event',self.onMotion)

    def onZoom(self, event):
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
        if event.inaxes != self.ax: return
        self.cur_xlim = self.ax.get_xlim()
        self.cur_ylim = self.ax.get_ylim()
        self.press = self.x0, self.y0, event.xdata, event.ydata
        self.x0, self.y0, self.xpress, self.ypress = self.press

    def onRelease(self, event):
        self.press = None
        self.ax.figure.canvas.draw()

    def onMotion(self, event):
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
        self.fig.canvas.mpl_disconnect(self.scrollID)
        self.fig.canvas.mpl_disconnect(self.pressID)
        self.fig.canvas.mpl_disconnect(self.releaseID)
        self.fig.canvas.mpl_disconnect(self.motionID)
        
        self.LimsDialog.accept()
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

    def __init__(self, Vradar, Vtilt, ax, display, name="ROI", parent=None):
        '''
        Initialize the class to select an ROI on display.
    
        Parameters::
        ----------
        Vradar - Variable instance
            Radar signal variable to be used.
        Vtilt - Variable instance
            Tilt signal variable to be used.
        ax - Matplotlib axis instance
            Axis instance to use.
    
        [Optional]
        name - string
            Field Radiobutton window name.
        parent - PyQt instance
            Parent instance to associate to ZoomPan instance.
            If None, then Qt owns, otherwise associated with parent PyQt instance.
        
        Notes::
        -----
        '''
        super(ROI, self).__init__(parent)
        self.parent = parent
        self.name = name
        self.Vradar = Vradar
        self.Vtilt = Vtilt
        #QtCore.QObject.connect(Vradar, QtCore.SIGNAL("ValueChanged"), self.NewRadar)
        
        self.ax = ax
#        self.statusbar = statusbar
        self.fig = ax.get_figure()
        self.display = display
        
        self.previous_point = []
        self.start_point = []
        self.end_point = []
        self.line = None
        self.verts = []
        self.ind = []
        self.xys = []
        self.xpts = self.display.x[:,self.Vtilt]
        self.ypts = self.display.y[:,self.Vtilt]
        self.xys = np.array([self.xpts,self.ypts]).transpose()
        print self.Vtilt
        print self.display.x
        print self.display.x[:,self.Vtilt]
        print np.amin(self.xpts)
        print np.amax(self.xpts)
        print np.amin(self.ypts)
        print np.amax(self.ypts)
        print np.amin(self.xys)
        print np.amax(self.xys)
#        self.fig.canvas.draw()

    def motion_notify_callback(self, event):
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
                ax.add_line(line)
                self.previous_point = [x, y]
                self.verts.append([x, y])
                self.fig.canvas.draw()


    def button_press_callback(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            ax = event.inaxes
            if event.button == 1:  # If you press the right button
                if self.line == None: # if there is no line, create a line
                    self.line = Line2D([x, x], [y, y], marker = 'o')
                    self.start_point = [x,y]
                    self.previous_point =  self.start_point
                    self.verts.append([x, y])
                    ax.add_line(self.line)
                    self.fig.canvas.draw()
                # add a segment
                else: # if there is a line, create a segment
                    self.line = Line2D([self.previous_point[0], x],
                                       [self.previous_point[1], y],
                                       marker = 'o')
                    self.previous_point = [x,y]
                    self.verts.append([x, y])
                    event.inaxes.add_line(self.line)
                    self.fig.canvas.draw()

            elif event.button == 3 and self.line != None: # close the loop
                self.line.set_data([self.previous_point[0], self.start_point[0]],
                                 [self.previous_point[1], self.start_point[1]])
                ax.add_line(self.line)
                self.fig.canvas.draw()
                self.line = None
                path = Path(self.verts)
                self.ind = np.nonzero([path.contains_point(xy) for xy in self.xys])[0]
                print self.ind
                print "Closed Loop"
                print self.verts

    def connect(self):
        self.motionID = self.fig.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.buttonID = self.fig.canvas.mpl_connect('button_press_event', self.button_press_callback)

    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.motionID)
        self.fig.canvas.mpl_disconnect(self.buttonID)
    
    def NewRadar(self, variable, value, False):
        '''Update the display list when radar variable is changed.'''
        print "In NewRadar"
