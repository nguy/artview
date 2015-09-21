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


class AdvancedIO(Component):
    '''
    Open an interactive python console so the direct manipulation
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        return self(), False

    def __init__(self, dirIn=None, name="AdvancedIO", parent=None):
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
        super(AdvancedIO, self).__init__(name=name, parent=parent)
        self.dirView = DirView(dirIn)
        self.setCentralWidget(self.dirView)
        self.dirView.opened.connect(self.open)
        self.dirView.customContextMenuRequested.connect(self.contextMenu)
        self.Vradar = Variable(None)
        self.Vgrid = Variable(None)
        self.sharedVariables = {"Vradar": None,
                                "Vgrid": None}
        self.connectAllVariables()
        self.show()

    def open(self, path):
        ''' Slot of :py:attr:`DirView.opened` '''
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
        menu = QtGui.QMenu(self)
        index = self.dirView.currentIndex()
        path = str(self.dirView.model().filePath(index))
        for func in open_functions:
            action = QtGui.QAction("Open with: %s" % func.__name__, self)
            # lambda inside loop: problem with variable capturing
            f = lambda boo, func=func: self.open_with(func, path)
            action.triggered.connect(f)
            menu.addAction(action)
        menu.exec_(self.dirView.mapToGlobal(pos))

    def open_with(self, func, path):
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


class DirView(QtGui.QListView):
    '''
    adapted from
    http://stackoverflow.com/questions/23993895/python-pyqt-qtreeview-example-selection
    '''

    opened = QtCore.pyqtSignal(str)  #: signal that a file should be open

    def __init__(self, dirIn=None):
        super(DirView, self).__init__()
        model = QtGui.QFileSystemModel()
        model.setFilter(QtCore.QDir.AllEntries |
                        QtCore.QDir.AllDirs |
                        QtCore.QDir.NoDot)
        model.setRootPath(QtCore.QDir.currentPath())
        self.setModel(model)
        if dirIn is None:  # avoid reference to path while building doc
            dirIn = os.getcwd()
        index = model.index(dirIn)
        self.setRootIndex(index)
        # self.clicked.connect(self.test)
        self.doubleClicked.connect(self.doubleClick)

        # context (right-click) menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def doubleClick(self, index):
        indexItem = self.model().index(index.row(), 0, index.parent())
        if self.model().fileName(indexItem) == '..':
            if index.parent().parent().isValid():
                self.setRootIndex(index.parent().parent())
        elif self.model().isDir(index):
            print ("dir")
            self.setRootIndex(index)
        else:
            self.opened.emit(self.model().filePath(indexItem))

    def test(self, index):
        indexItem = self.model().index(index.row(), 0, index.parent())

        # path or filename selected
        fileName = self.model().fileName(indexItem)
        print("hello!")
        print(fileName)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec_())

_plugins = [AdvancedIO]
