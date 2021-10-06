############################################################################################
# MyRouter类继承自Router类
# 算法在找某个液滴的路径的时候尽量避免移动别的液滴，如果非得移动其它液滴，就要找这些退让液滴的退让点，
# 如果退让点找不到，就得reroute当前的液滴，退让过的液滴需要返回到自己的终点
# Created by 吴贻能 on 2019/12/10.
############################################################################################

from Router import Router
from Router import MyCell
from Utils import *
from copy import deepcopy


class MyRouter(Router):
    def __init__(self, height, width, blockages, droplets, assay):
        super(MyRouter, self).__init__(height, width, blockages, droplets, assay)

    def router_specific_inits(self):
        for x in range(self.height):
            row = []
            for y in range(self.width):
                cell = MyCell(x, y)
                row.append(cell)
            self.board.append(row)

        for block in self.blockages:
            self.board[block[0]][block[1]].is_block = True

    # 找到目标点周围的可以移动的cell加入目标
    def cells_around_target(self, droplet):
        target = droplet.target
        dests = []  # 终点
        if self.board[target.x][target.y].block_for_target == 0:
            dests.append(target)

        for cell in self.neighbors(target):
            if self.board[cell.x][cell.y].block_for_target == 0:
                dests.append(cell)

        if len(dests) == 0:
            dests.append(target)
            for cell in self.neighbors(target):
                dests.append(cell)

            if len(dests) == 0:
                for cell in self.neighbors2(target):
                    dests.append(cell)
                for cell in self.around_cells(target):
                    dests.append(cell)
        return dests

    # 获得A-cell
    def get_a_cells(self, droplet):
        target = droplet.target
        a_cells = []
        for cell in self.neighbors(target):
            a_cells.append(cell)
        return a_cells

    # 搜索算法
    def dijkstra_search(self, source, target):
        frontier = PriorityQueue()
        frontier.put(source, 0)
        cost_so_far = dict()
        came_from = dict()
        came_from[source] = None
        cost_so_far[source] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == target:
                if cost_so_far[target] >= self.MAX_COST:
                    return False, came_from, cost_so_far
                else:
                    return True, came_from, cost_so_far

            for next_cell in self.neighbors(current):
                # new_cost = cost_so_far[current]
                # if not self.board[next_cell.x][next_cell.y].is_used:
                #     new_cost += 1.0
                # if self.board[next_cell.x][next_cell.y].block_for_source > 0:
                #     new_cost += self.board[next_cell.x][next_cell.y].block_for_source * 2.0
                # if self.board[next_cell.x][next_cell.y].block_for_target > 0:
                #     new_cost += self.board[next_cell.x][next_cell.y].block_for_target * 4.0

                new_cost = 0.0
                if not self.board[next_cell.x][next_cell.y].is_used:
                    new_cost = cost_so_far[current] + 1.0
                if self.board[next_cell.x][next_cell.y].block_for_source > 0:
                    new_cost = cost_so_far[current] + self.board[next_cell.x][next_cell.y].block_for_source * 2.0
                if self.board[next_cell.x][next_cell.y].block_for_target > 0:
                    new_cost = cost_so_far[current] + self.board[next_cell.x][next_cell.y].block_for_target * 4.0

                if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                    cost_so_far[next_cell] = new_cost
                    priority = new_cost
                    frontier.put(next_cell, priority)
                    came_from[next_cell] = current
        return False, None, None

    # 搜索算法用于找退让点的路径
    def dijkstra_search_for_concession_zone(self, source, target):
        frontier = PriorityQueue()
        frontier.put(source, 0)
        cost_so_far = dict()
        came_from = dict()
        came_from[source] = None
        cost_so_far[source] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == target:
                return came_from

            for next_cell in self.neighbors(current):
                # 区别于正常的液滴搜索算法
                if self.board[next_cell.x][next_cell.y].block_for_source == 0 \
                        and self.board[next_cell.x][next_cell.y].block_for_target == 0:
                    new_cost = cost_so_far[current]
                    if not self.board[next_cell.x][next_cell.y].is_used:
                        new_cost += 1.0

                    if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                        cost_so_far[next_cell] = new_cost
                        priority = new_cost
                        frontier.put(next_cell, priority)
                        came_from[next_cell] = current
        return None

    # route = (id, route)
    def get_2d_paths(self, new_droplets):
        id_to_index = {}  # id : index
        for idx in range(len(new_droplets)):
            id_to_index[new_droplets[idx].id] = idx

        all_routes = []  # 用于保存路径，list中的元素为(id, route)
        # 所有液滴的起点的critical zone先被记录
        for d in new_droplets:
            self.add_down_block_for_source_target_helper(d.source, self.ADD_BLOCK_FOR_SOURCE, 1)

        current_cycle = 0
        rounds = 0
        d = 0
        find_other_path = False
        recover_blocks = False
        find_concession_times = 0
        re_round = 0

        size = len(new_droplets)

        while d < size:
            copy_board = deepcopy(self.board)  # 深拷贝当前的board
            if new_droplets[d].is_arrive:
                d += 1
                if d == size:  # 检查是否有没抵达终点的液滴
                    for droplet in new_droplets:
                        if not droplet.is_arrive:
                            d = 0
                    re_round += 1
                    if re_round > 10:
                        # print("    [ERROR] meet over 10 recursions, check it!!!")
                        return False, None
                continue

            # 液滴的起点
            source = new_droplets[d].source
            if new_droplets[d].is_concession:
                source = new_droplets[d].concession_cells[-1]

            # 移动当前液滴，起始点不再是block
            self.add_down_block_for_source_target_helper(source, self.DOWN_BLOCK_FOR_SOURCE, 1)

            # 找当前液滴的终点附近的cell
            dests = self.cells_around_target(new_droplets[d])  # 终点
            if len(dests) == 0:
                # print("Due to deadlock, droplet #" + new_droplets[d].id
                #       + " cannot arrive the 2 cells away from dest")
                return False, None

            best_target = sort_targets_in_des_distance(source, dests)
            new_droplets[d].true_target = best_target

            if new_droplets[d].is_concession and new_droplets[d].concession_cells[-1] == best_target:
                self.add_down_block_for_source_target_helper(best_target, self.ADD_BLOCK_FOR_TARGET, 1)
                new_droplets[d].is_arrive = True

                vis_x = best_target.y + 1
                vis_y = self.height - best_target.x
                # print("[Routing INFO] Due to concession, droplet #" + str(new_droplets[d].id)
                #       + " has already arrived best target (" + str(vis_x) + "," + str(vis_y) + ") Round->" + str(rounds))
                # print("=============================================================================================")
                rounds += 1
                continue

            if rounds == 7:
                debug = 1
            #     self.print_board_block_for_source()
            #     self.print_board_block_for_target()

            if rounds == 7 and find_concession_times == 1:
                # self.print_board_block_for_source()
                # self.print_board_block_for_target()
                # self.print_concessive_block()
                debug = 1

            # 找当前液滴路径
            has_route, came_from, cost_so_far = self.dijkstra_search(source, best_target)
            if has_route:
                route = get_one_path(source, best_target, came_from)
                # print('    [INFO]Best target cost = ' + str(cost_so_far[best_target]))
                # print_route(route, new_droplets[d].id)
            else:
                # print("   [ERROR] Cannot find the route of droplet #" + str(new_droplets[d].id))
                return False, None

            if rounds == 7 and find_concession_times == 2:
                debug = 1

            # 处理可能存在的退让液滴的情况
            concession_droplets = self.find_concession_droplets(d, new_droplets, route, find_concession_times)
            concession_droplets_back = deepcopy(concession_droplets)

            if rounds == 7 and find_concession_times == 2:
                # self.print_board_block_for_source()
                # self.print_board_block_for_target()
                # self.print_temporary_block()
                # self.print_concessive_block()
                debug = 1

            # 处理退让液滴
            if len(concession_droplets) > 0:
                self.add_down_block_for_source_target_helper(source, self.ADD_BLOCK_FOR_SOURCE, 1)

                count_concession_routes = 0
                con_routes = []  # 记录退让液滴的退让路径

                for droplet in concession_droplets:
                    if droplet.is_arrive:  # 退让液滴已经抵达终点
                        dl_source = droplet.true_target
                        self.add_down_block_for_source_target_helper(dl_source, self.DOWN_BLOCK_FOR_TARGET, 1)
                    else:  # 退让液滴未抵达终点
                        if droplet.is_concession:
                            dl_source = droplet.concession_cells[-1]
                        else:
                            dl_source = droplet.source
                        self.add_down_block_for_source_target_helper(dl_source, self.DOWN_BLOCK_FOR_SOURCE, 1)

                    has_con, con_cell, _ = self.find_concession_zone_from_target(droplet.target, dl_source)
                    # 找到退让区
                    if has_con:
                        # vis_x = con_cell.y + 1
                        # vis_y = self.height - con_cell.x
                        #
                        # if droplet.is_arrive:
                        #     print("    [Concession INFO] Arrived droplet #" + str(droplet.id) + " is going to ("
                        #           + str(vis_x) + "," + str(vis_y) + ")")
                        # else:
                        #     print("    [Concession INFO] Un-routed droplet #" + str(droplet.id) + " is going to ("
                        #           + str(vis_x) + "," + str(vis_y) + ")")

                        con_came_from = self.dijkstra_search_for_concession_zone(dl_source, con_cell)
                        if con_came_from is not None:
                            con_route = get_one_path(dl_source, con_cell, con_came_from)
                            con_routes.append((droplet.id, con_route))
                            count_concession_routes += 1

                            current_cycle += len(con_route)
                            droplet.concession_source = con_cell
                            droplet.concession_cells.append(con_cell)
                            droplet.is_concession = True
                            droplet.is_arrive = False

                            self.add_down_block_for_source_target_helper(con_cell, self.ADD_BLOCK_FOR_SOURCE, 1)
                        else:
                            # print("    [ERROR] There is a problem with droplet #" + str(droplet.id) + "for concession!")
                            return False, None
                    else:  # 未找到退让区
                        # print("    [MSG] Cannot find concession zone for droplet #" + str(droplet.id)
                        #       + " ,when droplet id is #" + str(new_droplets[d].id))
                        # print("     =========================new try=====================================")

                        # 给予一个特别大的值
                        # if droplet.is_arrive:
                        #     self.add_down_block_for_source_target_helper(dl_source, self.ADD_BLOCK_FOR_TARGET, self.MAX_COST)
                        # else:
                        #     self.add_down_block_for_source_target_helper(dl_source, self.ADD_BLOCK_FOR_SOURCE, self.MAX_COST)

                        # 退让液滴找不到退让点，所以让退让液滴的critical zone暂时被block
                        for x in range(dl_source.x - 1, dl_source.x + 2):
                            for y in range(dl_source.y - 1, dl_source.y + 2):
                                if 0 <= x < self.height and 0 <= y < self.width and not copy_board[x][y].is_block:
                                    copy_board[x][y].temporary_block = True

                        find_other_path = True
                        recover_blocks = True
                        find_concession_times += 1
                        break

                if find_concession_times >= 10:
                    # self.print_board_block_for_source()
                    # self.print_board_block_for_target()
                    # print("  [ERROR] Find other paths over 10 times, when droplet is #" + str(new_droplets[d].id))
                    return False, None

                if find_other_path:  # 需要reroute
                    # 恢复block_for_concession
                    for cell in route[::-1]:
                        for c in self.around_cells(cell):
                            self.board[c.x][c.y].block_for_concession = False
                    # 恢复board
                    self.board = copy_board
                    # 恢复退让液滴
                    for copy_d in concession_droplets_back:
                        new_droplets[id_to_index[copy_d.id]] = copy_d
                    find_other_path = False
                    continue
                else:
                    all_routes.extend(con_routes)
                    # for con_d in concession_droplets:  # 修改液滴状态
                    #     new_droplets[id_to_index[con_d.id]] = con_d

                self.add_down_block_for_source_target_helper(source, self.DOWN_BLOCK_FOR_SOURCE, 1)

            for cell in route[::-1]:
                for c in self.around_cells(cell):
                    self.board[c.x][c.y].block_for_concession = False

            if rounds == 3:
                debug = 1

            all_routes.append((new_droplets[d].id, route))
            current_cycle += len(route)
            self.add_down_block_for_source_target_helper(best_target, self.ADD_BLOCK_FOR_TARGET, 1)
            new_droplets[d].is_arrive = True

            # vis_x = new_droplets[d].true_target.y + 1
            # vis_y = self.height - new_droplets[d].true_target.x
            # if len(concession_droplets) == 0:
            #     print("[Routing INFO] Droplet #" + str(new_droplets[d].id) + " is successful at (" + str(vis_x)
            #           + "," + str(vis_y) + "), WITHOUT moving other droplets! Round->" + str(rounds))
            # else:
            #     print("[Routing INFO] Droplet #" + str(new_droplets[d].id) + " is successful at (" + str(vis_x)
            #           + "," + str(vis_y) + "), AFTER moving other droplets! Round->" + str(rounds))
            #
            # print("=============================================================================================")

            # 恢复被block的critical zone
            if recover_blocks:
                for x in range(self.height):
                    for y in range(self.width):
                        if self.board[x][y].temporary_block:
                            self.board[x][y].temporary_block = False

                        # if self.board[x][y].block_for_source >= self.MAX_COST:
                        #     n = self.board[x][y].block_for_source // self.MAX_COST
                        #     self.board[x][y].block_for_source -= (n * self.MAX_COST)
                        # elif self.board[x][y].block_for_target >= self.MAX_COST:
                        #     n = self.board[x][y].block_for_target // self.MAX_COST
                        #     self.board[x][y].block_for_target -= (n * self.MAX_COST)
            if rounds == 3:
                debug = 1

            d += 1
            rounds += 1
            find_concession_times = 0
            if d == len(new_droplets):
                for droplet in new_droplets:
                    if not droplet.is_arrive:
                        d = 0
                re_round += 1
                if re_round > 10:
                    # print("    [ERROR] meet recursion, check it!!!")
                    return False, None
        # print("[MSG] Success! 2D routing time is = " + str(current_cycle))
        return True, all_routes

    def get_3d_compaction(self, all_routes, max_cycle, droplets_num):
        sub_routes = [[] for _ in range(droplets_num)]  # compaction routes

        record_last_cell = deepcopy(all_routes)  # copy all routes
        record_cycles = [0 for _ in range(droplets_num)]  # 记录每个液滴的时长

        current_max_cycle = 0
        idx = 0
        while idx < len(all_routes):
            id_route = all_routes[idx]  # (id, route)
            cur_id = id_route[0]  # 当前路径所对应的液滴的ID
            route = id_route[1]  # 当前的路径
            route_map = record_last_cell[idx][1]  # 保存最初始的路径

            t = 0
            last_same_id_cycle = record_cycles[cur_id - 1]
            if last_same_id_cycle > 0:
                t = last_same_id_cycle

            route_map_idx = 0
            current_max_cycle = max(current_max_cycle, len(route) - 1)
            insert_head = False
            while t <= max_cycle and t <= current_max_cycle:
                is_interference = False
                static_interference = False
                dynamic_interference = False

                if t - last_same_id_cycle >= len(route):
                    rp = route[-1]  # current cell
                else:
                    rp = route[t - last_same_id_cycle]

                for k in range(idx):
                    past_id = all_routes[k][0]
                    past_route = sub_routes[past_id - 1]
                    if past_id == cur_id:
                        continue

                    # past cell
                    if t >= len(past_route):
                        prp = past_route[-1]
                    else:
                        prp = past_route[t]

                    prp_next_cell = None  # past route's next cell
                    if t + 1 < len(past_route):
                        prp_next_cell = past_route[t + 1]

                    rp_next_cell = None  # this route's next cell
                    if t + 1 - last_same_id_cycle < len(route):
                        rp_next_cell = route[t + 1 - last_same_id_cycle]

                    if prp is not None and does_interfere(rp, prp):
                        is_interference = True
                        static_interference = True  # static constraint

                    if prp_next_cell is not None and does_interfere(prp_next_cell, rp):
                        is_interference = True
                        dynamic_interference = True

                    if rp_next_cell is not None and does_interfere(prp, rp_next_cell):
                        is_interference = True
                        dynamic_interference = True

                if is_interference:
                    insert_index = t - last_same_id_cycle

                    if insert_index >= len(route):
                        insert_index = len(route) - 1

                    if rp == route_map[0]:
                        route.insert(0, route[0])
                        t += 1
                        insert_head = True
                    else:
                        if static_interference:
                            stall_num = 1
                            while insert_index > 0:
                                if route[insert_index] == route[insert_index - 1]:
                                    stall_num += 1
                                else:
                                    break
                                insert_index -= 1
                            rp_stall = route[insert_index - 1]
                            if insert_index != t - last_same_id_cycle:
                                if t - last_same_id_cycle >= len(route):
                                    for _ in range(insert_index + 1, len(route)):
                                        route.pop()
                                else:
                                    tmp_route = [route[i] for i in range(len(route)) if i < insert_index
                                                 or i >= t - last_same_id_cycle]
                                    route = tmp_route
                                for _ in range(stall_num):
                                    route.insert(insert_index, rp_stall)
                                t -= stall_num
                            else:
                                route.insert(insert_index - 1, rp_stall)
                        else:
                            rp_stall = route[insert_index]
                            route.insert(insert_index, rp_stall)
                            t += 1
                else:
                    t += 1
                    route_map_idx += 1

            if len(sub_routes[cur_id - 1]) == 0 or insert_head:
                record_cycles[cur_id - 1] += len(route)
                sub_routes[cur_id - 1].extend(route)
            else:
                sub_routes[cur_id - 1].extend(route[1:])
                record_cycles[cur_id - 1] = len(sub_routes[cur_id - 1])

            if record_cycles[cur_id - 1] > current_max_cycle:
                current_max_cycle = record_cycles[cur_id - 1]

            # print('index = ' + str(idx), end='  ')
            # self.print_vis_route(route, cur_id)
            idx += 1

        return sub_routes

