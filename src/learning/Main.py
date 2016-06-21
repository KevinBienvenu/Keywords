# -*- coding: utf-8 -*-
'''
Created on 27 mai 2016

@author: Kévin Bienvenu
'''

import os
import random
import time

import unidecode

import KeywordTraining, InterfaceGraphique
from learning import GeneticTraining, GraphLearning, GeneticKeywords01, GeneticKeywords03
from main import IOFunctions, Constants, TextProcessing
import numpy as np
import pandas as pd


# # Interface Graphique
# IOFunctions.importKeywords()
# interface = InterfaceGraphique.Interface()
# interface.fenetre.mainloop()
# # Genetic Algorithm - Step 01
# temps = time.time()
#      
# geneticProcess = GeneticKeywords01.GeneticKeywords01(nbChromo = 20, nbTotalStep=10, toPrint=True)
# geneticProcess.run()
#      
# IOFunctions.printTime(temps)
# # Graph Learning
# X,Y = GraphLearning.importData()
# XTrain, YTrain, XTest, YTest = GraphLearning.testTrainSplit(X, Y)
# classifiers = GraphLearning.trainClassifiers(XTrain, YTrain)
# GraphLearning.testClassifiers(classifiers, XTest, YTest)
# # Genetic Algorithm - Step 03
# temps = time.time()
  
for i in range(10):   
    geneticProcess = GeneticKeywords03.GeneticKeywords03(nbChromo = 100, nbTotalStep=200, toPrint=True)
    geneticProcess.run()
      
# IOFunctions.printTime(temps)
# ran = xrange(18)
# array = [-1,-1,-1,1,-1,-1,1,1,-1,1,1,1,1,-1,-1,1,-1,1]
# array1 = [-1,-1,-1,-1,-1,-1,1,1,-1,1,1,1,1,1,-1,1,1,1]
# array2 = [-1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1]
# df = pd.DataFrame(data={"pos":ran,"a":array,"b":array1,"c":array2})
#
#
# ran = xrange(1000)
# posATrouver = int(random.random()*500.0+250)
# array3 = [-1 if i<posATrouver else 1 for i in ran]
# df = pd.DataFrame(data={"pos":ran,"a":array3})
# df.a = df.a.apply(lambda x : -x if random.random()>0.95 else x)
# 
#  
# def computeViaMoyennes(colonne):
#     moyennes = [np.mean(df.pos.loc[df[colonne]==-1.0].values), np.mean(df.pos.loc[df[colonne]==1.0].values)]
#     moyenne = (moyennes[0]+moyennes[1])/(2.0)
#     return moyenne
#  
# def computeViaMoyennesPonderees(colonne):
#     moyennes = [np.mean(df.pos.loc[df[colonne]==-1].values), np.mean(df.pos.loc[df[colonne]==1].values)]
#     variances = [np.var(df.pos.loc[df[colonne]==-1].values), np.var(df.pos.loc[df[colonne]==1].values)]
#     moyenne = (variances[0]*moyennes[0]+variances[1]*moyennes[1])/(variances[0]+variances[1])
#     return moyenne
#  
# def computeOptimal(colonne):
#     li = [evaluateNombre(colonne, i+0.5) for i in range(len(df)-1)]
#     with open("vaneau.txt", "w") as fichier:
#         for l in li:
#             fichier.write(str(l)+"\n")
#     v = max(li)
#     return li.index(v)+0.5
# 
# def computeOptimalReduit(colonne):
#     mini = 0.5
#     maxi = len(df)-0.5
#     while maxi-mini>1:
#         test = (mini+maxi)/2.0
#         score = evaluateNombre(colonne, test)
#         score1 = evaluateNombre(colonne, test+1)
#         if score>score1:
#             maxi = test
#         else:
#             mini = test
#     return mini
#         
#     
#  
# def evaluateNombre(colonne, nombre):
#     score = 0
#     for i in range(len(df)):
#         if np.sign(i-nombre)*df[colonne].values[i]==1:
#             score+=1
#     return int(1000.0*score/len(df))/10.0
#  
# print "réponse :",posATrouver
#  
# for colonne in ['a']:
#     temps = time.time()
#     moy = computeViaMoyennes(colonne)
#     print "moy temp:", time.time() - temps
#     
#     temps = time.time()
#     moyPond = computeViaMoyennesPonderees(colonne)
#     print "moyPond temp:", time.time() - temps
#     
#     temps = time.time()
#     optimal = computeOptimal(colonne)
#     print "optimal temp:", time.time() - temps
#     
#     temps = time.time()
#     optRed = computeOptimalReduit(colonne)
#     print "optRed temp:", time.time() - temps
#     
#     
#     print colonne, "moy", moy, evaluateNombre(colonne, moy)
#     print colonne, "moyPond", moyPond, evaluateNombre(colonne, moy)
#     print colonne, "optimal", optimal, evaluateNombre(colonne, optimal)
#     print colonne, "optimal réduit", optRed, evaluateNombre(colonne, optRed)
#     print ""






