import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math


class MED(object):
    #初始化
    def __init__(self):
        self.vecotr_length = 0 
        self.center_coordinates = {} #计算向量之和并最后求均值
        self.point_number = {} #统计向量个数
        #self.score = []

    #向量距离
    def __distance(self, x, y):
        #print(x)
        #print(y)
        tot = 0
        for i in range(0,self.vecotr_length):
            tot += (x[i]-y[i])*(x[i]-y[i])
        return math.sqrt(tot)

    #分割数据集
    def split(self, data, rate):
        #生成训练集
        Iris_linear_train = data.iloc[0:int(len(data)*rate)]
        #print(Iris_linear_train)
        X_train = Iris_linear_train[[0, 1, 2, 3]]
        Y_train = Iris_linear_train['target']
        #print(X_train)
        #print(Y_train)

        #生成测试集
        Iris_linear_test = data.iloc[int(len(data)*rate):len(data)].reset_index(drop=True)
        #print(Iris_linear_test)
        X_test = Iris_linear_test[[0, 1, 2, 3]]
        Y_test = Iris_linear_test['target']
        #print(X_test)
        #print(Y_test)
        return X_train , Y_train , X_test , Y_test

    #训练
    def fit(self, X_train, Y_train):
        self.__init__()
        self.vecotr_length = len(X_train.columns)
        #计算向量之和
        for i in X_train.index:
            x = X_train.iloc[i]
            y = Y_train.iloc[i]
            if y not in self.center_coordinates.keys():
                self.center_coordinates[y]=x
                self.point_number[y]=0
            else:
                self.center_coordinates[y]=self.center_coordinates[y].add(x)
                self.point_number[y]+=1
        #计算均值
        for i in self.center_coordinates:
            self.center_coordinates[i]=self.center_coordinates[i]/self.point_number[i]
    
    #打分
    def __score(self, X_test):
        Y_score = []
        for i in X_test.index:
            x = X_test.iloc[i]
            total = 0
            for j in self.center_coordinates:
                total += 1/self.__distance(x, self.center_coordinates[j])
            score = 1/self.__distance(x, self.center_coordinates[1]) / total
            Y_score.append(score)
        return Y_score

    def __TFNP(self, Y_scores, Y_test, thresholds):
        TP , FP , TN , FN = 0 , 0 , 0 , 0
        for i in range(0,len(Y_scores)):
            if Y_scores[i] > thresholds:
                if  Y_test[i] == 1:
                    TP += 1
                else:
                    FP += 1
            elif Y_scores[i] < thresholds:
                if  Y_test[i] == 1:
                    FN += 1
                else:
                    TN += 1
        return TP , FP , TN , FN

    #可视化评估
    def __evaluate(self, X_test, Y_test):
        Y_score = self.__score(X_test)

        #数据集预处理
        Iris_df = pd.DataFrame(X_test)
        Iris_df.insert(0,'target',Y_test)
        #按目标分类
        Iris_div = []
        for i in range(0,2):
            Iris_div.append(Iris_df[Iris_df['target']==i])
        
        #颜色表
        colmaps = ['green', 'blue']
        fig_id = 0
        for i in range(0,4):
            for j in range(i+1,4):
                fig_id += 1
                plt.subplot(3,3,fig_id)
                for k in range(0,2):
                    #挑选出ij两个维度作为x轴和y轴，k作为目标种类
                    x_axis = Iris_div[k][i]
                    y_axis = Iris_div[k][j]
                    #画ij子图的第k种颜色
                    plt.scatter(x_axis, y_axis, c=colmaps[k], label=k)
                    #画类均值中心
                    plt.plot(self.center_coordinates[k][i], self.center_coordinates[k][j], marker='*', c='red')
                #画决策边界
                #连线向量
                vector_linear_x = self.center_coordinates[0][i]-self.center_coordinates[1][i]
                vector_linear_y = self.center_coordinates[0][j]-self.center_coordinates[1][j]
                #垂线向量
                vector_vertical_x = vector_linear_y
                vector_vertical_y = -vector_linear_x
                #中点坐标
                mid_x = (self.center_coordinates[0][i]+self.center_coordinates[1][i])/2
                mid_y = (self.center_coordinates[0][j]+self.center_coordinates[1][j])/2
                #画连线
                # line_x , line_y = [mid_x] , [mid_y]
                # line_x.append(mid_x + vector_linear_x)
                # line_y.append(mid_y + vector_linear_y)
                # line_x.append(mid_x - vector_linear_x)
                # line_y.append(mid_y - vector_linear_y)
                # plt.plot(line_x , line_y)
                #画垂直平分线
                line_x , line_y = [mid_x] , [mid_y]
                line_x.append(mid_x + vector_vertical_x)
                line_y.append(mid_y + vector_vertical_y)
                line_x.append(mid_x - vector_vertical_x)
                line_y.append(mid_y - vector_vertical_y)
                plt.plot(line_x , line_y)
                #添加图例
                plt.legend()

        # 曲线度量
        precision = []
        recall = []
        FPR = []
        area_sum = 0
        area = []
        for thresholds in range(0,1000):
            TP , FP , TN , FN = self.__TFNP(Y_score, Y_test, thresholds/1000)
            if TP + FP != 0 :
                precision.append(TP / (TP + FP))
            else:
                precision.append(1)
            recall.append(TP / (TP + FN))
            FPR.append(FP / (FP + TN))
            area_sum += FP / (FP + TN)
            area.append(area_sum)
        # PR
        plt.subplot(3,3,7)
        plt.title('PR Curve')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.plot(recall,precision)
        # ROC
        plt.subplot(3,3,8)
        plt.title('ROC Curve')
        plt.xlabel('FPR')
        plt.ylabel('Recall')
        plt.plot(FPR,recall)
        # AUC
        plt.subplot(3,3,9)
        plt.title('AUC Curve')
        plt.xlabel('area')
        plt.ylabel('Recall')
        plt.plot(area,recall)

        #保存并显示
        plt.show()
    
    #留出法
    def Holdout(self, data, rate, n):
        accuracy = []
        precision = []
        recall = []
        specificity = []
        f1score = []

        for i in range(0,n):
            X_train  , Y_train, X_test , Y_test = self.split(data, rate)
            self.fit(X_train, Y_train)
            Y_score = self.__score(X_test)
            TP , FP , TN , FN = self.__TFNP(Y_score, Y_test, 0.5)
            accuracy.append((TP + TN) / (TP + TN + FP + FN))
            precision.append(TP / (TP + FP))
            recall.append(TP / (TP + FN))
            specificity.append(TN / (TN + FP))
            f1score.append(2*recall[i]*precision[i]/(recall[i]+precision[i]))

        Accuracy = np.mean(accuracy)
        Precision = np.mean(precision)
        Recall = np.mean(recall)
        Specificity = np.mean(specificity)
        F1score = np.mean(f1score)

        print('Accuracy: ', Accuracy)
        print('Precision: ', Precision)
        print('Recall: ', Recall)
        print('Specificity: ', Specificity)
        print('F1score: ', F1score)

        #利用残留数据进行曲线度量
        self.__evaluate(X_test , Y_test)

