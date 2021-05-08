This document is a description of the results of the experiment.

##### 1. In this experiment, the benchmark in the original paper is simply converted, and the calculated path is carried out according to the new coordinate system. The specific conversion is as follows:

（1）Convert the original coordinate system with $(0,0)$as the far point to the coordinate system with $(1,1)$as the origin point

​     （2）The droplet number is changed from 1, that is, the droplet number of the original Benchmark is added by 1.

​    （3）The original block gives the coordinates of the lower left and right corners, but now the coordinates of the upper left and right corners are converted.

##### 2. Description of file directory

This experiment consists of three benchmark suites——benchmark1，benchmark2，real_assay。Each test benchamrk contains three folders under it. Under the folder is the original data set, **transition** is the data set after the coordinate transformation, and **final_PATH** is the final path output by the algorithm under the transformed coordinate system. Each subfile corresponds to the experimental results of a test sample.

##### 3. Text description format for test sets and experimental results

Under the Transition folder, all the test sample description formats are standardized as follows:

$grid ::= 'grid' \{width \quad height\}$

$blockages ::= 'blockages' \quad \{ <up\_left\_x> \quad <up\_left\_y> \quad <down\_right\_x> \quad <down\_right\_y> \}$

$net ::= 'net' \quad \{ <ID> \quad <source\_x> \quad <source\_y>  \quad <target\_x> \quad <target\_y>    \}$

$xet ::= 'net' \quad \{ <ID> \quad <source\_x> \quad <source\_y>  \quad <target\_x> \quad <target\_y>  \quad '\#'  \quad   <source\_x2> \quad <source\_y2> \}$

(1) grid: Represents the size of the chip. Width means the width of the chip and height means the height of the chip. The chip size can be expressed as: grid 12 12.

(2) blockages: represents the obstacle area; up_left_x represents the X-axis coordinate of grid in the upper-left corner of the obstacle area; up_left_y represents the Y-axis coordinate of grid in the upper-left corner of the obstacle area; down_right_x represents the X-axis coordinate of grid in the lower-right corner of the obstacle area; down_right_y represents the Y-axis coordinate of grid in the lower-right corner of the obstacle area.

(3) net: represents the droplet to be moved, including the number, starting point and ending point. Where ID represents the droplet number (starting with 1), source_x represents the X-axis coordinate of the starting point, source_y represents the Y-axis coordinate of the starting point, target_x represents the X-axis coordinate of the ending point, and target_y represents the Y-axis coordinate of the ending point.

(4) xet: refers to the two droplets to be mixed, including the number, the starting and ending points of one of the droplets, and the number and starting point of another of the droplets. If there is a droplet to be mixed in the droplet path planning problem, the two droplet starting points are different, but have the same endpoint, the algorithm will split the two droplet to be mixed into two net processing when processing the input, but does not consider the constraint between them.

For example, benchmark1's first test set:

grid 12 12

blockages 2 10 4 8
blockages 9 5 10 4
blockages 4 4 5 2
blockages 9 11 10 10

net 1 1 1 10 6
net 2 1 12 3 3
net 3 3 12 7 6
net 4 3 1 5 11
net 5 5 12 9 8
net 6 8 12 5 9
net 7 8 1 5 7
net 8 12 4 3 11
net 9 10 1 1 11
net 10 12 7 3 5
net 11 11 12 1 9
net 12 12 10 2 7

Under the path folder, the description format of all the final solution results is unified, as follows:

$grammar ::= <grid>|<blockage>|<nets>|<routes>$

$positon::='('<int>','<int>')'$

$grid ::= 'grid' \quad \{<position> \quad <position>\} \quad 'end'$ 

$blockages ::= 'blockages' \quad \{ <position> \quad <position> \}\quad 'end'$

$source::=<position>$

$target::=<position>$

$nets ::= 'nets' \{ <ID> \quad <source> \quad '->' \quad <target>  \} \quad 'end'$

$routes ::= 'routes' \{ <ID> \quad <position> \cdots <pisiton> \} \quad 'end'$

(1) position: Represents the coordinates of the grid.

(2) grid: Represents the size of the chip, and uses two positions to determine the size of the chip. The first position represents the lower left corner grid coordinates of the chip, and the second position represents the upper right corner grid coordinates of the chip.

