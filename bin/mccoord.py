#!/usr/bin/env python3
"""
Tool to convert minecraft coordinates.
"""
__author__ = "Alexander Dietz"
__license__ = "MIT"


import sys
import math
import argparse

from pyblock import converter as conv


parser = argparse.ArgumentParser(description='Converting minecraft coordinates.')
parser.add_argument("--coords", nargs = 3,
                     help="Basic Minecraft block coordinates (x/y/z).")
parser.add_argument("--region", nargs=2,
                 help="Region file coordinates (x/z).")
args = parser.parse_args()

if not args.coords and not args.region:
    print("Error: Must specify either block coordinates or region coordinates.")
    parser.print_help()
    sys.exit(0)

region_size = 512
chunk_size = 16

if args.coords:
    x,y,z = map(int, args.coords)
    print(f"Coordinates: x={x} / y={y} / z={z}")
    
    region_x, region_z = conv.block_to_region(x, z)
    print(f"Region-file: r.{region_x}.{region_z}.mca")
    
    chunk_x, chunk_z = conv.block_to_chunk(x, z)
    print(f"Chunk: x={chunk_x} / z={chunk_z}")

elif args.region:
    x,z = map(int, args.region)
    print(f"Region-file: r.{x}.{z}.mca")
    
    ((min_x, max_x), (min_z, max_z)) = conv.region_to_block(x,z)    
    print(f"Coordinate ranges (inclusive): x: {min_x}-{max_x}  / z: {min_z}-{max_z}")