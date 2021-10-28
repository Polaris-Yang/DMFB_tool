from copy import error
from typing_extensions import final
from numpy.core.fromnumeric import trace
from numpy.lib.function_base import average
from numpy.lib.utils import safe_eval
from problem import *
from operators import *
from Assay import *
from abc import ABCMeta, abstractmethod
import os
import time
import numpy as np
from os import path
from TargetRouter import TargetRouter
from Utils import *
import arguments
from tqdm import tqdm

class SingleObjectiveAlgorithm:
    def __init__(self, problem, pop_size=50, offspring_size=50, mutate_prob=0.5,
                 selector=None,
                 comparator=None):
        self.problem = problem
        self.pop_size = pop_size
        self.offspring_size = offspring_size
        self.mutate_prob = mutate_prob
        self.selector = selector
        self.comparator = comparator

    def initialize(self):
        self.population = [generate(self.problem) for _ in range(0, self.pop_size)]
        self.evaluate_all(self.population)

        self.initial_pop = []
        self.fittest_in_each_gen = []
        self.feasible_num = []
        self.final_result = []
        self.avg_fittest_each_gen = []

    def evaluate_all(self, solutions):
        for solution in solutions:
            solution.objectives.append(self.problem.get_time_steps(solution.variables))

    @abstractmethod
    def iterate(self):
        raise NotImplementedError("method not implemented")

    def save_name(self, generation):
        if not os.path.exists('soea_results'):
            os.makedirs('soea_results')

        file_dir = 'soea_results/' + self.problem.assay.assay_name
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        file_info = [self.problem.assay.assay_name, self.pop_size, self.offspring_size, self.mutate_prob, generation]
        file_name = file_dir + '/' + '_'.join(list(map(str, file_info))) + '.info'
        return file_name

    def save_info(self, file, run_time, pass_time):
        file.write('第' + str(run_time) + '执行该程序，执行时间为' + str(pass_time) + '秒\n')
        feasible_num = 'feasible_num: ' + ','.join(list(map(str, self.feasible_num)))
        file.write(feasible_num + '\n')

        best_so_far = 'best_so_far: ' + ','.join((list(map(str, self.fittest_in_each_gen))))
        file.write(best_so_far + '\n')

        file.write('Best result occur in ' + str(np.argmin(self.fittest_in_each_gen)) + '\n')
        file.write('Best Result: ' + str(self.final_result[0]) + '\n\n')

        file.write('=================================================================================\n\n')
        print(pass_time)
        print('第' + str(run_time) + '执行该程序完毕，pass time =' + str(pass_time))
        print('最好的一代出现在第 %s 代' % np.argmin(self.fittest_in_each_gen))
        print('Best Result: ' + str(self.final_result[0]))
        print('=================================================================================')


class EliteGeneticAlgorithm(SingleObjectiveAlgorithm):
    """
    该算法每次迭代保留一个精英
    """

    def __init__(self, problem, pop_size=50, offspring_size=50, mutate_prob=0.5,
                 selector=None,
                 comparator=None):
        super(EliteGeneticAlgorithm, self).__init__(problem, pop_size, offspring_size, mutate_prob, selector,
                                                    comparator)

    def initialize(self):
        super(EliteGeneticAlgorithm, self).initialize()
        self.population = sorted(self.population, key=lambda x: x.objectives[0])
        self.fittest = self.population[0]

    def iterate(self):
        offspring = []
        while len(offspring) < self.offspring_size:
            # parents = random_select(self.population)
            parents = tournament_select(self.population, 2)
            # 父代的变量
            pv1 = parents[0].variables
            pv2 = parents[1].variables
            offspring_vars = PMX(pv1, pv2)  # crossover
            offspring1 = Solution(swap_mutate(offspring_vars[0]))
            offspring2 = Solution(swap_mutate(offspring_vars[1]))
            offspring.append(offspring1)
            offspring.append(offspring2)

        self.evaluate_all(offspring)
        offspring.append(self.fittest)
        offspring = sorted(offspring, key=lambda x: x.objectives[0])

        self.population = offspring[:self.pop_size]
        self.fittest = self.population[0]

    def run(self, generation):
        for i in tqdm(range(1, generation+1)):
            if i == 1:
                self.initialize()
                self.initial_pop = self.population
            else:
                self.iterate()
                self.final_result = self.population
            self.fittest_in_each_gen.append(self.fittest.objectives[0])
            num = 0
            for pop in self.population:
                if pop.objectives[0] != MAX_VALUE:
                    num += 1
            self.feasible_num.append(num)
        return self.fittest_in_each_gen, self.feasible_num


