############################################################################################
# Cell类用于表示路径的每一个cell
# Droplet类表示的是每一个液滴
# Created by 吴贻能 on 2019/12/10.
############################################################################################


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        return tuple([self.x, self.y]) < tuple([other.x, other.y])

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __hash__(self):
        return hash(self.x ^ (self.y << 4))


class Droplet:
    def __init__(self, idx, priority, source, target):
        self.id = idx  # ID
        self.priority = priority  # 优先级
        self.source = source  # 起点
        self.target = target  # benchmark上面注明的终点
        self.concession_source = self.source  # 记录最近的一次退让点
        self.concession_cells = []  # list记录每次的退让点
        self.is_concession = False  # 是否发生了退让
        self.is_arrive = False  # 是否到达终点
        self.true_target = self.target  # 实际抵达的终点
        self.other = 0  # 没有特殊的意义，可以随意定义

    def __eq__(self, other):
        return self.id == other.id

