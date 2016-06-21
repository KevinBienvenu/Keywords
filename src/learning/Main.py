# -*- coding: utf-8 -*-
'''
Created on 27 mai 2016

@author: Kévin Bienvenu
'''

import os
import time

import unidecode

import KeywordTraining, InterfaceGraphique
from learning import GeneticTraining, GraphLearning, GeneticKeywords01, GeneticKeywords03
from main import IOFunctions, Constants, TextProcessing
import pandas as pd
import numpy as np




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

# Genetic Algorithm - Step 03
temps = time.time()
       
geneticProcess = GeneticKeywords03.GeneticKeywords03(nbChromo = 20, nbTotalStep=10, toPrint=True)
geneticProcess.run()
       
IOFunctions.printTime(temps)








