

from .components import RadarDisplay, GridDisplay, Menu
from .plugins import _plugins
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


radar_mode = ([Menu, RadarDisplay],
              [
                  ((0,'Vradar'),(1,'Vradar'))
                  # link component 1 (RadarDisplay) Vradar to
                  # component 0 (Menu) Vradar
                  ]
             )

map_to_grid_mode = (
    [Menu, RadarDisplay, GridDisplay, _plugins["Mapper"]],
    [
        ((0,'Vradar'),(1,'Vradar')),
        ((1,'Vradar'),(3,'Vradar')),
        ((3,'Vgrid'),(2,'Vgrid')),
        ((1,'Vfield'),(2,'Vfield')),
        ]
    )


modes ={
    'radar': radar_mode,
    'map_to_grid': map_to_grid_mode
    }
