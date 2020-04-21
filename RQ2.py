# 计算RQ2的结果

import csv
import os
import scipy.stats as stats
import math

# 数据的文件路径
cons = '../analysis-script/data/constrained/'
uncons = '../analysis-script/data/unconstrained/'

# 信息存储的文件路径
file_cons_save = '../cons_RQ2_infos.csv'
file_uncons_save = '../uncons_RQ2_infos.csv'

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


# 传入两个需处理的字符串（时间，大小）、算法和覆盖强度；返回一个结果字串： Strength-nameIndex-algorithm,Strength,Model,Algorithm,Size,Time
# Name的格式为：way-名字在name中的下标-算法 如：2-0-acts，表示apache模型用acts生成的2-way结果
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
    # 大小字串
    sizes = size.split('] ')[1]
    # 时间字串
    times = time.split('] ')[1]
    # 如果等于-9，表示超内存，size和time为-9，直接返回结果
    if '-9' in sizes:
        re = [strength + '-' + str(nameIndex) + '-' + algorithm, strength, model, algorithm, '-9', '-9']
        return ','.join(re)
    else:
        re = [strength + '-' + str(nameIndex) + '-' + algorithm, strength, model, algorithm, sizes, times]
        return ','.join(re)


def RQ2(data_path, save_path, name):
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
    # 打开结果文件
    RQ2_result = open(save_path, 'w')
    fileHeader = ['Strength', 'Model', 'P-value-Size', 'P-value-Time', 'Num', 'Timeout', 'RAMout']
    try:
        f_csv = csv.writer(RQ2_result)
        f_csv.writerow(fileHeader)
        # 计算p-value并将结果写入结果文件中，每4个一组
        i = 0
        while i < len(result):
            re = result[i]
            # 模型名称
            name = re.split(',')[2]
            for j in range(1,4):
                if i + j < len(result) and result[i + j].split(',')[2] == name:
                    re += '|' + result[i + j]
                else:
                    break
            # 得到一个模型名称一致的列表，用于接下来计算p value
            res = re.split('|')
            # for j in range(len(res)):
            #     print(res[j])
            # print('----------------------------')
            # 计算p-value的size列表，用于存四种算法的结果
            s = [[], [], [], []]
            # 计算p-value的time列表，用于存四种算法的结果
            t = [[], [], [], []]
            # 比较个数，初始化为一开始的比较个数
            n = len(res)
            # 更新i
            i = i + n
            # 超时
            Timeout = ''
            # 超内存
            RAMout = ''
            # 每四个一组
            for j in range(n):
                size = res[j].split(',')[-2].split(' ')
                time = res[j].split(',')[-1].split(' ')
                # 判断是否超内存
                if '-9' in size:
                    if RAMout == '':
                        RAMout = res[j].split(',')[-3]
                    else:
                        RAMout = RAMout + ',' + res[j].split(',')[-3]
                else:
                    flag = True
                    for k in range(len(size)):
                        # 如果存在不为-1 说明不超时
                        if size[k] != '-1':
                            s[j].append(int(size[k]))
                            t[j].append((int(time[k])))
                            flag = False
                        # 如果存在-1，说明其中有的超时了
                        # else:
                        #     flag = True

                    # 如果有超时
                    if flag:
                        if Timeout == '':
                            Timeout = res[j].split(',')[-3]
                        else:
                            Timeout = Timeout + ',' + res[j].split(',')[-3]

            # 去掉s和t中的空列表
            s = [x for x in s if x]
            t = [x for x in t if x]

            # 更新n
            n = len(s)

            # 如果没有可计算的p-value值
            if n <= 1:
                info1 = [re.split(',')[1], re.split(',')[2], '-', '-', n, Timeout, RAMout]
                f_csv.writerow(info1)
                continue

            # 写文件
            p_value_size = stats.f_oneway(*s)[1]
            if math.isnan(p_value_size):
                p_value_size = 'identical'

            p_value_time = stats.f_oneway(*t)[1]
            if math.isnan(p_value_time):
                p_value_time = 'identical'

            info = [re.split(',')[1], re.split(',')[2], p_value_size, p_value_time, n, Timeout, RAMout]
            f_csv.writerow(info)

    finally:
        RQ2_result.close()

RQ2(cons, file_cons_save, name_cons)
RQ2(uncons, file_uncons_save, name_uncons)