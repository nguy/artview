"""
io.py

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


class DirectoryList(Component):
    '''
    Open an directory view to open files.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("DirectoryList").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent
        return self(), False

    def __init__(self, dirIn=None, name="DirectoryList", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        dirIn: string
            Initial directory path to open.
        name : string
            Window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(DirectoryList, self).__init__(name=name, parent=parent)
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
        for func in read_functions:
            action = QtGui.QAction("Open with: %s" % func.__name__, self)
            # lambda inside loop: problem with variable capturing
            if func not in broken_read_functions:
                f = lambda boo, func=func: self.open_with(func, path)
                action.triggered.connect(f)
            else:
                action.setEnabled(False)
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


class FileDetail(Component):
    '''
    Open an interactive button driven file advancement.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("FileDetail").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent
        return self(), False

    def __init__(self, dirIn=None, name="FileDetail", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        dirIn: string
            Initial directory path to open.
        name : string
            Window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(FileDetail, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        # Set up signal, so that DISPLAY can react to
        # changes in radar or gatefilter shared variables
        self.Vradar = Variable(None)
        self.Vgrid = Variable(None)
        self.sharedVariables = {"Vradar": None,
                                "Vgrid": None}
        self.connectAllVariables()

        # Set the layout
        self.generalLayout = QtGui.QVBoxLayout()
        self.generalLayout.addWidget(self.createShortUI())
        self.generalLayout.addWidget(self.createLongUI())

        self.layout.addLayout(self.generalLayout, 0, 0, 1, 2)

        self.show()

    def createShortUI(self):
        '''
        Choose to save minimal information from Radar instance.
        '''
        groupBox = QtGui.QGroupBox("Output Short Radar Text Information")
        gBox_layout = QtGui.QGridLayout()

        self.RadarShortButton = QtGui.QPushButton("Save Short Info File")
        self.RadarShortButton.setStatusTip('Save Short Radar Structure Info')
        self.RadarShortButton.clicked.connect(self._get_RadarShortInfo)
        gBox_layout.addWidget(self.RadarShortButton, 0, 0, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def createLongUI(self):
        '''
        Choose to save full information from Radar instance.
        '''
        groupBox = QtGui.QGroupBox("Output Long Radar Text Information")
        gBox_layout = QtGui.QGridLayout()

        self.RadarLongButton = QtGui.QPushButton("Save Long Info File")
        self.RadarLongButton.setStatusTip('Save Long Radar Structure Info')
        self.RadarLongButton.clicked.connect(self._get_RadarLongInfo)
        gBox_layout.addWidget(self.RadarLongButton, 0, 0, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def _get_RadarLongInfo(self):
        '''Print out the radar info to text box.'''
        path = QtGui.QFileDialog.getSaveFileName(
            self, 'Save Text File',
            QtCore.QString('long_radar_info.txt'), 'TXT(*.txt)')

        # Get info and print to file
        file_obj = open(path, 'w')
        self.Vradar.value.info(out=file_obj)
        file_obj.close()

    def _get_RadarShortInfo(self):
        '''Print out some basic info about the radar.'''
        # For any missing data
        infoNA = "Info not available"

        try:
            rname = self.Vradar.value.metadata['instrument_name']
        except:
            rname = infoNA
        try:
            rlon = str(self.Vradar.value.longitude['data'][0])
        except:
            rlon = infoNA
        try:
            rlat = str(self.Vradar.value.latitude['data'][0])
        except:
            rlat = infoNA
        try:
            ralt = str(self.Vradar.value.altitude['data'][0])
            raltu = self.Vradar.value.altitude['units'][0]
        except:
            ralt = infoNA
            raltu = " "
        try:
            maxr = str(self.Vradar.value.instrument_parameters[
                'unambiguous_range']['data'][0])
            maxru = self.Vradar.value.instrument_parameters[
                'unambiguous_range']['units'][0]
        except:
            maxr = infoNA
            maxru = " "
        try:
            nyq = str(self.Vradar.value.instrument_parameters[
                'nyquist_velocity']['data'][0])
            nyqu = self.Vradar.value.instrument_parameters[
                'nyquist_velocity']['units'][0]
        except:
            nyq = infoNA
            nyqu = " "
        try:
            bwh = str(self.Vradar.value.instrument_parameters[
                'radar_beam_width_h']['data'][0])
            bwhu = self.Vradar.value.instrument_parameters[
                'radar_beam_width_h']['units'][0]
        except:
            bwh = infoNA
            bwhu = " "
        try:
            bwv = str(self.Vradar.value.instrument_parameters[
                'radar_beam_width_v']['data'][0])
            bwvu = self.Vradar.value.instrument_parameters[
                'radar_beam_width_v']['units'][0]
        except:
            bwv = infoNA
            bwvu = " "
        try:
            pw = str(self.Vradar.value.instrument_parameters[
                'pulse_width']['data'][0])
            pwu = self.Vradar.value.instrument_parameters[
                'pulse_width']['units'][0]
        except:
            pw = infoNA
            pwu = " "
        try:
            ngates = str(self.Vradar.value.ngates)
        except:
            ngates = infoNA
        try:
            nsweeps = str(self.Vradar.value.nsweeps)
        except:
            nsweeps = infoNA

        txOut = (('Radar Name: %s\n' % rname) +
                 ('Radar longitude: %s\n' % rlon) +
                 ('Radar latitude: %s\n' % rlat) +
                 ('Radar altitude: %s %s\n' % (ralt, raltu)) +
                 ('    \n') +
                 ('Unambiguous range: %s %s\n' % (maxr, maxru)) +
                 ('Nyquist velocity: %s %s\n' % (nyq, nyqu)) +
                 ('    \n') +
                 ('Radar Beamwidth, horiz: %s %s\n' % (bwh, bwhu)) +
                 ('Radar Beamwidth, vert: %s %s\n' % (bwv, bwvu)) +
                 ('Pulsewidth: %s %s \n' % (pw, pwu)) +
                 ('    \n') +
                 ('Number of gates: %s\n' % ngates) +
                 ('Number of sweeps: %s\n' % nsweeps))

        self.showSaveDialog('short_radar_info.txt', txOut)

    def showSaveDialog(self, fsuggest, txt):

        path = QtGui.QFileDialog.getSaveFileName(
            self, 'Save Text File', QtCore.QString(fsuggest), 'TXT(*.txt)')

        with open(path, "w") as text_file:
            text_file.write(txt)


_plugins = [DirectoryList, FileDetail]
