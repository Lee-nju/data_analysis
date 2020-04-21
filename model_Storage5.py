# 计算和存储模型本身的特征
# 1. 模型的特征与格式无关，为了方便，使用casa格式的文件来做数据分析，这样能方便计算搜索空间
# 2. 结果文件中模型的名称按照字符串顺序排序的： 1.1: 由于文件显示的配置不同，不同电脑可能有不同的排序 1.2: os.listdir()是递归的，不保证顺序
# 注： 2如果不满足的话，可以按所需的顺序排序，后处理或预处理都可以改一下实现

import csv
import os
# from itertools import combinations
from dd import autoref as _bdd
import datetime
import itertools

# 定义时间格式
ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S,f'

# 使用2-way的模型信息, 模型的路径
constrained = '../analysis-script/benchmark/constrained/casa/2-way/'
unconstrained = '../analysis-script/benchmark/unconstrained/casa/2-way/'

# 信息存储的文件路径
file_cons_save = '../Storage5.csv'
file_uncons_save = '../uncons_model_infos.csv'

bdd = _bdd.BDD()


# 看是否是macOS所自带的文件'.DS_Store'
def is_valid(name):
    if name[0] == '.':
        return False
    else:
        return True


# 处理模型，即将模型转换成bdd需要的格式再做处理
def dispose_model(model, cons):
    f1 = open(model)
    if cons != '':
        f2 = open(cons)
    str = f1.readlines()
    # 模型的参数
    paras = str[2].replace(" \n", '').split(" ")
    para_sum = 0
    # 模型参数个数总和
    for item in paras:
        para_sum += int(item)
    model_con = []
    # 变量下表跟踪
    index = 0
    # 对每个参数，生成一条约束
    for para_num, num in enumerate(paras):
        current_c = ''
        for i in range(int(num)):
            current_c += '('
            value = []
            for j in range(int(num)):
                value.append('~x{}'.format(index + j))
                if i == j:
                    value[j] = 'x{}'.format((index + i))
            for c_index, c in enumerate(value):
                if c_index != len(value) - 1:
                    current_c = current_c + c + ' /\ '
                else:
                    current_c = current_c + c

            if i != int(num) - 1:
                current_c += ') \\/ '
            else:
                current_c += ')'
                # last cons
        index += int(num)
        model_con.append(current_c)

    if cons != '':
        constr = f2.readlines()
        # 再将cons文件中的约束加入
        k = int(constr[0][:-1])
        if k == 0:
            pass
        else:
            length = len(constr)
            for i in range(2, length, 2):
                cn = constr[i].replace(' ', "").replace('\n', '').split('-')[1:]
                value = '~('
                for j, ck in enumerate(cn):
                    if j == len(cn) - 1:
                        value += 'x{}'.format(ck)
                    else:
                        value = value + 'x{}'.format(ck) + ' /\ '
                value += ')'
                model_con.append(value)

    # print(para_sum)
    # for cm in model_con:
    #     print(cm)
    f1.close()
    if cons != '':
        f2.close()
    return para_sum, model_con


# 计算搜索空间
def count_space_and_combs(model, model_paras, cons=''):
    # 处理模型和约束
    para_sum, model_con = dispose_model(model, cons)
    vrs = ['x{i}'.format(i=i) for i in range(para_sum)]
    bdd.declare(*vrs)
    u = bdd.add_expr(model_con[0])
    # 添加约束
    for cm in model_con[1:]:
        u = u & bdd.add_expr(cm)

    bdd.collect_garbage()
    # 返回原始搜索空间和带约束的搜索空间的大小

    return [u.count(nvars=para_sum), compute_valid_combs(6, u, model_paras)]
    # return [u.count(nvars=para_sum), compute_valid_combs(2, u, model_paras), compute_valid_combs(3, u, model_paras)]


