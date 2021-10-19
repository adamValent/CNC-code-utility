import argparse, re
from enum import Enum
from io import TextIOWrapper
from typing import DefaultDict, Tuple
from math import inf


def get_formatted_coords(x: float, y: float) -> str:
    """Creates formatted coordinates."""

    x_str = "{:.3f}".format(x)
    y_str = "{:.3f}".format(y)
    
    return f"X{x_str}Y{y_str}"


def write_sorted_blocks(blocks: DefaultDict, out: TextIOWrapper) -> None:
    """Writes blocks of code into output file in ascending order.
    
    Keyword arguments:
    blocks -- dictionary which stores set of 
              tool definitions and corresponding coordinates.
    out    -- output file where modified contents of 
              original file will be written
    """

    for tool_def in sorted(blocks.keys()):
        include_definition = True

        for x, y in blocks[tool_def]:
            out_line = get_formatted_coords(x, y)

            if include_definition:
                out_line += tool_def
                include_definition = False
                                                                
            out.write(out_line + '\n')

def get_coords(match: re.Match[str]) -> Tuple[float, float]:
    """Gets coordinates from string matched by regex pattern 
       as a pair of floats.
    
       Keyword arguments:
       match -- matched substring of original line
    """

    x_coord = float(match.group(1))
    y_coord = float(match.group(2))

    return x_coord, y_coord

def parse_line(match: re.Match[str], blocks: DefaultDict, 
               out: TextIOWrapper, tool_def: str) -> str:
    """Extracts XY coordinates and tool definition, if present. Modifies Y coordinate
       if X > 50 and stores data in dictionary if tool definition is set.
       Returns new tool definition.
       
       Keyword arguments:
       match    -- matched substring of original line.
       blocks   -- dictionary which stores set of coordinates associated with tool definition.
       tool_def -- string representing tool definition. Indicates which block is being processed.
        """

    if match.group(3) is not None:
        # set tool_def if it is present in current line
        tool_def = match.group(3)

    x_coord, y_coord = get_coords(match)

    if x_coord > 50:
        y_coord += 10

    if tool_def:    
        blocks[tool_def].append((x_coord, y_coord))
    else:  
        # tool definition not set means CNC code blocks are not being processed. 
        out.write(get_formatted_coords(x_coord, y_coord) + '\n')

    return tool_def


def funkce1(path: str) -> None:
    """Parses input CNC program file. 

       Sorts blocks of CNC code according to tool definition in ascending order. 
       For every coordinate with X > 50, 10 will be added to corresponding Y. 
       
       Creates a new file cnc.txt in directory where script was executed.
       
    Keyword arguments:
    path -- path to the input CNC program file. 
    """

    # Regular expression for finding coordinates in file lines
    pattern = "X(-*[0-9]+\.[0-9]{3})Y(-*[0-9]+\.[0-9]{3})(T[0-9]{2,})?"
    blocks = DefaultDict(list)
    tool_definition = None
    
    try:
        with open(path, 'r', encoding="utf-8") as infile, open("cnc.txt", 'w', encoding="utf-8") as outfile:
            lines = infile.readlines()

            for line in lines:
                match = re.search(pattern, line)

                if match:
                    # tool_definition gets updated if line contains tool definition (e.g. T01)
                    tool_definition = parse_line(match, blocks, outfile, tool_definition)

                # no match and tool definition set indicates end of CNC code blocks
                elif tool_definition:
                    write_sorted_blocks(blocks, outfile)
                    outfile.write(line)
                    tool_definition = None
                else:
                    outfile.write(line)
                    
    except OSError:
        print("Cannot open/read file", path)


# Helping class for better readability.
class Extreme(Enum):
    min_x = 1
    max_x = 2
    min_y = 3
    max_y = 4


def update_min_max(xy: Tuple[float, float], ex: dict[float]) -> None:
    """Checks if x and y values are not new minimum or maximum values.
       If so, extremas are updated.
    
       Keyword arguments:
       xy   -- X and Y value to be checked
       ex   -- dictionary with minimum and maximum values for X and Y
    """

    x, y = xy[0], xy[1]
    
    if x < ex[Extreme.min_x]:
        ex[Extreme.min_x] = x

    if x > ex[Extreme.max_x]:
        ex[Extreme.max_x] = x

    if y < ex[Extreme.min_y]:
        ex[Extreme.min_y] = y

    if y > ex[Extreme.max_y]:
        ex[Extreme.max_y] = y


def print_min_max(ex: dict[float]) -> None:
    """Prints minimum and maximum values for X and Y.
       
       ex -- minimum and maximum values 
            stored in order xmin/xmax/ymin/ymax
    """

    extremas = []

    for value in ex.values():
        extremas.append("{:.3f}".format(value))

    print('/'.join(extremas))


def funkce2(path: str) -> None:
    """Finds and prints minimum and maximum values for 
       X and Y from CNC program code blocks.

       Keyword arguments:
       path -- path to the input CNC program file
    """

    extremas = { Extreme.min_x : inf, Extreme.max_x : -inf, 
                 Extreme.min_y : inf, Extreme.max_y : -inf  }
    pattern = "X(-*[0-9]+\.[0-9]{3})Y(-*[0-9]+\.[0-9]{3})(T[0-9]{2,})?"
    in_block = False

    try:
        with open(path, 'r', encoding="utf-8") as infile:
            lines = infile.readlines()

            for line in lines:
                match = re.search(pattern, line)
                
                if match:
                    # check if code blocks were reached
                    if not in_block:
                        in_block = match.group(3) is not None

                    # search for min/max values inside code blocks
                    if in_block:
                        xy_coords = get_coords(match)
                        update_min_max(xy_coords, extremas)
                
                # reaching the end of code blocks
                elif in_block:
                    break
    except OSError:
        print("Cannot open/read file")

    print_min_max(extremas)


parser = argparse.ArgumentParser()
parser.add_argument("-funkce1", action="store")
parser.add_argument("-funkce2", action="store")
args = parser.parse_args()

if args.funkce1:
    funkce1(args.funkce1)
elif args.funkce2:
    funkce2(args.funkce2)
