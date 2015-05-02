###########
# tilt.py
###########
# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial


class TiltButtonWindow(QtGui.QMainWindow):
    '''Class to display the Window with Tilt Buttons'''

    tiltClicked = QtCore.pyqtSignal()
    
    def __init__(self, Vradar, Vtilt, name="TiltButtons", parent=None):
        '''Initialize the class to create the interface'''
        super(TiltButtonWindow, self).__init__(parent)
        self.parent = parent
        self.name = name
        self.setWindowTitle(name)
        self.Vradar = Vradar
        
        # Set up signal, so that DISPLAY can react to external 
        # (or internal) changes in tilt (Core.Variable instances expected)
        self.Vtilt = Vtilt
        QtCore.QObject.connect(Vtilt, QtCore.SIGNAL("ValueChanged"), self.NewTilt)

        self.CreateTiltWidget()
        self.rButtons = self.SetTiltRadioButtons()
        self.show()
           
    ########################
    # Button methods #
    ########################
        
    def TiltSelectCmd(self, ntilt):
        '''Captures a selection and redraws the field with new tilt'''
##        print ntilt
        #self.tiltClicked.emit()
        self.Vtilt.change(ntilt)

    def CreateTiltWidget(self):
        '''Create a widget to store radio buttons to control tilt adjust'''
        self.radioBox = QtGui.QGroupBox("Tilt Selection", parent=self)
        self.rBox_layout = QtGui.QVBoxLayout(self.radioBox)
                
    def SetTiltRadioButtons(self):
        '''Set a tilt selection using radio buttons'''
        # Instantiate the buttons into a list for future use
        self.tiltbutton = []
        
        # Pull out the tilt indices and elevations for display
        tilt_indices = self.Vradar.value.sweep_start_ray_index['data'][:]
        elevs = self.Vradar.value.elevation['data'][tilt_indices]
        
        # Loop through and create each tilt button and connect a value when selected
        for ntilt in self.Vradar.value.sweep_number['data'][:]:
            btntxt = "%2.1f deg (Tilt %d)"%(elevs[ntilt], ntilt+1)
            button = QtGui.QRadioButton(btntxt, self.radioBox)
            self.tiltbutton.append(button)
            QtCore.QObject.connect(self.tiltbutton[ntilt], QtCore.SIGNAL("clicked()"), \
                         partial(self.TiltSelectCmd, ntilt))
            
            self.rBox_layout.addWidget(self.tiltbutton[ntilt])
        
        self.NewTilt(self.Vtilt, self.Vtilt.value)  # setChecked the current tilt
        self.radioBox.setLayout(self.rBox_layout)
        self.setCentralWidget(self.radioBox)
        
        return self.radioBox
    
    def NewTilt(self, variable, value):
        tilt = self.Vtilt.value
        if tilt >= 0 and tilt < len(self.tiltbutton):
            self.tiltbutton[tilt].setChecked(True)
        
