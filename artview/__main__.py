# add this folder to path so I can import artview
import sys
import os

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)

import artview
try:
    from version import profiling
except:
    profiling = False

def main(argv):
    if profiling:
        import cProfile, pstats, StringIO
        pr = cProfile.Profile()
        pr.enable()

    script, DirIn, filename, field = artview.parser.parse(argv)

    if script:
        artview.scripts.scripts[script](DirIn, filename, field)
    else:
        artview.run(DirIn, filename, field)


    if profiling:
        pr.disable()
        stream = open('profile.txt', 'w')
        ps = pstats.Stats(pr, stream=stream).sort_stats('cumulative')
        ps.print_stats('artview')
        stream.close()

if __name__ == "__main__":
    main(sys.argv)
