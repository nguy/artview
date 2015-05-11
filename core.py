"""
core.py

Class instance to create Variables and establish change signals.
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore

class Variable(QtCore.QObject):
    def __init__(self, value=None):
        """
        Class that holds a value, modifying with change() emits a signal.
        """
        QtCore.QObject.__init__(self)
        self.value = value

    def change(self, value, strong=True):
        """
        Change the Variable value and emit 'ValueChanged' signal.

        Parameters::
        ----------
        value : 
            New Value to be assigned to the variable.
        
        [Optional]
        strong : bool, optional
            Define if this is a strong, or a soft change. This is a some what
            subjective decision: strong is default, a soft change should be
            used to indicate to the slot that this change should not trigger
            any costly computation. Reasons for this are: When initialising
            variables, variable is likely to change again shortly, another
            more important variable is being changed as well etc.
            .. note:
                Defining how to respond to strong/soft changes is
                responsibility of the slot, most can just ignore the
                difference, but the costly ones should be aware.
        
        Notes::
        -----
        The arguments of the emitted signal are (self, value, strong).
        """
        self.value = value
        self.emit(QtCore.SIGNAL("ValueChanged"), self, value, strong)    