# 利用bdd计算t维合法的组合数
def compute_valid_combs(t, u, para_num):
    print(datetime.datetime.now().strftime(ISOTIMEFORMAT) + ' -- ' + str(t) + '-way')
    # 参数取值个数总和
    v_num = 0
    for x in para_num:
        v_num += x
    # 参数下标
    para_index = [i for i in range(len(para_num))]
    s = ['x{}'.format(i) for i in range(v_num)]
    # 给s分组
    para = []
    l = 0
    for i in range(len(para_num)):
        k = para_num[i] + l
        para.append(list(s[l:k]))
        l = k

    # 统计总合法组合数
    combs_num = 0
    # 初始化下标的组合
    comb = [i for i in range(t)]

    try:
        k = 0
        sum = 0
        # 如果下标组合不为空
        while comb:
            if (sum - k) // 10000000 > 0:
                k = sum
                print(datetime.datetime.now().strftime(ISOTIMEFORMAT) + ' -- ' + str(sum))
            bdd.collect_garbage()
            m_c = []
            # 将约束组合的下标换成的相应的参数值
            for i in comb:
                m_c.append(para[i])

            # 约束的所有参数值的组合
            v_combs = list(itertools.product(*m_c))

            # 对每个参数值的组合
            for v_comb in v_combs:
                comb2cons = ''
                # 将['x1', 'x3']改成格式'x1 /\ x3'
                for i in range(t):
                    if i == t - 1:
                        comb2cons += v_comb[i]
                    else:
                        comb2cons += v_comb[i] + ' /\ '

                # u的新约束
                x = bdd.add_expr(comb2cons)
                # 和u合并
                check = u & x
                # 如果可满足，可满足总数加
                if bdd.exist(s, check) == bdd.true:
                    combs_num += 1
                else:
                    pass
                    # 否则，不做动作

            # 更新到下一个下标的组合
            comb = next_comb(t, comb, para_index)
            sum += len(v_combs)

        print(str(t) + '-way: 共' + str(combs_num) + '个合法组合!')
        return combs_num

    except:
        print(str(t) + '-way: 出错!!!')
        return '-'

# t:维度 para_num:每个参数取值个数列表
def compute_raw_combs(t, para_num):
    # 组合数个数
    combs_num = 0
    # 总的参数个数
    paras = len(para_num)
    # 参数下标
    para_index = [i for i in range(paras)]
    comb = [i for i in range(t)]
    while comb:
        current_comb = 1
        for i in comb:
            current_comb *= para_num[i]
        combs_num += current_comb
        # 更新到下一个comb
        comb = next_comb(t, comb, para_index)

    return combs_num


def next_comb(t, comb, para_index):
    if comb[-1] < para_index[-1]:
        comb[-1] += 1
        return comb
    else:
        k = 2
        while k <= t:
            if comb[-k] < para_index[-k]:
                comb[-k] += 1
                for i in range(-k + 1, 0):
                    comb[i] = comb[i - 1] + 1
                return comb
            else:
                k += 1

        # 如果没有下一个组合 返回空
        return []


