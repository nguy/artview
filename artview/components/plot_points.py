"""
plot_points.py

Class instance used to plot information over a set of points.
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


class PointsDisplay(Component):
    '''
    Class to create a display plot, using data from a Points instance.
    '''

    Vpoints = None  #: see :ref:`shared_variable`
    Vfield = None  #: see :ref:`shared_variable`
    Vlimits = None  #: see :ref:`shared_variable`
    Vcolormap = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class'''
        kwargs, independent = \
            common._SimplePluginStart("PointsDisplay").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vpoints=None, Vfield=None, Vlimits=None, Vcolormap=None,
                 plot_type="histogram", name="PointsDisplay", parent=None):
        '''
        Initialize the class to create display.

        Parameters
        ----------
        [Optional]
        Vpoints : :py:class:`~artview.core.core.Variable` instance
            Points signal variable. If None start new one with None.
        Vfield : :py:class:`~artview.core.core.Variable` instance
            Field signal variable. If None start new one with empty string.
        Vlimits : :py:class:`~artview.core.core.Variable` instance
            Limits signal variable.
            A value of None will instantiate a limits variable.
        Vcolormap : :py:class:`~artview.core.core.Variable` instance
            Colormap signal variable.
            A value of None will instantiate a colormap variable.
        plot_type : str
            Type of plot to produce (e.g. histogram, statistics, table).
        name : string
            Display window name.
        parent : PyQt instance
            Parent instance to associate to Display window.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        '''
        super(PointsDisplay, self).__init__(name=name, parent=parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        if Vpoints is None:
            self.Vpoints = Variable(None)
        else:
            self.Vpoints = Vpoints

        if Vfield is None:
            self.Vfield = Variable('')
        else:
            self.Vfield = Vfield

        if Vlimits is None:
            self.Vlimits = Variable({})
        else:
            self.Vlimits = Vlimits

        if Vcolormap is None:
            self.Vcolormap = Variable(None)
        else:
            self.Vcolormap = Vcolormap

        self.sharedVariables = {"Vpoints": self.NewPoints,
                                "Vfield": self.NewField,
                                "Vlimits": self.NewLimits,
                                "Vcolormap": self.NewColormap,
                                }

        # Connect the components
        self.connectAllVariables()

        # Set plot title and colorbar units to defaults
        self.title = self._get_default_title()
        self.units = self._get_default_units()

        # Find the PyArt colormap names
        self.cm_names = ["pyart_" + m for m in pyart.graph.cm.datad
                         if not m.endswith("_r")]
        self.cm_names.sort()

        # Create a figure for output
        self._set_fig_ax()

        # Launch the GUI interface
        self.LaunchGUI()

        # Set up Default limits and cmap
        if Vcolormap is None:
            self._set_default_cmap(strong=False)
        if Vlimits is None:
            self._set_default_limits(strong=False)

        self.plot_type = None
        self.changePlotType(plot_type)

        self.show()

    ####################
    # GUI methods #
    ####################

    def LaunchGUI(self):
        '''Launches a GUI interface.'''
        # Create layout
        self.layout = QtGui.QVBoxLayout()

        # Create the widget
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self._set_figure_canvas()

        self.central_widget.setLayout(self.layout)

        # Add Menu
        self.addStandardMenu()

        # Set the status bar to display messages
        self.statusbar = self.statusBar()

    def addStandardMenu(self):
        '''Add Standard Menus.'''
        self.menubar = self.menuBar()

        self.filemenu = self.menubar.addMenu('File')

        openCSV = self.filemenu.addAction('Open Tabular Data')
        openCSV.setStatusTip('Open a Region Data CSV file')
        openCSV.triggered.connect(self.openTable)

        saveCSV = self.filemenu.addAction('Save Tabular Data')
        saveCSV.setStatusTip('Save a Region Data CSV file')
        saveCSV.triggered.connect(self.saveTable)

        self.plotTypeMenu = self.menubar.addMenu('Plot Type')

        hist = self.plotTypeMenu.addAction('Histogram')
        hist.setStatusTip('Plot histogram of Data ')
        hist.triggered.connect(lambda: self.changePlotType('histogram'))

        stats = self.plotTypeMenu.addAction('Statistics')
        stats.setStatusTip('Show basic statistics of Data')
        stats.triggered.connect(lambda: self.changePlotType('statistics'))

        table = self.plotTypeMenu.addAction('Table')
        table.setStatusTip('Show data in a Table')
        table.triggered.connect(lambda: self.changePlotType('table'))

        self.displayMenu = self.menubar.addMenu('Display')

    ##################################
    # User display interface methods #
    ##################################

    #############################
    # Functionality methods #
    #############################

    def changePlotType(self, plot_type):

        try:
            if self.plot_type == 'histogram':
                self.layout.removeWidget(self.canvas)
                self.canvas.hide()
            elif self.plot_type == 'statistics':
                self.layout.removeWidget(self.statistics)
                self.statistics.close()
            elif self.plot_type == 'table':
                self.layout.removeWidget(self.table)
                self.table.close()
        except:
            pass

        self.plot_type = plot_type
        self.displayMenu.clear()

        if plot_type == 'histogram':
            self._fill_histogram_menu()
            # Add the widget to the canvas
            self.layout.addWidget(self.canvas, 0)
            self.canvas.show()
        elif plot_type == 'statistics':
            pass
        elif plot_type == 'table':
            pass

        self._update_plot()

    def _open_LimsDialog(self):
        '''Open a dialog box to change display limits.'''
        from .limits import limits_dialog
        limits, cmap, aspect, change = limits_dialog(
            self.Vlimits.value, self.Vcolormap.value, self.ax.get_aspect(),
            self.name)
        if aspect != self.ax.get_aspect():
            self.ax.set_aspect(aspect)
        if change == 1:
            self.Vcolormap.change(cmap)
            self.Vlimits.change(limits)

    def _title_input(self):
        '''Retrieve new plot title.'''
        val, entry = common.string_dialog_with_reset(
            self.title, "Plot Title", "Title:", self._get_default_title())
        if entry is True:
            self.title = val
            self._update_plot()

    def _units_input(self):
        '''Retrieve new plot units.'''
        val, entry = common.string_dialog_with_reset(
            self.units, "Plot Units", "Units:", self._get_default_units())
        if entry is True:
            self.units = val
            self._update_plot()

    def _fill_histogram_menu(self):
        '''Create the Display Options Button menu.'''

        self.dispButton = QtGui.QPushButton("Display Options")
        self.dispButton.setToolTip("Adjust display properties")
        self.dispButton.setFocusPolicy(QtCore.Qt.NoFocus)
        dispmenu = QtGui.QMenu(self)
        dispLimits = self.displayMenu.addAction("Adjust Display Limits")
        dispLimits.setToolTip("Set data, X, and Y range limits")
#        dispTitle = dispmenu.addAction("Change Title")
#        dispTitle.setToolTip("Change plot title")
#        dispUnit = dispmenu.addAction("Change Units")
#        dispUnit.setToolTip("Change units string")
        dispSaveFile = self.displayMenu.addAction("Save Image")
        dispSaveFile.setShortcut("Ctrl+S")
        dispSaveFile.setStatusTip("Save Image using dialog")
#        dispHelp = self.displayMenu.addAction("Help")

        dispLimits.triggered.connect(self._open_LimsDialog)
#        dispTitle.triggered.connect(self._title_input)
#        dispUnit.triggered.connect(self._units_input)
        dispSaveFile.triggered.connect(self._savefile)
#        dispHelp.triggered.connect(self._displayHelp) #XXX help is out dated

    def _displayHelp(self):
        text = (
            "<b>Using the PlotPoints Display</b><br><br>"
            "<i>Purpose</i>:<br>"
            "Display a plot of selected points.<br><br>"
            "The limits dialog is a common format that allows the user "
            "change:<br>"
            "<i>X and Y limits<br>"
            "Data limits</i><br>"
            "However, not all plots take each argument.<br>"
            "For example, a simple line plot has no data min/max data "
            "value.<br>")

        common.ShowLongText(text, set_html=True)

    def NewPoints(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vradar <artview.core.core.Variable>`.

        This will:

        * Update fields and tilts lists and MenuBoxes
        * Check radar scan type and reset limits if needed
        * Reset units and title
        * If strong update: update plot
        '''
        # test for None
        if self.Vpoints.value is None:
            # self.fieldBox.clear()
            return

        # Get field names
        self.fieldnames = self.Vpoints.value.fields.keys()

#        self._fillFieldBox()

        self.units = self._get_default_units()
        self.title = self._get_default_title()
        if strong:
            self._update_plot()
#            self._update_infolabel()

    def NewField(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vfield <artview.core.core.Variable>`.

        This will:

        * Reset colormap
        * Reset units
        * Update fields MenuBox
        * If strong update: update plot
        '''
        if self.Vcolormap.value['lock'] is False:
            self._set_default_cmap(strong=False)
        self.units = self._get_default_units()
        self.title = self._get_default_title()
#        idx = self.fieldBox.findText(variable.value)
#        self.fieldBox.setCurrentIndex(idx)
        if strong:
            self._update_plot()
#            self._update_infolabel()

    def NewLimits(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vlimits <artview.core.core.Variable>`.

        This will:

        * If strong update: update axes
        '''
        if strong:
            self._update_axes()

    def NewColormap(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vcolormap <artview.core.core.Variable>`.

        This will:

        * If strong update: update plot
        '''
        if strong:
            pass
            # self._update_plot()

    ########################
    # Selectionion methods #
    ########################

    ####################
    # Plotting methods #
    ####################

    def _set_fig_ax(self):
        '''Set the figure and axis to plot.'''
        self.XSIZE = 5
        self.YSIZE = 5
        self.fig = Figure(figsize=(self.XSIZE, self.YSIZE))
        self.ax = self.fig.add_axes([0.2, 0.2, 0.7, 0.7])

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area.'''
        self.canvas = FigureCanvasQTAgg(self.fig)

    def _update_plot(self):
        '''Draw/Redraw the plot.'''

        if self.Vpoints.value is None:
            return

        # Create the plot with PyArt PlotDisplay
        self.ax.cla()  # Clear the plot axes

        # Reset to default title if user entered nothing w/ Title button

        colorbar_flag = False

        points = self.Vpoints.value
        field = self.Vfield.value
        cmap = self.Vcolormap.value

        if field not in points.fields.keys():
            self.canvas.draw()
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;" +
                                         "background:rgba(255,0,0,255);" +
                                         "color:black;font-weight:bold;}")
            self.statusbar.showMessage("Field not Found", msecs=5000)
            return
        else:
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;" +
                                         "background:rgba(0,0,0,0);" +
                                         "color:black;font-weight:bold;}")
            self.statusbar.clearMessage()

        if self.plot_type == "histogram":
            self.plot = self.ax.hist(
                points.fields[field]['data'], bins=25,
                range=(cmap['vmin'], cmap['vmax']),
                figure=self.fig)
            self.ax.set_ylabel("Counts")

            # If limits exists, update the axes otherwise retrieve
            # self._update_axes()
            self._update_limits()

            # If the colorbar flag is thrown, create it
            if colorbar_flag:
                # Clear the colorbar axes
                self.cax.cla()
                self.cax = self.fig.add_axes([0.2, 0.10, 0.7, 0.02])
                norm = mlabNormalize(vmin=cmap['vmin'],
                                     vmax=cmap['vmax'])
                self.cbar = mlabColorbarBase(self.cax, cmap=self.cm_name,
                                             norm=norm,
                                             orientation='horizontal')
                # colorbar - use specified units or default depending on
                # what has or has not been entered
                self.cbar.set_label(self.units)

            self.canvas.draw()

        elif self.plot_type == 'statistics':
            if (self.Vpoints.value is None or
                self.Vfield.value not in self.Vpoints.value.fields):
                common.ShowWarning("Please select Region and Field first")
            else:
                points = self.Vpoints.value
                field = self.Vfield.value
                SelectRegionstats = common._array_stats(
                    points.fields[field]['data'])
                text = ("<b>Basic statistics for the selected Region</b>"
                        "<br><br>")
                for stat in SelectRegionstats:
                    text += ("<i>%s</i>: %5.2f<br>" %
                             (stat, SelectRegionstats[stat]))
                self.statistics = QtGui.QDialog()
                layout = QtGui.QGridLayout(self.statistics)
                self.statistics = QtGui.QTextEdit("")
                self.statistics.setAcceptRichText(True)
                self.statistics.setReadOnly(True)
                self.statistics.setText(text)
                self.layout.addWidget(self.statistics, 0)

        elif self.plot_type == "table":
            if self.Vpoints.value is not None:
                # Instantiate Table
                self.table = common.CreateTable(self.Vpoints.value)
                self.layout.addWidget(self.table, 0)
                self.table.display()
                # Show the table
                self.table.show()
            else:
                common.ShowWarning("Please select or open Region first")

    def _update_axes(self):
        '''Change the Plot Axes.'''
        limits = self.Vlimits.value
        self.ax.set_xlim(limits['xmin'], limits['xmax'])
        self.ax.set_ylim(limits['ymin'], limits['ymax'])
        self.canvas.draw()

    def _update_limits(self):
        limits = self.Vlimits.value
        ax = self.ax.get_xlim()
        limits['xmin'] = ax[0]
        limits['xmax'] = ax[1]
        ax = self.ax.get_ylim()
        limits['ymin'] = ax[0]
        limits['ymax'] = ax[1]
        self.Vlimits.update()

    def _set_default_cmap(self, strong=True):
        ''' Set colormap to pre-defined default.'''
        cmap = pyart.config.get_field_colormap(self.Vfield.value)
        d = {}
        d['cmap'] = cmap
        d['lock'] = False
        lims = pyart.config.get_field_limits(self.Vfield.value,
                                             self.Vpoints.value)
        if lims != (None, None):
            d['vmin'] = lims[0]
            d['vmax'] = lims[1]
        else:
            d['vmin'] = -10
            d['vmax'] = 65
        self.Vcolormap.change(d, False)

    def _set_default_limits(self, strong=True):
        ''' Set limits to pre-defined default.'''
        cmap = self.Vcolormap.value
        d = {}
        d['xmin'] = cmap['vmin']
        d['xmax'] = cmap['vmax']
        d['ymin'] = 0
        d['ymax'] = 1000
        self.Vlimits.change(d, False)

    def _get_default_title(self):
        '''Get default title.'''
        if (self.Vpoints.value is None or
            self.Vfield.value not in self.Vpoints.value.fields):
            return ''
        return 'Points Plot'
        # pyart.graph.common.generate_title(self.Vpoints.value,
        #                                  self.Vfield.value,
        #                                  0)

    def _get_default_units(self):
        '''Get default units for current radar and field.'''
        if self.Vpoints.value is not None:
            try:
                return self.Vpoints.value.fields[self.Vfield.value]['units']
            except:
                return ''
        else:
            return ''

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

    def openTable(self):
        '''Open a saved table of SelectRegion points from a CSV file.'''
        path = QtGui.QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV(*.csv)')
        if path == '':
            return
        points = read_points_csv(path)
        self.Vpoints.change(points)

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
