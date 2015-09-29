"""
_parse_field.py

function to parse for a valid reflectivity field
"""
import pyart

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

    if container is None:
        return field

    fieldnames = container.fields.keys()
    Zinfile = set(fieldnames).intersection(Zlike)
    if field == pyart.config.get_field_name('reflectivity'):
        if field not in fieldnames and len(Zinfile) > 0:
            field = Zinfile.pop()

    return field
