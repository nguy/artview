"""
common.py

Common routines run throughout ARTView.
"""

# Load the needed packages
from .core import QtWidgets, QtCore, QtGui
import numpy as np
import os, glob

########################
# Dialog methods #
########################


def ShowWarning(msg):
    '''
    Show a warning message.

    Parameters::
    ----------
    msg - string
        Message to display in MessageBox.
    '''
    Dialog = QtWidgets.QDialog()
    flags = QtWidgets.QMessageBox.StandardButton()
    response = QtWidgets.QMessageBox.warning(Dialog, "Warning!", msg, flags)
    if response == 0:
        print(msg)
    else:
        print("Warning Discarded!")

    return response


def ShowQuestion(msg):
    '''
    Show a Question message.

    Parameters::
    ----------
    msg - string
        Message to display in MessageBox.
    '''
    Dialog = QtWidgets.QDialog()
    response = QtWidgets.QMessageBox.question(
        Dialog, "Question", msg,
        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
    if response == QtWidgets.QMessageBox.Ok:
        print(msg)
    else:
        print("Warning Discarded!")

    return response

def ShowQuestionYesNo(msg):
    '''
    Show a Question message with yes no.

    Parameters::
    ----------
    msg - string
        Message to display in MessageBox.
    '''
    Dialog = QtWidgets.QDialog()
    response = QtWidgets.QMessageBox.question(
        Dialog, "Question", msg,
        QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.Cancel)

    return response


def ShowLongText(msg, modal=True, set_html=False):
    '''
    Show a Long message with QTextEdit.

    Parameters::
    ----------
    msg - string
        Message to display in MessageBox.
    '''
    Dialog = QtWidgets.QDialog()
    Dialog.resize(600, 400)
    layout = QtWidgets.QGridLayout(Dialog)
    text = QtWidgets.QTextEdit("")
    layout.addWidget(text, 0, 0)
    text.setAcceptRichText(True)
    text.setReadOnly(True)
    if set_html:
        text.setHtml(msg)
    else:
        text.setText(msg)
    if modal is True:
        response = Dialog.exec_()
        return response
    else:
        response = Dialog.show()
        return Dialog, response


def ShowLongTextHyperlinked(msg, modal=True):
    '''
    Show a Long message with QLabel that will display
    hyperlinks and take user to website.

    Parameters::
    ----------
    msg - string
        Message to display in MessageBox.
    '''
    Dialog = QtWidgets.QDialog()
#    Dialog.resize(600, 400)
    layout = QtWidgets.QGridLayout(Dialog)
    text = QtWidgets.QLabel("")
    text.setText(msg)
    text.setOpenExternalLinks(True)
    text.setWordWrap(True)
    layout.addWidget(text)
    if modal is True:
        response = Dialog.exec_()
        return response
    else:
        response = Dialog.show()
        return Dialog, response


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
    The value that is then entered is returned via the
    stringOut and entry variables.
    '''
    Dialog = QtWidgets.QDialog()
    if stringIn is None:
        old_val = ''
    else:
        old_val = stringIn
    stringOut, entry = QtWidgets.QInputDialog.getText(
        Dialog, title, msg, 0, old_val)

    return stringOut, entry


def string_dialog_with_reset(stringIn, title, msg, reset=None):
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
    reset - default value

    Notes::
    -----
    This box displays an initial value that can be changed. The value that is
    then entered is returned via the stringOut and entry variables.
    '''
    if stringIn is None:
        old_val = ''
    else:
        old_val = stringIn

    # start dialog
    Dialog = QtWidgets.QDialog()
    Dialog.setWindowTitle(title)
    gridLayout = QtWidgets.QGridLayout(Dialog)
    # add mensage and edit line
    gridLayout.addWidget(QtWidgets.QLabel(msg), 0, 0, 1, 1)
    lineEdit = QtWidgets.QLineEdit(old_val, Dialog)
    gridLayout.addWidget(lineEdit, 1, 0, 1, 1)
    # add buttons
    buttonBox = QtWidgets.QDialogButtonBox(Dialog)
    buttonBox.setOrientation(QtCore.Qt.Horizontal)
    if reset is not None:
        buttons = (QtWidgets.QDialogButtonBox.Reset |
                   QtWidgets.QDialogButtonBox.Cancel |
                   QtWidgets.QDialogButtonBox.Ok)
    else:
        buttons = (QtWidgets.QDialogButtonBox.Cancel |
                   QtWidgets.QDialogButtonBox.Ok)
    buttonBox.setStandardButtons(buttons)
    gridLayout.addWidget(buttonBox, 2, 0, 1, 1)

    # handel click signal
    def handleClick(button):
        enum = buttonBox.standardButton(button)
        if enum == QtWidgets.QDialogButtonBox.Reset:
            lineEdit.setText(reset)
        elif enum == QtWidgets.QDialogButtonBox.Cancel:
            Dialog.done(0)
        elif enum == QtWidgets.QDialogButtonBox.Ok:
            Dialog.done(1)
    buttonBox.clicked.connect(handleClick)

    # run dialog
    entry = Dialog.exec_()
    if entry == 1:
        entry = True
    else:
        entry = False
    # get result
    stringOut = lineEdit.text()

    return stringOut, entry

########################
# Start methods #
########################


class _SimplePluginStart(QtWidgets.QDialog):
    '''
    Dialog Class for graphical Start of Display,
    to be used in guiStart.
    '''

    def __init__(self, name):
        '''Initialize the class to create the interface.'''
        super(_SimplePluginStart, self).__init__()
        self.result = {}
        self.layout = QtWidgets.QGridLayout(self)
        self._name = name
        self.setWindowTitle(name)
        # set window as modal
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.setupUi()

    def setupUi(self):
        self.layout.addWidget(QtWidgets.QLabel("Name"), 0, 0)
        self.name = QtWidgets.QLineEdit(self._name)
        self.layout.addWidget(self.name, 0, 1)

        self.independent = QtWidgets.QCheckBox("Independent Window")
        self.independent.setChecked(True)
        self.layout.addWidget(self.independent, 1, 1, 1, 1)

        self.closeButton = QtWidgets.QPushButton("Start")
        self.closeButton.clicked.connect(self.closeDialog)
        self.layout.addWidget(self.closeButton, 2, 0, 1, 2)

    def closeDialog(self):
        self.done(QtWidgets.QDialog.Accepted)

    def startDisplay(self):
        self.exec_()

        self.result['name'] = str(self.name.text())

        return self.result, self.independent.isChecked()

########################
#    Table methods     #
########################


class CreateTable(QtWidgets.QTableWidget):
    """Creates a custom table widget."""
    def __init__(self, points, name="Table",
                 textcolor="black", bgcolor="gray", parent=None, *args):
        QtWidgets.QTableWidget.__init__(self, *args)
        self.points = points
        self.setSelectionMode(self.ContiguousSelection)
        self.setGeometry(0, 0, 700, 400)
        self.setShowGrid(True)
        self.textcolor = textcolor
        self.bgcolor = bgcolor

    def display(self):
        """Reads in data from a 2D array and formats and displays it in
            the table."""

        if self.points is None:
            data = ["No data for selected."]
            nrows = 0
            ncols = 0
        else:
            nrows = self.points.npoints
            colnames = self.points.axes.keys() + self.points.fields.keys()
            ncols = len(colnames)

        self.setRowCount(nrows)
        self.setColumnCount(ncols)
        colnames = self.points.axes.keys() + self.points.fields.keys()
        self.setHorizontalHeaderLabels(colnames)

        for i in xrange(nrows):
            # Set each cell to be a QTableWidgetItem from _process_row method
            for j, name in enumerate(colnames):
                if name in self.points.axes:
                    item = QtWidgets.QTableWidgetItem(
                        "%8.3f" % self.points.axes[name]['data'][i])
                else:
                    item = QtWidgets.QTableWidgetItem(
                        "%8.3f" % self.points.fields[name]['data'][i])

                item.setBackgroundColor = QtGui.QColor(self.bgcolor)
                item.setTextColor = QtGui.QColor(self.textcolor)
                self.setItem(i, j, item)

        # Format column width
        self.resizeColumnsToContents()

        return

########################
#  Arithmetic methods  #
########################


def _array_stats(data):
    """Return a dictionary of statistics from a Numpy array"""
    statdict = {}
    statdict['Minimum'] = np.ma.min(data)
    statdict['Maximum'] = np.ma.max(data)
    statdict['Mean'] = np.ma.mean(data)
    statdict['Median'] = np.ma.median(data)
    statdict['Standard_Deviation'] = np.ma.std(data)
    statdict['Variance'] = np.ma.var(data)

    return statdict


########################
#   Colormap methods   #
########################

class select_cmap(QtWidgets.QDialog):
    def __init__(self):
        '''Allow the user to select a colormap.'''
        super(select_cmap, self).__init__()
        self.layout = QtWidgets.QGridLayout(self)
        self.setWindowTitle("Select Colormap")
        # set window as modal
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir))
        images = glob.glob(parentdir + "/icons/colormaps/*.png")

        for i,path in enumerate(images):
            name = path.split('/')[-1].split('.')[0]
            button = QtWidgets.QPushButton(name)
            self.layout.addWidget(button, 2*(i/3)+1, 2*(i%3))
            button.clicked.connect(lambda ans,name=name: self.select(name))
            label = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap(path)
            label.setPixmap(pixmap)
            label.setScaledContents(True)
            self.layout.addWidget(label, 2*(i/3)+1, 2*(i%3)+1)

        self.selection = None
        self.exec_()

    def select(self, name):
        self.selection = name
        self.done(QtWidgets.QDialog.Accepted)