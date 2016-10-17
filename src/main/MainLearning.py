# -*- coding: utf-8 -*-
'''
Created on 27 mai 2016

@author: Kévin Bienvenu

=== MAIN FUNCTION FOR LEARNING ===

possible args :
- "Interface Graphique" : launch the graph interface to increase the training set size
- "Genetic Algorithm Step 01" : learns new genetic parameters for step 01
- "Model Learning Step 03" : learns new models for the step 03
- "Genetic Algorithm Step 03" : learns new genetic parameters for step 03
- "Testing Step 03" : print models and genetic results for the step 03

'''

import time

import GeneticKeywords01, GraphLearning, UtilsConstants, InterfaceGraphiqueV2, KeywordSelector


def main(arg=""):
    if arg == "Interface Graphique":
        # Interface Graphique
        InterfaceGraphiqueV2.InterfaceGraphique()
        # the files are automatically updated
        
    elif arg == "Genetic Algorithm Step 01":
        # Training Genetic Algorithm - Step 01
        temps = time.time()
               
        geneticProcess = GeneticKeywords01.GeneticKeywords01(nbChromo = 100, nbTotalStep=20, toPrint=True)
        geneticProcess.run()
               
        UtilsConstants.printTime(temps)
        # results saved in preprocessedData/Step01Genetic-results.csv
        
    elif arg == "Model Learning Step 03":
        # Graph Learning
        temps = time.time()
        GraphLearning.preprocessClassifiers(GraphLearning.classifiers, nbPrise=1, toSave=True, nbChromo=200, nbTotalStep=100)
        # if toSave=True, results saved in preprocessedData/classifiers
        UtilsConstants.printTime(temps)
        # results saved in preprocessedData/Step03Genetic-results.csv
    
    elif arg == "Testing Step 03":
        # Graph Learning
        classifier = [GraphLearning.Step3Classifier()]
        GraphLearning.evaluateClassifiers(classifier, ["Step03Clf"])
        # no modification, only print classifiers evaluation
    


main("Interface Graphique")
# main("Genetic Algorithm Step 01")
# main("Model Learning Step 03")
# main("Testing Step 03")



