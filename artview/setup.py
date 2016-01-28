
def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('artview', parent_package, top_path)
    config.add_subpackage('core')
    config.add_subpackage('components')
    config.add_subpackage('plugins')
    config.add_subpackage('scripts')
#    config.add_subpackage('icons')
    config.add_data_dir('icons')

    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
