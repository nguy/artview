"""
_common.py

auxiliary functions for scripts
"""
import pyart
from ..components import (Menu, RadarDisplay, GridDisplay, LinkSharedVariables,
                          SelectRegion, PointsDisplay)
from ..core import QtGui, QtCore


def _add_all_advanced_tools(menu):

    # add graphical starts
    for comp in [LinkSharedVariables, RadarDisplay, GridDisplay,
                 SelectRegion, PointsDisplay]:
        action = QtGui.QAction(comp.__name__, menu)
        action.triggered[()].connect(
            lambda comp=comp: menu.startComponent(comp))
        menu.addMenuAction(("File", "Plugins", ), action)

    # add all plugins to graphical start
    try:
        from .. import plugins
        for plugin in plugins._plugins.values():
            action = QtGui.QAction(plugin.__name__, menu)
            action.triggered[()].connect(
                lambda plugin=plugin: menu.startComponent(plugin))
            menu.addMenuAction(("File", "Plugins", ), action)
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

    MainMenu = Menu(DirIn, filename, mode=("Radar", "Grid"))

    try:
        from ..modes import modes
        group_names = [m['group'] for m in modes]
        seen = set()
        group_names = [x for x in group_names if x not in seen and not seen.add(x)]
        groups = [[m for m in modes if m['group']==name] for name in group_names]
        for group in groups:
            for mode in group:
                action = QtGui.QAction(mode['label'], MainMenu)
                action.triggered[()].connect(
                    lambda mode=mode: MainMenu.change_mode(mode['action']))
                if mode['group'] != 'io':
                    MainMenu.addMenuAction(("Modes",), action)
                else:
                    MainMenu.addMenuAction(("File",), action)
            MainMenu.addMenuSeparator(("Modes",))
    except:
        import warnings
        warnings.warn("Loading Modes Fail")

    _add_all_advanced_tools(MainMenu)

    return MainMenu
    # resize menu
    menu_width = 300
    menu_height = 180

    MainMenu.setGeometry(0, 0, menu_width, menu_height)
