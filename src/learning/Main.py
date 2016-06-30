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
from learning import  GeneticKeywords03, GraphLearning
from main import IOFunctions, Constants, TextProcessing
import numpy as np
import pandas as pd
from learning.GraphLearning import Step3Classifier


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
# # GraphLearning.preprocessClassifiers(GraphLearning.classifiers, nbPrise=1, toSave=True)
# cla, nam = GraphLearning.loadClassifiers()
# GraphLearning.evaluateClassifiers(cla, nam)


# # Genetic Algorithm - Step 03
# temps = time.time()
#        
# for i in range(1):   
#     geneticProcess = GeneticKeywords03.GeneticKeywords03(nbChromo = 10, nbTotalStep=1, toPrint=True)
#     geneticProcess.run()
#            
# IOFunctions.printTime(temps)


# # Main Pipeline
# des = [
#        "Production cinématograhique et audiovisuelle",
# #        "Enseignement de la conduite de véhicules terrestres et de sécurité routière, école de conduite et pilotage de tous engins flottants ou aériens, formation de tous moniteurs.",
# #        "Gestion, propriété, administration et disposition des biens qui pourront devenir la propriété de la société par voie d'acquisition, d'échange, d'apport, de construction ou autrement.",
# #        "Laboratoire d'analyses de biologie médicale",
# #        "Restaurant rapide et traditionnel, à emporter, sur place et en livraison"
#        ]
# codeNaF = [
#            "",
# #            "",
# #            "",
# #            "",
# #            ""
#            ]
# csvdesc = pd.DataFrame(data={"codeNaf":codeNaF, "description":des})
# print csvdesc
#           
# tab = KeywordTraining.pipeline(csvdesc, 20, True)
# for t in tab:
#     print t
