############################################################################################
# MyCell类用于表示board上面的每一个cell，这个可以作为不同的board的cell类型的父类
# Router类是不同的routing算法的父类
# Created by 吴贻能 on 2019/12/10.
############################################################################################

import random
from Droplet import Cell
from Utils import *
from copy import deepcopy


class MyCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_block = False  # 表示cell不可用
        self.block_for_concession = False  # 用于寻找退让液滴的时候做标记
        self.block_for_source = 0  # 用于记录一个cell被多少个液滴的起点影响，值为0,1,2
        self.block_for_target = 0  # 用于记录一个cell被多少个液滴的终点影响，值为0,1,2
        self.is_used = False  # 用于记录一个cell是否被使用过
        self.temporary_block = False  # 用于reroute某个液滴，让没有退让点的液滴的critical zone暂时block


class Router:
    A_DIFF = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    TWO_DIFF = [(-2, 0), (0, 2), (2, 0), (0, -2)]

    ADD_BLOCK_FOR_SOURCE = 0
    DOWN_BLOCK_FOR_SOURCE = 1
    ADD_BLOCK_FOR_TARGET = 2
    DOWN_BLOCK_FOR_TARGET = 3

    MAX_COST = 10000

    def __init__(self, height, width, blockages, droplets, assay):
        self.height = height
        self.width = width
        self.blockages = blockages
        self.droplets = droplets
        self.board = []
        self.assay = assay

        self.id_to_droplet = {}  # id : droplet
        for d in self.droplets:
            self.id_to_droplet[d.id] = d

    # 初始化board
    def router_specific_inits(self):
        pass

    # 产生液滴的顺序，order 中的数字代表液滴的 id
    def shuffle_order(self):
        order = [idx + 1 for idx in range(len(self.droplets))]
        random.shuffle(order)
        return order

    # 根据 order 返回一组按照给定顺序排序后的液滴
    def assign_priority(self, order):
        order_droplets = []
        priority = len(order)
        for o in order:
            droplet = deepcopy(self.id_to_droplet[o])
            droplet.priority = priority
            order_droplets.append(droplet)
            priority -= 1
        return order_droplets

    # 返回一个cell的上下左右的cell, 不包括block以及不存在的cell
    def neighbors(self, cell):
        res = []
        for diff in self.A_DIFF:
            n_cell = Cell(cell.x + diff[0], cell.y + diff[1])
            if 0 <= n_cell.x < self.height and 0 <= n_cell.y < self.width \
                    and not self.board[n_cell.x][n_cell.y].is_block and not self.board[n_cell.x][n_cell.y].temporary_block:
                res.append(n_cell)
        return res

    # 返回一个cell的上下左右隔两格的cell, 不包括block以及不存在的cell
    def neighbors2(self, cell):
        res = []
        for diff in self.TWO_DIFF:
            n_cell = Cell(cell.x + diff[0], cell.y + diff[1])
            if 0 <= n_cell.x < self.height and 0 <= n_cell.y < self.width \
                    and not self.board[n_cell.x][n_cell.y].is_block and not self.board[n_cell.x][n_cell.y].temporary_block:
                res.append(n_cell)
        return res

    # 返回一个cell所在的9个周围的cell，包括自身，不包括block以及不存在的cell
    def around_cells(self, cell):
        cells = []
        for x in range(cell.x - 1, cell.x + 2):
            for y in range(cell.y - 1, cell.y + 2):
                if 0 <= x < self.height and 0 <= y < self.width and not self.board[x][y].is_block:
                    cells.append(Cell(x, y))
        return cells

    # 给定一条路径，寻找这个路径中造成阻碍的其它液滴
    def find_concession_droplets(self, d, new_droplets, route, times):
        target = new_droplets[d].true_target
        concession_droplets = []
        for cell in route[::-1]:
            for c in self.around_cells(cell):
                self.board[c.x][c.y].block_for_concession = True

        if d == 7 and times == 2:
            debug = 1

        for idx in range(len(new_droplets)):
            if idx == d:
                continue
            if new_droplets[idx].is_arrive:
                if new_droplets[idx].true_target in self.assay.waste_reservoir:  # 终点在回收cell处就不需要再退让了
                    continue
                else:
                    q_source = new_droplets[idx].true_target
            elif new_droplets[idx].is_concession:
                q_source = new_droplets[idx].concession_cells[-1]
            else:
                q_source = new_droplets[idx].source

            if self.board[q_source.x][q_source.y].block_for_concession:
                if new_droplets[idx] not in concession_droplets:
                    new_droplets[idx].other = abs(q_source.x - target.x) + abs(q_source.y - target.y)
                    concession_droplets.append(new_droplets[idx])
        concession_droplets.sort(key=lambda x: x.other)  # 靠近target的液滴排在前面
        return concession_droplets

    # lee算法
    def lee(self, source, target):
        queue = Queue()
        queue.put(source)
        came_from = dict()
        came_from[source] = None

        while not queue.empty():
            cur = queue.get()

            if cur == target:
                return True, came_from
            for next_cell in self.neighbors(cur):
                if next_cell not in came_from and self.board[cur.x][cur.y].block_for_source == 0 \
                        and self.board[cur.x][cur.y].block_for_target == 0:
                    came_from[next_cell] = cur
                    queue.put(next_cell)
        return False, None

    # 从当前cell往外找concession zone
    def find_concession_zone(self, cell):
        queue = Queue()
        queue.put(cell)
        came_from = dict()
        came_from[cell] = None

        while not queue.empty():
            cur = queue.get()

            if not self.board[cur.x][cur.y].block_for_concession:
                return True, cur, came_from

            for next_cell in self.neighbors(cur):
                if self.board[cur.x][cur.y].block_for_source == 0 and self.board[cur.x][cur.y].block_for_target == 0 \
                        and next_cell not in came_from:
                    came_from[next_cell] = cur
                    queue.put(next_cell)
        return False, None, came_from

    # 从当前液滴的终点处往外找concession zone
    def find_concession_zone_from_target(self, target, cell):
        queue = Queue()
        queue.put(target)
        visited = list()
        visited.append(target)
        while not queue.empty():
            cur = queue.get()

            if self.board[cur.x][cur.y].block_for_source == 0 and self.board[cur.x][cur.y].block_for_target == 0 \
                    and not self.board[cur.x][cur.y].block_for_concession:
                is_legal, came_from = self.lee(cell, cur)
                if is_legal:
                    return True, cur, came_from,

            for next_cell in self.neighbors(cur):
                if next_cell not in visited:
                    visited.append(next_cell)
                    queue.put(next_cell)
        return False, None, None

    # 2d-routing
    # order_droplets是按照路径顺序排序后的液滴
    def get_2d_paths(self, order_droplets):
        pass

    # 3d-compaction
    def get_3d_compaction(self, all_routes, max_cycle, droplets_num):
        pass

    def route_droplet_one_by_one(self, all_routes):
        routes = [[] for _ in range(len(self.droplets))]
        cycle = 0
        for route in all_routes:
            repeat_cell = [route[1][0] for _ in range(cycle - len(routes[route[0] - 1]))]
            routes[route[0] - 1].extend(repeat_cell)
            if len(routes[route[0] - 1]) == 0:
                routes[route[0] - 1].extend(route[1])
                cycle += len(route[1])
            else:
                routes[route[0] - 1].extend(route[1][1:])
                cycle += len(route[1]) - 1
        return routes

    # 这个传入的cell可能是source也可能是是target
    def add_down_block_for_source_target_helper(self, cell, status, val):
        if status == self.ADD_BLOCK_FOR_SOURCE:
            for c in self.around_cells(cell):
                self.board[c.x][c.y].block_for_source += val

        elif status == self.ADD_BLOCK_FOR_TARGET:
            for c in self.around_cells(cell):
                self.board[c.x][c.y].block_for_target += val

        elif status == self.DOWN_BLOCK_FOR_SOURCE:
            for c in self.around_cells(cell):
                if self.board[c.x][c.y].block_for_source > 0:
                    self.board[c.x][c.y].block_for_source -= val

        elif status == self.DOWN_BLOCK_FOR_TARGET:
            for c in self.around_cells(cell):
                if self.board[c.x][c.y].block_for_target > 0:
                    self.board[c.x][c.y].block_for_target -= val

    def print_board_block_for_source(self):
        print("===BOARD BLOCK FOR SOURCE===")
        for x in range(self.height):
            for y in range(self.width):
                if self.board[x][y].is_block:
                    print('# ', end='')
                else:
                    print(str(self.board[x][y].block_for_source) + ' ', end='')
            print('\n')

    def print_board_block_for_target(self):
        print("===BOARD BLOCK FOR TARGET===")
        for x in range(self.height):
            for y in range(self.width):
                if self.board[x][y].is_block:
                    print('# ', end='')
                else:
                    print(str(self.board[x][y].block_for_target) + ' ', end='')
            print('\n')

    def print_temporary_block(self):
        print("===Temporary Blocks===")
        for x in range(self.height):
            for y in range(self.width):
                if self.board[x][y].temporary_block:
                    print('* ', end='')
                elif self.board[x][y].is_block:
                    print('# ', end='')
                else:
                    print('0 ', end='')
            print('\n')

    def print_concessive_block(self):
        print("===Concessive Blocks===")
        for x in range(self.height):
            for y in range(self.width):
                if self.board[x][y].block_for_concession:
                    print('@ ', end='')
                elif self.board[x][y].is_block:
                    print('# ', end='')
                else:
                    print('0 ', end='')
            print('\n')

    # 按照可视化工具的坐标输出，原点在左下角
    def print_vis_route(self, route, droplet_id):
        print("Droplet #" + str(droplet_id) + " has route size => " + str(len(route) - 1))
        cycle = 0
        for cell in route:
            print("{" + str(cycle) + ":(" + str(cell.y + 1) + "," + str(self.height - cell.x) + ")},", end='')
            cycle += 1
        print('\n')
