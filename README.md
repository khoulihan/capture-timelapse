# capture-timelapse

Capture a timelapse of an activity as a series of screenshots, and process it into video clips.

Copyright (c) 2020 by Kevin Houlihan

License: MIT, see LICENSE for more details.

## Prerequisites

Depends on Python 3.7 (though possibly earlier versions of Python 3 will work fine), the [python-xlib](https://github.com/python-xlib/python-xlib), [pyscreenshot](https://github.com/ponty/pyscreenshot), and [Pillow](https://python-pillow.org/) libraries. The ffmpeg command line utility must be installed and available in the path. Only Unix systems with the X.org windowing system are supported at this time.

## Usage

The script accepts three commands - capture, clean, and convert. They are expected to be used in sequence.

### Capture

At a minimum, this command requires a path to a destination directory and the partial title of a window to capture. Every 3 seconds, if a window is active that matches the specified title, its interior will be captured and output to a PNG file.

```
timelapse capture ~/kevin/timelapses/readme README
```

Any window containing the specified text in its title will be captured. The matching is performed in a case-insensitive manner.

Multiple strings to match can also be specified, and any window matching any of the strings will be captured.

```
timelapse capture ~/kevin/timelapses/webdev Sublime Firefox Chromium
```

The interval between screenshots, in seconds, can be specified using the `--interval` (`-i` for short) switch. The default is 3. It is not recommended to go much lower than this, as capturing and saving the screenshots is relatively intensive.

By default, captures are made to numbered sub-directories of the destination directory. To capture directly to the destination, use the `--single` (`-s` for short) switch. Repeated captures to a single directory will continue the image sequence.

```
timelapse capture --single ~/kevin/timelapses/webdev/01 Sublime Firefox Chromium
```

### Clean

This command requires at least one specification file to define what a "good" frame is, and a target directory with the timelapse sequence to check.

```
timelapse clean specs/pyxel_edit.json ./timelapse
```

If multiple applications were expected to be captured by the timelapse, multiple specification files can be listed. If a frame passes according to at least one of the specifications, it will not be rejected.

```
timelapse clean specs/pyxel_edit.json specs/godot.json timelapse
```

Specification files can also be specified by name if they are included in the script's config directory (`~/.config/timelapse/framespecs` by default). The file extension is not required in this case.

```
timelapse clean pyxel_edit timelapse
```

#### Destination

By default, any bad frames detected will be moved to a directory called "rejected" in the current working directory.

The specify a different destination, use the `--destination` flag.

```
timelapse clean --destination ../rejected_frames pyxel_edit timelapse
```

#### Delete Immediately

To delete frames immediately instead of moving them, add the `--delete` flag. This is not recommended unless you're sure your specification files work exactly as you want.

```
timelapse clean --delete pyxel_edit timelapse
```

#### Single

By default, the source is expected to be structured as several sequences in subdirectories. The rejected frames will be placed in subdirectories of the destination with the same names. To check a single sequence directly, use the `--single` (`-s` for short) switch. Rejected frames will be placed directly in the output directory.

```
timelapse clean --single --destination ./rejected/01 pyxel_edit ./timelapse/01
```

#### Test

To only perform the checks, but not move or delete the detected bad frames, use the `--test` switch. A list of detected bad frames will be output to the terminal.

```
timelapse clean --test specs/pyxel_edit.json timelapse
```

### Convert

At minimum, this command just takes a source directory as input. The source is expected to contain subdirectories, as per the output of the `capture` command. An mp4 video clip will be generated for each subdirectory at 20 FPS and placed in an output directory called "clips" in the current working directory.

An extra clip will also be generated based on the final frame of the last subdirectory, stretched out to a minute in length, to be used as padding if a pause is desired at the end of the video.

```
timelapse convert ~/timelapses/ldjam/
```

An alternative destination can be specified with the `--destination` switch.

The framerate can be specified with the `--framerate` (`-f` for short) switch.

If the source is a single image sequence, the `--single` (`-s` for short) can be used to indicate this.

Finally, if a padding clip is not required, it can be skipped with the switch `--skip-pad-clip`.

### Debug

The `--debug` or `-d` switch can be used with all commands to print debugging information to the terminal. This can be quite verbose, but may be useful in determining why something is going wrong, particularly with the `clean` command.

## Frame Specification Format

Frame specification files contain a json formatted set of rules to match each frame against. If any rule is broken then the frame is deemed to be "bad" according to the specification.

The root of the file should be a json object with keys "name", which is the name of the specification, and "rules", which is an array of rule objects to apply.

```json
{
    "name": "Pyxel Edit",
    "rules": [
    		...
    ]
}
```

Rule objects must always contain "name" and "type" keys. The name can be anything, but is used in debugging output to indicate broken rules, while the type must be one of `size`, `pixel_colour`, `pixel_not_colour`, or `or`. The remaining required keys differs for each type.

### size

This rule type checks that the dimensions of the screenshot match what was expected. If a dialog box was captured instead of the main application window, it will be rejected based on this rule.

```json
{
    "name": "Size",
    "type": "size",
    "width": 2560,
    "height": 1356
}
```

### pixel_colour

This rule type checks that a specific pixel in the image is a particular colour. Select an invariant location on the target application's window to detect frames where the window has just been minimized or where another application has been captured accidentally. Also can be useful for detecting when dropdown menus were open.

```json
{
    "name": "Window normal",
    "type": "pixel_colour",
    "x": 3,
    "y": 1353,
    "colour": "#555555"
}
```

### pixel_not_colour

This rule is the inverse of `pixel_colour`, and is passed as long as the specified pixel is *not* the specified colour.

```json
{
    "name": "Edit menu",
    "type": "pixel_not_colour",
    "x": 34,
    "y": 2,
    "colour": "#ebe9ed"
}
```

### or

This rule type takes a set of sub-rules. If any one of the sub-rules is passed then the rule as a whole will pass. This is useful where a pixel can be one of several colours without indicating a bad frame.

```json
{
    "name": "Window normal",
    "type": "or",
    "rules": [
        {
            "name": "Window normal",
            "type": "pixel_colour",
            "x": 3,
            "y": 1353,
            "colour": "#1f2531"
        },
        {
            "name": "Window occluded",
            "type": "pixel_colour",
            "x": 3,
            "y": 1353,
            "colour": "#0c0f14"
        }
    ]
}
```
