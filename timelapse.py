#!/usr/bin/env python3

import sys
import argparse
from capture import capture
from clean import clean
from convert import convert

def _parse_arguments():
    parser = argparse.ArgumentParser(
        description="Capture a timelapse of some activity."
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        dest="debug",
        help="print debugging information"
    )
    subparsers = parser.add_subparsers(dest='command')

    # Capture command
    capture_parser = subparsers.add_parser(
        'capture', aliases=['cap'],
        help="capture a timelapse"
    )
    capture_parser.add_argument(
        "destination",
        type=str,
        action="store",
        help="destination directory for timelapse captures"
    )
    # Consider nargs='*' to allow a default of capturing all processes.
    capture_parser.add_argument(
        "windows",
        metavar='W',
        type=str,
        nargs='+',
        help="title of window(s) that should be captured when active"
    )
    capture_parser.add_argument(
        "-i", "--interval",
        metavar='I',
        dest="interval",
        action="store",
        default=3,
        type=int,
        help="the period between screenshots, in seconds"
    )
    capture_parser.add_argument(
        "-s", "--single",
        dest="single",
        action="store_true",
        help=(
            "indicates that the destination should be treated as a single image"
            " sequence instead of storing separate sessions in subdirectories"
        )
    )

    clean_parser = subparsers.add_parser(
        'clean',
        help="detect and remove bad frames from the image sequence"
    )
    clean_parser.add_argument(
        "source",
        type=str,
        action="store",
        help="source directory for image sequences"
    )
    clean_parser.add_argument(
        "specification",
        type=str,
        action="store",
        nargs="+",
        help="specification of what to check for in the images"
    )
    clean_parser.add_argument(
        "--destination",
        dest="destination",
        metavar='D',
        type=str,
        action="store",
        default="rejected",
        help="destination directory for bad frames"
    )
    clean_parser.add_argument(
        "--delete",
        action="store_true",
        dest="delete_immediately",
        help=(
            "delete detected frames immediately instead of moving them to a"
            " rejection directory"
        )
    )
    clean_parser.add_argument(
        "-s", "--single",
        action="store_true",
        dest="single",
        help="only check the specified directory instead of looking for subdirectories"
    )
    clean_parser.add_argument(
        "--test",
        action="store_true",
        dest="test",
        help="check the rules but do not move or delete the frames"
    )

    compile_parser = subparsers.add_parser(
        'convert', aliases=['con'],
        help="prepare video clips"
    )
    compile_parser.add_argument(
        "source",
        type=str,
        action="store",
        help="source directory for image sequences"
    )
    compile_parser.add_argument(
        "--destination",
        dest="destination",
        metavar='D',
        type=str,
        action="store",
        default="clips",
        help="destination directory for raw clips"
    )
    compile_parser.add_argument(
        "-f",
        "--framerate",
        metavar='F',
        dest="framerate",
        action="store",
        default=20,
        type=int,
        help="the framerate to use for the video clips"
    ) # TODO: Determine best default
    compile_parser.add_argument(
        "-s",
        "--single",
        dest="single",
        action="store_true",
        help=(
            "indicates that the source should be treated as a single image"
            " sequence instead of separate sessions stored in subdirectories"
        )
    )
    compile_parser.add_argument(
        "--skip-pad-clip",
        action="store_true",
        dest="skip_pad_clip",
        help="skip creation of a padding clip based  on the final frame"
    )

    args = parser.parse_args()
    return args


def _main():
    args = _parse_arguments()
    global _debug
    _debug = args.debug
    try:
        if args.command in ['capture', 'cap']:
            capture(args)
        elif args.command in ['clean']:
            clean(args)
        elif args.command in ['convert', 'con']:
            convert(args)
    except KeyboardInterrupt:
        # TODO: Maybe track some statistics and print them on exit.
        # Redisplay the cursor
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()
        print()
        sys.exit(0)


if __name__ == "__main__":
    _main()
