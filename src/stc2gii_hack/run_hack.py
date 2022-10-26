import argparse
import textwrap
from stc2gii_hack.hack import to_gii_simple

EXAMPLE_TEXT = """
---------------------------------------------------------------------------
Examples
---------------------------------------------------------------------------

Example 1: Basic Usage
----------------------
Suppose you have a BEM model called mymodel.fif, which was used to create
the source reconstruction files me-lh.stc and me-rh.stc in freesurfer
space. You would like the output gifti files to be called myhead*.gii.
Run

stc2gii_hack \ 
    mymodel.fif \ 
    me-lh.stc \ 
    me-rh.stc \ 
    myhead 

Example 2: Scaling Values
-------------------------
Suppose that in addition to getting output GIFTI files, you would like to
scale up the values in the STC file for visualization purposes. For this,
you can use the --scale parameter. To mirror Example 1, but scaling up data
values by one million, you would use

stc2gii_hack \ 
    --scale 1e6 \ 
    mymodel.fif \ 
    me-lh.stc \ 
    me-rh.stc \ 
    myhead 

Example 3: Scaling Coordinates
-------------------------
Suppose that in addition to getting output GIFTI files, you would like to
scale up the coordinates space in the STC file for visualization purposes.
This may be done if, for example, your visualization tool is expecting
millimeters but the STC is in meters. You can use the --scale_coordinates
parameter to do this. To mirror Example 1, but scale the coordinates
from meters to millimeters (a factor of one thousand), use

stc2gii_hack \ 
    --scale_coordinates 1e3 \ 
    mymodel.fif \ 
    me-lh.stc \ 
    me-rh.stc \ 
    myhead 
"""


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Hacky converter from MNE surfaces to GIFTI surfaces',
        epilog=textwrap.dedent(EXAMPLE_TEXT),
    )
    parser.add_argument('fif', help='The .fif file you would like to use.')
    parser.add_argument(
        'stc_left',
        help='The left .stc file you would like to use.'
    )
    parser.add_argument(
        'stc_right',
        help='the right .stc file you would like to use.'
    )
    parser.add_argument(
        'basename',
        help='The base name for the output GIFTI files.',
    )
    parser.add_argument(
        '--scale',
        type=float,
        default=1.0,
        help='The amount to scale STC data values by. Default 1.0.'
    )
    parser.add_argument(
        '--scale_coordinates',
        type=float,
        default=1e3,
        help='The amount to scale STC coordinates by. Default 1e3.'
    )
    args = parser.parse_args()

    if args.fif[-4:] != '.fif':
        raise ValueError(f'File {args.fif} is not a .fif file!')

    if args.stc_left[-4:] != '.stc':
        raise ValueError(f'File {args.stc_left} is not a .stc file!')

    if args.stc_right[-4:] != '.stc':
        raise ValueError(f'File {args.stc_right} is not a .stc file!')

    to_gii_simple(
        args.fif, [args.stc_left, args.stc_right], args.basename,
        args.scale, args.scale_coordinates,
    )


if __name__ == '__main__':
    main()
