library(stringr)
library(effsize)

# 设置工作路径
setwd('.')

# 数据的文件路径
cons = '../analysis-script/data/constrained/'
uncons = '../analysis-script/data/unconstrained/'

# 信息存储的文件路径
file_cons_save = '../cons_RQ4_infos.csv'
file_uncons_save = '../uncons_RQ4_infos.csv'

# 带约束的模型名称
name_cons = c('apache', 'bugzilla', 'gcc', 'spins', 'spinv', 'flex', 'grep', 'gzip', 'make', 'nanoxml', 'sed', 'siena', 'tcas', 'replace', 'printtokens', 'apache-small', 'mysql', 'mysql-small', 'html5-vcl', 'html5-parsing', 'slider', 'credit', 'Banking2', 'CommProtocol', 'Healthcare1', 'Healthcare2', 'Healthcare3', 'Healthcare4', 'NetworkMgmt', 'ProcessorComm1', 'ProcessorComm2', 'Services', 'Storage3', 'Storage4', 'Storage5', 'SystemMgmt', 'Telecom', 'Drupal', 'Sensor', 'AspectOptima')

# 不带约束的模型名称
name_uncons = c('tokens', 'vim', 'sort', 'totinfo', 'schedule', 'schedule2', 'find', 'findstr', 'attrib', 'fc', 'chmod', 'desigo', 'nvd', 'html5-video', 'html5-audio', 'soot-pdg', 'dsi-rax1', 'dsi-rax2', 'dsi-rax3', 'dsi-rax4', 'las', 'dmas', 'ti', 'modem', 'fgs', 'simured', 'smartphone', 'addpark', 'voice', 'contiki', 'xterm', 'sylpheed', 'Insurance')

data_disposal <- function(size, time, algorithm, strength, name){
  model = str_sub(size, 2, str_locate(size, ']')[1] - 1)
  if(!model %in% name) {
    if(length(name) == 40) {
      print(paste('带约束的模型名称中不存在',model,',其位于带约束的',algorithm,'-',strength,'-way中', sep = ''))
    } else {
      print(paste('不带约束的模型名称中不存在',model,',其位于不带约束的',algorithm,'-',strength,'-way中', sep = ''))
    }
    return('')
  }
  # 计算模型下标的二进制表示
  index = which(name == model)
  index_0b = str_sub(paste(rev(as.integer(intToBits(index))), collapse=""), -6)
  # 大小字串
  sizes = unlist(strsplit(size, '] '))[2]
  # 时间字串
  times = unlist(strsplit(time, '] '))[2]
  # 如果等于-9，表示超内存，size和time为-9，直接返回结果
  if(str_detect(sizes, '-9')) {
    m = paste(paste(strength, '-', index_0b, '-', algorithm, sep = ''), strength, model, algorithm, '-9', '-9', sep = ',')
    return(m)
  } else {
    m = paste(paste(strength, '-', index_0b, '-', algorithm, sep = ''), strength, model, algorithm, sizes, times, sep = ',')
    return(m)
  }
}

