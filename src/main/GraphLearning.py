# -*- coding: utf-8 -*-
'''
Created on 20 juin 2016

@author: Kévin Bienvenu
'''


from operator import add
import os
import random

from numpy import divide
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
import numpy as np
import pandas as pd

import GeneticKeywords03


method = 1

classifiers = [
               SVR(kernel="rbf",gamma=200),
               RandomForestRegressor(n_estimators=15),
               GeneticKeywords03.GeneticClassifier(nbChromo=100, nbTotalStep=100)
               ]
names = ["SVC","RandomForest","Genetic"]

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
    os.chdir(GeneticKeywords03.GeneticTraining.Constants.pathCodeNAF+"/../")
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
    columns.sort()
    XTrain = df.loc[indexTrain][columns].values
    YTrain = df.loc[indexTrain].Y.values
    XTest = df.loc[indexTest][columns].values
    YTest = df.loc[indexTest].Y.values
    return XTrain, YTrain, XTest, YTest
    
def trainClassifiers(XTrain, YTrain, classifiers, names=names, toPrint=False):
    i=0
    for classifier in classifiers:
        print "training", names[i],
        try:
            classifier.fit(XTrain, YTrain, toPrint=toPrint)
        except:
            classifier.fit(XTrain, YTrain)
        i+=1
        print "...done"
    return classifiers

def testClassifiers(classifiers, names, XTest, YTest, toPrint = True):
    scores = []
    j=0
    for classifier in classifiers:
        print "testing", names[j],
        j+=1
        result = classifier.predict(XTest)
        for i in range(len(result)):
            result[i] = int(result[i]+0.5)-YTest[i]
        score = (np.sum([[1-abs(a),-min(a,0),max(a,0)] for a in result], axis = 0))
        scores.append([int(100.0*(s)/len(result)) for s in score])
        scores[-1].append(100*np.sum([1 if a[0]==0 and a[1]==1 else 0 for a in zip(result, YTest)])/sum(YTest))
        print "done"
    return scores

def printClassifiers(classifiers, scores, names):
    print "                     prec fNeg fPos %Pos"
    for i in range(len(scores)):#     print "data split :"
#     print "   train -",len(XTrain),"lignes"
#     print "   test -",len(XTest),"lignes"
        print names[i], 
        print " "*(20-len(names[i])),
        for s in scores[i]:
            print str(s).replace(".",",")," ",
        
def preprocessClassifiers(classifiers, names, nbPrise = 1, toSave = False):
    print " === Evaluating classifiers"
    print ""
#     evaluating learning classifiers
    scores = [[0,0,0] for _ in classifiers]
    for _ in range(nbPrise):
        df = importData()
        XTrain, YTrain, XTest, YTest = testTrainSplit(df)
        classifiers = trainClassifiers(XTrain, YTrain, classifiers, names, toPrint=True)
        scores = [map(add,tupleScore[0],tupleScore[1]) for tupleScore in zip(scores,testClassifiers(classifiers, names, XTest, YTest, False))]
    scores = [ [s/nbPrise for s in score] for score in scores]
    if toSave:
        saveClassifiers(classifiers,names)
    printClassifiers(classifiers, scores, names)

def evaluateClassifiers(classifiers=[], names=[]):
    if len(classifiers)==0:
        classifiers,names = loadClassifiers()
    _,_,XTest,YTest = testTrainSplit(importData())
    scores = testClassifiers(classifiers, names, XTest, YTest, True)
    printClassifiers(classifiers, scores, names)
    

''' function about saving and importing classifiers '''

def saveClassifiers(classifiers, names, location=GeneticKeywords03.GeneticTraining.Constants.pathClassifiers):
    # first we delete old files (except gentic files)
    os.chdir(location)
    for filename in os.listdir("."):
        os.remove(filename)
    i=0
    for classifier in classifiers:
        if names[i]!="Genetic":
            joblib.dump(classifier, str(names[i]).replace(" ","_")+".pkl")
        else:
            classifier.save("Genetic.gen")
        i+=1
    
def loadClassifiers(location=GeneticKeywords03.GeneticTraining.Constants.pathClassifiers):
    os.chdir(location)
    classifiers = []
    names = []
    for filename in os.listdir("."):
        if filename[-4:]==".pkl":
            classifiers.append(joblib.load(filename))
            names.append(str(filename[:-3]).replace("_"," "))
        if filename[-4:]==".gen":
            classifiers.append(GeneticKeywords03.GeneticClassifier(filename = filename))
            names.append(str(filename[:-3]).replace("_"," "))
    return classifiers, names   
  
        
class Step3Classifier():
    
    def __init__(self):
        self.classifiers, self.names = loadClassifiers()
   
    def predict(self, X):
        if len(X)==0:
            return []
        normalizer = [xi if xi>0 else 1 for xi in np.max(np.array(X),axis=0)]
        
        X1 = [map(divide, xi, normalizer) for xi in X]
        try:
            result = [ [min(1,max(0,x)) for x in classifier.predict(X1)] for classifier in self.classifiers]
        except:
            print X
            print X1
            print normalizer
            result = [[0,0,0] for _ in X]
        return [1 if res[0]==1 else 0 if res[2]==0 else sum(res)/3.0 for res in zip(*result)]

  


    