# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

import codecs
import os
import pandas as pd

import  Constants
import IOFunctions
from main import KeywordSelector

def main(arg):
    if arg=="extract subset":
        codeNAF = ""
        n = 10000
        IOFunctions.extractSubset(codeNAF, n)

    elif arg=="compute graph":
        subsetname = "graphcomplet_size_10000"
        path = Constants.pathCodeNAF
        localKeywords = True
        IOFunctions.extractGraphFromSubset(subsetname, path, localKeywords)

    elif arg=="create all NAF":
        # step 0 : importing list of codeNAF
        codeNAFs =IOFunctions.importListCodeNAF()
        # step 1 : creating all subsets
        compt = Constants.Compt(codeNAFs, 1, False)
        for codeNAF in codeNAFs:
            compt.updateAndPrint()
            IOFunctions.extractSubset(codeNAF, n, path = Constants.pathCodeNAF, toPrint=True)
        # step 2 : creating all graph
        compt = Constants.Compt(codeNAFs, 1, False)
        for codeNAF in codeNAFs:
            compt.updateAndPrint()
            IOFunctions.extractGraphFromSubset("subset_NAF_"+codeNAF, Constants.pathCodeNAF)
        # step 3 : creating all keywords
            os.chdir(Constants.pathCodeNAF)
            for directory in os.listdir("."):
                if directory[0]=="s":
                    IOFunctions.extractKeywordsFromGraph(directory, Constants.pathCodeNAF)
    
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
        print csvdesc
                   
        tab = KeywordSelector.pipeline(csvdesc, 20, True)
        for t in tab:
            print t

main("main pipeline")
