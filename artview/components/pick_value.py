"""
pick_value.py

Class to pick a value with the mouse.
"""
# Load the needed packages
import numpy as np

from ..core import Variable, Component, common, VariableChoose, QtGui, QtCore


class ValueClick(Component):

    def __init__(self, display, name="ValueClick", parent=None):
        '''
        Initialize the class to pick value from display.

        Parameters::
        ----------
        display - ARTview Display
            Display instance to associate ValueClick.
            Must have following elements:
                * getPlotAxis() - Matplotlib axis instance
                * getStatusBar() - QtGui.QStatusBar
                * getField() - string
                * getUnits() - string
                * getNearestPoints(xdata, ydata) - see
                  :py:func:`~artview.components.GridDisplay.getNearestPoints`

        [Optional]
        name - string
            Window name.
        parent - PyQt instance
            Parent instance to associate to ROI instance.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        NOTE
        ----
        Since ARTView 1.2 this is not more a valid Component, since it
        has mandatory arguments and this is no longer allowed
        '''
        super(ValueClick, self).__init__(name=name, parent=parent)
        self.sharedVariables = {}

        self.ax = display.getPlotAxis()
        self.statusbar = display.getStatusBar()
        self.fig = self.ax.get_figure()
        self.getNearestPoints = display.getNearestPoints
        self.getField = display.getField
        self.getUnits = display.getUnits
        self.connect()

    def connect(self):
        '''Connect the ValueClick instance.'''
        self.pickPointID = self.fig.canvas.mpl_connect(
            'button_press_event', self.onPick)

    def onPick(self, event):
        '''Get value at the point selected by mouse click.'''
        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        if (xdata is None) or (ydata is None):
            msg = "Please choose point inside plot area."
        else:
            aux = self.getNearestPoints(xdata, ydata)
            msg1 = ('x = %4.2f km,  y = %4.2f km,  z = %4.2f km,  ' %
                    (aux[0][0]/1000., aux[1][0]/1000., aux[2][0]/1000.))
            msg2 = '%s = %4.2f %s' % (self.getField(), aux[3][0],
                                      self.getUnits())
            msg = msg1 + msg2

        self.statusbar.showMessage(msg)

    def disconnect(self):
        '''Disconnect the ValueClick instance.'''
        self.fig.canvas.mpl_disconnect(self.pickPointID)

    def closeEvent(self, QCloseEvent):
        '''Re-implementation to disconnect.'''
        self.disconnect()
        super(ValueClick, self).closeEvent(QCloseEvent)
