############################################################################################
# 该py文件用于处理实际的生化反应
############################################################################################

import os
from platypus import NSGAII, Problem, Permutation, nondominated
from TargetRouter import TargetRouter
from Utils import *
from Assay import *
from copy import deepcopy
import functools


# routing问题定义
def droplet_routing_problem(order, assay):
    router = TargetRouter(assay.board_size, assay.board_size, assay.blockages, assay.droplets, assay)
    router.router_specific_inits()

    order_droplets = router.assign_priority(order[0])
    find_2d_path, all_routes = router.get_2d_paths_for_real_assay(order_droplets)

    if find_2d_path:
        sub_routes = router.get_3d_compaction_for_real_assay(all_routes, 50, assay.droplet_num, assay)
        time_step, cell_num = router.get_time_steps_and_used_cell_num(sub_routes)
        return [time_step, cell_num], [time_step, cell_num]  # 目标、约束
    else:
        return [-1, -1], [-1, -1]


# 获取初始化或者最终的result以及non-dominated result，各自对应的个体，时间以及cell数量
def get_pop_time_cell(solutions, non_solutions):
    pop = []
    times = []
    cells = []
    sort_results = sorted(solutions, key=lambda x: x.objectives[0])  # 按照时间排序
    for p in sort_results:
        pop.append(p.variables[0])
        times.append(p.objectives[0])
        cells.append(p.objectives[1])

    # non_solutions.sort(key=lambda x: x.objectives[0])
    sort_non_results = sorted(non_solutions, key=lambda x: x.objectives[0])  # 按照时间排序
    non_pop = []
    non_times = []
    non_cells = []
    for n in sort_non_results:
        non_pop.append(n.variables[0])
        non_times.append(n.objectives[0])
        non_cells.append(n.objectives[1])
    return pop, times, cells, non_pop, non_times, non_cells


def read_real_assay(directory):
    file_name = os.listdir(directory)
    file_name.sort(key=lambda x: int(x.split('.')[-1]))
    relative_path = [directory + '/' + name for name in file_name]
    return relative_path


# 保存初始化种群的结果
def keep_final_result(file_obj, assay_name, all_pop, all_time, all_cell_num, non_pop, non_time, non_cell_num):

    success = 0
    file_obj.write('===' + assay_name + ' Population Result===\n')
    str_time = 'Time:'
    for t in all_time:
        str_time += ' ' + mat.format(str(t))
        if t != -1:
            success += 1
    file_obj.write(str_time + '\n')

    str_cell = 'Cell:'
    for c in all_cell_num:
        str_cell += ' ' + mat.format(str(c))
    file_obj.write(str_cell + '\n')

    success_rate = success / len(all_pop)
    file_obj.write('final successful rate = ' + str(success_rate * 100) + '%\n\n')

    file_obj.write(assay_name + ' Non-dominated Individual:\n')
    str_time = 'Non-Time:'
    for t in non_time:
        str_time += ' ' + mat.format(str(t))
        if t != -1:
            success += 1
    file_obj.write(str_time + '\n')

    str_cell = 'Non-Cell:'
    for c in non_cell_num:
        str_cell += ' ' + mat.format(str(c))
    file_obj.write(str_cell + '\n\n')

    file_obj.write(assay_name + ' Non-dominated Individual Details:\n')
    idx = 1
    for order in zip(non_pop, non_time, non_cell_num):
        file_obj.write('population ' + str(idx) + '\n')
        file_obj.write('path order: ' + str(order[0]) + '\n')
        file_obj.write('time step: ' + str(order[1]) + '\n')
        file_obj.write('used cell number: ' + str(order[2]) + '\n\n')
        idx += 1

    file_obj.write('=================================================================================\n\n')

    print('Save final result for ' + assay_name)
    print('=================================================================================')


if __name__ == '__main__':
    # assay_name = 'in_vitro_1'
    assay_name = 'protein_2'
    directory = 'assay/real_assay/' + assay_name
    res_path = 'results/real/' + assay_name + '.txt'
    paths = read_real_assay(directory)

    min_time = 0
    total_time = 0
    used_cells = 0
    sub_num = 0

    with open(res_path, 'w') as f:
        for path in paths:
            assay = Assay(path, REAL_ASSAY)
            assay.read_sub_assay()

            problem = Problem(1, 2, 2)  # 一个输入， 两个目标， 两个约束
            problem.types[0] = Permutation(range(1, assay.droplet_num + 1))
            problem.constraints[:] = '>=0'
            problem.function = functools.partial(droplet_routing_problem, assay=assay)

            if assay.droplet_num >= 4:
                pop_size = 10
                gen = 20
            else:
                pop_size = 3
                gen = 5

            algorithm = NSGAII(problem, population_size=pop_size)

            algorithm.initialize()  # 初始化

            algorithm.run(gen)

            # 处理结果
            final_nondominated = nondominated(deepcopy(algorithm.result))  # 最终结果non-dominated的部分个体
            final_pop, final_times, final_cells, final_non_pop, final_non_times, final_non_cells = \
                get_pop_time_cell(algorithm.result, final_nondominated)

            if final_non_times[0] > min_time:
                min_time = final_non_times[0]

            sub_num += 1
            used_cells += final_non_cells[0]
            total_time += final_non_times[0]

            keep_final_result(f, assay.assay_name, final_pop, final_times, final_cells, final_non_pop, final_non_times,
                              final_non_cells)

    print('latest T = ' + str(min_time) + ', avg time = ' + str(total_time / sub_num) +
          ' , used cells = ' + str(used_cells))


