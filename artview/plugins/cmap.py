"""
cmap_value.py
"""

# Load the needed packages
import numpy as np
from PyQt4 import QtGui, QtCore

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib import colors

import pyart

from .. import core, components

gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))

class ColormapEdit(core.Component):

    @classmethod
    def guiStart(self, parent=None):
        kwargs, independent = core.common._SimplePluginStart(
                                            "ColormapEdit").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vcolormap=None, name="ColormapEdit", parent=None):
        '''
        Print out Color Table Name
        '''
        super(ColormapEdit, self).__init__(name=name, parent=parent)

        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        if Vcolormap is None:
            self.Vcolormap = core.Variable(None)
        else:
            self.Vcolormap = Vcolormap

        self.sharedVariables = {"Vcolormap": self.NewColormap}
        self.connectAllVariables()

        self._set_fig_ax()
        self.createUI()

        self.NewColormap(None, True)

        self.show()

    def _set_fig_ax(self):
        '''Set the figure and axis to plot.'''
        self.fig = Figure(figsize=(2, 4))
        self.ax = self.fig.add_axes([0.0, 0.0, 0.01, 0.01])
        self.cax = self.fig.add_axes([0, 0, 0.8, 1])
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.mpl_connect('button_press_event', self.select_cmap)

    def createUI(self):
        '''
        Mount the component layout.
        '''
        self.norm_type = QtGui.QComboBox()
        self.norm_type.addItem('None (linear)')
        self.norm_type.addItem('Linear')
        self.norm_type.addItem('Logarithmic')
        self.norm_type.addItem('Symmetric logarithmic')
        self.norm_type.addItem('Power-law')
        self.norm_type.addItem('Discrete')
        self.norm_type.activated[int].connect(self.change_norm)

        self.ent_vmax = QtGui.QLineEdit()
        self.ent_vmax.editingFinished.connect(self.update_colormap)
        self.ent_vmin = QtGui.QLineEdit()
        self.ent_vmin.editingFinished.connect(self.update_colormap)

        self.ent_linthresh = QtGui.QLineEdit('0.1')
        self.ent_linthresh.editingFinished.connect(self.update_colormap)
        self.ent_linscale = QtGui.QLineEdit('1')
        self.ent_linscale.editingFinished.connect(self.update_colormap)

        self.ent_gamma = QtGui.QLineEdit('1')
        self.ent_gamma.editingFinished.connect(self.update_colormap)

        self.lock_box = QtGui.QCheckBox('lock colormap')
        self.lock_box.stateChanged.connect(self.update_colormap)
        self.layout.addWidget(self.lock_box, 6, 0, 1, 2)

        self.select_button = QtGui.QPushButton("Select cmap")
        self.select_button.clicked.connect(self.select_cmap)

        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply)

        self.add_button = QtGui.QPushButton("+ bound")
        self.add_button.clicked.connect(self.add_bound)

        self.remove_button = QtGui.QPushButton("- bound")
        self.remove_button.setEnabled(False)
        self.remove_button.clicked.connect(self.remove_bound)

        self.ent_bounds = [self.ent_vmax,
                           QtGui.QLineEdit('0'),
                           self.ent_vmin,
                           ]

        for ent in self.ent_bounds:
            ent.editingFinished.connect(self.update_colormap)

        self.set_layout()

    def set_layout(self):
        for i in reversed(range(self.layout.count())):
                widget = self.layout.itemAt(i).widget()
                self.layout.removeWidget(widget)
                widget.setParent(None)

        self.layout.addWidget(QtGui.QLabel("Normalize"), 0, 0, 1, 1)
        self.layout.addWidget(self.norm_type, 0, 1, 1, 3)
        self.layout.addWidget(self.select_button, 1, 2, 1, 1)

        idx = self.norm_type.currentIndex()
        if idx in [0, 1, 2, 3, 4]:
            self.layout.addWidget(QtGui.QLabel("Vmax"), 1, 0, 1, 1)
            self.layout.addWidget(self.ent_vmax, 1, 1, 1, 1)

            self.layout.addWidget(QtGui.QLabel("Vmin"), 5, 0, 1, 1)
            self.layout.addWidget(self.ent_vmin, 5, 1, 1, 1)

            self.layout.addWidget(self.canvas, 2, 2, 3, 1)

        if idx in [0, 1, 2]:
            self.layout.addWidget(self.lock_box, 6, 0, 1, 2)
            self.layout.addWidget(self.apply_button, 6, 2, 1, 1)
        elif idx == 3:
            self.layout.addWidget(QtGui.QLabel("linthresh"), 6, 0, 1, 1)
            self.layout.addWidget(self.ent_linthresh, 6, 1, 1, 1)

            self.layout.addWidget(QtGui.QLabel("linscale"), 7, 0, 1, 1)
            self.layout.addWidget(self.ent_linscale, 7, 1, 1, 1)

            self.layout.addWidget(self.lock_box, 8, 0, 1, 2)
            self.layout.addWidget(self.apply_button, 8, 2, 1, 1)
        elif idx == 4:
            self.layout.addWidget(QtGui.QLabel("gamma"), 6, 0, 1, 1)
            self.layout.addWidget(self.ent_gamma, 6, 1, 1, 1)

            self.layout.addWidget(self.lock_box, 7, 0, 1, 2)
            self.layout.addWidget(self.apply_button, 7, 2, 1, 1)
        elif idx ==5:
            count=0
            for ent in self.ent_bounds:
                self.layout.addWidget(ent, 2 * count + 1, 0, 1, 2)
                count += 1

            self.layout.addWidget(self.canvas, 2, 2, 2 * count - 3, 1)
            self.layout.addWidget(self.add_button, 2 * count, 0, 1, 1)
            self.layout.addWidget(self.remove_button, 2 * count, 1, 1, 1)
            self.layout.addWidget(self.lock_box, 2 * count + 1, 0, 1, 2)
            self.layout.addWidget(self.apply_button, 2 * count + 1, 2, 1, 1)

    def plot(self):
        '''Replot the colorbar.'''
        if self.cmap is None:
            return

        self.ax.cla()
        self.cax.cla()
        cmap = self.cmap
        if 'norm' not in cmap or cmap['norm'] is None:
            self.norm_type.setCurrentIndex(0)
        else:
            norm_name = cmap['norm'].__class__.__name__
            if norm_name == 'Normalize':
                self.norm_type.setCurrentIndex(1)
            elif norm_name == 'LogNorm':
                self.norm_type.setCurrentIndex(2)
            elif norm_name == 'SymLogNorm':
                self.norm_type.setCurrentIndex(3)
            elif norm_name == 'PowerNorm':
                self.norm_type.setCurrentIndex(4)
            elif norm_name == 'BoundaryNorm':
                self.norm_type.setCurrentIndex(5)

        if cmap is not None:
            if 'norm' in cmap:
                norm = cmap['norm']
            else:
                norm = None
            im = self.ax.imshow(gradient, aspect='auto', cmap=cmap['cmap'],
                                vmin=cmap['vmin'], vmax=cmap['vmax'], norm=norm)
            plt.colorbar(im, cax=self.cax)

        self.canvas.draw()

    def change_norm(self, idx):
        self.set_layout()
        self.update_colormap()

    def update_colormap(self):
        '''Get colormap from GUI.'''
        self.cmap['lock'] = self.lock_box.isChecked()
        idx = self.norm_type.currentIndex()

        self.cmap['vmin'] = float(self.ent_vmin.text())
        self.cmap['vmax'] = float(self.ent_vmax.text())

        if idx == 0:
            self.cmap['norm'] = None
        elif idx == 1:
            self.cmap['norm'] = colors.Normalize(vmin=self.cmap['vmin'],
                                                 vmax=self.cmap['vmax'])
        elif idx == 2:
            self.cmap['norm'] = colors.LogNorm(vmin=self.cmap['vmin'],
                                               vmax=self.cmap['vmax'])
        elif idx == 3:
            self.cmap['norm'] = colors.SymLogNorm(
                linthresh=float(self.ent_linthresh.text()),
                linscale=float(self.ent_linscale.text()),
                vmin=self.cmap['vmin'],
                vmax=self.cmap['vmax'])
        elif idx == 4:
            self.cmap['norm'] = colors.PowerNorm(
                gamma=float(self.ent_gamma.text()),
                vmin=self.cmap['vmin'],
                vmax=self.cmap['vmax'])
        elif idx == 5:
            bounds = self.get_bounds()
            self.cmap['norm'] = colors.BoundaryNorm(bounds,
                                                    ncolors=256)
        self.plot()

    def select_cmap(self, post):
        '''Select cmap from a list of pyart colormaps.'''
        cmap = core.common.select_cmap().selection
        if cmap is not None:
            self.cmap['cmap'] = cmap
            self.plot()

    def apply(self):
        '''Apply changes to shared colormap.'''
        self.update_colormap()
        self.Vcolormap.change(self.cmap)

    def get_bounds(self):
        return [float(ent.text()) for ent in reversed(self.ent_bounds)]

    def add_bound(self):
        self.ent_bounds.insert(-1, QtGui.QLineEdit(self.ent_bounds[-1].text()))
        self.ent_bounds[-1].editingFinished.connect(self.update_colormap)
        self.remove_button.setEnabled(True)
        self.set_layout()
        self.update_colormap()

    def remove_bound(self):
        self.ent_bounds.pop(-2)
        if len(self.ent_bounds) < 4:
            self.remove_button.setEnabled(False)
        self.set_layout()
        self.update_colormap()

    def NewColormap(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vfield <artview.core.core.Variable>`.

        This will:

        * replot colorbar
        '''
        cmap = self.Vcolormap.value
        if cmap is not None:
            self.cmap = dict(cmap)
            self.ent_vmin.setText(str(cmap['vmin']))
            self.ent_vmax.setText(str(cmap['vmax']))
            self.lock_box.setChecked(cmap['lock'])

        else:
            self.cmap = cmap
        self.plot()

_plugins = [ColormapEdit]

radar_mode = (
    [components.Menu, components.RadarDisplay, ColormapEdit],
    [
        ((1, 'Vcolormap'), (2, 'Vcolormap')),
        ]
    )

grid_mode = (
    [components.Menu, components.GridDisplay, ColormapEdit],
    [
        ((1, 'Vcolormap'), (2, 'Vcolormap')),
        ]
    )

_modes = [
    {'label': 'Edit Colormap (radar)',
     'group': 'graph',
     'action': radar_mode},
    {'label': 'Edit Colormap (grid)',
     'group': 'graph',
     'action': grid_mode},
    ]

