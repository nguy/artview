"""
_common.py

auxiliary functions for scripts
"""
import pyart
from ..components import RadarDisplay, LinkPlugins, SelectRegion


def _add_all_advanced_tools(menu):

    # add grafical starts
    menu.addComponent(LinkPlugins)
    menu.addComponent(RadarDisplay)
    menu.addComponent(SelectRegion)

    # add all plugins to grafical start
    try:
        from .. import plugins
        for plugin in plugins._plugins:
            menu.addComponent(plugin)
    except:
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
