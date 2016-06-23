# -*- coding: utf-8 -*-
'''
Created on 20 juin 2016

@author: Kévin Bienvenu
'''


from operator import add
import os
import random

from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sknn.mlp import Classifier, Layer

from main import Constants
import numpy as np
import pandas as pd

method = 1


# # panel of classifiers
# names = ["Nearest Neighbors","Decision Tree", 
#          "Random Forest", "AdaBoost",
#          "Naive Bayes", "QDA"]
# classifiers = [
#     KNeighborsClassifier(3),
#     DecisionTreeClassifier(max_depth=5),
#     RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
#     AdaBoostClassifier(),
#     GaussianNB(),
#     QuadraticDiscriminantAnalysis()]

# # testing rbf
# # gamma = [0.001,0.01,0.02,0.05,0.1,0.2,0.5,0.7,1,2,3,5,10,20,50,100,200,500,1000,2000]
# gamma = [50,75,100,150,200,300,500,1000]
# 
# names = [str(g) for g in gamma]
# classifiers = [SVC(kernel="rbf",gamma=g) for g in gamma]

# # testing sigmoid
# gamma = [0.01, 0.1, 0.5, 1.0, 10.0]
# coef0 = [-5.0, -1.0, 0.0, 1.0, 2.0]
# params = []
# for g in gamma:
#     params += [(g, c) for c in coef0]
# names = [str(param[0]).replace(".",",")+"_"+str(param[1]).replace(".",",") for param in params]    
# classifiers = [SVC(kernel="sigmoid", gamma=param[0], coef0=param[1]) for param in params]

# # testing neural networks
# learning_rates = [0.01, 0.02, 0.05, 0.1, 0.5]
# classifiers = [ Classifier(layers=[Layer("Rectifier", units=100),
#                                    Layer("Sigmoid", units = 100),
#                                    Layer("Softmax")],
#                            learning_rate=learning,
#                            n_iter=20)
#                for learning in learning_rates]
# 
# names = [str(learning) for learning in learning_rates]




def importData():
    os.chdir(Constants.pathCodeNAF+"/../")
    df = pd.DataFrame.from_csv("trainingStep3.csv", sep=";")
    # normalisation step
    columns = list(df.columns.values)
    columns.remove("Y")
    df.Y = df.Y.apply(lambda y : 1 if y else 0)
    df[columns] = df[columns].apply(lambda s: s/max(s))
    return df
    
    
def testTrainSplit(df):
    nbYPos = len(df.loc[df.Y==1])
    if method == 0:
        frac = 0.8
        index = list(df.loc[df.Y==1].index.values) + list(random.sample(df.loc[df.Y==0].index.values, nbYPos))
        k = int(len(index)*frac)
        indexTrain = random.sample(index, k)
        indexTest = list(set(index)-set(indexTrain))
    elif method == 1:
        frac = 0.5
        k = int(nbYPos*frac)
        indexTrain = list(random.sample(df.loc[df.Y==1].index.values,k)) + list(random.sample(df.loc[df.Y==0].index.values, k))
        indexTest = df.index
    columns = list(df.columns.values)
    columns.remove("Y")
    XTrain = df.loc[indexTrain][columns].values
    YTrain = df.loc[indexTrain].Y.values
    XTest = df.loc[indexTest][columns].values
    YTest = df.loc[indexTest].Y.values
    return XTrain, YTrain, XTest, YTest
    
def trainClassifiers(XTrain, YTrain):
    for classifier in classifiers:
        classifier.fit(XTrain, YTrain)
    return classifiers

def testClassifiers(classifiers, XTest, YTest, toPrint = True):
    scores = []
    for classifier in classifiers:
        result = classifier.predict(XTest)
        for i in range(len(result)):
            result[i] = result[i]-YTest[i]
        score = (np.sum([[1-abs(a),-min(a,0),max(a,0)] for a in result], axis = 0))
        scores.append([int(100.0*(s)/len(result)) for s in score])
    if toPrint:
        printClassifiers(classifiers, scores, names)
    return scores

def printClassifiers(classifiers, scores, names):
    print "                     prec fNeg fPos"
    for i in range(len(scores)):#     print "data split :"
#     print "   train -",len(XTrain),"lignes"
#     print "   test -",len(XTest),"lignes"
        print names[i], 
        st = ""
        for s in scores[i]:
            st += "_"+str(s).replace(".",",")
        print st
        
def evaluateClassifiers(classifiers, nbPrise = 5):
    scores = [[0,0,0] for _ in classifiers]
    for _ in range(nbPrise):
        df = importData()
        XTrain, YTrain, XTest, YTest = testTrainSplit(df)
        classifiers = trainClassifiers(XTrain, YTrain)
        scores = [map(add,tupleScore[0],tupleScore[1]) for tupleScore in zip(scores,testClassifiers(classifiers, XTest, YTest, False))]
    scores = [ [s/nbPrise for s in score] for score in scores]
    printClassifiers(classifiers, scores, names)

    
    
    
    
    
    
    