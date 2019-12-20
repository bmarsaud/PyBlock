#!/usr/bin/env python3
"""
Application to analyze and find block in minecraft.
"""
__author__ = "Alexander Dietz"
__license__ = "MIT"

import os
import sys
import pprint
import argparse

from pyblock import converter as conv
from pyblock import parsemca


parser = argparse.ArgumentParser(description='Minecrafter is a tool to help minecrafting.'\
                                 ' It helps you find blocks in your area.')
parser.add_argument("--world",
                    help="Path to the minecraft world. Or define MINECRAFTWORLD.")
parser.add_argument("--coords", nargs = 3, type=int,
                    help="Basic Minecraft coordinates (x/y/z).")
parser.add_argument("--radius", type=int, default=10,
                    help="The search radius (in block units, max 50).")
parser.add_argument("--vertical",  action="store_true", default=False,
                    help="The whole vertical area is being searched.")
parser.add_argument("--region", nargs=2,
                    help="Region file coordinates (x/z).")
parser.add_argument("--find", action="store",
                    help="Specifies the item to find in the search area.")
parser.add_argument("--list", action="store_true", default=False,
                    help="Creates a list of all items in the search area.")
parser.add_argument("--debug", action="store_true", default=False,
                    help="Debugging activated. Use -v!!!")
parser.add_argument('-v', '--verbose', action='count', default=0)
args = parser.parse_args()

if 'MINECRAFTWORLD' in os.environ:
    worldpath = os.environ['MINECRAFTWORLD']
elif args.world:
    worldpath = args.world
else:
    parser.error("Path to world must be defined.")

# Check input parameters
if not args.radius:
    parser.error("Radius must be defined.")
if not args.coords and not args.region:
    parser.error("Coordinates or region must be defined.")   
if args.radius>200:
    parser.error("Radius must be below 50.")

# Define the search area
if args.region:
    area = None
else:
    coord_min = [c - args.radius for c in args.coords]
    coord_max = [c + args.radius for c in args.coords]
    if args.vertical:
        # If 'args.vertical' is specified the whole vertical column is being searched
        coord_min[1] = -1
        coord_max[1] = 256
    area = (coord_min, coord_max)
    

if args.region:
    regions = {(args.region[0], args.region[1]): 'all'}
    check_range = None 
else:
    # block centerpoint coordinates
    x_c = args.coords[0]
    z_c = args.coords[2]

    region = conv.block_to_region(x_c, z_c)
    chunk = conv.block_to_chunk(x_c, z_c)
    if args.verbose>2:
        print(f"Middle chunk: {chunk}")

    # calculate the minimum and maximum chunks for the edges
    chunk_x_min = conv.block_to_chunk(x_c - args.radius, z_c)[0]
    chunk_x_max = conv.block_to_chunk(x_c + args.radius, z_c)[0]
    chunk_z_min = conv.block_to_chunk(x_c, z_c - args.radius)[1]
    chunk_z_max = conv.block_to_chunk(x_c, z_c + args.radius)[1]

    x_min = conv.chunk_to_block(chunk_x_min, z_c)[0][0]
    x_max = conv.chunk_to_block(chunk_x_max, z_c)[0][1]
    z_min = conv.chunk_to_block(x_c, chunk_z_min)[1][0]
    z_max = conv.chunk_to_block(x_c, chunk_z_max)[1][1]
    if args.verbose>2:
        print(f"Analyzing blocks x: {x_min} to {x_max}  z: {z_min} to {z_max}")

    regions = {}
    for chunk_x in range(chunk_x_min, chunk_x_max+1):
        for chunk_z in range(chunk_z_min, chunk_z_max+1):
            chunk = (chunk_x, chunk_z)
            if args.verbose>2:
                print(f"Using chunk {chunk}")

            reg = conv.chunk_to_region(*chunk)
            if reg in regions:
                regions[reg].append(chunk)
            else:
                regions[reg] = [chunk]


# Now we have the regions to be analyzed
if args.verbose>0:
    print(f"Analyzing {len(regions.keys())} regions.")

# prepare variables
blocks = {}
locations = []
number_chunks = 0

# check all regions
for region, chunk_list in regions.items():

    # Create region filename
    filename = f"r.{region[0]}.{region[1]}.mca"

    # Load the region
    if args.verbose>0:
        print(f"Loading region {filename}.")
    mca = parsemca.MCA(os.path.join(worldpath, filename), chunk_list, area, args.verbose)
    number_chunks += mca.number_chunks()

    # Analyze the region
    if args.list:
        region_blocks = mca.extract_sum_blocks()
        for block, value in region_blocks.items():
            if block in blocks:
                blocks[block] += value
            else:
                blocks[block] = value

    if args.find:
        locs = mca.find_block_locations(args.find)
        locations.extend(locs)


print("\n" + 40*"-")
if args.region:
    square = 512 * 512 
    volume = square * 256
else:
    square = 4 * args.radius * args.radius # factor 2 because only the half length is given by 'radius'.
    if args.vertical:
        volume = square * 256
    else:
        volume = 2 * square * args.radius

#area = 256*number_chunks # TODO!!!!
#print(f"Analyzed {number_chunks} chunks, correponding to {area} m^2.")
if  args.list:
    total_sum = sum(blocks.values())
    pprint.pprint(blocks)
    print(f"\nAnalyzed {number_chunks} chunks, found {total_sum:_} blocks.")


if args.find:
    n = len(locations)
    # TODO: sort by distance

    pprint.pprint(locations)
    print(f"\nAnalyzed {number_chunks} chunks.")
    print(f"Found {n} {args.find} within {square} m^2, that is {1e6*n/square:.2f} {args.find} per km^2.")
    