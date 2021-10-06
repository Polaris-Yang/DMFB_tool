############################################################################################
# 该py文件用于增加一些工具方法
# Created by 吴贻能 on 2019/12/10.
############################################################################################

import collections
import heapq
from Assay import *


VISUAL_ONE_BY_ONE = 0  # 液滴一个接着一个移动
VISUAL_COMPACTION = 1  # 液滴同时移动
VISUAL_FOR_RECORD = 2  # 延迟一下液滴的移动，用于录屏工具截取液滴移动过程

INITIAL_ALL_VALID = 0  # 种群初始化的时候个体都是合法的
INITIAL_PARTIAL_VALID = 1  # 种群初始化的时候个体不一定合法

GENERATION = 100
POP_SIZE = 50

INIT = 0
FINAL = 1

mat = "{:5}"


class Queue:  # 普通的队列，先进先出
    def __init__(self):
        self.elements = collections.deque()
    def empty(self):
        return len(self.elements) == 0
    def put(self, x):
        self.elements.append(x)
    def get(self):
        return self.elements.popleft()


class PriorityQueue:  # 优先级队列
    def __init__(self):
        self.elements = []
    def empty(self):
        return len(self.elements) == 0
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    def get(self):
        return heapq.heappop(self.elements)[1]


# 输出board
def print_board(board):
    idx = 0
    mat = "{:5}"
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y].is_block:
                print(mat.format('#'), end='')
            else:
                print(mat.format(str(idx)), end='')
                idx += 1
        print('\n')


def print_droplets_order(order_droplets):
    print('/////////////////////////////////////Droplet Order/////////////////////////////////////')
    for droplet in order_droplets:
        print(str(droplet.id) + ', ', end='')
    print('\n')


# 让目标点按照与起始点的距离排序，近的排在前面
def sort_targets_in_des_distance(source, dests):
    if len(dests) > 0:
        dis = []
        for dest in dests:
            dis.append(abs(dest.x - source.x) + abs(dest.y - source.y))

        best_target = dests[0]
        tmp = dis[0]
        for i in range(1, len(dests)):
            if dis[i] < tmp:
                tmp = dis[i]
                best_target = dests[i]
        return best_target
    else:
        return None


# 这个方法用于处理came_from, came_from是路径字典，每个点包含上一个点
def get_one_path(source, target, came_from):
    route = []
    cur = target
    while cur != source:
        route.append(cur)
        cur = came_from[cur]
    route.append(source)
    route.reverse()
    return route


# 判断两个液滴的位置是否冲突
def does_interfere(cell1, cell2):
    return abs(cell1.x - cell2.x) <= 1 and abs(cell1.y - cell2.y) <= 1


def print_route(route, did):
    """ 输出液滴的路径，这个路径的坐标原点在左上角
    """
    print("Droplet #" + str(did) + " has route size => " + str(len(route) - 1))
    cycle = 0
    for cell in route:
        print("{" + str(cycle) + ":(" + str(cell.x) + "," + str(cell.y) + ")},", end='')
        cycle += 1
    print('\n')


def delay_routes_in_source(routes, delay_times):
    """ 这个函数是为可视化服务的，在每个最终的路径上在头处插入delay_times次初始点
    """
    for route in routes:
        for _ in range(delay_times):
            route.insert(0, route[0])


def process_compact_routes(routes):
    """ 这个函数是为可视化服务的，让每个液滴的路径等长，在短的路径添加它们的终点
    """
    max_step = 0
    for route in routes:
        max_step = max(max_step, len(route))

    for route in routes:
        if len(route) < max_step:
            ends = [route[-1] for _ in range(max_step - len(route))]
            route.extend(ends)


# 输出可视化文件
def visualize_route(assay_path, size, droplets, routes, blocks, visual_type):
    pre_path = ''
    if visual_type == VISUAL_ONE_BY_ONE:
        pre_path = 'visualization/one_by_one/'
    elif visual_type == VISUAL_COMPACTION:
        pre_path = 'visualization/compaction/'
    elif visual_type == VISUAL_FOR_RECORD:
        pre_path = 'visualization/delay/'
        delay_routes_in_source(routes, 10)
    visual_path = pre_path + assay_path.split('/')[-1].split('.')[0] + '.bio'

    with open(visual_path, 'w') as f:
        f.write('grid\n')
        f.write('(1,1) (' + str(size) + ',' + str(size) + ')\n')
        f.write('end\n')
        f.write('\n')
        f.write('routes\n')
        process_compact_routes(routes)

        idx = 1
        for route in routes:
            output = str(idx)
            for cell in route:
                output = output + ' (' + str(cell.y + 1) + ',' + str(size - cell.x) + ')'
            f.write(output)
            f.write('\n')
            idx += 1
        f.write('end\n')
        f.write('\n')

        f.write('nets\n')
        for droplet in droplets:
            net = str(droplet.id) + ' (' + str(droplet.source.y + 1) + ',' + str(size - droplet.source.x) + ') -> (' \
                  + str(droplet.target.y + 1) + ',' + str(size - droplet.target.x) + ')\n'
            f.write(net)
        f.write('end\n')
        f.write('\n')

        f.write('blockages\n')
        for blk in blocks:
            block = '(' + str(blk[0][1] + 1) + ',' + str(size - blk[0][0]) + ') (' + str(blk[1][1] + 1) + ',' \
                    + str(size - blk[1][0]) + ')\n'
            f.write(block)
        f.write('end\n')
        f.write('\n')


