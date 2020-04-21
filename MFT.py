import itertools

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
                # 如果后一列表 add 前一列表后，集合的个数没有增加，说明前一列表包含后一列表
                leng = len(x)
                s = set(x)
                s.update(xt)
                if leng == len(s):
                    del_index.add(cons.index(x))
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


# MFT example1
# cons = [['0', '3'], ['0', '5'], ['1', '9'], ['2', '9'], ['4', '9']]
# para_num = [3,3,3,3]
# p_range = para_range(para_num)

# MFT apache model
# para = '3 4 2 3 3 3 3 2 2 2 2 2 2 2 3 2 2 2 4 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 4 2 2 2 4 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 5 2 2 2 2 3 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 6 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 3 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2'
# para_num = para.split(' ')
# para_num = [int(x) for x in para_num]
#
# cons = [['80', '102', '104', '106', '353'], ['102', '104', '355', '357'], ['38', '359'], ['361', '363'], ['174', '176'], ['200', '216', '365'], ['80', '102', '104', '288']]
# p_range = para_range(para_num)

# AspectOptima 模型
cons = [['0'], ['21', '26'], ['23', '28'], ['29', '32'], ['4'], ['6'], ['23', '32'], ['8'], ['18'], ['24'], ['12', '17'], ['14', '11'], ['34'], ['36'], ['26', '28'], ['11', '26'], ['10', '15'], ['30', '14'], ['16', '13'], ['11', '20'], ['20', '12'], ['26', '32'], ['15', '26'], ['15', '20'], ['17', '30'], ['30', '10'], ['28', '12'], ['20', '16'], ['12', '26'], ['28', '16'], ['13', '30'], ['12', '32'], ['28', '30']]
para = '2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2'
para_num = para.split(' ')
para_num = [int(x) for x in para_num]
p_range = para_range(para_num)
print(MFT(cons, para_num, p_range))