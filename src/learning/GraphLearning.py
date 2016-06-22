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

from main import Constants
import numpy as np
import pandas as pd



names = ["Nearest Neighbors","Decision Tree", 
         "Random Forest", "AdaBoost",
         "Naive Bayes", "QDA"]

# panel of classifiers
classifiers = [
    KNeighborsClassifier(3),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()]

# testing rbf
gamma = [0.1,0.2,0.5,0.7,1.0,2.0,3.0,5.0,10.0]
names = ["rbf_gamma="+str(g) for g in gamma]
classifiers = [SVC(kernel="rbf",gamma=g) for g in gamma]

def importData():
    os.chdir(Constants.pathCodeNAF+"/../")
    df = pd.DataFrame.from_csv("trainingStep3.csv", sep=";")
    nbYPos = len(df.loc[df.Y==1])
    if nbYPos<len(df)/2:
        indexToKeep = list(df.loc[df.Y==1].index.values) + list(random.sample(df.loc[df.Y==0].index.values, nbYPos))
    df = df.loc[indexToKeep]
    # normalisation step
    columns = list(df.columns.values)
    columns.remove("Y")
    df[columns] = df[columns].apply(lambda s: s/max(s))
    X = np.array(df[['nbVoisins','nbVoisins1','propSumVoisins1','propVoisins1','size','sumVoisins','sumVoisins1']].values)
    Y = np.array(df.Y.apply(lambda y : 1 if y else 0).values)
#     print "imported Data"
    return X,Y
    
    
def testTrainSplit(X, Y, frac=0.8):
    k = int(len(X)*frac)
    index = random.sample(xrange(len(X)), k)
    indexComp = list(set(range(len(X)))-set(index))
    XTrain = X[index]
    YTrain = Y[index]
    XTest = X[indexComp]
    YTest = Y[indexComp]

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
        for _ in range(20-len(names[i])):
            print "",
        print scores[i]
        
def evaluateClassifiers(classifiers, nbPrise = 100):
    scores = [[0,0,0] for _ in classifiers]
    for _ in range(nbPrise):
        X,Y = importData()
        XTrain, YTrain, XTest, YTest = testTrainSplit(X, Y)
        classifiers = trainClassifiers(XTrain, YTrain)
        scores = [map(add,tupleScore[0],tupleScore[1]) for tupleScore in zip(scores,testClassifiers(classifiers, XTest, YTest, False))]
    scores = [ [s/nbPrise for s in score] for score in scores]
    printClassifiers(classifiers, scores, names)

    
    
    
    
    
    
    