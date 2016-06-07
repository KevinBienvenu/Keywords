# -*- coding: utf-8 -*-
'''
Created on 27 mai 2016

@author: Kévin Bienvenu
'''

import os

import KeywordTraining, InterfaceGraphique, GeneticTraining
from main import TextProcessing, IOFunctions, Constants




interface = InterfaceGraphique.Interface()
interface.fenetre.mainloop()

# training = GeneticTraining.TrainingSet("0111Z", nbDesc=20, nbChromo = 500, nbTotalStep=20)
# training.run()



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