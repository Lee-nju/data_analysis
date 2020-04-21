library(stringr)
library(agricolae)
library(multcomp)

# 设置工作路径
# setwd('/Users/ligang/Downloads/data_analysis')

# 数据的文件路径
cons = '../analysis-script/data/constrained/'
uncons = '../analysis-script/data/unconstrained/'

# 信息存储的文件路径
file_cons_save = '../cons_RQ3_infos.csv'
file_uncons_save = '../uncons_RQ3_infos.csv'

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

RQ3 <- function(data_path, save_path, name){
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
  Group_Size = list('Group_Size')
  Group_Time = list('Group_Time')
  num = 1
  # 对result中的每个元素
  while (k < length(result)) {
    compare_time = list('algorithm', 0)
    compare_size = list('algorithm', 0)
    model = strsplit(result[k], ',')[[1]][3]
    print(paste(model, strsplit(result[k], ',')[[1]][4], strsplit(result[k], ',')[[1]][2]))
    # print(result[k])
    step = 0
    while (k + step <= length(result) && model == strsplit(result[k + step], ',')[[1]][3]){
      if (str_detect(strsplit(result[k + step], ',')[[1]][5], '-9')) {
        Strength[[1]][num] = strsplit(result[k + step], ',')[[1]][2]
        Model[[1]][num] = strsplit(result[k + step], ',')[[1]][3]
        Algorithm[[1]][num] = strsplit(result[k + step], ',')[[1]][4]
        Group_Size[[1]][num] = '-'
        Group_Time[[1]][num] = '-'
        num = num + 1
      } else {
        ss = strsplit(result[k + step], ',')[[1]][5]
        tt = strsplit(result[k + step], ',')[[1]][6]
        algo = strsplit(result[k + step], ',')[[1]][4]
        # 是否全是-1
        flag = FALSE
        for (s in strsplit(ss, ' ')[[1]]) {
          if (s != '-1') {
            flag = TRUE
            break()
          }
        }
        # 不是全-1
        if (flag) {
          # 去掉存在的-1
          for (s in strsplit(ss, ' ')[[1]]) {
            if (s != '-1') {
              compare_size[[1]] = append(compare_size[[1]], algo)
              compare_size[[2]] = append(compare_size[[2]], as.integer(s))
            }
          }
          for (t in strsplit(tt, ' ')[[1]]) {
            if (t != '-1') {
              compare_time[[1]] = append(compare_time[[1]], algo)
              compare_time[[2]] = append(compare_time[[2]], as.integer(t))
            }
          }
        # 全是-1
        } else {
          Strength[[1]][num] = strsplit(result[k + step], ',')[[1]][2]
          Model[[1]][num] = strsplit(result[k + step], ',')[[1]][3]
          Algorithm[[1]][num] = algo
          Group_Size[[1]][num] = '-'
          Group_Time[[1]][num] = '-'
          num = num + 1
        }
      }
      step = step + 1
    }
    
    algos = unique(compare_size[[1]][-1])
    n = length(algos)
    if (n <= 1) {
      if (n == 1) {
        Strength[[1]][num] = strsplit(result[k], ',')[[1]][2]
        Model[[1]][num] = strsplit(result[k], ',')[[1]][3]
        Algorithm[[1]][num] = algos
        Group_Size[[1]][num] = '-'
        Group_Time[[1]][num] = '-'
        num = num + 1
      }
    } else {
      # 不要第一个元素，构成一个frame
      compareS = data.frame('algorithm' = compare_size[[1]][-1], 'size' = compare_size[[2]][-1])
      compareT = data.frame('algorithm' = compare_time[[1]][-1], 'time' = compare_time[[2]][-1])
      # 生成aov模型
      mo_size = aov(size~algorithm, data = compareS)
      mo_time = aov(time~algorithm, data = compareT)
      # tukey hsd检验
      out_size = tryCatch({cld(glht(mo_size, linfct = mcp(algorithm = "Tukey")))},
      error = function(e) {
        '-'
      })
      
      out_time = cld(glht(mo_time, linfct = mcp(algorithm = "Tukey")))
      for (algo in algos) {
        Strength[[1]][num] = strsplit(result[k], ',')[[1]][2]
        Model[[1]][num] = strsplit(result[k], ',')[[1]][3]
        Algorithm[[1]][num] = algo
        # 将组别加入要写的数据中
        # print(out_size$mcletters$Letters[algo][[1]])
        if (out_size == '-') {
          Group_Size[[1]][num] = '-'
        } else {
          Group_Size[[1]][num] = as.character(out_size$mcletters$Letters[algo][[1]])
        }
        Group_Time[[1]][num] = as.character(out_time$mcletters$Letters[algo][[1]])
        num = num + 1
      }
    }
    # 下标迭代
    k = k + step
  }
  result_write = data.frame(Strength, Model, Algorithm, Group_Size, Group_Time)
  names(result_write) = c('Strength', 'Model', 'Algorithm', 'Group-Size', 'Group-Time')
  # row.names = FALSE 表去掉行名 1,2,3,4,..
  write.csv(result_write, save_path, row.names = FALSE)
}

RQ3(cons, file_cons_save, name_cons)
RQ3(uncons, file_uncons_save, name_uncons)