# 获得初始化结果的文件路径
def get_initial_path(assay_name, assay_type=TEST_ASSAY, initial_type=INITIAL_PARTIAL_VALID):
    path = ''
    if assay_type == TEST_ASSAY:
        path = 'initialization/test/'
    elif assay_type == MINSIK_ASSAY:
        path = 'initialization/minsik/'
    elif assay_type == REAL_ASSAY:
        path = 'initialization/real/'

    if initial_type == INITIAL_ALL_VALID:
        path += 'all_valid/'
    elif initial_type == INITIAL_PARTIAL_VALID:
        path += 'partial_valid/'
    path = path + assay_name + '.txt'
    return path


# 获得最终结果的文件路径
def get_final_path(assay_name, assay_type=TEST_ASSAY):
    path = ''
    if assay_type == TEST_ASSAY:
        path = 'results/test/'
    elif assay_type == MINSIK_ASSAY:
        path = 'results/minsik/'
    elif assay_type == REAL_ASSAY:
        path = 'results/real/'

    path = path + assay_name + '.txt'
    return path


# 保存初始化种群的结果
def keep_initial_pop(assay_name, pop, time, cell_num, assay_type, initial_type):
    path = get_initial_path(assay_name, assay_type, initial_type)

    with open(path, 'w') as f:
        success = 0
        f.write('===Initial Population Result===\n')
        str_time = 'Time:'
        for t in time:
            str_time += ' ' + mat.format(str(t))
            if t != -1:
                success += 1
        f.write(str_time + '\n')

        str_cell = 'Cell:'
        for c in cell_num:
            str_cell += ' ' + mat.format(str(c))
        f.write(str_cell + '\n')

        success_rate = success / len(pop)
        f.write('initial successful rate = ' + str(success_rate * 100) + '%\n')
        print('initial successful rate = ' + str(success_rate * 100) + '%')

        f.write('\n')

        f.write('===DETAILS===\n')
        idx = 1
        for order in zip(pop, time, cell_num):
            f.write('population ' + str(idx) + '\n')
            f.write('path order: ' + str(order[0]) + '\n')
            f.write('time step: ' + str(order[1]) + '\n')
            f.write('used cell number: ' + str(order[2]) + '\n\n')
            idx += 1


# 保存初始化种群的结果
def keep_initial_final_pop(assay_name, all_pop, all_time, all_cell_num, non_pop, non_time, non_cell_num, assay_type,
                           initial_type, init_or_final=0):
    if init_or_final == 0:  # 处理初始化
        path = get_initial_path(assay_name, assay_type, initial_type)
        output_str = 'Initial '
    elif init_or_final == 1:
        path = get_final_path(assay_name, assay_type)
        output_str = 'Final '

    with open(path, 'w') as f:
        f.write('population = ' + str(len(all_pop)) + ', generation = ' + str(GENERATION) + '\n')
        success = 0
        f.write('===' + output_str + 'Population Result===\n')
        str_time = 'Time:'
        for t in all_time:
            str_time += ' ' + mat.format(str(t))
            if t != -1:
                success += 1
        f.write(str_time + '\n')

        str_cell = 'Cell:'
        for c in all_cell_num:
            str_cell += ' ' + mat.format(str(c))
        f.write(str_cell + '\n')

        success_rate = success / len(all_pop)
        f.write(output_str + 'successful rate = ' + str(success_rate * 100) + '%\n')
        print(output_str + 'successful rate = ' + str(success_rate * 100) + '%')

        f.write('\n')

        f.write('===' + output_str + 'Non-dominated Individual===\n')
        str_time = 'Non-Time:'
        for t in non_time:
            str_time += ' ' + mat.format(str(t))
            if t != -1:
                success += 1
        f.write(str_time + '\n')

        str_cell = 'Non-Cell:'
        for c in non_cell_num:
            str_cell += ' ' + mat.format(str(c))
        f.write(str_cell + '\n\n')

        f.write('===' + output_str + 'Non-dominated Individual Details===\n')
        idx = 1
        for order in zip(non_pop, non_time, non_cell_num):
            f.write('population ' + str(idx) + '\n')
            f.write('path order: ' + str(order[0]) + '\n')
            f.write('time step: ' + str(order[1]) + '\n')
            f.write('used cell number: ' + str(order[2]) + '\n\n')
            idx += 1

        f.write('===All Individual Details===\n')
        idx = 1
        for order in zip(all_pop, all_time, all_cell_num):
            f.write('population ' + str(idx) + '\n')
            f.write('path order: ' + str(order[0]) + '\n')
            f.write('time step: ' + str(order[1]) + '\n')
            f.write('used cell number: ' + str(order[2]) + '\n\n')
            idx += 1

    print('Save ' + output_str + ' result for ' + assay_name)
    print('=================================================================================')



