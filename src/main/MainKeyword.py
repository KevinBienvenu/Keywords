# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

import time

import  Constants
import IOFunctions
import KeywordSelector


def main(arg):
    if arg=="compute graph pipeline":
        # COMPUTING GRAPH
        print "COMPUTING COMPLETE GRAPH PIPELINE"
        print ""
        n = 200
        startingPhase = 1
        path = Constants.pathCodeNAF
        codeNAFs = IOFunctions.importListCodeNAF()
        
        # Step 0 : creating subset for all NAF
        if(startingPhase<=0):
            startTime = time.time()
            print "Step 0 : creating subset for all NAF"
            compt = Constants.Compt(codeNAFs, 1, True)
            for codeNAF in codeNAFs:
                compt.updateAndPrint()
                IOFunctions.extractAndSaveSubset(codeNAF, n, path = path, toPrint=False)
            Constants.printTime(startTime)
            print ""
        
        # Step 1 : computing graph and keywords for all code NAF, using keywords from Step 0-1
        if(startingPhase<=1):
            startTime = time.time()
            print "Step 1 : computing graph and keywords for all code NAF, using all keywords"
            compt = Constants.Compt(codeNAFs, 1, True)
            for codeNAF in codeNAFs:
                compt.updateAndPrint()
                KeywordSelector.extractGraphFromSubset("subset_NAF_"+codeNAF, path)
            Constants.printTime(startTime)
            print ""
        
        # Step 2 : compute complete graph using local keywords
        if(startingPhase<=2):
            startTime = time.time()
            print "Step 2 : compute complete graph using local keywords"
            subsetname = "graphcomplet"
            localKeywords = True
            KeywordSelector.extractGraphFromSubset(subsetname, path, localKeywords, toPrint=True)
            Constants.printTime(startTime)
            print ""
        
    elif arg=="main pipeline":
        # Main Pipeline
        entreprises = IOFunctions.extractSubset("", 10)                
        KeywordSelector.pipeline(entreprises, 20, True)

    elif arg=="test pipeline":
        KeywordSelector.pipelineTest()

# main("main pipeline")
# main("test pipeline")
main("compute graph pipeline")

# KeywordSelector.statsAboutKeywords()
# KeywordSelector.computeSlugEquivalence()
# ScriptFunctions.findExamples()




