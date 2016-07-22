# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

import time

import UtilsConstants, IOFunctions, KeywordSelector


def main(arg):
    if arg=="compute graph pipeline":
        # pipeline graph
        KeywordSelector.pipelineGraph(n=200)
        
    elif arg=="main pipeline":
        # Main Pipeline
        entreprises = IOFunctions.extractSubset("", 5)  
        KeywordSelector.pipeline(entreprises, 20)

    elif arg=="test pipeline":
        KeywordSelector.pipelineTest()




# main("main pipeline")
# main("test pipeline")
# main("compute graph pipeline")


KeywordSelector.deleteKeyword(["automatisme"])



