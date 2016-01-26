"""
icons.py

Functions for icon retrieval
"""
import os
from ..core import QtGui, QtCore


def get_arrow_icon_dict():
    ''' Return arrow dictionary of PyQt icons. '''
    arrow_icons = {}
#    previmage = QtGui.QPixmap(os.path"arrow_go_previous_icon.png")
    previmage = QtGui.QPixmap(os.path.join("/Users/guy/software/python/artview/icons","arrow_go_previous_icon.png"))
    arrow_icons['previous'] = QtGui.QIcon(previmage)

    nextimage = QtGui.QPixmap("arrow_go_next_icon.png")
    arrow_icons['next'] = QtGui.QIcon(nextimage)

    firstimage = QtGui.QPixmap("arrow_go_first_icon.png")
    arrow_icons['first'] = QtGui.QIcon(firstimage)

    lastimage = QtGui.QPixmap("arrow_go_last_icon.png")
    arrow_icons['last'] = QtGui.QIcon(lastimage)

    playimage = QtGui.QPixmap("arrow_go_play_icon.png")
    arrow_icons['play'] = QtGui.QIcon(playimage)
    return arrow_icons

def get_playback_icon_dict():
    ''' Return playback dictionary of PyQt icons. '''
    playback_icons = {}
    startimage = QtGui.QPixmap("playback_start_icon.png")
    playback_icons['start'] = QtGui.QIcon(startimage)

    stopimage = QtGui.QPixmap("playback_stop_icon.png")
    playback_icons['stop'] = QtGui.QIcon(stopimage)

    pauseimage = QtGui.QPixmap("playback_pause_icon.png")
    playback_icons['pause'] = QtGui.QIcon(pauseimage)

    recordimage = QtGui.QPixmap("playback_record_icon.png")
    playback_icons['record'] = QtGui.QIcon(recordimage)

    backimage = QtGui.QPixmap("playback_skip_backward_icon.png")
    playback_icons['back'] = QtGui.QIcon(backimage)

    forwardimage = QtGui.QPixmap("playback_skip_forward_icon.png")
    playback_icons['forward'] = QtGui.QIcon(forwardimage)

    fastbackimage = QtGui.QPixmap("playback_seek_backward_icon.png")
    playback_icons['fastback'] = QtGui.QIcon(fastbackimage)

    fastforwardimage = QtGui.QPixmap("playback_seek_forward_icon.png")
    playback_icons['fastforward'] = QtGui.QIcon(fastforwardimage)
    return playback_icons