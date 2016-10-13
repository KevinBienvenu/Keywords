# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''


import os
import time

import KeywordSelector
from main import UtilsConstants
import pandas as pd


def main(arg):
    if arg=="compute graph pipeline":
        # pipeline graph
        KeywordSelector.pipelineGraph(200, percent=100, steps = [False, False, True])
    if arg=="main pipeline":
        KeywordSelector.computeKeywordsForNAF()
        # global keyword selector
        startTime = time.time()
        filename = os.path.join(UtilsConstants.pathAgreg,"BRep_Step2_0_1000000.csv")
        df = pd.read_csv(filename,usecols=["siren","codeNaf","description"],encoding="utf8").values
        dic = KeywordSelector.pipeline(df)
        df = pd.DataFrame.from_dict(dic, orient="index")
        filename = os.path.join(UtilsConstants.pathAgreg,"BRep_Step2_0_1000000_keywords.csv")
        UtilsConstants.printTime(startTime)
        df.to_csv(filename, encoding="utf8")


# KeywordSelector.cleanKeyword()


# print UtilsConstants.tokenizeAndStemmerize("produits pharmaceutiques, distribution en pharmacie, médicaments")

# main("extract NAF keywords")
# main("main pipeline")
# t = time.time()
# main("test pipeline")
# UtilsConstants.printTime(t)
main("compute graph pipeline")

# KeywordSelector.deleteKeyword(["promotion",
#                                 "gestion"])

# string = "Pose d'antenne, courant faible, Wifi, Iptv, câblage, vidéo surveillance, sono."
# print KeywordSelector.extractFromDescription(string, toPrint=False)
# print KeywordSelector.getProbKeywordInDescription("vidéo surveillance", string,  toPrint=True)
# 
# main("main pipeline")
