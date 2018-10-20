import configHelper
import logging
import sqlite3

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score



class configReader():
    '''
    读入指标数据的类，初始化需要包含数据库名字，以及配置文件的名字
    '''
    def __init__(self, dbname, configFileName, scoreFileName):
        self.dbname =  dbname
        self.configIndex = configHelper.jsonread(configFileName)
        
        if self.configIndex == None:
            return None
        self.scoreData = configHelper.csvread(scoreFileName)
        if self.scoreData == None:
            return None
        self.indexParameter = []#体系指标参数名称
        self.indexSocre = scoreFileName.replace(".csv",'下')#体系指标的评分的列的名称
        self.excelSheet = {}
        self.X = []#np.array([]) #体系指标的具体数据
        self.y = []#np.array([]) #体系指标的具体评分值

    def _praseConfigFile(self):
        '''
        解析配置文件，读入相应的需要分析的指标名称
        '''    
        for _, index in zip(self.configIndex.keys(), self.configIndex.values()):
            indexName = index["Index"]
            self.indexParameter.extend(indexName)
    

    def _readHelperSql(self, st, et,c):

        #根据单行的分段的时间范围，构建sql命令查询读取其相应的数据指标
        res = []
        for table, index in zip(self.configIndex.keys(), self.configIndex.values()):
            indexName = index["Index"]
            #self.indexParameter.extend(indexName)
            sql = "SELECT " + ' , '.join(indexName) + ' FROM ' + table + " WHERE Timestamp > %f AND Timestamp < %f" % (st-1, et+1)
            c.execute(sql)
            data = np.mean(np.array(c.fetchall()),axis=0)
            res.extend(data)
        return res

    def _readHelperExcel(self, st, et):
    
        #根据单行的分段的时间范围，读取相应的excel里面的数据
        res = []
        for table, index in zip(self.configIndex.keys(), self.configIndex.values()):
            indexName = index["Index"]
            #self.indexParameter.extend(indexName)
            dataMean = np.mean(self.excelSheet[table].loc[st:et])
            #print(indexName)
            #print(dataMean)

            for idn in indexName:
                res.append(dataMean[idn])
        
        return res


    def _excelReadHelper(self):
        #读出所有的excel的sheet表的数据
        for sheet in self.configIndex:
            dt = pd.read_excel(self.dbname, sheetname=sheet)
            self.excelSheet[sheet] = dt

    def generateExcelData(self):
        '''
        根据指标文件的配置，读取相应的excel，获取到相应的指标和评估的数据
        '''
        self._praseConfigFile()
        self._excelReadHelper()#读入excel表

        i = 0
        for row in self.scoreData:
            #根据每一行的分段评分值，去读取出该分段对应的所有指标数据
            if len(row) != 4 or i == 0:
                i =+ 1
                continue
            
            st = int(row[1])
            et = int(row[2])
            sc = float(row[3])
            self.y.append(sc)
            self.X.append(self._readHelperExcel(st,et))



    def generateSQLcommand(self):
        '''
        根据指标的配置名称，执行相应的sql命令查询，获取到相应的指标和评估的数据
        '''

        self._praseConfigFile()

        #初始化连接数据库
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()

        for row in self.scoreData:
            #根据每一行的分段评分值，去读取出该分段对应的所有指标数据
            if len(row) != 4:
                continue
            st = int(row[1])
            et = int(row[2])
            sc = float(row[3])
            self.y.append(sc)
            self.X.append(self._readHelperSql(st,et,c))
        
        c.close()
        
    
    def randomForestModel(self, n, f, filename):
        '''
        基于读到的数据进行随机森林的建模
        n: 随机森林的数的个数
        f: 并行运行的处理器的个数（-1：所有处理器，1：表示一个处理器， 2：表示两个处理器，以此类推，f最大值4）
        '''
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.unicode_minus'] = False  

        #X_train, X_test, y_train, y_test = train_test_split(np.array(self.X), np.array(self.y), test_size=0,)
        X_train,  y_train =  np.array(self.X),np.array(self.y)
        rfr = RandomForestRegressor(n_estimators=n, n_jobs=f)
        rfr.fit(X_train, y_train)
        print('the random Forest train R^2 score is %.2f' % r2_score(y_train, rfr.predict(X_train)))
        #logging.info('the random Forest test R^2 score is %.2f' % r2_score(y_test, rfr.predict(X_test)))

        IndexImportance = pd.Series(data=rfr.feature_importances_, index=self.indexParameter).sort_values()
        #IndexImportance.sort_values()
        plt.figure(figsize=(12,9))
        mpl.rcParams['ytick.direction'] = 'in' 
        mpl.rcParams['xtick.direction'] = 'in' 
        #IndexImportance.plot(kind='bar')
        _ = sns.barplot( x=IndexImportance.index,y=IndexImportance,ci=0)#color="#34495e"
        for xi in range(len(self.indexParameter)):
            plt.text(xi, IndexImportance[xi]+0.005, '%.6f' % IndexImportance[xi], 
                    ha='center', va= 'bottom',fontsize=16)
        plt.ylim([0,max(IndexImportance) + 0.1])
        plt.xlabel('指标体系参数',fontsize=20)
        plt.ylabel('指标贡献率得分',fontsize=20)
        plt.title(self.indexSocre +'指标体系贡献率分析')
        #plt.show()
        plt.savefig(+filename +'.png',bbox_inches = 'tight',dpi=256)


    def run(self,n,f,filename):

        if self.dbname.endswith('.db3'):
            #以读sqlite3数据库的方式运行
            self.generateSQLcommand()
            self.randomForestModel(n,f,filename)
        
        if self.dbname.endswith('.xlsx'):
            #以读excel数据的方式运行
            self.generateExcelData()
            self.randomForestModel(n,f,filename)


