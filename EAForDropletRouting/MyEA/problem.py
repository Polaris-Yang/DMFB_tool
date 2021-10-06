import sys
sys.path.append('../')

import random
import copy
from TargetRouter import TargetRouter


MAX_VALUE = 10000


class Solution:
    def __init__(self, variables):
        self.variables = variables
        self.objectives = []
        self.constraints = []
        self.constraint_violation = 0.0
        self.evaluated = False

    def __str__(self):
        return "Solution[" + ",".join(list(map(str, self.variables))) + "|" + ",".join(list(map(str, self.objectives))) + "]"


class RoutingProblem:
    def __init__(self, assay, nobjs=1, nconstrs=0):
        self.assay = assay
        self.nobjs = nobjs
        self.nconstrs = nconstrs

    def generate_individual(self):
        return generate_permutation(range(1, self.assay.droplet_num + 1))

    def get_time_steps(self, order):
        """
        单目标
        :param order:
        :return:
        """
        router = TargetRouter(self.assay.board_size, self.assay.board_size, self.assay.blockages,
                              self.assay.droplets, self.assay)
        router.router_specific_inits()

        order_droplets = router.assign_priority(order)
        find_2d_path, all_routes = router.get_2d_paths(order_droplets)

        if find_2d_path:
            sub_routes = router.get_3d_compaction(all_routes, 300, self.assay.droplet_num)
            time_step, cell_num = router.get_time_steps_and_used_cell_num(sub_routes)
            return time_step
        else:
            return MAX_VALUE


def generate(problem):
    solution = Solution(problem.generate_individual())
    return solution


def generate_permutation(elements):
    """
    表示一种排列，排列中的每个元素都只出现一次.
    Examples
    --------
        # A permutation of integers 1 through 10.
        Permutation(range(1, 11))

    :param elements: list of objects
    :return: 返回一组排列
    """
    order = copy.deepcopy(list(elements))
    random.shuffle(order)
    return order


def droplet_routing_problem(order, assay):
    """
    routing问题定义
    :param order: 一个测试问题的路径优先级
    :param assay: 测试问题的反应
    :return: 如果该问题有路径就返回对应的时间的cell数量，否则就返回一个最大值
    """
    router = TargetRouter(assay.board_size, assay.board_size, assay.blockages, assay.droplets, assay)
    router.router_specific_inits()

    order_droplets = router.assign_priority(order)
    find_2d_path, all_routes = router.get_2d_paths(order_droplets)

    if find_2d_path:
        sub_routes = router.get_3d_compaction(all_routes, 300, assay.droplet_num)
        time_step, cell_num = router.get_time_steps_and_used_cell_num(sub_routes)
        return [time_step, cell_num]
    else:
        return [MAX_VALUE, MAX_VALUE]
        # return [-1, -1]










