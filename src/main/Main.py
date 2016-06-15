# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''


import Constants
import ScriptFunctions


path = Constants.path
pathAgreg = Constants.pathAgreg
pathSubset = Constants.pathSubset

# codeNAfs = ['4322B','4399C','6201Z','7311Z','9003A']
# 
# os.chdir(pathSubset)
# graph = IOFunctions.importGraph("extrait_501")
# for codeNaf in codeNAfs:
#     print codeNaf, IOFunctions.saveGexfFileNaf("graphNAF.gexf", graph[0], graph[1], codeNaf)
# for codeNaf in codeNAfs:
#     (entreprises,_,_) = KeywordSubset.importSubset("extrait_501")
#     compt = 0
#     for entreprise in entreprises:
#         if entreprise[1]==codeNaf:
#             compt+=1
#     print compt

ScriptFunctions.extractCompleteGraphUsingNAFKeywords()

# size = 100
# KeywordSubset.extractRandomSubset(size, "extrait_"+str(size))
# GraphPreprocess.extractGraphFromSubset("extrait_"+str(size))

# codeNAF = "4120A"
# KeywordSubset.extractSubsetFromCodeNAF(codeNAF, 50)
# KeywordSubset.extractWholeSubsetFromCodeNAF(codeNAF)
# GraphPreprocess.extractGraphFromSubset("extrait_NAF_"+codeNAF,)

# os.chdir(path+"/motscles")
# ExtractingKeywordsFromInternet.cleanMotsCles("keywords.txt")

# keywords = IOFunctions.importKeywords()
# 
# string = "Construction et vente de maisons individuelles, l'étude et réalisation de tous travaux de construction et de travaux publics de rénovation et de promotion immobilière."
# 
# TextProcessing.extractKeywordsFromString(string, keywords, {}, True)

