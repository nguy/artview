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


def ShowQuestion(msg):
    '''
    Show a Question message.
    
    Parameters::
    ----------
    msg - string
        Message to display in MessageBox.
    '''
    Dialog = QtGui.QDialog()
    response = QtGui.QMessageBox.question(Dialog, "Question", msg,
                            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
    if response == QtGui.QMessageBox.Ok:
        print msg
    else:
        print "Warning Discarded!"
        
    return response


def ShowLongText(msg):
    '''
    Show a Long message with QTextEdit.
    
    Parameters::
    ----------
    msg - string
        Message to display in MessageBox.
    '''
    Dialog = QtGui.QDialog()
    Dialog.resize(600,400)
    layout = QtGui.QGridLayout(Dialog)
    text = QtGui.QTextEdit("")
    layout.addWidget(text, 0, 0)
    text.setAcceptRichText(True)
    text.setReadOnly(True)
    text.setText(msg)
    response = Dialog.exec_()
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
    

class CreateTable(QtGui.QTableWidget):
    """ Creates a custom table widget """
    def __init__(self, column_names, name="Table",\
                  textcolor="black", bgcolor="gray", parent=None, *args):
        QtGui.QTableWidget.__init__(self, *args)
        self.setSelectionMode(self.ContiguousSelection)
        self.setGeometry(0,0,700,400)
        self.setShowGrid(True)
        self.textcolor = textcolor
        self.bgcolor = bgcolor
        
        self.colnames = column_names

    def display_data(self, data):
        """ Reads in data from a 2D array and formats and displays it in
            the table """

        if len(data)==0:
            data = ["No data for selected ROI."]

        nrows, ncols = data.shape[0], data.shape[1]
        self.setRowCount(nrows)
        self.setColumnCount(ncols)
        self.setHorizontalHeaderLabels(self.colnames)

        for i in xrange(nrows):
            # Set each cell to be a QTableWidgetItem from the _process_row method
            for j in xrange(ncols):
                item = QtGui.QTableWidgetItem(str(data[i, j]).format("%8.3f"))
                item.setBackgroundColor = QtGui.QColor(self.bgcolor)
                item.setTextColor = QtGui.QColor(self.textcolor)
                self.setItem(i, j, item)

        # Format column width
        self.resizeColumnsToContents()

        return 
