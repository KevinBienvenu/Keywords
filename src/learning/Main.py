# -*- coding: utf-8 -*-
'''
Created on 27 mai 2016

@author: Kévin Bienvenu
'''

import os

import unidecode

import KeywordTraining, InterfaceGraphique, GeneticTraining
from main import TextProcessing, IOFunctions, Constants
import time



# IOFunctions.importKeywords()

# interface = InterfaceGraphique.Interface()
# interface.fenetre.mainloop()

temps = time.time()

training = GeneticTraining.TrainingSet("0111Z", nbChromo = 2000, nbTotalStep=1000)
training.run()

IOFunctions.printTime(temps)



# desc = "Activités agricoles culture de céréales légumineuses graines oléagineuses"
# codeNAF = "0111Z"
#  
# tokens = TextProcessing.nltkprocess(desc)
#  
# print "[",
# for token in tokens:
#     print token,",",
# print "]"
#  
# 
# keyword = "gilles de bouard"
# 
# keywordSet = {keyword : TextProcessing.nltkprocess(keyword)}
# 
# stemmedDesc = TextProcessing.nltkprocess(desc,keepComa=True)
# print TextProcessing.getProbKeywordInDescription(keyword, keywordSet[keyword], stemmedDesc )
#         