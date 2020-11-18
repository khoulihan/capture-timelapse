import sys
import os
from PIL import Image, ImageColor
from pathlib import Path
import json


_debug = False
_test = False


def _verify_source(source):
    p = Path(source)
    if not p.exists():
        raise FileNotFoundError()
    else:
        if p.is_file():
            raise NotADirectoryError()


def _verify_destination(destination):
    p = Path(destination)
    if not p.exists():
        p.mkdir()
    else:
        if p.is_file():
            raise NotADirectoryError()


def _check_rule(frame, rule):
    rule_type = rule['type']
    if rule_type == 'size':
        match = frame.width == rule['width'] and frame.height == rule['height']
        if not match and _debug:
            print("Size rule broken (%s) (image is (%d, %d), rule requires (%d, %d))" % (rule['name'], frame.width, frame.height, rule['width'], rule['height']))
        return match
    elif rule_type == 'pixel_colour' or rule_type == 'pixel_not_colour':
        pixel = None
        try:
            pixel = frame.getpixel((rule['x'], rule['y']))
        except IndexError:
            # This occurs if the frame is smaller than expected
            return False
        rule_color = ImageColor.getrgb(rule['colour'])
        match = rule_color == pixel
        if rule_type == 'pixel_colour' and not match and _debug:
            print("Colour rule broken (%s)" % rule['name'])
        if rule_type == 'pixel_not_colour' and match and _debug:
            print("Inverse colour rule broken (%s)" % rule['name'])
        if rule_type == 'pixel_colour':
            return match
        else:
            return not match
    elif rule_type == 'or':
        sub_rules = rule["rules"]
        match = any(map(lambda sub_rule: _check_rule(frame, sub_rule), sub_rules))
        if not match and _debug:
            print("Or rule broken (%s)" % rule['name'])
        return match


def _check_rules(frame, specification):
    passed = all(map(lambda rule: _check_rule(frame, rule), specification['rules']))
    if not passed:
        if _debug:
            print('Frame broke rules for specification "%s"' % specification['name'])
    return passed


def _process_frame(frame_path, destination, delete_immediately, specifications):
    passed = None
    with Image.open(frame_path) as frame:
        passed = any(map(lambda spec: _check_rules(frame, spec), specifications))
    if not passed:
        if _debug:
            print('Bad frame detected (%s)' % frame_path)
        if not _test:
            if delete_immediately:
                frame_path.unlink()
            else:
                frame_path.rename(Path(destination) / frame_path.name)

    return passed


def _process_ultimate_source(
    source,
    destination,
    delete_immediately,
    specifications,
    rejected,
    processed
):
    for frame in Path(source).iterdir():
        if frame.is_file():
            processed += 1
            if not _process_frame(frame, destination, delete_immediately, specifications):
                rejected.append(frame)
    return processed, rejected


def _process_source(
    source,
    check_children,
    destination,
    delete_immediately,
    specifications
):
    rejected = []
    processed = 0
    processed, rejected = _process_ultimate_source(
        source,
        destination,
        delete_immediately,
        specifications,
        rejected,
        processed
    )
    if check_children:
        for child in Path(source).iterdir():
            if child.is_dir():
                child_destination = Path(destination) / child.name
                if not delete_immediately:
                    child_destination.mkdir(exist_ok=True)
                processed, rejected = _process_ultimate_source(
                    child,
                    child_destination,
                    delete_immediately,
                    specifications,
                    rejected,
                    processed
                )

    return processed, rejected


def _get_spec_path(spec):
    spec_path = Path(spec)
    if spec_path.exists():
        return spec_path
    try:
        xdg_config = Path(os.environ['XDG_CONFIG_HOME'])
    except KeyError:
        xdg_config = Path('~/.config').expanduser()
    spec_path = xdg_config / 'timelapse' / 'framespecs' / '{}.json'.format(spec)
    return spec_path


def clean(args):
    global _debug, _test
    _debug = args.debug
    _test = args.test
    parsed_specifications = []

    try:
        _verify_source(args.source)
    except FileNotFoundError:
        print ("The specified source does not exist.")
        sys.exit(1)
    except NotAFileError:
        print ("The specified source is not a file.")
        sys.exit(1)

    try:
        if not args.delete_immediately:
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
        for spec in args.specification:
            spec_path = _get_spec_path(spec)
            with spec_path.open() as spec_file:
                parsed_specifications.append(json.load(spec_file))
    except FileNotFoundError as e:
        print ("The specification file does not exist (%s)." % e.filename)
        sys.exit(1)

    # TODO: Validate specifications

    if _debug:
        print("Parsed specifications:")
        for spec in parsed_specifications:
            print(spec)

    processed, rejected = _process_source(args.source, args.check_children, args.destination, args.delete_immediately, parsed_specifications)

    print("%d frame(s) rejected of %d processed" % (len(rejected), processed))
    if _test:
        for r in rejected:
            print (r)