def parameters_set():
    args = arguments.get_arguments()
    test_case = list(args.testcase.split('_'))
    if (test_case[0] == 'test'):
        path = test[test_case[1]][int(test_case[2]) - 1]
        job_type = TEST_ASSAY
    elif (test_case[0 == 'minsik']):
        path = MINSIK[int(test_case[1]) - 1]
        job_type = MINSIK_ASSAY
    else:
        raise Exception("Invalid test case!", args.testcase)
    PATH = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir)) + '/' + path
    assay = Assay(PATH, job_type)
    assay.read_assay()
    problem = RoutingProblem(assay, nobjs=1, alpha=args.alpha, beta=args.beta, gamma=args.gamma)
    generation = args.ng
    max_exe_time = args.maxtimes
    algorithm = EliteGeneticAlgorithm(problem, args.ps, args.ps, args.pm)
    save_file = algorithm.save_name(generation)
    return algorithm, save_file, assay, max_exe_time, args.ng, args


def runAlgotithm(algorithm, save_file, assay, max_exe_time, max_gen):
    with open(save_file, 'w') as file:
        best_results = []
        best_orders = []
        Evo_traces_fit = []
        Evo_traces_feasible = []
        total_start_time = time.time()
        exe_time = 1
        while exe_time <= max_exe_time:
            print(assay.assay_name + " 正在执行第 %s 次" % exe_time)
            start_time = time.time()
            fit, feasible = algorithm.run(max_gen)
            Evo_traces_feasible.append(feasible)
            Evo_traces_fit.append(fit)
            end_time = time.time()
            algorithm.save_info(file, exe_time, end_time - start_time)
            exe_time += 1
            best_results.append(algorithm.fittest_in_each_gen[-1])
            best_orders.append(algorithm.fittest)
        total_end_time = time.time()
        total_cost_time = total_end_time - total_start_time
        average_time_run_onece = total_cost_time / max_exe_time
        file.write('程序执行' + str(max_exe_time) + '之后的结果如下：\n')
        file.write(','.join(list(map(str, best_results))) + '\n')
        file.write('最好的结果为: ' + str(best_orders[np.argmin(best_results)]) + '\n')
        file.write('平均值为: ' + str(np.mean(best_results)) + ', 标准差为: ' + str(np.std(best_results)) + '\n')
        file.write('total_run_time： ' + str(total_cost_time) + 's' + ', avg_rumtime： ' + str(
            average_time_run_onece) + 's' + '\n')
    return best_results, [i.variables for i in best_orders], Evo_traces_fit, Evo_traces_feasible


def print_routing_path(assay, order,args):
    router = TargetRouter(assay.board_size, assay.board_size, assay.blockages, assay.droplets, assay,args.alpha,args.beta, args.gamma)
    router.router_specific_inits()
    order_droplets = router.assign_priority(order)
    print_droplets_order(order_droplets)
    print("////////////////////////////////////Begin 2D Routing///////////////////////////////////")
    find_2d_path, all_routes = router.get_2d_paths(order_droplets)
    if find_2d_path:
        print("////////////////////////////////////2D Routing Result///////////////////////////////////")
        router.print_each_route(all_routes)
        print("////////////////////////////////////After Compaction///////////////////////////////////")
        sub_routes = router.get_3d_compaction(all_routes, 100, assay.droplet_num)
        router.print_each_route_3d(sub_routes)
        print("////////////////////////////Time steps and cells number///////////////////////////////")
        time_step, used_cell = router.get_time_steps_and_used_cell_num(sub_routes)
        print("Time steps are " + str(time_step) + "; The number of used cells is " + str(used_cell))
    else:
        print('This droplet order cannot find all routes')


if __name__ == '__main__':
    alg, savefunc, assay, max_exe_time, max_gen, args = parameters_set()
    best_results, best_orders, evo_trace_fit, evo_trace_feasible \
    = runAlgotithm(alg, savefunc, assay, max_exe_time, max_gen)
    best_order = best_orders[np.argmin(best_results)]
    print_routing_path(assay, best_order,args)
    evo_trace_fit = np.array(evo_trace_fit)
    evo_trace_feasible = np.array(evo_trace_feasible)
    np.save(assay.assay_name + '_evo_trace_feasible', evo_trace_feasible)
    np.save(assay.assay_name + '_evo_trace_fit', evo_trace_fit)
