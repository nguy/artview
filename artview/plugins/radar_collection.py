"""
radar_collection.py

Classes for interaction with files.
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

from ..core import Component, Variable, common, QtGui, QtCore

# get list of read functions
import inspect
aux_read_functions = inspect.getmembers(pyart.aux_io, inspect.isfunction)
read_functions = [
    pyart.io.read,
    pyart.io.read_grid,
    pyart.io.read_grid_mdv] + [a[1] for a in aux_read_functions]
try:
    read_functions.append(pyart.io.read_legacy_grid)
except:
    pass

# test for missing dependency
broken_read_functions = []
try:
    for func in read_functions:
        try:
            func(None)
        except pyart.exceptions.MissingOptionalDependency:
            broken_read_functions.append(func)
        except:
            pass
except:
    pass


class RadarCollectionView(Component):
    '''
    Add and remove files from a RadarCollection.
    '''

    VradarCollection = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("RadarCollectionView").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent
        return self(), False

    def __init__(self, dirIn=None,VradarCollection=None ,
                 name="RadarCollectionView", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        dirIn: string
            Initial directory path to open.
        VradarCollection: py:class:`~artview.core.core.Variable` instance
            radar collection signal variable.
            A value of None will instantiate a empty list variable.
        name : string
            Window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(RadarCollectionView, self).__init__(name=name, parent=parent)
        self.directoryView = QtGui.QListView()
        self.collectionView = QtGui.QListView()

        # set up directoryView
        directoryModel = QtGui.QFileSystemModel()
        directoryModel.setFilter(QtCore.QDir.AllEntries |
                                 QtCore.QDir.AllDirs |
                                 QtCore.QDir.NoDot)
        directoryModel.setRootPath(QtCore.QDir.currentPath())
        self.directoryView.setModel(directoryModel)
        if dirIn is None:  # avoid reference to path while building doc
            dirIn = os.getcwd()
        index = directoryModel.index(dirIn)
        self.directoryView.setRootIndex(index)
        # self.clicked.connect(self.test)
        self.directoryView.doubleClicked.connect(self.doubleClick)
        # context (right-click) menu
        #self.directoryView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # set up collectionView
        collectionModel = QtGui.QStringListModel()
        self.collectionView.setModel(collectionModel)
        self.collectionView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.collectionView.customContextMenuRequested.connect(
            self.collectionContextMenu)

        # setup widget
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)
        self.layout.addWidget(self.directoryView, 0, 0)
        self.layout.addWidget(self.collectionView, 0, 1)
        #self.directoryView.customContextMenuRequested.connect(
        #    self.directoryContextMenu)
        if VradarCollection:
            self.VradarCollection = VradarCollection
        else:
            self.VradarCollection = Variable([])
        self.sharedVariables = {"VradarCollection": self.NewRadarCollection}
        self.connectAllVariables()
        self.NewRadarCollection(None, True)
        self.show()

    def doubleClick(self, index):
        '''Open Directory or File on double click.'''
        model = self.directoryView.model()
        indexItem = model.index(index.row(), 0, index.parent())
        if model.fileName(indexItem) == '..':
            if index.parent().parent().isValid():
                self.directoryView.setRootIndex(index.parent().parent())
        elif model.isDir(index):
            self.directoryView.setRootIndex(index)
        else:
            self.open(model.filePath(indexItem))

    def open(self, path):
        '''Open file.'''
        # try several open
        print("open: %s" % path)
        self.filename = str(path)
        try:
            radar = pyart.io.read(self.filename, delay_field_loading=True)
            # Add the filename for Display
            radar.filename = self.filename
            self.VradarCollection.value.append(radar)
            self.VradarCollection.update()
            return
        except:
            try:
                radar = pyart.io.read(self.filename)
                # Add the filename for Display
                radar.filename = self.filename
                self.VradarCollection.value.append(radar)
                self.VradarCollection.update()
                return
            except:
                import traceback
                print(traceback.format_exc())
                radar_warning = True


        if grid_warning or radar_warning:
            msg = "Py-ART didn't recognize this file!"
            common.ShowWarning(msg)

        return

    def directoryContextMenu(self, pos):
        '''Contruct right-click menu.'''
        menu = QtGui.QMenu(self)
        index = self.directoryView.currentIndex()
        path = str(self.directoryView.model().filePath(index))
        for func in read_functions:
            action = QtGui.QAction("Open with: %s" % func.__name__, self)
            # lambda inside loop: problem with variable capturing
            if func not in broken_read_functions:
                f = lambda boo, func=func: self.open_with(func, path)
                action.triggered.connect(f)
            else:
                action.setEnabled(False)
            menu.addAction(action)
        menu.exec_(self.directoryView.mapToGlobal(pos))

    def collectionContextMenu(self, pos):
        '''Contruct right-click menu.'''
        print("menu")
        menu = QtGui.QMenu(self)
        index = self.collectionView.currentIndex().row()
        action = QtGui.QAction("remove", self)
        f = lambda : self.remove_radar(index)
        action.triggered.connect(f)
        menu.addAction(action)
        menu.exec_(self.collectionView.mapToGlobal(pos))

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

    def remove_radar(self, index):
        self.VradarCollection.value.pop(index)
        self.VradarCollection.update()

    def NewRadarCollection(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vradar <artview.core.core.Variable>`.

        This will:

        * Update list of radar
        '''
        # test for None
        str_list = []
        for radar in self.VradarCollection.value:
            if hasattr(radar, 'filename'):
                str_list.append(radar.filename)
            else:
                str_list.append(radar.__str__())
        self.collectionView.model().setStringList(str_list)


_plugins = [RadarCollectionView]
