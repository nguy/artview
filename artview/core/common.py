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
    '''
    Show a warning message.
    
    Parameters::
    ----------
    msg - string
        Message to display in MessageBox.
    '''
    Dialog = QtGui.QDialog()
    flags = QtGui.QMessageBox.StandardButton()
    response = QtGui.QMessageBox.warning(Dialog, "Warning!", msg, flags)
    if response == 0:
        print msg
    else:
        print "Warning Discarded!"
        
    return response
    
def string_dialog(stringIn, title, msg):
    '''
    Show a Dialog box.
    
    Parameters::
    ----------
    stringIn - string
        Input string to fill box initially.
    title - string
        Title of the dialog box.
    msg - string
        Message to display in box.
        
    Notes::
    -----
    This box displays an initial value that can be changed.
    The value that is then entered is returned via the stringOut and entry variables.
    '''
    Dialog = QtGui.QDialog()
    if stringIn is None:
        old_val = ''
    else:
        old_val = stringIn
    stringOut, entry = QtGui.QInputDialog.getText(Dialog, title, msg, 0, old_val)
    
    return stringOut, entry