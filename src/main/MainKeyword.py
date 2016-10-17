# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''


import os
import time

import KeywordSelector
import UtilsConstants
import pandas as pd


def main(arg):
    if arg=="compute graph pipeline":
        # pipeline graph
        KeywordSelector.pipelineGraph(200, percent=100, steps = [False, False, True])
    if arg=="main pipeline":
        # global keyword selector
        startTime = time.time()
        print "== GLOBAL PIPELINE"
        print ""
        for fname in ["BRep_Step2_0_1000000",
                      "BRep_Step2_1000000_2000000",
                      "BRep_Step2_2000000_3000000",
                      "BRep_Step2_3000000_4000000",
                      "BRep_Step2_4000000_5000000",
                      "BRep_Step2_5000000_6000000",
                      "BRep_Step2_6000000_7000000",
                      "BRep_Step2_7000000_8000000",
                      "BRep_Step2_8000000_9176180",
                      ]:
            print "computing ",fname
            filename = os.path.join(UtilsConstants.pathAgreg,fname+".csv")
            df = pd.read_csv(filename,usecols=["siren","codeNaf","description"],encoding="utf8").values
            dic = KeywordSelector.pipeline(df, printProgress=True)
            df = pd.DataFrame.from_dict(dic, orient="index")
            filename = os.path.join(UtilsConstants.pathAgreg,fname+"_keywords.csv")
            UtilsConstants.printTime(startTime)
            df.to_csv(filename, encoding="utf8")


# KeywordSelector.cleanKeyword()



# main("compute graph pipeline")


main("main pipeline")

