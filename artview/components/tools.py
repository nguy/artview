"""
tools.py

Routines and class instances to create tools for the ToolBox in Display.
"""

# Load the needed packages
import numpy as np
import warnings
import csv

from . import limits
from ..core import common, QtGui, QtCore

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
    tooldict - dictionary
        A dictionary of tool instances.
    field - string
        Name of field to display.
    scan_type - "ppi", "rhi", "airborne" or None
        Scan type for radar file.

    Notes
    -----
    Disconnects all tools and resets limits and colormap to default.
    '''
    import warnings
    warnings.warn("this function is deprecated")
    tooldict = reset_tools(tooldict)

    display_limits, cmap = limits._default_limits(field, scan_type)

    return tooldict, display_limits, cmap


def reset_tools(tooldict):
    '''Reset the Tools dictionary.

    Parameters
    ----------
    tooldict - dictionary
        A dictionary of tool instances.

    Notes
    -----
    Disconnects all tools.
    '''
    import warnings
    warnings.warn("this function is deprecated")
    for tool in tooldict:
        if tooldict[tool] is not None:
            tooldict[tool].disconnect()
            tooldict[tool] = None

    return tooldict

##################################
# Mouse Click Value Class Method #
##################################


class ValueClick(QtGui.QMainWindow):
    '''
    Class for retrieving value by mouse click on display.
    '''
    def __init__(self, display, name="ValueClick", parent=None):
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
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        Notes::
        -----
        This class records the values at the point selected by mouse click and
        displays in the statusbar.
        '''
        super(ValueClick, self).__init__(parent=parent)

        self.parent = parent
        self.name = name
        self.Vradar = display.Vradar
        self.Vtilt = display.Vtilt
        self.Vfield = display.Vfield
        self.units = display.getUnits()
        self.ax = display.getPlotAxis()
        self.statusbar = display.getStatusBar()
        self.fig = self.ax.get_figure()
        self.plot_type = display.plot_type
        QtCore.QObject.connect(
            self.Vradar, QtCore.SIGNAL("ValueChanged"), self.NewRadar)

        self.msg = "Click to display value"

    def connect(self):
        '''Connect the ValueClick instance'''
        self.pickPointID = self.fig.canvas.mpl_connect(
            'button_press_event', self.onPick)

    def onPick(self, event):
        '''Get value at the point selected by mouse click.'''
        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        if ((xdata is None) or (ydata is None) or
            (self.Vradar.value is None)):
            self.msg = "Please choose point inside plot area"
        else:
            az = np.arctan2(xdata, ydata) * 180. / np.pi
            radar = self.Vradar.value  # keep equations clean
            if az < 0:
                az = az + 360.
            rng = np.sqrt(xdata*xdata + ydata*ydata)

            azindex = np.argmin(np.abs(
                radar.azimuth['data'][radar.sweep_start_ray_index['data'][
                    self.Vtilt.value]:radar.sweep_end_ray_index['data'][
                    self.Vtilt.value] + 1] - az)) + \
                radar.sweep_start_ray_index['data'][self.Vtilt.value]
            if azindex == radar.sweep_end_ray_index['data'][self.Vtilt.value]:
                if az < 10:
                    az = az + 360.
                if np.abs(
                        radar.azimuth['data'][radar.sweep_start_ray_index[
                        'data'][self.Vtilt.value]] + 360. - az) < \
                        np.abs(radar.azimuth['data'][
                        radar.sweep_end_ray_index['data'][
                        self.Vtilt.value]] - az):
                    azindex = \
                        radar.sweep_start_ray_index['data'][self.Vtilt.value]
                else:
                    azindex = \
                        radar.sweep_end_ray_index['data'][self.Vtilt.value]

            rngindex = np.argmin(np.abs(radar.range['data'] - rng*1000.))
            if self.plot_type == 'radarPpi':
                msg1 = 'x = %4.2f, y = %4.2f, ' % (xdata, ydata)
                msg2 = 'Azimuth = %4.2f deg., Range = %4.3f km, ' % (
                    radar.azimuth['data'][azindex],
                    radar.range['data'][rngindex]/1000.)
                msg3 = '%s = %4.2f %s' % (
                    self.Vfield.value,
                    radar.fields[self.Vfield.value]['data'][azindex][rngindex],
                    self.units)
                self.msg = msg1 + msg2 + msg3
            elif self.plot_type == 'radarRhi':
                msg1 = 'x = %4.2f, y = %4.2f, ' % (xdata, ydata)
                msg2 = 'Range = %4.3f km, ' % (
                    radar.range['data'][rngindex]/1000.)
                msg3 = '%s = %4.2f %s' % (
                    self.Vfield.value,
                    radar.fields[self.Vfield.value]['data'][azindex][rngindex],
                    self.units)
                self.msg = msg1 + msg2 + msg3
            elif self.plot_type == 'radarAirborne':
                rotind = np.argmin(np.abs(radar.rotation['data'] - az))
                msg1 = 'x = %4.2f, y = %4.2f, ' % (xdata, ydata)
                msg2 = 'Angle of Rotation = %4.2f deg., Range = %4.3f km, ' % (
                    radar.rotation['data'][rotind],
                    radar.range['data'][rngindex]/1000.)
                msg3 = '%s = %4.2f %s' % (
                    self.Vfield.value,
                    radar.fields[self.Vfield.value]['data'][rotind][rngindex],
                    self.units)
                self.msg = msg1 + msg2 + msg3
            else:
                raise ValueError("Plot type not currently supported...")
        self.statusbar.showMessage(self.msg)

    def disconnect(self):
        '''Disconnect the ZoomPan instance'''
        self.fig.canvas.mpl_disconnect(self.pickPointID)

    def NewRadar(self, variable, strong=False):
        '''Update the display list when radar variable is changed.'''
        print("In NewRadar")
