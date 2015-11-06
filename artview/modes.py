

from .components import *
from .plugins import *
from .core import componentsList

'''
A mode is a  tuple: (components, links) where:
* components is a list of uninitialized components
* links is a list of links, where a link is a tuple:
  ((destination_index, var_name), (origin_index, var_name))
  where `destination_index` and `origin_index` refere to the indexes in the
  components list of the origin and destination of the linking process, and
  `var_name` is the respective shared variable name.
'''


radar_mode = (
    [Menu, RadarDisplay],
    [
        ((0,'Vradar'),(1,'Vradar')),
        # link component 1 (RadarDisplay) Vradar to
        # component 0 (Menu) Vradar
        ]
    )

grid_mode = (
    [Menu, GridDisplay],
    [
        ((0,'Vgrid'),(1,'Vgrid')),
        ]
    )

radar_and_grid_mode = (
    [Menu, RadarDisplay, GridDisplay],
    [
        ((0,'Vradar'),(1,'Vradar')),
        ((0,'Vgrid'),(2,'Vgrid')),
        ((1,'Vfield'),(2,'Vfield')),
        ]
    )

map_to_grid_mode = (
    [Menu, RadarDisplay, Mapper, GridDisplay],
    [
        ((0,'Vradar'),(1,'Vradar')),
        ((1,'Vradar'),(2,'Vradar')),
        ((2,'Vgrid'),(3,'Vgrid')),
        ]
    )

compare_fields_mode = (
    [Menu, RadarDisplay, RadarDisplay],
    [
        ((0,'Vradar'),(1,'Vradar')),
        ((1,'Vradar'),(2,'Vradar')),
        ((1,'Vtilt'),(2,'Vtilt')),
        ]
    )

corrections_mode = (
    [Menu, RadarDisplay, DealiasRegionBased, DealiasUnwrapPhase, PhaseProcLp,
        CalculateAttenuation],
    [
        ((0,'Vradar'),(1,'Vradar')),
        ((1,'Vradar'),(2,'Vradar')),
        ((1,'Vradar'),(3,'Vradar')),
        ((1,'Vradar'),(4,'Vradar')),
        ((1,'Vradar'),(5,'Vradar')),
        ]
    )

gatefilter_mode = (
    [Menu, RadarDisplay, GateFilter],
    [
        ((0,'Vradar'),(1,'Vradar')),
        ((1,'Vradar'),(2,'Vradar')),
        ((1,'Vgatefilter'),(3,'Vgatefilter')),
        ]
    )

select_region_mode = (
    [Menu, RadarDisplay, SelectRegion],
    [
        ((0,'Vradar'),(1,'Vradar')),
        ((1,'VplotAxes'),(2,'VplotAxes')),
        ((1,'Vfield'),(2,'Vfield')),
        ((1,'VpathInteriorFunc'),(2,'VpathInteriorFunc')),
        ((1,'Vgatefilter'),(2,'Vgatefilter')),
        ((1,'Vradar'),(2,'Vradar')),
        ]
    )


map_to_grid_mode = (
    [Menu, RadarDisplay, GridDisplay, Mapper],
    [
        ((0,'Vradar'),(1,'Vradar')),
        ((1,'Vradar'),(3,'Vradar')),
        ((3,'Vgrid'),(2,'Vgrid')),
        ((1,'Vfield'),(2,'Vfield')),
        ]
    )

manual_unfold_mode = (
    [Menu, RadarDisplay, SelectRegion, ManualUnfold],
    [
        ((0,'Vradar'),(1,'Vradar')),
        ((1,'VplotAxes'),(2,'VplotAxes')),
        ((1,'Vfield'),(2,'Vfield')),
        ((1,'VpathInteriorFunc'),(2,'VpathInteriorFunc')),
        ((1,'Vgatefilter'),(2,'Vgatefilter')),
        ((1,'Vradar'),(2,'Vradar')),
        ((1,'Vradar'),(3,'Vradar')),
        ((2,'Vpoints'),(3,'Vpoints')),
        ]
    )

modes ={
    'radar': radar_mode,
    'map_to_grid': map_to_grid_mode,
    'grid': grid_mode,
    'radar_and_grid': radar_and_grid_mode,
    'compare_fields': compare_fields_mode,
    'corrections': corrections_mode,
    'gatefilter': gatefilter_mode,
    'select_region': select_region_mode,
    'manual_unfold': manual_unfold_mode,}
