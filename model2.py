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
file_cons_save = '../cons_model_infos2.csv'
# file_uncons_save = '../uncons_model_infos.csv'

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
def count_space_and_combs(model, cons=''):
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
    return u.count(nvars=para_sum)


# 计算原始搜索空间 t:维度 para_num:每个参数取值个数列表
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
                  '3-way', '4-way', '5-way', '6-way', '2-way(valid)', '3-way(valid)', '4-way(valid)', '5-way(valid)',
                  '6-way(valid)']

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
        # 存模型具体约束
        para_cons = []
        # 把约束提取出来
        for i in range(2, len(f_str_cons), 2):
            para_cons.append(f_str_cons[i][2:].replace('\n', '').split(' - '))

        cons_num = f_str_cons[0]
        para_num = f_str_models[1]
        # 具体参数的取值个数
        model_paras = f_str_models[2].replace(' \n', '').split(' ')
        model_paras = [int(x) for x in model_paras]
        # 具体参数的取值范围
        p_range = para_range(model_paras)

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
        raw_combs = [compute_raw_combs(2, model_paras), compute_raw_combs(3, model_paras),
                     compute_raw_combs(4, model_paras), compute_raw_combs(5, model_paras),
                     compute_raw_combs(6, model_paras)]

        valid = count_space_and_combs(path + f_model_path, path + f_cons_path)
        # 先调整一下，再计算
        para_cons = adjust_cons(para_cons, p_range)
        valid_combs = MFT_combs(MFT(para_cons, model_paras, p_range), model_paras, p_range)

        # 以追加的格式打开文件
        result = open(file_cons_save, 'a')
        f_csv = csv.writer(result)
        # 更新info
        info = [name, para_num, cons_num, len(para_cons_involved), raw, valid, float(valid) / float(raw), *raw_combs,
                *valid_combs]
        # 将info写入result中的一行
        f_csv.writerow(info)
        result.close()
        # 打印时间和模型
        print(datetime.datetime.now().strftime(ISOTIMEFORMAT) + ' -- cons ' + str(
            int(index / 2)) + ': ' + f_model_path + ' is done!')


# 根据参数取值个数列表来得到参数的取值范围
def para_range(para_num):
    p_range = []
    l = r = 0
    for i in range(len(para_num)):
        if i == 0:
            r = para_num[0] - 1
        else:
            l = r + 1
            r += para_num[i]
        p_range.append((l, r))

    return p_range


# 对约束做调整:
# 1.去掉集合中的重复元素
# 2.去掉包含其他约束的约束，包含其他约束一定不是MFT
# 3.去掉约束中一参数取多值的约束，其本身就是矛盾的
def adjust_cons(cons, p_range):
    # 去掉集合中的重复元素
    m_c = []
    for c in cons:
        # 保证参数不取重复的值
        v_c = []
        for v in c:
            if v not in v_c:
                v_c.append(v)

        # 排次序 排除['20', '36']和['36', '20']判断不相等的情况
        v_c.sort()
        if v_c not in m_c:
            m_c.append(v_c)

    cons = m_c

    # 存放能包含其他约束的下标集合，用于删除掉列表中的对应元素
    del_index = set()
    for x in cons:
        for xt in cons:
            if xt == x:
                pass
            else:
                # 如果后一列表 add 前一列表后，集合的个数没有增加，说明后一列表包含前一列表
                leng = len(xt)
                s = set(xt)
                s.update(x)
                if leng == len(s):
                    del_index.add(cons.index(xt))
    # 更新cons
    cons = [cons[i] for i in range(len(cons)) if i not in del_index]

    # 存在约束中一参数取多值的约束下标
    del_index = set()
    # 对每条约束
    for c in cons:
        # 存一个参数取值表 L = [0, 0, 0,..]
        L = [0 for i in range(len(p_range))]
        # 对c中每个值
        for v in c:
            for i in range(len(p_range)):
                if p_range[i][0] <= int(v) <= p_range[i][1]:
                    L[i] = L[i] + 1
            # 如果某个参数取了两个值，退出循环
            if 2 in L:
                del_index.add(cons.index(c))
                break

    # 更新cons
    cons = [cons[i] for i in range(len(cons)) if i not in del_index]

    return cons


# put con to paras，把约束组放到对应的参数下面
def putC2paras(cons, para_num):
    # 存放每个参数对应的约束
    para_cons = []
    # 右值
    r = 0
    for i in range(len(para_num)):
        para_cons.append([])
        # 左值
        l = 0
        if i != 0:
            l = r
            r += para_num[i]
        else:
            r = para_num[0]
        # 对cons中的每条约束
        for c in cons:
            # 对c中的每个参数
            for v in c:
                # 如果某个参数在左值和右值之间，将约束加入相应的参数中
                if l <= int(v) < r:
                    para_cons[i].append(c)
                else:
                    pass

    return para_cons


