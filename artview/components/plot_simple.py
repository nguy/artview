"""
plot_simple.py

Class instance used to make a minor Display.
"""
# Load the needed packages
import numpy as np
import os
import pyart

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as \
    NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import Normalize as mlabNormalize
from matplotlib.colorbar import ColorbarBase as mlabColorbarBase
from matplotlib.pyplot import cm

from ..core import Variable, Component, common, VariableChoose, QtGui, QtCore

# Save image file type and DPI (resolution)
IMAGE_EXT = 'png'
DPI = 200
# ========================================================================


class PlotDisplay(Component):
    '''
    Class to create a display plot, using data and a key for plot type.
    '''

    def __init__(self, data, ydata=None, plot_type=None,
                 title=None, xlabel=None, ylabel=None,
                 name="PlotDisplay", parent=None):
        '''
        Initialize the class to create display.

        Parameters
        ----------
        data : data array
            The data to be plotted.
        [Optional]
        plot_type : str
            Type of plot to produce (e.g. plot, barplot, etc).
        name : string
            Display window name.
        parent : PyQt instance
            Parent instance to associate to Display window.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        Notes
        -----
        This class records the selected button and passes the
        change value back to variable.
        '''
        super(PlotDisplay, self).__init__(name=name, parent=parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.data = data
        self.ydata = ydata
        self.plot_type = plot_type

        # Set plot title and colorbar units to defaults
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.units = None
        self.limits = None

        # Find the PyArt colormap names
        self.cm_names = ["pyart_" + m for m in pyart.graph.cm.datad
                         if not m.endswith("_r")]
        self.cm_names.sort()

        # Create a figure for output
        self._set_fig_ax()

        # Launch the GUI interface
        self.LaunchGUI()

        # Create the plot
        self._update_plot()
#        self.NewRadar(None, None, True)

        self.show()

    ####################
    # GUI methods #
    ####################

    def LaunchGUI(self):
        '''Launches a GUI interface.'''
        # Create layout
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(4)

        # Create the widget
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self._set_figure_canvas()

        self.central_widget.setLayout(self.layout)

        # Add buttons along display for user control
        self.addButtons()
        self.setUILayout()

        # Set the status bar to display messages
        self.statusbar = self.statusBar()

    ##################################
    # User display interface methods #
    ##################################
    def addButtons(self):
        '''Add a series of buttons for user control over display.'''
        # Create the Display controls
        self._add_displayBoxUI()

    def setUILayout(self):
        '''Setup the button/display UI layout.'''
        self.layout.addWidget(self.dispButton, 0, 1)

    #############################
    # Functionality methods #
    #############################

    def _open_LimsDialog(self):
        '''Open a dialog box to change display limits.'''
        from .limits import limits_dialog
        limits, cmap, aspect, change = limits_dialog(
            self.limits, self.cmap, self.ax.get_aspect(), self.name)
        if aspect != self.ax.get_aspect():
            self.ax.set_aspect(aspect)
        if change == 1:
            self.cmap = cmap
            self.limits = limits
            self._update_plot()

    def _title_input(self):
        '''Retrieve new plot title.'''
        val, entry = common.string_dialog(self.title, "Plot Title", "Title:")
        if entry is True:
            self.title = val
            self._update_plot()

    def _units_input(self):
        '''Retrieve new plot units.'''
        val, entry = common.string_dialog(self.units, "Plot Units", "Units:")
        if entry is True:
            self.units = val
            self._update_plot()

    def _add_cmaps_to_button(self):
        '''Add a menu to change colormap used for plot.'''
        for cm_name in self.cm_names:
            cmapAction = self.dispCmapmenu.addAction(cm_name)
            cmapAction.setStatusTip("Use the %s colormap" % cm_name)
            cmapAction.triggered[()].connect(
                lambda cm_name=cm_name: self.cmapSelectCmd(cm_name))
            self.dispCmap.setMenu(self.dispCmapmenu)

    def _add_displayBoxUI(self):
        '''Create the Display Options Button menu.'''
        self.dispButton = QtGui.QPushButton("Display Options")
        self.dispButton.setToolTip("Adjust display properties")
        self.dispButton.setFocusPolicy(QtCore.Qt.NoFocus)
        dispmenu = QtGui.QMenu(self)
        dispLimits = dispmenu.addAction("Adjust Display Limits")
        dispLimits.setToolTip("Set data, X, and Y range limits")
        dispTitle = dispmenu.addAction("Change Title")
        dispTitle.setToolTip("Change plot title")
        dispUnit = dispmenu.addAction("Change Units")
        dispUnit.setToolTip("Change units string")
#        toolZoomPan = dispmenu.addAction("Zoom/Pan")
        self.dispCmap = dispmenu.addAction("Change Colormap")
        self.dispCmapmenu = QtGui.QMenu("Change Cmap")
        self.dispCmapmenu.setFocusPolicy(QtCore.Qt.NoFocus)
        dispSaveFile = dispmenu.addAction("Save Image")
        dispSaveFile.setShortcut("Ctrl+S")
        dispSaveFile.setStatusTip("Save Image using dialog")
        self.dispHelp = dispmenu.addAction("Help")

        dispLimits.triggered[()].connect(self._open_LimsDialog)
        dispTitle.triggered[()].connect(self._title_input)
        dispUnit.triggered[()].connect(self._units_input)
#        toolZoomPan.triggered[()].connect(self.toolZoomPanCmd)
        dispSaveFile.triggered[()].connect(self._savefile)
        self.dispHelp.triggered[()].connect(self._displayHelp)

        self._add_cmaps_to_button()
        self.dispButton.setMenu(dispmenu)

    def _displayHelp(self):
        '''Launch pop-up help window.'''
        text = (
            "<b>Using the Simple Plot Feature</b><br><br>"
            "<i>Purpose</i>:<br>"
            "Display a plot.<br><br>"
            "The limits dialog is a common format that allows the user "
            "change:<br>"
            "<i>X and Y limits<br>"
            "Data limits</i><br>"
            "However, not all plots take each argument.<br>"
            "For example, a simple line plot has no data min/max data "
            "value.<br>")

        common.ShowLongText(text)

    ########################
    # Selectionion methods #
    ########################

#     def _create_plot(self):
#         '''
#         Create a plot
#         '''
#         # test for None
#         if self.Vradar.value is None:
#             self.fieldBox.clear()
#             self.tiltBox.clear()
#             return
#
#         # Get the tilt angles
#         self.rTilts = self.Vradar.value.sweep_number['data'][:]
#         # Get field names
#         self.fieldnames = self.Vradar.value.fields.keys()
#
#         # Check the file type and initialize limts
#         self._check_file_type()
#
#         # Update field and tilt MenuBox
#         self._fillTiltBox()
#         self._fillFieldBox()
#
#         self.units = None
#         if strong:
#             self._update_plot()

#     def NewLimits(self, variable, strong):
#         '''
#         Slot for 'ValueChanged' signal of
#         :py:class:`Vlimits <artview.core.core.Variable>`.
#
#         This will:
#
#         * If strong update: update axes
#         '''
#         if strong:
#             self._update_axes()

#     def NewColormap(self, variable, strong):
#         '''
#         Slot for 'ValueChanged' signal of
#         :py:class:`Vcolormap <artview.core.core.Variable>`.
#
#         This will:
#
#         * If strong update: update plot
#         '''
#         if strong and self.Vradar.value is not None:
#             self._update_plot()

    def cmapSelectCmd(self, cm_name):
        '''Captures colormap selection and redraws.'''
        self.cmap['cmap'] = cm_name
#        self.Vcolormap.value['cmap'] = cm_name
#        self.Vcolormap.update()

#    def toolZoomPanCmd(self):
#        '''Creates and connects to a Zoom/Pan instance.'''
#        from .tools import ZoomPan
#        scale = 1.1
#        self.tools['zoompan'] = ZoomPan(
#            self.limits, self.ax,
#            base_scale=scale, parent=self.parent)
#        self.tools['zoompan'].connect()

    ####################
    # Plotting methods #
    ####################

    def _set_fig_ax(self):
        '''Set the figure and axis to plot.'''
        self.XSIZE = 5
        self.YSIZE = 5
        self.fig = Figure(figsize=(self.XSIZE, self.YSIZE))
        self.ax = self.fig.add_axes([0.2, 0.2, 0.7, 0.7])

#    def _update_fig_ax(self):
#        '''Set the figure and axis to plot.'''
#        if self.plot_type in ("radarAirborne", "radarRhi"):
#            self.YSIZE = 5
#        else:
#            self.YSIZE = 8
#        xwidth = 0.7
#        yheight = 0.7 * float(self.YSIZE) / float(self.XSIZE)
#        self.ax.set_position([0.2, 0.55-0.5*yheight, xwidth, yheight])
#        self.cax.set_position([0.2, 0.10, xwidth, 0.02])
#        self._update_axes()

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area.'''
        self.canvas = FigureCanvasQTAgg(self.fig)
        # Add the widget to the canvas
        self.layout.addWidget(self.canvas, 1, 0, 4, 3)

    def _update_plot(self):
        '''Draw/Redraw the plot.'''

        # Create the plot with PyArt PlotDisplay
        self.ax.cla()  # Clear the plot axes

        # Reset to default title if user entered nothing w/ Title button
        if self.title == '':
            title = None
        else:
            title = self.title

        colorbar_flag = False

        self.cmap = {'vmin': self.data.min(), 'vmax': self.data.max(),
                     'cmap': 'pyart_RefDiff'}

        if self.plot_type == "hist":
            self.plot = self.ax.hist(
                self.data, bins=25,
                range=(self.cmap['vmin'], self.cmap['vmax']),
                figure=self.fig)
            self.ax.set_ylabel("Counts")
            if self.xlabel:
                self.ax.set_xlabel(self.xlabel)

        elif self.plot_type == "hist2d":
            # Check that y data was provided
            if self.ydata:
                y = self.ydata
            # Create Plot
            self.plot = self.ax.hist2d(
                self.data, y, bins=[25, 20],
                range=([self.cmap['vmin'], self.cmap['vmax']],
                       [y.min(), y.max()]),
                cmap=self.cm_name,
                figure=self.fig)
            colorbar_flag = True

        elif self.plot_type == "plot":
            # Check that y data was provided
            if self.ydata:
                y = self.ydata
            # Create Plot
            self.plot = self.ax.plot(self.data, y, figure=self.fig)

        # Set the axis labels if arguments passed
        if self.xlabel:
            self.ax.set_xlabel(self.xlabel)
        if self.ylabel:
            self.ax.set_ylabel(self.ylabel)

        # If limits exists, update the axes otherwise retrieve
        if self.limits:
            self._update_axes()
        else:
            self._get_axes_limits()

        # Set the title if passed
        if title is not None:
            self.ax.set_title(title)

        # If the colorbar flag is thrown, create it
        if colorbar_flag:
            # Clear the colorbar axes
            self.cax.cla()
            self.cax = self.fig.add_axes([0.2, 0.10, 0.7, 0.02])
            norm = mlabNormalize(vmin=self.cmap['vmin'],
                                 vmax=self.cmap['vmax'])
            self.cbar = mlabColorbarBase(self.cax, cmap=self.cm_name,
                                         norm=norm, orientation='horizontal')
            # colorbar - use specified units or default depending on
            # what has or has not been entered
            if self.units is None or self.units == '':
                self.units = ''
            self.cbar.set_label(self.units)

        self.canvas.draw()

    def _update_axes(self):
        '''Change the Plot Axes.'''
        self.ax.set_xlim(self.limits['xmin'], self.limits['xmax'])
        self.ax.set_ylim(self.limits['ymin'], self.limits['ymax'])
        self.ax.figure.canvas.draw()

    def _get_axes_limits(self):
        '''Get the axes limits'''
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.limits = {}
        self.limits['xmin'] = xlim[0]
        self.limits['xmax'] = xlim[1]
        self.limits['ymin'] = ylim[0]
        self.limits['ymax'] = ylim[1]

    ########################
    # Image save methods #
    ########################

    def _savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display using PyQt dialog interface.'''
        file_choices = "PNG (*.png)|*.png"
        path = unicode(QtGui.QFileDialog.getSaveFileName(
            self, 'Save file', ' ', file_choices))
        if path:
            self.canvas.print_figure(path, dpi=DPI)
            self.statusbar.showMessage('Saved to %s' % path)
