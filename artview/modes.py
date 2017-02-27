
from .components import *
from .plugins import *
from .core import componentsList
from .core import QtWidgets, QtGui

def change_mode(components, links):
        ''' Open and connect new components to satisfy mode.

        Parameters
        ----------
        components: is a list of uninitialized components
        links: list of links
            link is a tuple ((destination_index, var_name),
            (origin_index, var_name)) where `destination_index` and
            `origin_index` refer to the indexes in the components list of the
            origin and destination of the linking process, and
            `var_name` is the respective shared variable name.
        '''
        static_comp_list = componentsList[:]
        for j, comp in enumerate(static_comp_list):
            if isinstance(comp, Window):
                window = comp
                break

        # find already running components
        for i, component in enumerate(components):
            flag = False
            for j, comp in enumerate(static_comp_list):
                if isinstance(comp, component):
                    components[i] = static_comp_list.pop(j)
                    flag = True
                    break
            if not flag:
                # if there is no component open
                print("starting component: %s" % component.__name__)
                from .core.core import suggestName
                name = suggestName(components[i])
                components[i] = components[i](name=name, parent=window)
                window.addComponent(components[i])

        for link in links:
            dest = getattr(components[link[0][0]], link[0][1])
            orin = getattr(components[link[1][0]], link[1][1])
            if dest is orin:
                # already linked
                pass
            else:
                # not linked, link
                print("linking %s.%s to %s.%s" %
                      (components[link[1][0]].name, link[1][1],
                       components[link[0][0]].name, link[0][1]))
                # Disconect old Variable
                components[link[1][0]].disconnectSharedVariable(link[1][1])
                # comp1.var = comp0.var
                setattr(components[link[1][0]], link[1][1], dest)
                # Connect new Variable
                components[link[1][0]].connectSharedVariable(link[1][1])
                # Emit change signal
                dest.update()


def radar_mode():
    static_comp_list = componentsList[:]
    menu = None
    window = None
    for j, comp in enumerate(static_comp_list):
        print(comp)
        if isinstance(comp, FileNavigator) and menu is None:
            menu = comp
        elif isinstance(comp, Window) and window is None:
            window = comp
    if menu is None:
        menu = FileNavigator()
        window.addComponent(menu)

    from .core.core import suggestName
    radar = RadarDisplay(name=suggestName(RadarDisplay), Vradar=menu.Vradar,
                         parent=menu)
    window.addComponent(radar)

def grid_mode():
    static_comp_list = componentsList[:]
    menu = None
    window = None
    for j, comp in enumerate(static_comp_list):
        if isinstance(comp, FileNavigator) and menu is None:
            menu = comp
        elif isinstance(comp, Window) and window is None:
            window = comp

    if menu is None:
        menu = FileNavigator()
        window.addComponent(menu)

    from .core.core import suggestName
    grid = GridDisplay(name=suggestName(GridDisplay), Vgrid=menu.Vgrid,
                         parent=menu)
    window.addComponent(grid)

def map_to_grid_mode():
    change_mode(
        [FileNavigator, RadarDisplay, Mapper, GridDisplay],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            # link component 1 (RadarDisplay) Vradar to
            # component 0 (FileNavigator) Vradar
            ((1, 'Vradar'), (2, 'Vradar')),
            ((2, 'Vgrid'), (3, 'Vgrid')),
            ]
        )

# XXX Deprecated as this is standard startup
def compare_fields_mode():
    change_mode(
        [FileNavigator, RadarDisplay, RadarDisplay],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'Vradar'), (2, 'Vradar')),
            ((1, 'Vtilt'), (2, 'Vtilt')),
            ]
        )

def corrections_mode():
    change_mode(
        [FileNavigator, RadarDisplay],
        [((0, 'Vradar'), (1, 'Vradar')),]
        )

    static_comp_list = componentsList[:]
    window = None
    display = None
    for j, comp in enumerate(static_comp_list):
        if isinstance(comp, Window) and window is None:
            window = comp
        elif isinstance(comp, RadarDisplay) and display is None:
            display = comp

    widget = LayoutComponent(name="Corrections")
    window.addComponent(widget)

    widget.layout.addWidget(DealiasRegionBased(
        Vradar=display.Vradar, Vgatefilter=display.Vgatefilter), 0, 0)
    widget.layout.addWidget(DealiasUnwrapPhase(
        Vradar=display.Vradar, Vgatefilter=display.Vgatefilter), 1, 0)
    widget.layout.addWidget(PhaseProcLp(Vradar=display.Vradar), 2, 0)
    widget.layout.addWidget(CalculateAttenuation(Vradar=display.Vradar), 3, 0)
    widget.layout.addWidget(Despeckle(
        Vradar=display.Vradar, Vgatefilter=display.Vgatefilter,
        Vfield=display.Vfield), 4, 0)

    widget.layout.setRowStretch(5, 1)

def gatefilter_mode():
    change_mode(
        [FileNavigator, RadarDisplay, GateFilter],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'Vradar'), (2, 'Vradar')),
            ((1, 'Vgatefilter'), (2, 'Vgatefilter')),
            ]
        )

def select_region_mode():
    change_mode(
        [FileNavigator, RadarDisplay, SelectRegion],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'VplotAxes'), (2, 'VplotAxes')),
            ((1, 'Vfield'), (2, 'Vfield')),
            ((1, 'VpathInteriorFunc'), (2, 'VpathInteriorFunc')),
            ((1, 'Vgatefilter'), (2, 'Vgatefilter')),
            ((1, 'Vradar'), (2, 'Vradar')),
            ]
        )