# 筛选出所有的参数值被约束全覆盖的参数，做derive，返回derive的结果.
# para_cons是一个三维列表
def derive(para_cons, cons, p_range):
    for i in range(len(p_range)):
        if para_cons[i] == []:
            continue
        # pi的可能的取值
        pi_v = [x for x in range(p_range[i][0], p_range[i][1] + 1)]
        # 涉及pi的约束组
        pi_cons = para_cons[i]
        # pi涉及的约束中包含pi中的值
        pi_paras = set()
        # 对约束组中每个约束
        for pi_con in pi_cons:
            # 如果如果pi的所有可能的取值在这组约束都存在，跳出循环
            if len(pi_paras) == len(pi_v):
                break
            for v in pi_con:
                # 如果v在是pi的值之一
                if int(v) in pi_v:
                    pi_paras.add(v)
                    break

        # 如果pi的所有可能的取值在这组约束都存在，即一定存在隐含约束
        if len(pi_paras) == len(pi_v):
            # 将pi不同取值涉及的约束放在不同[]中
            pi_c = []
            for j in range(len(pi_v)):
                pi_c.append([])

            for pi_con in pi_cons:
                k = 0
                for v in pi_con:
                    # 找到pi取了什么值
                    if int(v) in pi_v:
                        k = int(v)
                        break

                # 把pi_con涉及的值加入相应的列表，pi的值不加入且值不重复
                pi_con = [x for x in pi_con if x != v]
                if pi_con:
                    # 否则加入对应的list
                    pi_c[k - pi_v[0]].append(pi_con)

            # 用笛卡尔乘积来算隐含约束，先去掉pi_c中空列表
            pi_c = [x for x in pi_c if x != []]
            # 防止为[]
            if not pi_c:
                pass
            else:
                derive_cons = list(itertools.product(*pi_c))
                # 将新的约束加到约束中, [['3','4'],['6','10']] => ['3','4','6','10']
                for x in derive_cons:
                    c = []
                    for h in list(x):
                        c += h
                    cons.append(c)
        else:
            pass

    return cons


# 计算mft
def MFT(cons, para_num, p_range):
    # 由于语言的机制，c1和c2总是指向同一地址即总是相等。用基本的元素复制
    m_c = []
    for x in cons:
        m_c.append(x)

    # 推导隐约束
    cons = derive(putC2paras(cons, para_num), cons, p_range)
    # 去重、去包含、去一参多值
    cons = adjust_cons(cons, p_range)
    # 如果c不变，直接返回，如果变了，进入迭代
    if m_c != cons:
        return MFT(cons, para_num, p_range)
    else:
        return cons


# 用MFT的信息计算2-6维的组合数
def MFT_combs(mft, para_num, p_range):
    mov_index = []
    for i in range(len(mft)):
        if len(mft[i]) == 1:
            for j in range(len(p_range)):
                if p_range[j][0] <= int(mft[i][0]) <= p_range[j][1]:
                    para_num[j] -= 1
                    mov_index.append(i)
                    break

    mft = [mft[i] for i in range(len(mft)) if i not in mov_index]
    raw_combs = [compute_raw_combs(2, para_num), compute_raw_combs(3, para_num), compute_raw_combs(4, para_num),
                 compute_raw_combs(5, para_num), compute_raw_combs(6, para_num)]

    # 存放每个参数涉及的参数个数
    # v_sum = sum_index(mft, p_range)

    # sum_2_way, sum_3_way, sum_4_way, sum_5_way, sum_6_way
    v_sum = [[], [], [], [], []]

    for i in range(len(mft)):
        if len(mft[i]) <= 6:
            v_sum[len(mft[i]) - 2].append(mft[i])

    # 对于约束中涉及的参数个数正好为t的，直接减去项的个数
    for i in range(len(v_sum)):
        raw_combs[i] -= len(v_sum[i])

    # 存放用于返回的组合数, 2-way的已经算出来了
    combs = [raw_combs[0]]
    # 进一步计算3-6维组合数
    for t in range(3, 7):
        flag = -1
        valid_combs = raw_combs[t - 2]
        # 3-way 只能由2-way的组成；4-way 可能由2-way组成，也能由3-way组成；依次略推
        for i in range(t - 2):
            cons = v_sum[i]
            for x in cons:
                index = []
                for v in x:
                    for j in range(len(p_range)):
                        if p_range[j][0] <= int(v) <= p_range[j][1]:
                            index.append(j)
                            break
                # 更新参数的取值
                c_para_num = [para_num[k] for k in range(len(para_num)) if k not in index]
                valid_combs += flag * compute_raw_combs(t - 2 - i, c_para_num)

            conti = 0
            flag = 1
            while conti < t - 2:
                curr_cons = []
                for x in list(itertools.product(cons, cons)):
                    # 将元组变成列表，防止自己✖自己
                    if x[0] != x[1]:
                        curr_cons.append([*x[0], *x[1]])

                # 去掉集合中的重复元素
                m_c = []
                for c in curr_cons:
                    # 保证参数不取重复的值
                    v_c = []
                    for v in c:
                        if v not in v_c:
                            v_c.append(v)

                    m_c.append(v_c)

                curr_cons = m_c
                # 存在约束中一参数取多值的约束下标
                del_index = set()
                # 对每条约束
                for c in curr_cons:
                    # 存一个参数取值表 L = [0, 0, 0,..]
                    L = [0 for i in range(len(p_range))]
                    # 对c中每个值
                    for v in c:
                        for i in range(len(p_range)):
                            if p_range[i][0] <= int(v) <= p_range[i][1]:
                                L[i] = L[i] + 1
                        # 如果某个参数取了两个值，退出循环
                        if 2 in L:
                            del_index.add(curr_cons.index(c))
                            break

                # 更新curr_cons
                curr_cons = [curr_cons[i] for i in range(len(curr_cons)) if i not in del_index]

                for x in curr_cons:
                    # 如果长度等于t，说明是一个t-way约束
                    if len(x) == t:
                        # 如果生成的约束原来就有，说明多减了两次————这里有点问题
                        if x in v_sum[t - 2]:
                            valid_combs += 2 * flag
                        # 如果约束之前没有，说明只多减了一次
                        else:
                            valid_combs += flag

                conti += 1
                cons = curr_cons
                flag *= -1

        combs.append(valid_combs)

    return combs


