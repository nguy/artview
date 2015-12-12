"""
points.py
"""

import numpy as np


class Points:
    '''
    This class is a container for unstructured radar data and is designed
    based in :py:class:`pyart.core.Grid` as it stands now, modification in that
    class shall also be applied here. Just as :py:class:`~pyart.core.Grid` and
    :py:class:`~pyart.core.Radar` this is based in netCDF and the
    CF-conventions.
    This class has 4 attributes
    * npoints: number of points
    * fields: dictionary of pyart variables, representing radar data. All with
      shape (npoints,).
    * axes: dictionary of pyart variables. There is no mandatory variable, but
      the following ones can be present:
        * time, time_start, time_end: CF time variable with shape (1,) or
          (npoints,).
        * lat, lon, alt: geographic coordinated of origin, shape: (1,) or
          (npoints,).
        * x_disp, y_disp, z_disp: position of the points in Cartesian
          coordinates from origin, shape: (npoints,).
        * elevation, azimuth, range: position of the points in radar
          coordinates from origin, shape: (npoints,).
        * heading, roll, pitch, drift, rotation, tilt: localization variables
          for radar in moving platform, according to CfRadia convention,
          shape: (npoints,).
        * x_index, y_index, z_index: indexes in a Grid object,
          shape: (npoints,).
        * ray_index, range_index: indexes in a Radar object, shape: (npoints,).
    * metadata: dictionary of global attributes

    Py-ART Variable
    ---------------
    A Py-ART variable is a dictionary or dictionary-like instance made to
    represent a netcdf variable. It has some special keys:
        * 'data': numpy array containing the variables data
        * 'least_significant_digit', '_DeflateLevel', '_Endianness',
          '_Fletcher32', '_Shuffle', '_ChunkSizes', '_FillValue': netCDF4
          special netcdf attributes defining how the data is to be saved in
          the disc.
        * '_Write_as_dtype': numpy dtype indicating of preferential type to
          use while saving in disc.
        * 'scale_factor', 'add_offset': scaling information to convert from
          disc value to data value
    All other keys are interpreted as normal netcdf attributes. Besides
    'data', all keys are optional.
    '''

    axes_keys = ['time', 'time_start', 'time_end', 'lat', 'lon', 'alt',
                 'x_disp', 'y_disp', 'z_disp', 'elevation', 'azimuth',
                 'range', 'heading', 'roll', 'pitch', 'drift', 'rotation',
                 'tilt', 'x_index', 'y_index', 'z_index', 'ray_index',
                 'range_index']
    ''' recognised axes keys '''

    def __init__(self, fields, axes, metadata, npoints):
        ''' Initalize object. '''
        self.fields = {}
        self.metadata = metadata
        self.axes = axes
        self.npoints = npoints
        for key in fields.keys():
            self.add_field(key, fields[key])
        return

    def check_field_exists(self, field_name):
        '''
        Check that a field exists in the fields dictionary.
        If the field does not exist raise a KeyError.
        Parameters
        ----------
        field_name : str
            Name of field to check.
        '''
        if field_name not in self.fields:
            raise KeyError('Field not available: ' + field_name)
        return

    def add_field(self, field_name, dic, replace_existing=False):
        '''
        Add a field to the object.
        Parameters
        ----------
        field_name : str
            Name of the field to add to the dictionary of fields.
        dic : dict
            Dictionary contain field data and metadata.
        replace_existing : bool
            True to replace the existing field with key field_name if it
            exists, loosing any existing data.  False will raise a ValueError
            when the field already exists.
        '''
        # check that the field dictionary to add is valid
        if field_name in self.fields and replace_existing is False:
            err = 'A field with name: %s already exists' % (field_name)
            raise ValueError(err)
        if 'data' not in dic:
            raise KeyError("dic must contain a 'data' key")
        if dic['data'].shape != (self.npoints,):
            t = (self.npoints,)
            err = str("'data' has invalid shape, should be (%i,)" % t)
            raise ValueError(err)
        # add the field
        self.fields[field_name] = dic
        return

    def add_field_like(self, existing_field_name, field_name, data,
                       replace_existing=False):
        '''
        Add a field to the object with metadata from a existing field.
        Parameters
        ----------
        existing_field_name : str
            Name of an existing field to take metadata from when adding
            the new field to the object.
        field_name : str
            Name of the field to add to the dictionary of fields.
        data : array
            Field data.
        replace_existing : bool
            True to replace the existing field with key field_name if it
            exists, loosing any existing data.  False will raise a ValueError
            when the field already exists.
        '''
        if existing_field_name not in self.fields:
            err = 'field %s does not exist in object' % (existing_field_name)
            raise ValueError(err)
        dic = {}
        for k, v in self.fields[existing_field_name].items():
            if k != 'data':
                dic[k] = v
        dic['data'] = data
        return self.add_field(field_name, dic,
                              replace_existing=replace_existing)

import csv


def write_points_csv(filename, points):
    '''
    Write a Points object to a CSV file
    Parameters
    ----------
    filename : str
        Filename to save points to.
    point : Point
        Point object to write.
    '''
    axes_key = points.axes.keys()
    fields_keys = points.fields.keys()
    axes = {}
    for key in axes_key:
        axes[key] = np.ma.resize(points.axes[key]['data'], (points.npoints,))
    with open(unicode(filename), 'wb') as stream:
        writer = csv.writer(stream)

        # header
        rowdata = []
        for key in axes_key:
            rowdata.append(unicode(key).encode('utf8'))
        for key in fields_keys:
            rowdata.append(unicode(key).encode('utf8'))
        writer.writerow(rowdata)

        # data
        for row in range(points.npoints):
            rowdata = []
            for key in axes_key:
                item = axes[key][row]
                if item is not None:
                    rowdata.append(
                        unicode(item).encode('utf8'))
                else:
                    rowdata.append('')
            for key in fields_keys:
                item = points.fields[key]['data'][row]
                if item is not None:
                    rowdata.append(
                        unicode(item).encode('utf8'))
                else:
                    rowdata.append('')
            writer.writerow(rowdata)


def read_points_csv(filename):
    '''
    Read a Points object from a CSV file
    Parameters
    ----------
    filename : str
        Filename to read points from.
    Returns
    -------
    point : Point
        Point object read.
    '''
    data = []
    with open(unicode(filename), 'rb') as stream:
        for rowdata in csv.reader(stream):
            data.append(rowdata)

    header = data.pop(0)
    arrays = {}
    npoints = len(data)
    for key in header:
        arrays[key] = np.ma.masked_all((npoints,))

    for row, rowdata in enumerate(data):
        for column, item in enumerate(rowdata):
            if item != '':
                arrays[header[column]][row] = float(item.decode('utf8'))

    axes = {}
    fields = {}
    for key in header:
        if key in Points.axes_keys:
            axes[key] = {'data': arrays[key]}
        else:
            fields[key] = {'data': arrays[key]}
    points = Points(fields, axes, {}, npoints)
    return points
