import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--testcase',type=str,default='test_12_1',help='the test set name: like test_12_1 for benchmark1 or \
    minsik_1')
    parser.add_argument('--maxtimes',type=int,default=1,help='the crossover rate')
    parser.add_argument('--pc',type=int,default=1,help='the crossover rate')
    parser.add_argument('--pm',type=float,default=0.5,help='the muta rate')
    parser.add_argument('--ng',type=int,default=30,help='the number of iteriation')
    parser.add_argument('--ps',type=int,default=20,help='the population size')
    parser.add_argument('--alpha',type=int,default=4,help='the dijkstra parameter alpha')
    parser.add_argument('--beta',type=int,default=2,help='the dijkstra parameter alpha')
    parser.add_argument('--gamma',type=int,default=1,help='the dijkstra parameter alpha')
    args = parser.parse_args()
    return args