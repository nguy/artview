###########
# field.py
###########
# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial


class FieldButtonWindow(QtGui.QMainWindow):
    '''Class to display the Window with Field Buttons'''

    FieldClicked = QtCore.pyqtSignal()
    
    def __init__(self, Vradar, Vfield, name="FieldButtons", parent=None):
        '''Initialize the class to create the interface'''
        super(FieldButtonWindow, self).__init__(parent)
        self.parent = parent
        self.name = name
        self.setWindowTitle(name)
        self.Vradar = Vradar
        
        # Set up signal, so that DISPLAY can react to external 
        # (or internal) changes in field (Core.Variable instances expected)
        self.Vfield = Vfield
        QtCore.QObject.connect(Vfield, QtCore.SIGNAL("ValueChanged"), self.NewField)
        QtCore.QObject.connect(Vradar, QtCore.SIGNAL("ValueChanged"), self.NewRadar)

        self.CreateFieldWidget()
        self.SetFieldRadioButtons()
        self.show()
           
    ########################
    # Button methods #
    ########################
        
    def FieldSelectCmd(self, field):
        '''Captures a selection and redraws the field with new tilt'''
##        print ntilt
        #self.tiltClicked.emit()
        self.Vfield.change(field)

    def CreateFieldWidget(self):
        '''Create a widget to store radio buttons to control tilt adjust'''
        self.radioBox = QtGui.QGroupBox("Field Selection", parent=self)
        self.rBox_layout = QtGui.QVBoxLayout(self.radioBox)
        self.radioBox.setLayout(self.rBox_layout)
        self.setCentralWidget(self.radioBox)
                
    def SetFieldRadioButtons(self):
        '''Set a field selection using radio buttons'''
        # Instantiate the buttons into a list for future use
        self.fieldbutton = {}
        
        # Loop through and create each field button and connect a value when selected
        for field in self.Vradar.value.fields.keys():
            button = QtGui.QRadioButton(field, self.radioBox)
            self.fieldbutton[field] = button
            QtCore.QObject.connect(button, QtCore.SIGNAL("clicked()"), \
                         partial(self.FieldSelectCmd, field))
            
            self.rBox_layout.addWidget(button)
        
        self.NewField(self.Vfield, self.Vfield.value)  # setChecked the current field
    
    def NewField(self, variable, value):
        if value in self.Vradar.value.fields:
            self.fieldbutton[value].setChecked(True)
        
    def NewRadar(self, variable, value):
        # update field list
        self.CreateFieldWidget()
        self.SetFieldRadioButtons()
