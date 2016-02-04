

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
        ((1, 'Vgatefilter'), (3, 'Vgatefilter')),
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
    [Menu, RadarDisplay, SelectRegion_dev, PointsDisplay],
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
    [Menu, RadarDisplay, SelectRegion_dev, ManualUnfold],
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
    [Menu, RadarDisplay, SelectRegion_dev, ManualFilter],
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

filelist_mode= (
    [Menu, DirectoryList],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((0, 'Vgrid'), (1, 'Vgrid')),
    ]
)

filedetail_mode= (
    [Menu, FileDetail],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((0, 'Vgrid'), (1, 'Vgrid')),
    ]
)

navigate_mode= (
    [Menu, FileNavigator],
    [
        ((0, 'Vradar'), (1, 'Vradar')),
        ((0, 'Vgrid'), (1, 'Vgrid')),
        ((0, 'Vfilelist'), (1, 'Vfilelist')),
    ]
)

modes = [
         {'label': 'Add RadarDisplay',
          'action': radar_mode},
         {'label': 'Add GridDisplay',
          'action': grid_mode},
         {'label': 'Map Radar to Grid',
         'action': map_to_grid_mode},
         {'label': 'Apply corrections to Radar',
          'action': corrections_mode},
         {'label': 'Apply a filter to gates',
          'action': gatefilter_mode},
         {'label': 'Query a selectable region of interest ',
          'action': select_region_mode},
         {'label': 'Extract a selected region of points',
          'action': extract_points_mode},
         {'label': 'Manually unfold velocity',
          'action': manual_unfold_mode},
         {'label': 'Apply a filter to data',
          'action': manual_filter_mode},
         {'label': 'File navigator',
          'action': navigate_mode},
         {'label': 'File details',
          'action': filedetail_mode},
         {'label': 'Filelist',
          'action': filelist_mode},
        ]
