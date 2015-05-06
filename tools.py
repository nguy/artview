"""
tools.py

Routines and class instances to create tools for the ToolBox in Display.
"""
        
# Load the needed packages
from PyQt4 import QtGui, QtCore

import limits
import common

###############################
# Restore the default Display #
###############################
def restore_default_display(zoompan, field, airborne, rhi):
    '''Restore the Display defaults'''
    # ****Need to check if this would work****
    if zoompan != None:
        zoompan.disconnect()
        zoompan = None
    limits, CMAP = limits.initialize_limits(field, airborne, rhi)
    
    return zoompan, limits, CMAP    

###############################
# Use a custom Method #
###############################
def custom_tool(zoompan):
    '''Allow user to activate self-defined tool'''
    if zoompan != None:
        zoompan.disconnect()
        zoompan = None
    msg = "This feature is inactive at present"
    warn = common.ShowWarning(msg)
    print msg

##########################
# Zoom/Pan Class Methods #
##########################
class ZoomPan(QtGui.QMainWindow):
    '''
    Class for Zoom and Pan of plot
    Modified an original answer found here: http://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
    '''
    def __init__(self, Vlims, ax, limits, base_scale = 2., name="ZoomPan", parent=None):
        super(ZoomPan, self).__init__(parent)
        self.parent = parent
        self.name = name
        
        # Set up signal, so that DISPLAY can react to external 
        # (or internal) changes in limits (Core.Variable instances expected)
        # Send the new limits back to the main window
#        self.Vradar = Vradar
#        QtCore.QObject.connect(Vradar, QtCore.SIGNAL("ValueChanged"), self.NewRadar)
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
        self.limits = limits
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
        
    def _pass_lims(self):
        self.limits['xmin'] = self.entry['xmin']
        self.limits['xmax'] = self.entry['xmax']
        self.limits['ymin'] = self.entry['ymin']
        self.limits['ymax'] = self.entry['ymax']
        
        self.LimsDialog.accept()
        self.Vlims.change(self.limits)
             
    def NewLimits(self, variable, value):
        '''Retrieve new limits input'''
        #self._pass_lims()
        print "In NewLims"
    
    def NewRadar(self, variable, value):
        # update Limits
        #self._pass_lims()
        print "In NewRadar"