# -*- coding: utf-8 -*-
'''
Created on 27 mai 2016

@author: Kévin Bienvenu
'''

import os

import unidecode

import KeywordTraining, InterfaceGraphique, GeneticTraining
from main import TextProcessing, IOFunctions, Constants



# IOFunctions.importKeywords()

# interface = InterfaceGraphique.Interface()
# interface.fenetre.mainloop()

training = GeneticTraining.TrainingSet(nbChromo = 500, nbTotalStep=100)
training.run()



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
# keyword = "fruits"
#  
# keywordSet = {keyword : TextProcessing.nltkprocess(keyword)}
# parameters = [{'A':1.0/200,'B':1.0,
#                'C':1.0/5.0,'D':1.0,'E':1.0,
#                'F':1.0,'G':0.5,'H':0.8,
#                 'I0':2.0,
#                 'I1':2.0,
#                 'I-1':2.0,
#                 'J':1.0,
#                 'N':0.5}]
# stemmedDesc = TextProcessing.nltkprocess(desc,keepComa=True)
# print TextProcessing.getProbKeywordInDescription(keyword, keywordSet[keyword], stemmedDesc, parameters)
#         