(3) blockages: Blockages. The same two positions are used to determine the size and location of the obstacle area. The first position represents the grid coordinates of the upper left corner of the obstacle area, and the second position represents the grid coordinates of the lower right corner of the chip.

(4) source: Represents the starting point of the droplet.
(5) target: Represents the end point of the droplet.
(6) nets: refers to droplets to be moved and composed of their numbers, starting and ending points. For example: nets 1 (1,2) −> (5, 4) end.

(7) routes: represent the routes of all droplets moving at the same time. Among them, each path is composed of the number of droplets and a series of grid coordinates from start to end. Routes, for example, 1 (1, 2), (2, 2) (3, 2) (4, 2) (5, 2) (5, 4) (5, 3) end.

For example, the solution to benchmark1's first test set:

grid
(1,1) (12,12)
end

blockages
(2,10) (4,8)
(9,5) (10,4)
(4,4) (5,2)
(9,11) (10,10)
end

nets
5 (5,12) -> (9,8)
10 (12,7) -> (3,5)
9 (10,1) -> (1,11)
6 (8,12) -> (5,9)
11 (11,12) -> (1,9)
12 (12,10) -> (2,7)
3 (3,12) -> (7,6)
8 (12,4) -> (3,11)
1 (1,1) -> (10,6)
7 (8,1) -> (5,7)
2 (1,12) -> (3,3)
4 (3,1) -> (5,11)
end

routes
1 (1,1) (1,1) (2,1) (3,1) (4,1) (4,1) (5,1) (6,1) (6,1) (6,1) (6,1) (6,2) (6,3) (7,3) (8,3) (9,3) (10,3) (11,3) (11,4) (11,5) (11,6) (10,6)
2 (1,12) (1,11) (1,10) (1,9) (1,8) (1,7) (1,6) (1,5) (1,4) (1,3) (2,3) (3,3)
3 (3,12) (3,12) (3,12) (3,12) (3,12) (3,12) (3,12) (3,12) (3,12) (4,12) (5,12) (6,12) (7,12) (7,11) (7,11) (7,10) (7,9) (7,9) (7,9) (7,9) (7,9) (7,9) (7,9) (7,8) (7,7) (7,6) (7,7) (7,6)
4 (3,1) (4,1) (5,1) (6,1) (6,2) (6,3) (6,3) (6,3) (6,3) (7,3) (8,3) (9,3) (10,3) (11,3) (11,4) (11,5) (11,6) (11,7) (11,8) (11,9) (11,10) (11,11) (11,12) (10,12) (9,12) (8,12) (7,12) (6,12) (5,12) (5,11)
5 (5,12) (6,12) (6,11) (6,10) (7,10) (8,10) (8,9) (9,9) (9,8)
6 (8,12) (8,12) (8,12) (8,12) (7,12) (6,12) (5,12) (5,11) (5,10) (5,9)
7 (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,1) (8,2) (8,3) (8,4) (7,4) (6,4) (6,5) (5,5) (5,5) (5,6) (5,7)
8 (12,4) (12,4) (12,4) (12,4) (12,4) (12,4) (12,4) (12,4) (12,5) (12,6) (12,7) (12,8) (12,9) (12,10) (12,11) (12,12) (11,12) (10,12) (9,12) (8,12) (7,12) (6,12) (5,12) (4,12) (3,12) (3,11)
9 (10,1) (10,2) (10,3) (9,3) (8,3) (8,4) (8,4) (8,4) (8,5) (8,6) (7,6) (7,7) (6,7) (5,7) (4,7) (3,7) (2,7) (1,7) (1,8) (1,9) (1,10) (1,11)
10 (12,7) (11,7) (11,6) (10,6) (9,6) (8,6) (7,6) (6,6) (5,6) (4,6) (3,6) (3,5)
11 (11,12) (10,12) (10,12) (10,12) (10,12) (9,12) (8,12) (7,12) (7,11) (7,10) (7,9) (7,9) (7,9) (7,9) (7,8) (7,7) (6,7) (5,7) (4,7) (3,7) (2,7) (1,7) (1,8) (1,9)
12 (12,10) (11,10) (11,9) (11,8) (11,8) (11,7) (11,6) (10,6) (10,6) (10,6) (10,6) (9,6) (9,6) (9,6) (9,6) (9,6) (9,6) (8,6) (8,6) (7,6) (7,7) (6,7) (5,7) (4,7) (3,7) (2,7)
end