RQ4 <- function(data_path, save_path, name){
  folders = list.files(data_path)
  files = list()
  i = 1
  for (folder in folders) {
    folder = paste(data_path, folder, sep = '')
    files[[i]] = paste(folder, list.files(folder), sep = '/')
    i = i + 1
  }
  files = unlist(files)
  result = list()
  i = 1
  len = 1
  while (i <= length(files)) {
    file_size = files[i]
    file_time = files[i + 1]
    # 算法
    algorithm = strsplit(str_split(file_size, '/')[[1]][6], '-')[[1]][1]
    # 强度
    strength = strsplit(str_split(file_size, '/')[[1]][6], '-')[[1]][2]
    file1 = file(file_size, 'r')
    file2 = file(file_time, 'r')
    # 读文件
    strs_size = readLines(file1)
    strs_time = readLines(file2)
    # 关闭文件
    close(file1)
    close(file2)
    j = 1
    while (j <= length(strs_size)) {
      sizes = strs_size[j]
      times = strs_time[j]
      # 把结果放到result里面
      result[len] = data_disposal(sizes, times, algorithm, strength, name)
      len = len + 1
      j = j + 1
    }
    i = i + 2
  }
  result = c(unlist(result))
  # 对其按字符串顺序排序
  result = sort(result)
  k = 1
  # 存储最终的写信息
  Strength = list('Strength')
  Model = list('Model')
  Algorithm = list('Algorithm')
  A12_Size = list('A12_Size')
  A12_Time = list('A12_Time')
  num = 1
  # 对result中的每个元素
  while (k < length(result)) {
    # 必须得初始化，不然会下标越界
    compare_time = list(1, 2, 3, 4)
    # names(compare_time) = c('acts', 'casa', 'pict', 'fastca')
    compare_size = list(1, 2, 3, 4)
    
    model = strsplit(result[k], ',')[[1]][3]
    # print(paste(model, strsplit(result[k], ',')[[1]][4], strsplit(result[k], ',')[[1]][2]))
    # print(result[k])
    # step = 0
    # 把能比较得算法记下来
    algos = list('acts')
    # 可比较的个数
    n = 0
    while (k + n <= length(result) && model == strsplit(result[k + n], ',')[[1]][3]){
      if (str_detect(strsplit(result[k + n], ',')[[1]][5], '-9')) {
        compare_size[n + 1] = '-'
        compare_time[n + 1] = '-'
      } else {
        ss = strsplit(result[k + n], ',')[[1]][5]
        tt = strsplit(result[k + n], ',')[[1]][6]
        # size的值
        vs = strsplit(ss, ' ')[[1]]
        # 是否全是-1
        flag = FALSE
        for (s in strsplit(ss, ' ')[[1]]) {
          if (s != '-1') {
            flag = TRUE
            break()
          }
        }
        # 不全为-1
        if (flag) {
          # 去掉size中的-1，组成字串
          ss = ''
          for (ch in vs) {
            if (as.character(ch) != '-1')
              ss = paste(ss, ch)
          }
          # 去掉time中的-1，组成字串
          vt = strsplit(tt, ' ')[[1]]
          tt = ''
          for (ch in vt) {
            if (as.character(ch) != '-1') {
              tt = paste(tt, ch)
            }
          }
          # 加入比较的列表
          compare_size[n + 1] = str_sub(ss, 2)
          compare_time[n + 1] = str_sub(tt, 2)
        }
        else {
          # 加入比较的列表
          compare_size[n + 1] = '-'
          compare_time[n + 1] = '-'
        }
      }
      
      algo = strsplit(result[k + n], ',')[[1]][4]
      algos[[1]][n + 1] = algo
      n = n + 1
    }
    
    m = 1
    while (m <= n) {
      h = m + 1
      while (h <= n) {
        Strength[[1]][num] = strsplit(result[k], ',')[[1]][2]
        Model[[1]][num] = strsplit(result[k], ',')[[1]][3]
        print(Model[[1]][num])
        algo_cmp = paste(algos[[1]][m], algos[[1]][h], sep = '-')
        Algorithm[[1]][num] = algo_cmp
        # 将字符串串处理成数字串
        value_size = list(1,2)
        value_time = list(1,2)
        if (compare_size[[m]] == '-' || compare_size[[h]] == '-') {
          A12_Size[[1]][num] = '-'
          A12_Time[[1]][num] = '-'
        } else {
          # 将字符串串处理成数字串
          for (x in strsplit(compare_size[[m]], ' ')[[1]]) {
            value_size[[1]] = append(value_size[[1]], as.integer(x))
          }
          for (x in strsplit(compare_time[[m]], ' ')[[1]]) {
            value_time[[1]] = append(value_time[[1]], as.integer(x))
          }
          for (x in strsplit(compare_size[[h]], ' ')[[1]]) {
            value_size[[2]] = append(value_size[[2]], as.integer(x))
          }
          for (x in strsplit(compare_time[[h]], ' ')[[1]]) {
            value_time[[2]] = append(value_time[[2]], as.integer(x))
          }
          
          # 计算效应值
          out_size = VD.A(value_size[[1]][-1], value_size[[2]][-1])
          out_time = VD.A(value_time[[1]][-1], value_time[[2]][-1])
          
          A12_Size[[1]][num] = out_size$estimate
          A12_Time[[1]][num] = out_time$estimate
        }
        # 下标更新
        num = num + 1
        h = h + 1
      }
      m = m + 1
    }
    
    # 下标迭代
    k = k + n
  }
  result_write = data.frame(Strength, Model, Algorithm, A12_Size, A12_Time)
  names(result_write) = c('Strength', 'Model', 'Algorithm', 'A12-Size', 'A12-Time')
  write.csv(result_write, save_path, row.names = FALSE)
}

RQ4(cons, file_cons_save, name_cons)
RQ4(uncons, file_uncons_save, name_uncons)