def sum_index(mft, p_range):
    # 存放参数个数之和为2-6的参数组合
    # 存放由2拼成的组合，可能拼成的约束组合个数为：2,3,4,5,6
    sum_2_way = [[], [], [], [], []]
    # 3,4,5,6
    sum_3_way = [[], [], [], []]
    # 4,5,6
    sum_4_way = [[], [], []]
    # 5,6
    sum_5_way = [[], []]
    # 6
    sum_6_way = [[]]
    v_sum = [sum_2_way, sum_3_way, sum_4_way, sum_5_way, sum_6_way]

    for i in range(len(mft)):
        if len(mft[i]) <= 6:
            v_sum[len(mft[i]) - 2][0].append(mft[i])

    # 2✖2能拼成的约束 如:[['2', '4']]✖[['6','8']] = [['2', '4', '6','8']],而[['2', '4']]✖[['4','8']] = ['2', '4', '8']
    cons = []
    for x in list(itertools.product(v_sum[0][0], v_sum[0][0])):
        # 将元组变成列表，防止自己✖自己
        if x[0] != x[1]:
            cons.append([*x[0], *x[1]])

    cons = adjust_cons(cons, p_range)
    for x in cons:
        sum_2_way[len(x) - 2].append(x)

    # 给参数涉及个数和为4的列表赋值 2+3
    for x in list(itertools.product(v_sum[0][0], v_sum[1][0])):
        if len(x[0]) + len(x[1]) == len(set(x[0]).union(set(x[1]))):
            v_sum[0][2].append([*x[0], *x[1]])
            v_sum[1][1].append([*x[0], *x[1]])

    # 3 + 3 给sum_3_way赋值
    for x in list(itertools.product(v_sum[1][0], v_sum[1][0])):
        if len(x[0]) + len(x[1]) == len(set(x[0]).union(set(x[1]))):
            v_sum[1][2].append([*x[0], *x[1]])

    # 2 + 4 给sum_2_way赋值
    for x in list(itertools.product(v_sum[0][0], v_sum[0][1])):
        if len(x[0]) + len(x[1]) == len(set(x[0]).union(set(x[1]))):
            v_sum[0][3].append([*x[0], *x[1]])

    # 2 + 4 给sum_2_way赋值
    for x in list(itertools.product(v_sum[0][0], v_sum[2][0])):
        if len(x[0]) + len(x[1]) == len(set(x[0]).union(set(x[1]))):
            v_sum[0][3].append([*x[0], *x[1]])

    # 2 + 4 给sum_4_way赋值
    for x in list(itertools.product(v_sum[0][0], v_sum[2][0])):
        if len(x[0]) + len(x[1]) == len(set(x[0]).union(set(x[1]))):
            v_sum[2][1].append([*x[0], *x[1]])

    return v_sum


cons_basic_info()

# MFT example
# con = [['0', '3'], ['0', '5'], ['1', '9'], ['2', '9'], ['4', '9']]
# para_num = [3,3,3,3]
# p_range = para_range(para_num)
#
# print(MFT(con, para_num, p_range))
