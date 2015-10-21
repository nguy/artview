"""
tree_view.py
"""

# Load the needed packages
import code
import pyart

import sys
import os

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '...')
sys.path.insert(0, path)

import artview

from ..core import Component, Variable, common, QtGui, QtCore, componentsList

open_functions = [
    pyart.io.read,
    pyart.io.read_grid,
    pyart.io.read_grid_mdv,
    pyart.aux_io.read_d3r_gcpex_nc,
    pyart.aux_io.read_gamic,
    pyart.aux_io.read_kazr,
    pyart.aux_io.read_noxp_iphex_nc,
    pyart.aux_io.read_odim_h5,
    pyart.aux_io.read_pattern,
    pyart.aux_io.read_radx]


class FileList(Component):
    '''
    Open an interactive python console so the direct manipulation
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("FileList").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent
        return self(), False

    def __init__(self, dirIn=None, name="FileList", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        dirIn: string
            Initial directory path to open.
        name : string
            Field Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(FileList, self).__init__(name=name, parent=parent)
        self.listView = QtGui.QListView()

        # set up listView
        model = QtGui.QFileSystemModel()
        model.setFilter(QtCore.QDir.AllEntries |
                        QtCore.QDir.AllDirs |
                        QtCore.QDir.NoDot)
        model.setRootPath(QtCore.QDir.currentPath())
        self.listView.setModel(model)
        if dirIn is None:  # avoid reference to path while building doc
            dirIn = os.getcwd()
        index = model.index(dirIn)
        self.listView.setRootIndex(index)
        # self.clicked.connect(self.test)
        self.listView.doubleClicked.connect(self.doubleClick)
        # context (right-click) menu
        self.listView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # setup widget
        self.setCentralWidget(self.listView)
        self.listView.customContextMenuRequested.connect(self.contextMenu)
        self.Vradar = Variable(None)
        self.Vgrid = Variable(None)
        self.sharedVariables = {"Vradar": None,
                                "Vgrid": None}
        self.connectAllVariables()
        self.show()

    def doubleClick(self, index):
        '''Open Directory or File on double click.'''
        model = self.listView.model()
        indexItem = model.index(index.row(), 0, index.parent())
        if model.fileName(indexItem) == '..':
            if index.parent().parent().isValid():
                self.listView.setRootIndex(index.parent().parent())
        elif model.isDir(index):
            self.listView.setRootIndex(index)
        else:
            self.open(model.filePath(indexItem))

    def open(self, path):
        '''Open file.'''
        # try several open
        print ("open: %s" % path)
        self.filename = str(path)
        try:
            radar = pyart.io.read(self.filename, delay_field_loading=True)
            # Add the filename for Display
            radar.filename = self.filename
            self.Vradar.change(radar)
            return
        except:
            try:
                radar = pyart.io.read(self.filename)
                # Add the filename for Display
                radar.filename = self.filename
                self.Vradar.change(radar)
                return
            except:
                import traceback
                print(traceback.format_exc())
                radar_warning = True
        try:
            grid = pyart.io.read_grid(
                self.filename, delay_field_loading=True)
            self.Vgrid.change(grid)
            return
        except:
            try:
                grid = pyart.io.read_grid(self.filename)
                self.Vgrid.change(grid)
                return
            except:
                import traceback
                print(traceback.format_exc())
                grid_warning = True

        if grid_warning or radar_warning:
            msg = "Py-ART didn't recognize this file!"
            common.ShowWarning(msg)
        else:
            msg = "Could not open file, invalid mode!"
            common.ShowWarning(msg)
        return

    def contextMenu(self, pos):
        '''Contruct right-click menu.'''
        menu = QtGui.QMenu(self)
        index = self.listView.currentIndex()
        path = str(self.listView.model().filePath(index))
        for func in open_functions:
            action = QtGui.QAction("Open with: %s" % func.__name__, self)
            # lambda inside loop: problem with variable capturing
            f = lambda boo, func=func: self.open_with(func, path)
            action.triggered.connect(f)
            menu.addAction(action)
        menu.exec_(self.listView.mapToGlobal(pos))

    def open_with(self, func, path):
        '''Open file using a given function.'''
        try:
            container = func(path, delay_field_loading=True)
            if isinstance(container, pyart.core.Radar):
                self.Vradar.change(container)
            elif isinstance(container, pyart.core.Grid):
                self.Vgrid.change(container)
            else:
                raise NotImplementedError("Unknown container type %s\n" %
                                          container)
            return
        except:
            import traceback
            error = traceback.format_exc()
            common.ShowLongText(("Opening file %s with %s fails\n\n" %
                                 (path, func.__name__)) + error)
            traceback.format_exc()


_plugins = [FileList]
