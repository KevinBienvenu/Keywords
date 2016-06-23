# -*- coding: utf-8 -*-
'''
Created on 27 mai 2016

@author: Kévin Bienvenu
'''

from operator import div
import os
import random
import time

import unidecode

import KeywordTraining, InterfaceGraphique
from learning import  GeneticKeywords03
from main import IOFunctions, Constants, TextProcessing
import numpy as np
import pandas as pd


# Interface Graphique
IOFunctions.importKeywords()
interface = InterfaceGraphique.Interface()
interface.fenetre.mainloop()


# # Genetic Algorithm - Step 01
# temps = time.time()
#      
# geneticProcess = GeneticKeywords01.GeneticKeywords01(nbChromo = 20, nbTotalStep=10, toPrint=True)
# geneticProcess.run()
#      
# IOFunctions.printTime(temps)

# # Graph Learning
# GraphLearning.evaluateClassifiers(GraphLearning.classifiers)


# # Genetic Algorithm - Step 03
# temps = time.time()
#       
# for i in range(10):   
#     geneticProcess = GeneticKeywords03.GeneticKeywords03(nbChromo = 100, nbTotalStep=100, toPrint=True)
#     geneticProcess.run()
#           
# IOFunctions.printTime(temps)