# 处理模型的信息
def cons_basic_info():
    # 先处理带约束的模型信息
    path = constrained
    files = os.listdir(path)
    # 去掉'.DS_Store'
    files = list(filter(is_valid, files))
    # 文件名排序
    files.sort()
    # result存储结果
    result = open(file_cons_save, 'w')
    # 文件头
    fileHeader = ['Name', 'Parameter', 'Constraint', 'Constrained Parameter', 'Raw', 'Valid', 'Proportion', '2-way',
                  '3-way', '6-way(valid)']

    f_csv = csv.writer(result)
    f_csv.writerow(fileHeader)
    result.close()
    # 模型及其相应的下标使相连的
    for index in range(0, len(files), 2):
        f_cons_path = files[index]
        f_model_path = files[index + 1]

        if f_model_path != 'Storage5-casa-2-way.model':
            continue
        # 打印时间和模型
        print(datetime.datetime.now().strftime(ISOTIMEFORMAT) + ' -- cons ' + str(
            int(index / 2)) + ': ' + f_model_path + ' is running!')

        name = f_model_path.split('-casa-')[0]
        f_cons = open(path + f_cons_path)
        f_model = open(path + f_model_path)
        f_str_cons = f_cons.readlines()
        f_str_models = f_model.readlines()
        cons_num = f_str_cons[0]
        para_num = f_str_models[1]
        model_paras = f_str_models[2].replace(' \n', '').split(' ')
        model_paras = [int(x) for x in model_paras]
        # 用集合来存储约束涉及的参数，来保证不会重复
        para_cons_involved = set()
        for i in range(2, len(f_str_cons), 2):
            # 约束涉及的参数值
            para_values = f_str_cons[i].replace(' ', '').replace('\n', '').split('-')[1:]
            # 将约束的取值转换成相应的参数并加入集合
            for value in para_values:
                # 累计参数范围
                para = 0
                # 参数序号
                k = 0
                for v in model_paras:
                    para += int(v)
                    if int(value) < para:
                        break
                    else:
                        k = k + 1
                # 参数序号加入集合
                para_cons_involved.add(k)

        f_cons.close()
        f_model.close()
        # 原始搜索空间
        raw = 1
        for x in model_paras:
            raw *= x

        # 2-6 way的原始组合数
        raw_combs = [compute_raw_combs(2, model_paras), compute_raw_combs(3, model_paras)]

        valid = count_space_and_combs(path + f_model_path, model_paras, path + f_cons_path)
        # 以追加的格式打开文件
        result = open(file_cons_save, 'a')
        f_csv = csv.writer(result)
        # 更新info
        info = [name, para_num, cons_num, len(para_cons_involved), raw, valid[0], float(valid[0]) / float(raw),
                *raw_combs, *valid[1:]]
        # 将info写入result中的一行
        f_csv.writerow(info)
        result.close()
        # 打印时间和模型
        print(datetime.datetime.now().strftime(ISOTIMEFORMAT) + ' -- cons ' + str(
            int(index / 2)) + ': ' + f_model_path + ' is done!')


# 处理模型的信息
def uncons_basic_info():
    # 先处理带约束的模型信息
    path = unconstrained
    files = os.listdir(path)
    # 去掉'.DS_Store'
    files = list(filter(is_valid, files))
    # 也用一次sort，与上同步，且能把model和cons放在相邻下标
    files.sort()
    # result存储结果
    result = open(file_uncons_save, 'w')
    # 文件头
    fileHeader = ['Name', 'Parameter', 'Constraint', 'Constrained Parameter', 'Raw', 'Valid', 'Proportion', '2-way',
                  '3-way', '2-way(valid)', '3-way(valid)']

    f_csv = csv.writer(result)
    f_csv.writerow(fileHeader)
    result.close()
    # 模型及其相应的下标使相连的
    for index in range(0, len(files)):
        f_model_path = files[index]
        # 打印模型
        print('uncons ' + str(index) + ': ' + f_model_path + ' is running!')
        name = f_model_path.split('-casa-')[0]
        f_model = open(path + f_model_path)
        f_str_models = f_model.readlines()
        cons_num = 0
        para_num = f_str_models[1]
        # 得到参数列表
        model_paras = f_str_models[2].replace(' \n', '').split(' ')
        # 将字符参数列表转换成整型参数列表
        model_paras = [int(x) for x in model_paras]
        # 约束涉及的参数个数
        para_cons_involved = 0
        # 原始搜索空间大小
        raw = 1
        for x in model_paras:
            raw *= x

        # 2-6 way的原始组合数
        raw_combs = [compute_raw_combs(2, model_paras), compute_raw_combs(3, model_paras),
                     compute_raw_combs(4, model_paras), compute_raw_combs(5, model_paras),
                     compute_raw_combs(6, model_paras)]

        # 以追加的格式打开文件
        result = open(file_uncons_save, 'a')
        f_csv = csv.writer(result)
        # 更新info
        info = [name, para_num, cons_num, para_cons_involved, raw, raw, 1, *raw_combs, *raw_combs]
        # 将info写入result中的一行
        f_csv.writerow(info)
        # 关闭文件
        result.close()
        # 打印模型
        print('uncons ' + str(index) + ': ' + f_model_path + ' is done!')


cons_basic_info()
