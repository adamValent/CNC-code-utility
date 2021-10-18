import argparse, re
import enum
from io import TextIOWrapper
from typing import DefaultDict, Tuple
from math import inf

parser = argparse.ArgumentParser()
parser.add_argument("-funkce1", action="store")
parser.add_argument("-funkce2", action="store")
args = parser.parse_args()


def get_formatted_coords(x: float, y: float) -> str:
    """Creates formatted coordinates."""

    x_str = "{:.3f}".format(x)
    y_str = "{:.3f}".format(y)
    
    return f"X{x_str}Y{y_str}"


def write_sorted_blocks(blocks: DefaultDict, out: TextIOWrapper) -> None:
    """Writes blocks of code into output file in ascending order.
    
    Keyword arguments:
    blocks -- dictionary which stores set of coordinates associated with tool definition.
    out    -- output file where modified contents are stored
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

                # no match and tool definition set indicates end of CNC code block(s)
                elif tool_definition:
                    write_sorted_blocks(blocks, outfile)
                    outfile.write(line)
                    tool_definition = None
                else:
                    outfile.write(line)
                    
    except OSError:
        print("Cannot open/read file", path)


class X(enum.Enum):
    min = 1
    max = 2

class Y(enum.Enum):
    min = 1
    max = 2


def update_extremas(x: float, y: float, extr: dict[float]) -> None:
    """Updates minimum and maximum values for X and Y.
    
       Keyword arguments:
       x    -- new x value
       y    -- new y value
       extr -- minimum and maximum values
    """

    if x < extr[X.min]:
        extr[X.min] = x

    if x > extr[X.max]:
        extr[X.max] = x

    if y < extr[Y.min]:
        extr[Y.min] = y

    if y > extr[Y.max]:
        extr[Y.max] = y


def print_extremas(extr: dict[float]) -> None:
    """Prints minimum and maximum values for X and Y.
       
       extr -- minimum and maximum values 
               stored in order xmin/xmax/ymin/ymax
    """

    extremas = []

    for value in extr.values():
        extremas.append("{:.3f}".format(value))
    print('/'.join(extremas))


def funkce2(path: str) -> None:
    """Finds and prints minimum and maximum values for 
       X and Y in CNC program code blocks.

       Keyword arguments:
       path -- path to the input CNC program file
    """

    extremas = { X.min : inf, X.max : -inf, 
                 Y.min : inf, Y.max : -inf  }
    pattern = "X(-*[0-9]+\.[0-9]{3})Y(-*[0-9]+\.[0-9]{3})(T[0-9]{2,})?"
    in_block = False

    try:
        with open(path, 'r', encoding="utf-8") as infile:
            lines = infile.readlines()

            for line in lines:
                match = re.search(pattern, line)
                
                # reaching the end of code blocks
                if not match and in_block:
                    break

                # first occurence of tool definition indicates start of code blocks
                if match and not in_block:
                    in_block = match.group(3) is not None

                if in_block:
                    xy_coords = get_coords(match)
                    update_extremas(xy_coords[0], xy_coords[1], extremas)
    except OSError:
        print("Cannot open/read file")

    print_extremas(extremas)

if args.funkce1:
    funkce1(args.funkce1)
elif args.funkce2:
    funkce2(args.funkce2)
