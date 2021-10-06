############################################################################################
# Assay类用于读取benchmark
############################################################################################
from Droplet import Cell, Droplet

# 代表三种benchmark的测试样例
TEST_ASSAY = 0
MINSIK_ASSAY = 1
REAL_ASSAY = 2

TEST_12_12_PATHS = [
    'assay/test/test_12_12_1.in',
    "assay/test/test_12_12_2.in",
    "assay/test/test_12_12_4.in",
    "assay/test/test_12_12_4.in"
]

TEST_16_16_PATHS = [
    'assay/test/test_16_16_1.in',
    'assay/test/test_16_16_2.in',
    'assay/test/test_16_16_3.in',
    'assay/test/test_16_16_4.in',
    'assay/test/test_16_16_5.in',
    'assay/test/test_16_16_6.in'
]

TEST_24_24_PATHS = [
    'assay/test/test_24_24_1.in',
    'assay/test/test_24_24_2.in',
    'assay/test/test_24_24_3.in',
    'assay/test/test_24_24_4.in',
    'assay/test/test_24_24_5.in',
    'assay/test/test_24_24_6.in',
]

TEST_32_32_PATHS = [
    'assay/test/test_32_32_1.in',
    'assay/test/test_32_32_2.in',
    'assay/test/test_32_32_3.in',
    'assay/test/test_32_32_4.in'
]

test={'12': TEST_12_12_PATHS,'16': TEST_16_16_PATHS,'24': TEST_24_24_PATHS,'32': TEST_32_32_PATHS}

MINSIK = [
    'assay/minsik/benchmark_1_minsik',
    'assay/minsik/benchmark_2_minsik',
    'assay/minsik/benchmark_3_minsik',
    'assay/minsik/benchmark_4_minsik',
    'assay/minsik/benchmark_5_minsik',
    'assay/minsik/benchmark_6_minsik',
    'assay/minsik/benchmark_7_minsik',
    'assay/minsik/benchmark_8_minsik',
    'assay/minsik/benchmark_9_minsik',
    'assay/minsik/benchmark_10_minsik'
]

class Assay:
    def __init__(self, assay_path, assay_type):
        self.board_size = 0  # board 大小
        self.blockages = []  # list中包含所有的不可用的cell
        self.block_source_target = []  # list中的元素是tuple，一个tuple里面是两个tuple，表示着不可用区域的左上和右下两个cell
        self.assay_path = assay_path  # benchmark 路径
        self.droplet_num = 0  # 液滴数量
        self.droplets = []  # list中包含所有的液滴
        self.assay_type = assay_type
        self.assay_name = self.get_assay_name()
        self.nets_num = 0
        self.waste_reservoir = []

    def get_assay_name(self):
        test_name = ''
        if self.assay_type == TEST_ASSAY:
            test_name = self.assay_path.split('/')[-1].split('.')[0]
        elif self.assay_type == MINSIK_ASSAY:
            test_name = self.assay_path.split('/')[-1]
        elif self.assay_type == REAL_ASSAY:
            name = self.assay_path.split('/')[-1].split('.')
            test_name = name[0] + '_' + name[1]
        return test_name

    # 读取benchmark
    def read_assay(self):
        did = 1  # 液滴ID
        with open(self.assay_path, 'r') as f:
            for line in f.readlines():
                strs = list(line.rstrip('\n').split())
                if len(strs) > 0:
                    if strs[0] == 'grid':  # board大小
                        self.board_size = int(strs[1])
                    elif strs[0] == 'block':  # 处理block
                        pos = list(map(int, strs[1:]))
                        for x in range(pos[0], pos[2] + 1):
                            for y in range(pos[1], pos[3] + 1):
                                self.blockages.append((x, y))

                        self.block_source_target.append([(pos[0], pos[1]), (pos[2], pos[3])])
                    elif strs[0] == 'net':  # 处理液滴
                        pos = list(map(int, strs[2:]))
                        source = Cell(pos[0], pos[1])
                        target = Cell(pos[3], pos[4])
                        self.droplet_num += 1
                        droplet = Droplet(did, did, source, target)  # 液滴初始化
                        self.droplets.append(droplet)
                        did += 1

    def read_sub_assay(self):
        '''处理实际生化反应的子问题
        '''

        did = 1  # 液滴ID
        with open(self.assay_path, 'r') as f:
            for line in f.readlines():
                strs = list(line.rstrip('\n').split())
                if len(strs) > 0:
                    if strs[0] == 'grid':  # board大小
                        self.board_size = int(strs[1])
                    elif strs[0] == 'block':  # 处理block
                        pos = list(map(int, strs[1:]))
                        for x in range(pos[0], pos[2] + 1):
                            for y in range(pos[1], pos[3] + 1):
                                self.blockages.append((x, y))
                        self.block_source_target.append([(pos[0], pos[1]), (pos[2], pos[3])])
                    elif strs[0] == 'net' or strs[0] == 'xet':  # 处理液滴
                        pos = list(map(int, strs[2:7]))
                        source = Cell(pos[0], pos[1])
                        target = Cell(pos[3], pos[4])
                        self.droplet_num += 1
                        droplet = Droplet(did, did, source, target)  # 液滴初始化
                        self.droplets.append(droplet)
                        did += 1
                    elif strs[0] == 'nets':
                        self.nets_num = int(strs[1])
                    elif strs[0] == 'WAT':  # 液滴的终点是回收点
                        waste_cell = Cell(int(strs[1]), int(strs[2]))
                        if waste_cell not in self.waste_reservoir:
                            self.waste_reservoir.append(waste_cell)

if __name__ == '__main__':
    with open(PATH, 'r') as f:
        print('open ok')
