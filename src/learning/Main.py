# -*- coding: utf-8 -*-
'''
Created on 27 mai 2016

@author: Kévin Bienvenu
'''

import os
import time

import unidecode

import KeywordTraining, InterfaceGraphique
from learning import GeneticTraining
from main import IOFunctions, Constants, TextProcessing


IOFunctions.importKeywords()
interface = InterfaceGraphique.Interface()
interface.fenetre.mainloop()

# temps = time.time()
#     
# training = GeneticTraining.TrainingSet(nbChromo = 20, nbTotalStep=10, toPrint=False)
# training.run()
#     
# IOFunctions.printTime(temps)



# desc = "Activités agricoles culture de céréales légumineuses graines oléagineuses"
# codeNAF = "0111Z"
#   
# tokens = 1_TextProcessing.nltkprocess(desc)
#   
# print "[",
# for token in tokens:
#     print token,",",
# print "]"
#   
#  
# keyword = "fruits"
#  
# keywordSet = {keyword : 1_TextProcessing.nltkprocess(keyword)}
# parameters = [{'A':1.0/200,'B':1.0,
#                'C':1.0/5.0,'D':1.0,'E':1.0,
#                'F':1.0,'G':0.5,'H':0.8,
#                 'I0':2.0,
#                 'I1':2.0,
#                 'I-1':2.0,
#                 'J':1.0,
#                 'N':0.5}]
# stemmedDesc = 1_TextProcessing.nltkprocess(desc,keepComa=True)
# print 1_TextProcessing.getProbKeywordInDescription(keyword, keywordSet[keyword], stemmedDesc, parameters)
#         