# capture-timelapse

A script to capture a timelapse of an activity as a series of screenshots.

Copyright (c) 2019 by Kevin Houlihan

License: MIT, see LICENSE for more details.

## Prerequisites

The script depends on Python 3.6 (though possibly earlier versions of Python 3 will work fine), and the [python-xlib](https://github.com/python-xlib/python-xlib) and [pyscreenshot](https://github.com/ponty/pyscreenshot) libraries. Only Unix systems with the X.org windowing system are supported at this time.

## Usage

At a minimum, the script requires a path to a destination directory and the partial title of a window to capture. Every 3 seconds, if a window is active that matches the specified title, its interior will be captured and output to a PNG file in the destination directory.

```
timelapse.py ~/kevin/timelapses/readme/01 README
```

Any window containing the specified text in its title will be captured. The matching is performed in a case-insensitive manner.

Multiple strings to match can also be specified, and any window matching any of the strings will be captured.

```
timelapse.py ~/kevin/timelapses/webdev/01 Sublime Firefox Chromium
```

The interval between screenshots, in seconds, can be specified using the `--interval` (`-i` for short) switch. The default is 3. It is not recommended to go much lower than this, as capturing and saving the screenshots is relatively intensive.