"""
artview.view
============

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
import pyart
from PyQt4 import QtGui, QtCore

from .core import Variable
from .components import (
    RadarDisplay, GridDisplay, Menu, LinkPlugins, SelectRegion)

app = None
displays = []
MainMenu = None
reflectivity = pyart.config.get_field_name('reflectivity')

def view(containers, field=reflectivity):
    '''
    Launch ARTview from shell.

    Parameters
    ----------
    container : list of Radar or Grid objects
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

def start():
    ''' Start Qt Application and Menu '''
    global app
    if app is None:
        app = QtGui.QApplication([ ])

    global MainMenu
    MainMenu = Menu(os.getcwd(), filename=False, mode="All")
    MainMenu.addComponent(LinkPlugins)
    MainMenu.addComponent(RadarDisplay)
    MainMenu.addComponent(GridDisplay)
    MainMenu.addComponent(SelectRegion)

    # add all plugins to grafical start
    try:
        from . import plugins
        for plugin in plugins._plugins:
            MainMenu.addComponent(plugin)
    except:
        import warnings
        warnings.warn("Loading Plugins Fail")

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
    addRadar to Artview Application.

    Parameters
    ----------
    radar : Radar objects
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
    addRadar to Artview Application.

    Parameters
    ----------
    grid : Grid objects
        Object to add to visualisation
    field : str
        Field to start visualization with
    '''
    i = len(displays)
    displays.append(GridDisplay(
        Variable(grid), Variable(field), Variable(0), name="Display%i" % i,
        parent=MainMenu))
