"""
standard.py

auxiliar functions for scripts
"""
import pyart
from ..components import (Menu, RadarDisplay, GridDisplay, LinkPlugins,
                          SelectRegion)
from ..core import QtGui, QtCore

def _add_all_advanced_tools(menu):

    # add grafical starts
    menu.addComponent(LinkPlugins)
    menu.addComponent(RadarDisplay)
    menu.addComponent(GridDisplay)
    menu.addComponent(SelectRegion)

    # add all plugins to grafical start
    try:
        from .. import plugins
        for plugin in plugins._plugins.values():
            menu.addComponent(plugin)
    except:
        import traceback
        print(traceback.format_exc())
        import warnings
        warnings.warn("Loading Plugins Fail")


def _parse_dir(DirIn):
    if DirIn is None:  # avoid reference to path while building documentation
        DirIn = os.getcwd()
    return DirIn

Zlike = ['CZ', 'DZ', 'AZ', 'Z',
         'dbz', 'DBZ', 'dBZ', 'DBZ_S', 'DBZ_K',
         'reflectivity_horizontal', 'DBZH', 'corr_reflectivity']


def _parse_field(container, field):
    '''
    Hack to perform a check on reflectivity to make it work with
    a larger number of files as there are many nomenclature is the
    weather radar world.

    This should only occur upon start up with a new file.
    '''

    if field is None:
        field = pyart.config.get_field_name('reflectivity')
        if container is None:
            return field

        fieldnames = container.fields.keys()
        Zinfile = set(fieldnames).intersection(Zlike)

        if field not in fieldnames and len(Zinfile) > 0:
            field = Zinfile.pop()

    return field


def startMainMenu(DirIn=None, filename=None):

    MainMenu = Menu(DirIn,  filename, mode="All")

    for comp in [LinkPlugins, RadarDisplay, GridDisplay, SelectRegion]:
        action = QtGui.QAction(comp.__name__, MainMenu)
        action.triggered[()].connect(
            lambda comp=comp: MainMenu.startComponent(comp))
        MainMenu.addMenuAction(("Advanced Tools",), action)

    try:
        from .. import plugins
        for plugin in plugins._plugins.values():
            action = QtGui.QAction(plugin.__name__, MainMenu)
            action.triggered[()].connect(
                lambda comp=comp: MainMenu.startComponent(plugin))
            if plugin.__name__ != 'FileList':
                MainMenu.addMenuAction(("Advanced Tools",), action)
            else:
                MainMenu.addMenuAction(("File",), action)
    except:
        import warnings
        warnings.warn("Loading Plugins Fail")

    return MainMenu
    # resize menu
    menu_width = 300
    menu_height = 180

    MainMenu.setGeometry(0, 0, menu_width, menu_height)
