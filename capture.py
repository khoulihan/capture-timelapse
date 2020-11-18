import sys
import Xlib.display
import time
from pathlib import Path
import os
#from os import path
import pyscreenshot as ImageGrab


_debug = False


def _verify_destination(destination):
    p = Path(destination)
    if not p.exists():
        p.mkdir()
    else:
        if p.is_file():
            raise NotADirectoryError()


def _determine_initial_index(destination):
    p = Path(destination)
    index_found = 0
    for f in p.iterdir():
        if f.is_file():
            if int(f.stem) > index_found:
                index_found = int(f.stem)
    return index_found + 1


def _determine_subdirectory_index(destination):
    p = Path(destination)
    index_found = 0
    for f in p.iterdir():
        if f.is_dir():
            if int(f.stem) > index_found:
                index_found = int(f.stem)
    return index_found + 1


def _get_active_target_window(disp, windows):
    focus = disp.get_input_focus()
    if focus.focus != 0 and focus.focus != 1:
        for w in windows:
            if w.lower() in str(focus.focus.get_wm_name()).lower():
                return focus.focus
            elif callable(getattr(focus.focus.query_tree()._data['parent'], 'get_wm_name', None)):
                if w.lower() in str(focus.focus.query_tree()._data['parent'].get_wm_name()).lower():
                    return focus.focus.query_tree()._data['parent']
    return None


def _get_true_active_target_window(disp, windows):
    focus = disp.get_input_focus()
    if focus.focus != 0 and focus.focus != 1:
        for w in windows:
            if w.lower() in str(focus.focus.get_wm_name()).lower():
                return focus.focus
    return None


def _capture_screenshot(window, destination, index):
    capture_start = time.monotonic()
    geom = window.get_geometry()
    # The parent geometry is the one that tells us the actual position on screen - the window geometry is the window interior relative to the parent.
    parent = window.query_tree()._data['parent']
    pgeom = parent.get_geometry()

    im = ImageGrab.grab(bbox=(pgeom.x + geom.x, pgeom.y + geom.y, pgeom.x + geom.x + geom.width, pgeom.y + geom.y + geom.height))
    im.save(str(destination / '{0:06d}.png'.format(index)))
    return time.monotonic() - capture_start


def _capture_timelapse(args):
    disp = Xlib.display.Display()
    destination = args.destination
    if args.create_subdirectories:
        capture_number = _determine_subdirectory_index(destination)
        destination = Path(destination) / '{0:02}'.format(capture_number)
        if not destination.exists():
            destination.mkdir()
    screenshot_index = _determine_initial_index(destination)
    dest_path = Path(destination)
    initial_time = time.monotonic()
    while(True):
        if time.monotonic() - initial_time >= args.interval:
            initial_time = time.monotonic()
            window = _get_active_target_window(disp, args.windows)
            if window is not None:
                elapsed = _capture_screenshot(window, dest_path, screenshot_index)
                screenshot_index += 1
                if args.debug:
                    print ("Screenshot time: {0}".format(elapsed))
                if elapsed > args.interval:
                    print ("Warning: Screenshot capture took longer than wait interval ({0})".format(elapsed))
        time.sleep(0.001)


def capture(args):
    global _debug
    _debug = args.debug

    try:
        _verify_destination(args.destination)
    except NotADirectoryError:
        print ("The specified destination is not a directory.")
        sys.exit(1)
    except FileNotFoundError:
        print ("The specified destination directory could not be created because of missing parents.")
        sys.exit(1)
    except PermissionError:
        print ("The destination directory could not be created due to inadequate permissions.")
        sys.exit(1)

    try:
        _capture_timelapse(args)
    except IOError as error:
        print (error)
        print ("An IO error occurred while saving a screenshot to a file.")
        sys.exit(1)
    except PermissionError:
        print ("A screenshot could not be saved due to inadequate permissions")
        sys.exit(1)
