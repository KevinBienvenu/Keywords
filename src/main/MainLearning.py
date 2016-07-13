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
 
import InterfaceGraphique, GeneticKeywords01, GeneticKeywords03, GraphLearning, IOFunctions, Constants


def main(arg=""):
    if arg == "Interface Graphique":
        # Interface Graphique
        interface = InterfaceGraphique.Interface()
        interface.fenetre.mainloop()
        # the files are automatically updated
        
    elif arg == "Genetic Algorithm Step 01":
        # Training Genetic Algorithm - Step 01
        temps = time.time()
               
        for _ in range(1):
            geneticProcess = GeneticKeywords01.GeneticKeywords01(nbChromo = 20, nbTotalStep=10, toPrint=True)
            geneticProcess.run()
               
        Constants.printTime(temps)
        # results saved in preprocessedData/Step01Genetic-results.csv
        
    elif arg == "Model Learning Step 03":
        # Graph Learning
        GraphLearning.preprocessClassifiers(GraphLearning.classifiers, nbPrise=1, toSave=True)
        # if toSave=True, results saved in preprocessedData/classifiers

        temps = time.time()
                
        for _ in range(1):   
            geneticProcess = GeneticKeywords03.GeneticKeywords03(nbChromo = 20, nbTotalStep=20, toPrint=True)
            geneticProcess.run()
                    
        Constants.printTime(temps)
        # results saved in preprocessedData/Step03Genetic-results.csv
    
    elif arg == "Testing Step 03":
        # Graph Learning
        cla, nam = GraphLearning.loadClassifiers()
        GraphLearning.evaluateClassifiers(cla, nam)
        # no modification, only print classifiers evaluation
    


main("Model Learning Step 03")

