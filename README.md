# 灵敏度分析模块的运行说明

灵敏度分析模块的运行文件为configRun.py


使用了随机森林的变量重要性评分进行指标数据的灵敏度分析，所以使用的一些机器学习的依赖库，所以使用的python3，使用[Anaconda](<https://www.anaconda.com/download/)完全版进行安装。

使用python运行该脚本文件时其运行命名为：

```shell
python configRun.py configFile scoreFile dbname n f outImageFile
```

## 各个参数的说明

1. configFile ：指标数据的配置文件
2. scoreFile ：对应指标数据的分段的评估结果文件
3. dbname ：存储指标数据的文件，可以为excel或者.db3
4. n  : 构建随机森林时指定的树的个数
5. f ： 进行模型训练时使用的处理器的个数，-1时表示所有处理器，最大值为4
6. outImageFile ：生成的灵敏度分析结果保存输出的文件名

或者为:
```shell
python configRun.py configFile scoreFile dbname outImageFile
```

这种运行参数下，各个参数的说明和上面的一样，只是指定了默认的随机森林的树的个数和训练时使用的处理器的个数。此时，树的个数为1000，处理个数为-1，表示使用所有处理器进行训练

## note：

