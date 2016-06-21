# -*- coding: utf-8 -*-
'''
Created on 20 juin 2016

@author: Kévin Bienvenu
'''


import os
import pandas as pd
import numpy as np
import random

from matplotlib.colors import ListedColormap
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


from main import Constants


h = .02  # step size in the mesh

names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", 
         "Decision Tree", "Random Forest", "AdaBoost",
         "Naive Bayes", "QDA"]

classifiers = [
    KNeighborsClassifier(3),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()]

def importData():
    os.chdir(Constants.pathCodeNAF+"/../")
    df = pd.DataFrame.from_csv("trainingStep3.csv", sep=";")
    nbYPos = len(df.loc[df.Y==1])
    if nbYPos<len(df)/2:
        indexToKeep = list(df.loc[df.Y==1].index.values) + list(random.sample(df.loc[df.Y==0].index.values, nbYPos))
    df = df.loc[indexToKeep]
    X = np.array(df[['nbVoisins','nbVoisins1','propSumVoisins1','propVoisins1','size','sumVoisins','sumVoisins1']].values)
    Y = np.array(df.Y.apply(lambda y : 1 if y else 0).values)
    print "imported Data"
    return X,Y
    
    
def testTrainSplit(X, Y, frac=0.8):
    k = int(len(X)*frac)
    index = random.sample(xrange(len(X)), k)
    indexComp = list(set(range(len(X)))-set(index))
    XTrain = X[index]
    YTrain = Y[index]
    XTest = X[indexComp]
    YTest = Y[indexComp]
    print "data split :"
    print "   train -",len(XTrain),"lignes"
    print "   test -",len(XTest),"lignes"
    return XTrain, YTrain, XTest, YTest
    
def trainClassifiers(XTrain, YTrain):
    for classifier in classifiers:
        classifier.fit(XTrain, YTrain)
    return classifiers

def testClassifiers(classifiers, XTest, YTest):
    scores = []
    for classifier in classifiers:
        result = classifier.predict(XTest)
        for i in range(len(result)):
            result[i] = result[i]-YTest[i]
        score = (np.sum([[1-abs(a),-min(a,0),max(a,0)] for a in result], axis = 0))
        scores.append([int(100.0*(s)/len(result)) for s in score])
    print "                     prec fNeg fPos"
    for i in range(len(scores)):
        print names[i], 
        for j in range(20-len(names[i])):
            print "",
        print scores[i]

        
    
    

    
    
    
    
    
    
    