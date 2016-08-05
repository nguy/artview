
from .components import *
from .plugins import *
from .core import componentsList

'''
A mode is a  tuple: (components, links) where:
* components is a list of uninitialized components
* links is a list of links, where a link is a tuple:
  ((destination_index, var_name), (origin_index, var_name))
  where `destination_index` and `origin_index` refer to the indexes in the
  components list of the origin and destination of the linking process, and
  `var_name` is the respective shared variable name.
'''


radar_mode = (
    [Menu, RadarDisplay],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        # link component 1 (RadarDisplay) Vradar to
        # component 0 (Menu) Vradar
        ]
    )

grid_mode = (
    [Menu, GridDisplay],
    [
        ((0, 'Vgrid'), (1, 'Vgrid')),
        ]
    )

# Deprecated - duplicated of grid_mode and radar_mode
radar_and_grid_mode = (
    [Menu, RadarDisplay, GridDisplay],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((0, 'Vgrid'), (2, 'Vgrid')),
        ((1, 'Vfield'), (2, 'Vfield')),
        ]
    )

map_to_grid_mode = (
    [Menu, RadarDisplay, Mapper, GridDisplay],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'Vradar'), (2, 'Vradar')),
        ((2, 'Vgrid'), (3, 'Vgrid')),
        ]
    )

# XXX Deprecated as this is standard startup
compare_fields_mode = (
    [Menu, RadarDisplay, RadarDisplay],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'Vradar'), (2, 'Vradar')),
        ((1, 'Vtilt'), (2, 'Vtilt')),
        ]
    )

corrections_mode = (
    [Menu, RadarDisplay, DealiasRegionBased, DealiasUnwrapPhase, PhaseProcLp,
        CalculateAttenuation],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'Vradar'), (2, 'Vradar')),
        ((1, 'Vradar'), (3, 'Vradar')),
        ((1, 'Vradar'), (4, 'Vradar')),
        ((1, 'Vradar'), (5, 'Vradar')),
        ]
    )

gatefilter_mode = (
    [Menu, RadarDisplay, GateFilter],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'Vradar'), (2, 'Vradar')),
        ((1, 'Vgatefilter'), (2, 'Vgatefilter')),
        ]
    )

select_region_mode = (
    [Menu, RadarDisplay, SelectRegion],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'VplotAxes'), (2, 'VplotAxes')),
        ((1, 'Vfield'), (2, 'Vfield')),
        ((1, 'VpathInteriorFunc'), (2, 'VpathInteriorFunc')),
        ((1, 'Vgatefilter'), (2, 'Vgatefilter')),
        ((1, 'Vradar'), (2, 'Vradar')),
        ]
    )


extract_points_mode = (
    [Menu, RadarDisplay, SelectRegion, PointsDisplay],
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

map_to_grid_mode = (
    [Menu, RadarDisplay, GridDisplay, Mapper],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'Vradar'), (3, 'Vradar')),
        ((3, 'Vgrid'), (2, 'Vgrid')),
        ((1, 'Vfield'), (2, 'Vfield')),
        ]
    )

manual_unfold_mode = (
    [Menu, RadarDisplay, SelectRegion, ManualUnfold],
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

manual_filter_mode = (
    [Menu, RadarDisplay, SelectRegion, ManualFilter],
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

filelist_mode = (
    [Menu, DirectoryList],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((0, 'Vgrid'), (1, 'Vgrid')),
    ]
)

filedetail_mode = (
    [Menu, FileDetail],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((0, 'Vgrid'), (1, 'Vgrid')),
    ]
)

despeckle_mode = (
    [Menu, RadarDisplay, Despeckle],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'Vradar'), (2, 'Vradar')),
        ((1, 'Vfield'), (2, 'Vfield')),
        ((1, 'Vgatefilter'), (2, 'Vgatefilter')),
    ]
)

navigate_mode = (
    [Menu, FileNavigator],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((0, 'Vgrid'), (1, 'Vgrid')),
        ((0, 'Vfilelist'), (1, 'Vfilelist')),
    ]
)

topography_mode = (
    [Menu, RadarDisplay, TopographyBackground],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'VpyartDisplay'), (2, 'VpyartDisplay')),
        ]
    )

background_mode = (
    [Menu, RadarDisplay, ImageBackground],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((1, 'VpyartDisplay'), (2, 'VpyartDisplay')),
        ((1, 'Vradar'), (2, 'Vradar')),
        ((1, 'VplotAxes'), (2, 'VplotAxes')),
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
    {'label': 'Despeckle Radar',
     'group': 'correct',
     'action': despeckle_mode},
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
#    {'label': 'Add Image to Background',
#     'group': 'graph',
#     'action': background_mode},
    ]
