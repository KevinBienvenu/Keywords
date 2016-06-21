# -*- coding: utf-8 -*-
'''
Created on 6 juin 2016

@author: Kévin Bienvenu
'''
from operator import itemgetter
import os
import random


from main import Constants
import pandas as pd

class Chromosome():
    def __init__(self, parameters={}, parents = None,nature = ""):
        self.parameters = parameters
        self.probaEvolution = 0.0
        self.evaluated = False
        self.age = 0
        self.nature = nature
        self.mutations = []
            
    def toPrint(self):
        print self.parameters

class GeneticProcess():
    
    ''' méthode d'initialisation '''
    def __init__(self, nbChromo = 100, nbTotalStep = 100, toPrint=True):
        self.toPrint = toPrint
        # on prépare l'entraînement
        self.nStep = 0
        self.nbTotalStep = nbTotalStep
        self.nbAjoutRandom = nbChromo/10
        self.scoreMax = 0
        # on genere la pop de base
        self.pop = self.generatePop(nbChromo)
        if self.toPrint:
            print " nb Chromosomes :", len(self.pop)
            print " nb Etapes :", nbTotalStep
            print ""

    ''' méthodes à overider '''
    # on définit les méthodes à implémenter
    # non nécessaire mais bon, on oublie jamais vraiment le java, hein ?
    def generatePop(self,n):
        pass 
    def evaluatePop(self):
        pass  
    def generateRandomParam(self, param):
        pass 

    ''' méthodes du déroulé de l'algorithme'''
    def evaluationStep(self):
        self.evaluatePop()
        for chromo in self.pop:
            chromo.evaluated = True
            chromo.age += 1
            
    def selectionStep(self):
        # on sélectionne uniquement les meilleurs chromosomes
        l = {chromo : chromo.probaEvolution for chromo in self.pop}.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.pop = [l[i][0] for i in range(len(self.pop)/2)]
          
    def croisementStep(self):
        # on fabrique les enfants
        parents = random.sample(self.pop, len(self.pop)-self.nbAjoutRandom)
        random.shuffle(parents)
        for i in range(len(parents)/2):
            [chromo1, chromo2] = [parents[2*i], parents[2*i+1]]
            # performing cross over
            params = chromo1.parameters.keys()
            ind = random.sample(params,random.randint(0,len(chromo1.parameters)))
            chromo3 = Chromosome()
            chromo4 = Chromosome()
            chromo3.nature = "enfant"
            chromo4.nature = "enfant"
            if random.random()>0.3:
                param3 = {key : (chromo1.parameters[key] if key in ind else chromo2.parameters[key]) for key in params}
                param4 = {key : (chromo2.parameters[key] if key in ind else chromo1.parameters[key]) for key in params}
            else:
                param3 = {key : (0.5*(chromo1.parameters[key]+chromo2.parameters[key]) if key in ind else chromo2.parameters[key]) for key in params}
                param4 = {key : (0.5*(chromo1.parameters[key]+chromo2.parameters[key]) if key in ind else chromo1.parameters[key]) for key in params}
                chromo3.nature += " modifié"
                chromo4.nature += " modifié"
            chromo3.parameters = param3
            chromo4.parameters = param4
            # handling mutation
            while random.random()<0.5:
                r = random.randint(0,len(chromo3.parameters)-1)
                param = chromo3.parameters.keys()[r]
                chromo3.parameters[param] = self.generateRandomParam(param)
                chromo3.mutations.append(param)
            while random.random()<0.5:
                r = random.randint(0,len(chromo4.parameters)-1)
                param = chromo4.parameters.keys()[r]
                chromo4.parameters[param] = self.generateRandomParam(param)
                chromo4.mutations.append(param)
            # adding resulting chromosome to pop
            self.pop.append(chromo3)
            self.pop.append(chromo4)
        self.pop = self.pop + self.generatePop(self.nbAjoutRandom)
       
    def processStep(self):
        if self.toPrint:
            print "running step",self.nStep
        self.evaluationStep()
        self.selectionStep()
        self.croisementStep()
        self.nStep += 1
            
    def run(self):
        for _ in range(self.nbTotalStep):
            self.processStep()
            if self.toPrint:
                if self.pop[0].probaEvolution > self.scoreMax:
                    self.scoreMax = self.pop[0].probaEvolution
                    print self.pop[0].nature, self.pop[0].mutations
                print self.pop[0].probaEvolution
        if self.toPrint:
            print self.pop[0].parameters
        self.saveResults()

    ''' méthodes de sauvegarde des résultats '''

    def saveResults(self):
        dic = self.pop[0].parameters
        dfNew = pd.DataFrame.from_dict(data = dic,orient = "index")
        dfNew.columns = ['nbChr'+str(len(self.pop))+'-nbStep'+str(self.nbTotalStep)] 
        os.chdir(Constants.pathCodeNAF+"/../")
        df = pd.DataFrame.from_csv(self.name+"-results.csv",sep=";")
        if len(df)<len(dfNew):
            # on archive la vieille base
            df.to_csv(self.name+"-results(old).csv",sep=";")
            df = dfNew
        else:
            df = df.join(dfNew,rsuffix="-"+str(len(df.columns)),sort=True)
        df.sort_index(inplace=True)
        df.to_csv(self.name+"-results.csv",sep=";")
        
        