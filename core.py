"""
core.py

Class instance to create Variables and establish change signals.
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore

# keet track of all components, this is not fundamental, but may be usefull
# for some control utilities



class Variable (QtCore.QObject):
    def __init__(self,value=None):
        """Class that holds a value, changing that with change() emits a signal"""
        QtCore.QObject.__init__(self)
        self.value = value

    def change (self,value):
        self.value = value
        self.emit(QtCore.SIGNAL("ValueChanged"), self, value)


class ComponentsList(QtCore.QObject):
    '''Keep track of Components in a list and emit signals.
    Methods append and remove are provided and emit signals,
    direct acess to the list is allowed with 'ComponentList.list',
    but not recomended.'''

    def __init__(self):
        super(ComponentsList, self).__init__()
        self.list = []

    def append(self, item):
        self.list.append(item)
        self.emit(QtCore.SIGNAL("ComponentAppended"), item)

    def remove(self, item):
        self.list.remove(item)
        self.emit(QtCore.SIGNAL("ComponentRemoved"), item)

    def index(self, item):
        return self.list.index(item)
    def __delitem__(self, key):
        self.list.__delitem__(key)
    def __getitem__(self, key):
        return self.list.__getitem__(key)
    def __setitem__(self, key, value):
        self.list.__setitem__(key, value)
    def __len__(self):
        return len(self.list)

componentsList = ComponentsList()

class Component(QtGui.QMainWindow):
    '''Abstract class for a ART-view component'''
    

    def __init__(self, name="Component", parent=None):
        '''Initialize the class to create the interface'''
        super(Component, self).__init__(parent=parent)
        self.name = name
        self.parent = parent
        self.setWindowTitle(name)
        self.sharedVariables = {}
        componentsList.append(self)

    def connectAllVariables(self):
        '''Call connectSharedVariable for all keys in sharedVariables'''
        for var in self.sharedVariables.keys():
            self.connectSharedVariable(var)

    def disconnectAllVariables(self):
        '''Call connectSharedVariable for all keys in sharedVariables'''
        for var in self.sharedVariables.keys():
            self.disconnectSharedVariable(var)

    def connectSharedVariable(self,var):
        '''Connect variable 'var' to its slot as defined in
        sharedVariables dictionary'''
        if var in self.sharedVariables:
            if self.sharedVariables[var] is not None:
                QtCore.QObject.connect(
                    getattr(self, var), QtCore.SIGNAL("ValueChanged"),
                    self.sharedVariables[var])
        else:
            raise ValueError("Variable %s is not a shared variable of %s"
                            %(var,self.name))

    def disconnectSharedVariable(self,var):
        '''Connect variable 'var' to its slot as defined in
        sharedVariables dictionary'''
        if var in self.sharedVariables:
            if self.sharedVariables[var] is not None:
                QtCore.QObject.disconnect(
                    getattr(self, var), QtCore.SIGNAL("ValueChanged"),
                    self.sharedVariables[var])
        else:
            raise ValueError("Variable %s is not a shared variable of %s"
                            %(var,self.name))

    def keyPressEvent(self, event):
        '''Reimplementations, pass keyEvent to parent,
        even if a diferent window'''
        if self.parent == None:
            super(Component, self).keyPressEvent(self, event)
        else:
            # Send event to parent to handle (Limitation of pyqt not having a 
            # form that does this - AG)
            self.parent.keyPressEvent(event)

    def closeEvent(self, QCloseEvent):
        '''Reimplementations to remove from components list'''
        componentsList.remove(self)
        super(Component, self).closeEvent(QCloseEvent)


