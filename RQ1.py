# 计算RQ1的结果

import csv
import os

# 数据的文件路径
cons = '../analysis-script/data/constrained/'
uncons = '../analysis-script/data/unconstrained/'

# 信息存储的文件路径
file_cons_save = '../cons_RQ1_infos.csv'
file_uncons_save = '../uncons_RQ1_infos.csv'

# 模型名称
# def get_name():
#     path1 = '../constrained'
#     path2 = '../unconstrained'
#     f1 = open(path1)
#     f2 = open(path2)
#     try:
#         str1 = f1.readlines()
#         str2 = f2.readlines()
#         str1 = [x.strip() for x in str1]
#         str2 = [x.strip() for x in str2]
#         print(str1)
#         print(str2)
#     finally:
#         f1.close()
#         f2.close()
#
# get_name()

# 带约束的模型名称
name_cons = ['apache', 'bugzilla', 'gcc', 'spins', 'spinv', 'flex', 'grep', 'gzip', 'make', 'nanoxml', 'sed', 'siena', 'tcas', 'replace', 'printtokens', 'apache-small', 'mysql', 'mysql-small', 'html5-vcl', 'html5-parsing', 'slider', 'credit', 'Banking2', 'CommProtocol', 'Healthcare1', 'Healthcare2', 'Healthcare3', 'Healthcare4', 'NetworkMgmt', 'ProcessorComm1', 'ProcessorComm2', 'Services', 'Storage3', 'Storage4', 'Storage5', 'SystemMgmt', 'Telecom', 'Drupal', 'Sensor', 'AspectOptima']


# 不带约束的模型名称
name_uncons = ['tokens', 'vim', 'sort', 'totinfo', 'schedule', 'schedule2', 'find', 'findstr', 'attrib', 'fc', 'chmod', 'desigo', 'nvd', 'html5-video', 'html5-audio', 'soot-pdg', 'dsi-rax1', 'dsi-rax2', 'dsi-rax3', 'dsi-rax4', 'las', 'dmas', 'ti', 'modem', 'fgs', 'simured', 'smartphone', 'addpark', 'voice', 'contiki', 'xterm', 'sylpheed', 'Insurance']


# 用以排除macOS自带的'.DS_Store'
def is_valid(name):
    if name[0] == '.':
        return False
    else:
        return True


# 传入两个需处理的字符串（时间，大小）、算法和覆盖强度；返回一个结果字串： Strength-nameIndex-algorithm,Strength,Model,Algorithm,Size,Time,Success
# Name的格式为：way-名字在name中的下标-算法 如：2-0-acts，表示apache模型用acts生成的2-way结果
# 计算大小和时间的平均值，每行结果是一个以逗号分割的字符串
def compute_average(size, time, algorithm, strength, name):
    # 模型名称
    model = size.split(']')[0][1:]
    # 模型名称在name中的下标。
    if model not in name:
        if len(name) == 40:
            print('带约束的模型名称中不存在' + model + ',其位于带约束的' + algorithm + '-' + strength + '-way中')
            return ''
        else:
            print('不带约束的模型名称中不存在' + model + ',其位于带不约束的' + algorithm + '-' + strength + '-way中')
            return ''
    # 因为一共就40+个模型，所以我们用2进制来表示，再去掉前两个字符'0b'
    nameIndex = bin(name.index(model))[2:]
    # 大小列表
    sizes = size.split(' ')[1:]
    # 时间列表
    times = time.split(' ')[1:]
    # 执行次数。为了除法准确，将其变成浮点型
    leng = len(sizes)
    # 总大小，不加-1
    total_size = 0
    # 总时间，不加-1
    total_time = 0

    # 如果存在-9--超内存--直接返回结果
    if '-9' in sizes:
        re = [strength + '-' + str(nameIndex) + '-' + algorithm, strength, model, algorithm, '-9', '-9', '0.0']
        return ','.join(re)

    # 计算size和time的总和
    for i in range(0 ,len(sizes)):
        # 如果size等于-1，不算在size和time总和内，leng--
        if int(sizes[i]) != -1:
            total_size += int(sizes[i])
            total_time += int(times[i])
        else:
            leng -= 1

    # print(algorithm + '-' + strength + '-' + model)
    # 组成字串
    if leng == 0:
        re = [strength + '-' + str(nameIndex) + '-' + algorithm, strength, model, algorithm, '-1', '-1', '0.0']
    else:
        re = [strength + '-' + str(nameIndex) + '-' + algorithm, strength, model, algorithm, str(total_size/leng), str(total_time/leng), str(leng / len(sizes))]
    return ','.join(re)


def RQ1(data_path, save_path, name):
    folders = os.listdir(data_path)
    # 去掉os.list输出的多余的'.DS_Store'
    folders = list(filter(is_valid, folders))
    files = []
    for folder in folders:
        rpath = os.listdir(data_path + folder)
        # 去掉os.list输出的多余的'.DS_Store'
        rpath = list(filter(is_valid, rpath))
        # 将.time和.size放一起
        rpath.sort()
        rpath = [data_path + folder + '/' + path for path in rpath]
        # 将路径加入files
        for f in rpath:
            files.append(f)
        # print(rpath)

    # 用以存储数据分析的结果
    result = []
    # 每次从files中取两个元素，size在前，time在后
    for i in range(0, len(files), 2):
        file_size = files[i]
        file_time = files[i + 1]
        # 算法
        algorithm = file_size.split('/')[-1].split('-')[0]
        # 覆盖强度
        strength = file_size.split('/')[-1].split('-')[1]
        f1 = open(file_size)
        f2 = open(file_time)
        try:
            str_size = f1.readlines()
            str_time = f2.readlines()
            for i in range(0, len(str_size)):
                result.append(compute_average(str_size[i][:-1], str_time[i][:-1], algorithm, strength, name))
        finally:
            f1.close()
            f2.close()

    # 去掉result中的空字符''
    result = [x for x in result if x != '']
    # 按照预定义的格式，直接按字符串排序
    result.sort()
    RQ1_result = open(save_path, 'w')
    fileHeader = ['Strength', 'Model', 'Algorithm', 'Size', 'Time', 'Success']
    try:
        f_csv = csv.writer(RQ1_result)
        f_csv.writerow(fileHeader)
        for r in result:
            f_csv.writerow(r.split(',')[1:])
    finally:
        RQ1_result.close()

RQ1(cons, file_cons_save, name_cons)
RQ1(uncons, file_uncons_save, name_uncons)