#打印2d路径规划结果
    def print_each_route(self, all_routes):
        for route in all_routes:  # route = (id, route)
            print("droplet id: #" + str(route[0]) + " (route size = " + str(len(route[1])-1) + ") ==>")
            cycle = 0
            for cell in route[1]:
                print("{" + str(cycle) + ": (" + str(cell.y+1) + "," + str(self.height - cell.x) + ")}, ", end='')
                cycle += 1
            print('\n')
#打印最终路径规划结果            
    def print_each_route_3d(self, compact_routes):
        id=1
        # path=
        for route in compact_routes:  
            print(str(id),end='')
            for cell in route:
                print(' '+ '('+str(cell.x+1)+ ',' + str(cell.y+1)+ ')', end='')
            id+=1
            print('\n')   
    # 输出时间和使用的cell数量
    def get_time_steps_and_used_cell_num(self, compact_routes):
        time_steps = 0
        used_cell_num = 0
        board = [[0 for _ in range(self.width+1)] for _ in range(self.height+1)]
        for route in compact_routes:
            time_steps = max(time_steps, len(route) - 1)
            for cell in route[0:]:
                if board[cell.x][cell.y] == 0:
                    board[cell.x][cell.y] = 1

        for x in range(self.height+1):
            for y in range(self.width+1):
                if board[x][y] == 1:
                    used_cell_num += 1
        return time_steps, used_cell_num