##########################
# Zoom/Pan Class Methods #
##########################


class ZoomPan(QtGui.QMainWindow):
    '''
    Class for Zoom and Pan of display.
    Activated through mouse drags and wheel movements.

    Modified an original answer found here:
http://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
    '''
    def __init__(self, Vlimits, ax, base_scale=2.,
                 name="ZoomPan", parent=None):
        '''
        Initialize the class to create the interface.

        Parameters::
        ----------
        Vlimits - Variable instance
            Limits signal variable to be used.
        ax - Matplotlib axis instance
            Axis instance to use.

        [Optional]
        base_scale - float
            Scaling factor to use fo Zoom/Pan
        name - string
            Field Radiobutton window name.
        parent - PyQt instance
            Parent instance to associate to ZoomPan instance.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

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
        self.Vlimits = Vlimits

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
        # self.connect()
        self.ax = ax
        self.base_scale = base_scale
        self.fig = ax.get_figure()  # get the figure of interest

    def connect(self):
        '''Connect the ZoomPan instance.'''
        self.scrollID = self.fig.canvas.mpl_connect(
            'scroll_event', self.onZoom)
        self.pressID = self.fig.canvas.mpl_connect(
            'button_press_event', self.onPress)
        self.releaseID = self.fig.canvas.mpl_connect(
            'button_release_event', self.onRelease)
        self.motionID = self.fig.canvas.mpl_connect(
            'motion_notify_event', self.onMotion)

    def onZoom(self, event):
        '''Recalculate limits when zoomed.'''
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location

        if (xdata is None) or (ydata is None):
            return

        if event.button == 'down':
            # deal with zoom in
            scale_factor = 1 / self.base_scale
        elif event.button == 'up':
            # deal with zoom out
            scale_factor = self.base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print(event.button)

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

        # Record the new limits and pass them to main window
        self.Vlimits.value['xmin'] = xdata - new_width * (1-relx)
        self.Vlimits.value['xmax'] = xdata + new_width * (relx)
        self.Vlimits.value['ymin'] = ydata - new_height * (1-rely)
        self.Vlimits.value['ymax'] = ydata + new_height * (rely)
        self.Vlimits.update()

    def onPress(self, event):
        '''Get the current event parameters.'''
        if event.inaxes != self.ax:
            return
        self.cur_xlim = self.ax.get_xlim()
        self.cur_ylim = self.ax.get_ylim()
        self.press = self.x0, self.y0, event.xdata, event.ydata
        self.x0, self.y0, self.xpress, self.ypress = self.press

    def onRelease(self, event):
        self.press = None
        self.ax.figure.canvas.draw()

    def onMotion(self, event):
        '''Redraw the plot when panned.'''
        if self.press is None:
            return
        if event.inaxes != self.ax:
            return
        dx = event.xdata - self.xpress
        dy = event.ydata - self.ypress
        self.cur_xlim -= dx
        self.cur_ylim -= dy

        # Record the new limits and pass them to main window
        limits = self.Vlimits.value
        limits['xmin'], limits['xmax'] = \
            self.cur_xlim[0], self.cur_xlim[1]
        limits['ymin'], limits['ymax'] = \
            self.cur_ylim[0], self.cur_ylim[1]
        self.Vlimits.change(limits)

    def disconnect(self):
        '''Disconnect the ZoomPan instance.'''
        self.fig.canvas.mpl_disconnect(self.scrollID)
        self.fig.canvas.mpl_disconnect(self.pressID)
        self.fig.canvas.mpl_disconnect(self.releaseID)
        self.fig.canvas.mpl_disconnect(self.motionID)

##################################
# Another Tool Method #
##################################


##########################################################
#                     Auxiliary Functions              ###
##########################################################

# XXX deprecated in favor of pyart:RadarDisplay._get_x_y_z()
def interior_radar(path, radar, tilt):
    '''
    Return the bins of the Radar in the interior of the path.

    Parameters
    ----------
    path - Matplotlib Path instance
    radar - Pyart Radar Instance
    tilt - int
        Scan from the radar to be considered.

    Returns
    -------
    xy : Numpy Array
        Array of the shape (bins,2) containing the x,y
        coordinate for every bin inside path
    index : Numpy Array
        Array of the shape (bins,2) containing the ray and range
        coordinate for every bin inside path
    '''
    az = radar.azimuth['data'][radar.sweep_start_ray_index[
        'data'][tilt]:radar.sweep_end_ray_index['data'][tilt]+1]
    r = radar.range['data'] / 1000.
    ngates = r.size
    nrays = az.size
    xys = np.empty(shape=(nrays*ngates, 2))
    r, az = np.meshgrid(r, az)
    # XXX Disconsidering elevation and Projetion
    # XXX should use pyart.io.common.radar_coords_to_cart
    # XXX but this is not public (not in user manual or Radar)
    x = r*np.sin(az * np.pi / 180.)
    y = r*np.cos(az * np.pi / 180.)
    xys[:, 0] = x.flatten()
    xys[:, 1] = y.flatten()
    # XXX in new versions (1.3) of mpl there is contains_pointS function
    ind = np.nonzero([path.contains_point(xy) for xy in xys])[0]

    rayIndex = radar.sweep_start_ray_index['data'][tilt] + ind / ngates
    gateIndex = ind % ngates
    index = np.concatenate((rayIndex[np.newaxis],
                            gateIndex[np.newaxis]), axis=0)
    return (xys[ind], index.transpose().astype(np.int))


def interior_grid(path, grid, basemap, level, plot_type):
    '''
    Return the bins of the Radar in the interior of the path.

    Parameters
    ----------
    path : Matplotlib Path instance
    grid : :py:class:`pyart.core.Grid` Instance
    level : int
        Section from the grid to be considered.
    plot_type : "gridZ", "gridY" or "gridX"
        Plot type used

    Returns
    -------
    xy : Numpy Array
        Array of the shape (bins,2) containing the x,y
        coordinate for every bin inside path
    index : Numpy Array
        Array of the shape (bins,2) containing the ray and range
        coordinate for every bin inside path
    '''
    if plot_type == "gridZ":
        x, y = np.meshgrid(grid.axes['x_disp']['data'],
                           grid.axes['y_disp']['data'])
        ny = len(grid.axes['y_disp']['data'])
        if basemap is not None:
            from mpl_toolkits.basemap import pyproj
            proj = pyproj.Proj(proj='aeqd', datum='NAD83',
                               lat_0=grid.axes['lat']['data'][0],
                               lon_0=grid.axes['lon']['data'][0])
            lat, lon = proj(x, y, inverse=True)
            x, y = basemap(lat, lon)
    elif plot_type == "gridY":
        x, y = np.meshgrid(grid.axes['x_disp']['data'] / 1000.,
                           grid.axes['z_disp']['data'] / 1000.)
        ny = len(grid.axes['z_disp']['data'])
    elif plot_type == "gridX":
        x, y = np.meshgrid(grid.axes['y_disp']['data'] / 1000.,
                           grid.axes['z_disp']['data'] / 1000.)
        ny = len(grid.axes['z_disp']['data'])

    xys = np.empty(shape=(x.size, 2))
    xys[:, 0] = x.flatten()
    xys[:, 1] = y.flatten()
    # XXX in new versions (1.3) of mpl there is contains_pointS function
    ind = np.nonzero([path.contains_point(xy) for xy in xys])[0]

    x_index = ind / ny
    y_index = ind % ny
    index = np.concatenate((x_index[np.newaxis],
                            y_index[np.newaxis]), axis=0)
    return (xys[ind], index.transpose().astype(np.int))


def nearest_point_grid(grid, basemap, zvalue, yvalue, xvalue):
    '''
    Return the nearest bins to a given position.

    Parameters
    ----------
    grid : :py:class:`pyart.core.Grid` Instance
    xvalue, yvalue, zvalue : float, list of float or array of shape (npoints,)
        position in the plot coordinate system

    Returns
    -------
    index : Numpy Array
        Array of the shape (npoints, 3) containing the index in the Z, Y ,X
        axis of grid.
    '''
    if isinstance(xvalue, (list, tuple, np.ndarray)):
        xvalue = np.array((xvalue))
    else:
        xvalue = np.array((xvalue,))
    if isinstance(yvalue, (list, tuple, np.ndarray)):
        yvalue = np.array((yvalue))
    else:
        yvalue = np.array((yvalue,))
    if isinstance(zvalue, (list, tuple, np.ndarray)):
        zvalue = np.array((zvalue))
    else:
        zvalue = np.array((zvalue,))

    if basemap is not None:
        from mpl_toolkits.basemap import pyproj
        proj = pyproj.Proj(proj='aeqd', datum='NAD83',
                           lat_0=grid.axes['lat']['data'][0],
                           lon_0=grid.axes['lon']['data'][0])
        lat, lon = proj(xvalue, yvalue, inverse=True)
        xvalue, yvalue = basemap(lat, lon)
    zdata, zvalue = np.meshgrid(grid.axes["z_disp"]["data"], zvalue)
    z_index = np.argmin(np.abs(zdata-zvalue), axis=1)
    ydata, yvalue = np.meshgrid(grid.axes["y_disp"]["data"], yvalue)
    y_index = np.argmin(np.abs(ydata-yvalue), axis=1)
    xdata, xvalue = np.meshgrid(grid.axes["x_disp"]["data"], xvalue)
    x_index = np.argmin(np.abs(xdata-xvalue), axis=1)

    index = np.concatenate((z_index[np.newaxis],
                            y_index[np.newaxis],
                            x_index[np.newaxis],), axis=0)
    return index.transpose().astype(np.int)
