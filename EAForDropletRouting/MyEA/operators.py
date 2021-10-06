import random
import copy


def swap_mutate(parent, prob=0.5):
    result = copy.deepcopy(parent)
    if random.uniform(0.0, 1.0) <= prob:
        i = random.randrange(len(result))
        j = random.randrange(len(result))

        if len(result) > 1:
            while i == j:
                j = random.randrange(len(result))

        result[i], result[j] = result[j], result[i]

    return result


def insert_mutate(parent, prob=0.5):
    result = copy.deepcopy(parent)
    if random.uniform(0.0, 1.0) <= prob:
        i = random.randrange(len(result))
        j = random.randrange(len(result))

        if len(result) > 1:
            while i == j:
                j = random.randrange(len(result))

        temp = result[i]
        if i < j:
            for k in range(i + 1, j + 1):
                result[k - 1] = result[k]
        elif i > j:
            for k in range(i - 1, j - 1, -1):
                result[k + 1] = result[k]

        result[j] = temp
    return result


def PMX(parent1, parent2, prob=1.0):
    """
    crossover
    :param parent1: 父代1
    :param parent2: 父代2
    :param prob: 概率
    :return: 返回交叉后的两个子代
    """
    result1 = copy.deepcopy(parent1)
    result2 = copy.deepcopy(parent2)
    if random.uniform(0.0, 1.0) <= prob:
        p1 = result1
        p2 = result2
        n = len(p1)
        o1 = [None] * n
        o2 = [None] * n

        # select cutting points
        cp1 = random.randrange(n)
        cp2 = random.randrange(n)

        if n > 1:
            while cp1 == cp2:
                cp2 = random.randrange(n)

        if cp1 > cp2:
            cp1, cp2 = cp2, cp1

        # exchange between the cutting points, setting up replacement arrays
        replacement1 = {}
        replacement2 = {}

        for i in range(cp1, cp2 + 1):
            o1[i] = p2[i]
            o2[i] = p1[i]
            replacement1[p2[i]] = p1[i]
            replacement2[p1[i]] = p2[i]

        # fill in remaining slots with replacements
        for i in range(n):
            if i < cp1 or i > cp2:
                n1 = p1[i]
                n2 = p2[i]

                while n1 in replacement1:
                    n1 = replacement1[n1]

                while n2 in replacement2:
                    n2 = replacement2[n2]

                o1[i] = n1
                o2[i] = n2

        result1 = o1
        result2 = o2
    return [result1, result2]


def random_select(population):
    # 随机选择两个父代
    p1 = random.randint(0, len(population) - 1)
    p2 = random.randint(0, len(population) - 1)

    while p1 == p2:
        p2 = random.randint(0, len(population) - 1)
    return [population[p1], population[p2]]


def tournament_select(population, tour_size):
    def select_one():
        winner = random.choice(population)
        for _ in range(tour_size - 1):
            candidate = random.choice(population)
            if candidate.objectives[0] < winner.objectives[0]:
                winner = candidate
        return winner

    win1 = select_one()
    win2 = select_one()
    return [win1, win2]


if __name__ == '__main__':
    parent1 = [1, 2, 3, 4, 5]
    parent2 = [5, 4, 3, 2, 1]
    result = PMX(parent1, parent2)

    print("result1 = [" + ",".join(list(map(str, result[0]))) + "]")
    print("result1 = [" + ",".join(list(map(str, result[1]))) + "]")

