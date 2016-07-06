# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

import os
import time

import  Constants
import IOFunctions
import KeywordSelector
import pandas as pd


def main(arg):
    if arg=="compute graph pipeline":
        # COMPUTING GRAPH
        print "COMPUTING COMPLETE GRAPH PIPELINE"
        print ""
        n = 200
        startingPhase = 0
        path = Constants.pathCodeNAF
        codeNAFs = IOFunctions.importListCodeNAF()
        
        # Step 0 : creating subset for all NAF
        if(startingPhase<=0):
            startTime = time.time()
            print "Step 0 : creating subset for all NAF"
            compt = Constants.Compt(codeNAFs, 1, True)
            for codeNAF in codeNAFs:
                compt.updateAndPrint()
                IOFunctions.extractSubset(codeNAF, n, path = path, toPrint=False)
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
        des = [
               "Production cinématograhique et audiovisuelle",
                "Enseignement de la conduite de véhicules terrestres et de sécurité routière, école de conduite et pilotage de tous engins flottants ou aériens, formation de tous moniteurs.",
                "Gestion, propriété, administration et disposition des biens qui pourront devenir la propriété de la société par voie d'acquisition, d'échange, d'apport, de construction ou autrement.",
                "Laboratoire d'analyses de biologie médicale",
                "Restaurant rapide et traditionnel, à emporter, sur place et en livraison"
               ]
        codeNaF = ["" for _ in des]
        csvdesc = pd.DataFrame(data={"codeNaf":codeNaF, "description":des})                  
        KeywordSelector.pipeline(csvdesc, 20, True)


main("compute graph pipeline")






