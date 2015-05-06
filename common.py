"""
common.py 

Common routines run throughout ARTView.
"""

# Load the needed packages
from PyQt4 import QtGui

    ########################
    # Warning methods #
    ########################
def ShowWarning(msg):
    '''Show a warning message'''
    Dialog = QtGui.QDialog()
    flags = QtGui.QMessageBox.StandardButton()
    response = QtGui.QMessageBox.warning(Dialog, "Warning!", msg, flags)
    if response == 0:
        print msg
    else:
        print "Warning Discarded!"
        
    return response
    
def string_dialog(stringIn, title, msg):
    '''Retrieve new plot units'''
    Dialog = QtGui.QDialog()
    if stringIn is None:
        old_val = ''
    else:
        old_val = stringIn
    stringOut, entry = QtGui.QInputDialog.getText(Dialog, title, msg, 0, old_val)
    
    return stringOut, entry