def extract_points_mode():
    change_mode(
        [FileNavigator, RadarDisplay, SelectRegion, PointsDisplay],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'VplotAxes'), (2, 'VplotAxes')),
            ((1, 'Vfield'), (2, 'Vfield')),
            ((1, 'VpathInteriorFunc'), (2, 'VpathInteriorFunc')),
            ((1, 'Vgatefilter'), (2, 'Vgatefilter')),
            ((1, 'Vradar'), (2, 'Vradar')),
            ((2, 'Vpoints'), (3, 'Vpoints')),
            ((1, 'Vfield'), (3, 'Vfield')),
            # ((1, 'Vcolormap'), (3, 'Vcolormap')),
            ]
        )

def map_to_grid_mode():
    change_mode(
        [FileNavigator, RadarDisplay, GridDisplay, Mapper],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'Vradar'), (3, 'Vradar')),
            ((3, 'Vgrid'), (2, 'Vgrid')),
            ((1, 'Vfield'), (2, 'Vfield')),
            ]
        )

def manual_unfold_mode():
    change_mode(
        [FileNavigator, RadarDisplay, SelectRegion, ManualUnfold],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'VplotAxes'), (2, 'VplotAxes')),
            ((1, 'Vfield'), (2, 'Vfield')),
            ((1, 'VpathInteriorFunc'), (2, 'VpathInteriorFunc')),
            ((1, 'Vgatefilter'), (2, 'Vgatefilter')),
            ((1, 'Vradar'), (2, 'Vradar')),
            ((1, 'Vradar'), (3, 'Vradar')),
            ((2, 'Vpoints'), (3, 'Vpoints')),
            ]
        )

def manual_filter_mode():
    change_mode(
        [FileNavigator, RadarDisplay, SelectRegion, ManualFilter],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'VplotAxes'), (2, 'VplotAxes')),
            ((1, 'Vfield'), (2, 'Vfield')),
            ((1, 'VpathInteriorFunc'), (2, 'VpathInteriorFunc')),
            ((1, 'Vgatefilter'), (2, 'Vgatefilter')),
            ((1, 'Vradar'), (2, 'Vradar')),
            ((1, 'Vradar'), (3, 'Vradar')),
            ((2, 'Vpoints'), (3, 'Vpoints')),
            ((1, 'Vfield'), (3, 'Vfield')),
            ((1, 'Vgatefilter'), (3, 'Vgatefilter')),
            ]
        )

def filelist_mode():
    change_mode(
        [FileNavigator, DirectoryList],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((0, 'Vgrid'), (1, 'Vgrid')),
        ]
        )

def filedetail_mode():
    change_mode(
        [FileNavigator, FileDetail],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((0, 'Vgrid'), (1, 'Vgrid')),
        ]
        )

def despeckle_mode():
    change_mode(
        [FileNavigator, RadarDisplay, Despeckle],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'Vradar'), (2, 'Vradar')),
            ((1, 'Vfield'), (2, 'Vfield')),
            ((1, 'Vgatefilter'), (2, 'Vgatefilter')),
        ]
        )

def navigate_mode():
    change_mode(
        [FileNavigator, FileNavigator],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((0, 'Vgrid'), (1, 'Vgrid')),
            ((0, 'Vfilelist'), (1, 'Vfilelist')),
        ]
        )

def topography_mode():
    change_mode(
        [FileNavigator, RadarDisplay, TopographyBackground],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'VpyartDisplay'), (2, 'VpyartDisplay')),
            ]
        )

def background_mode():
    change_mode(
        [FileNavigator, RadarDisplay, ImageBackground],
        [
            ((0, 'Vradar'), (1, 'Vradar')),
            ((1, 'VpyartDisplay'), (2, 'VpyartDisplay')),
            ((1, 'Vradar'), (2, 'Vradar')),
            ((1, 'VplotAxes'), (2, 'VplotAxes')),
            ]
        )

def correlation_mode():
    change_mode(
    [FileNavigator, Correlation],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ]
    )

def radar_terminal_mode():
    change_mode(
    [FileNavigator, RadarDisplay, RadarTerminal],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'Vradar'), (2, 'Vradar')),
        ]
    )



modes = [
    {'label': 'Add RadarDisplay',
     'group': 'graph',
     'action': radar_mode},
    {'label': 'Add GridDisplay',
     'group': 'graph',
     'action': grid_mode},
    {'label': 'Map Radar to Grid',
     'group': 'map',
     'action': map_to_grid_mode},
    {'label': 'Apply corrections to Radar',
     'group': 'correct',
     'action': corrections_mode},
    {'label': 'Apply a filter to gates',
     'group': 'correct',
     'action': gatefilter_mode},
    {'label': 'Apply a filter to data',
     'group': 'correct',
     'action': manual_filter_mode},
    {'label': 'Manually unfold velocity',
     'group': 'correct',
     'action': manual_unfold_mode},
#    {'label': 'Despeckle Radar',
#     'group': 'correct',
#     'action': despeckle_mode},
    {'label': 'Query a selectable region of interest ',
     'group': 'select',
     'action': select_region_mode},
    {'label': 'Extract a selected region of points',
     'group': 'select',
     'action': extract_points_mode},
    {'label': 'File navigator',
     'group': 'io',
     'action': navigate_mode},
    {'label': 'File details',
     'group': 'io',
     'action': filedetail_mode},
    {'label': 'Directory View',
     'group': 'io',
     'action': filelist_mode},
    {'label': 'Add Topographic Background',
     'group': 'graph',
     'action': topography_mode},
    {'label': 'Radar Moments Correlation',
     'group': 'graph',
     'action': correlation_mode},
#    {'label': 'Add Image to Background',
#     'group': 'graph',
#     'action': background_mode},
    {'label': 'Manipulate Radar in Terminal',
     'group': 'terminal',
     'action': radar_terminal_mode},
    ]
