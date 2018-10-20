import configReader
import sys

if __name__ == "__main__":
    configFile = sys.argv[1] # 指标数据的配置文件
    scoreFile = sys.argv[2] # 分段数据的评估结果
    dbname  = sys.argv[3] # 存储指标数据的文件，为.db3或者.xlsx文件
    num_Tree = 1000
    num_pro = -1
    if len(sys.argv) == 7:
        num_Tree = int(sys.argv[4]) # 模型训练指定随机森林树的个数
        num_pro = int(sys.argv[5]) # 模型训练指定使用的处理器的个数，-1表示所有处理器
    outfilename = sys.argv[-1]
    
    RfSensitiveModel = configReader.configReader(dbname, configFile,scoreFile)
    RfSensitiveModel.run(num_Tree, num_pro, outfilename)
