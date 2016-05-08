"""
==================================
Shell Launch (:mod:`artview.view`)
==================================

Utilities easily running ARTview from shell.

.. autosummary::
    :toctree: generated/

    view
    start
    execute
    addRadar
    addGrid

"""

import os
import platform
import pyart

from .core import Variable, QtGui, QtCore
from .components import (
    RadarDisplay, GridDisplay, Menu, LinkSharedVariables, SelectRegion)
from .scripts._common import startMainMenu

app = None
displays = []
MainMenu = None
reflectivity = pyart.config.get_field_name('reflectivity')


def view(containers, field=reflectivity):
    '''
    Launch ARTview from shell.

    Parameters
    ----------
    container : list of :py:class:`~pyart.core.Radar` or \
    :py:class:`~pyart.core.Grid`  objects
        Object to visualise.
    field : str
        Field to start visualization with.
    '''

    # test if containers isn't itetable
    if not hasattr(containers, '__contains__'):
        containers = (containers,)

    start()

    for container in containers:
        if isinstance(container, pyart.core.Radar):
            addRadar(container, field)
        elif isinstance(container, pyart.core.Grid):
            addGrid(container, field)
        else:
            import warnings
            warnings.warn('Ignoring unknown container %s' % container)

    execute()


def start(DirIn=os.getcwd(), filename=False):
    ''' Start Qt Application and :py:class:`~artview.components.Menu` '''
    global app
    if app is None:
        app = QtGui.QApplication([])
        if checkifmac():
            app.setAttribute(QtCore.Qt.AA_MacPluginApplication, True)

    global MainMenu
    MainMenu = startMainMenu(DirIn, filename)

    # resize menu
    menu_width = 300
    menu_height = 180

    MainMenu.setGeometry(0, 0, menu_width, menu_height)


def execute():
    ''' Execute Application '''
    global app
    app.exec_()


def close():
    ''' Delet all references to allow Garbage Colletion. '''
    global displays
    displays = []

    global MainMenu
    MainMenu = None

    global app
    app = None


def addRadar(radar, field=reflectivity):
    '''
    add :py:class:`~artview.components.RadarDisplay` to Artview Application.

    Parameters
    ----------
    radar : :py:class:`~pyart.core.Radar` object
        Object to add to visualisation
    field : str
        Field to start visualization with
    '''
    i = len(displays)
    displays.append(RadarDisplay(
        Variable(radar), Variable(field), Variable(0), name="Display%i" % i,
        parent=MainMenu))


def addGrid(grid, field=reflectivity):
    '''
    add :py:class:`~artview.components.GridDisplay` to Artview Application.

    Parameters
    ----------
    grid : :py:class:`~pyart.core.Grid` object
        Object to add to visualisation
    field : str
        Field to start visualization with
    '''
    i = len(displays)
    displays.append(GridDisplay(
        Variable(grid), Variable(field), Variable(0), name="Display%i" % i,
        parent=MainMenu))


def checkifmac():
    '''Check to see if operating MacOSX'''
    ismac = False
    if os.name == 'posix':
        if platform.system().lower() == 'darwin':
            ismac = True
    return ismac
