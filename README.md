# CNC utility tool
This is a resulting command line tool to solve the following assignments. 
The tool accepts one argument, `-fun1` or `-fun2`, and one input file that is a CNC program code.

Example of use:

    >py script -fun1 D327971_fc1.i

The main objectives were:
 - ### Objective 1.
   For each coordinate, add a constant (10) to every Y where X is greater than 50
 - ### Objective 2.
   Each code block begins with the CNC machine definition *(e.g., T01, T02,...)*, and ends on line just before
   the following machine definition. Code blocks are mixed, and the objective is to sort them by machine
   definition number in ascending order.
 - ### Objective 3.
   Find and print maximum and minimum values for the X and Y axes in the `x_min/x_max/y_min/y_max` format.
 
## Command line arguments:
 - **-fun1** takes the input file, performs objectives 1 and 2, and writes modified file content into a new file, `cnc.txt`.
 - **-fun2** takes the input file, performs objective 3, and writes the result to the standard output.
