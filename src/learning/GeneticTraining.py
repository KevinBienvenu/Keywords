# -*- coding: utf-8 -*-
'''
Created on 6 juin 2016

@author: Kévin Bienvenu
'''
from operator import itemgetter
import os
import random

import nltk
from nltk.corpus import stopwords

from learning import KeywordTraining
from main import IOFunctions, Constants, KeywordSubset, TextProcessing
import numpy as np
import pandas as pd

class Chromosome():
    def __init__(self, parameters={}, parents = None,nature = ""):
        self.parameters = parameters
        self.probaEvolution = 0.0
        self.evaluated = False
        self.age = 0
        self.nature = nature
        self.mutations = []
   
    def mutation(self):
        while random.random()<0.5:
            r = random.randint(0,len(self.parameters)-1)
            param = self.parameters.keys()[r]
            self.parameters[param] = KeywordTraining.generateRandomParam(param)
            self.mutations.append(param)
            
    def toPrint(self):
        print self.parameters

class TrainingSet():
    def __init__(self, codeNAF=None, nbDesc=0, nbChromo = 100, nbTotalStep = 100, toPrint=True):
        self.toPrint = toPrint
        if self.toPrint:
            print "============================"
            print "=== INITIALIZING GENETIC ==="
            print "============================"
            print ""
        # on prépare l'entraînement
        self.descriptions = {}
        self.nStep = 0
        self.nbTotalStep = nbTotalStep
        self.nbAjoutRandom = nbChromo/10
        self.french_stopwords = set(stopwords.words('french'))
        self.stem = nltk.stem.snowball.FrenchStemmer()
        self.codeNAF = codeNAF
        self.scoreMax = 0
        if codeNAF is None: 
            entreprises = []
            os.chdir(os.path.join(Constants.path,"preprocessingData"))
            with open("trainingSet.txt","r") as fichier:
                for line in fichier:
                    entreprises.append(line.split("_"))
                    entreprises[-1][-1] = entreprises[-1][-1].split("=")[:-1]           
            self.keywordSet = {}
            self.dicWordWeight = {}
        else:
            (entreprises, self.keywordSet, self.dicWordWeight) = KeywordSubset.importTrainedSubset(subsetname="codeNAF_"+str(codeNAF), path=Constants.pathCodeNAF)
        if nbDesc>0:
            entreprises = random.sample(entreprises, min(len(entreprises),nbDesc))
        self.descriptions = {s[1]:[TextProcessing.nltkprocess(s[1],
                                                        keepComa=True,
                                                        french_stopwords=self.french_stopwords,
                                                        stem=self.stem),
                                   s[2],
                                   s[0]] 
                             for s in entreprises}
        self.pop = generateInitialPop(nbChromo)
        if self.toPrint:
            print " nb Chromosomes :", len(self.pop)
            print " nb Descriptions :", len(self.descriptions)
            print " nb Etapes :", nbTotalStep
            print ""

    def evaluationStep(self):
        KeywordTraining.evaluatePop(self)
        for chromo in self.pop:
            chromo.evaluated = True
            chromo.age += 1
            
    def selectionStep(self):
        # on sélectionne uniquement les meilleurs chromosomes
        l = {chromo : chromo.probaEvolution for chromo in self.pop}.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.pop = [l[i][0] for i in range(len(self.pop)/2)]
    
    def selectionStep2(self):
        # on sélectionne les survivants avec probabilités leurs scores:
        newPop = []
        for _ in range(len(self.pop)/2):
            valNorm = sum([chromo.probaEvolution**5 for chromo in self.pop])
            r = random.random()
            for chromo in self.pop:
                r -= (chromo.probaEvolution**5)/valNorm
                if r<=0:
                    newPop.append(chromo)
                    break
            self.pop.remove(newPop[-1])
        l = {chromo : chromo.probaEvolution for chromo in newPop}.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.pop = [i[0] for i in l]
                 
    def croisementStep(self):
        # on fabrique les enfants
        parents = random.sample(self.pop, len(self.pop)-self.nbAjoutRandom)
        random.shuffle(parents)
        
        for i in range(len(parents)/2):
            [chromo1, chromo2] = crossOver(parents[2*i], parents[2*i+1])
            chromo1.mutation()
            chromo2.mutation()
            self.pop.append(chromo1)
            self.pop.append(chromo2)
        self.pop = self.pop + generateInitialPop(self.nbAjoutRandom)
    
    def processStep(self):
        if self.toPrint:
            print "running step",self.nStep
        self.evaluationStep()
        if self.toPrint:
            self.printState()
        self.selectionStep()
        self.croisementStep()
        self.nStep += 1
        
    def printState(self):
        scores = [chromo.probaEvolution for chromo in self.pop]
        ages = [chromo.age for chromo in self.pop]
        dicAge = {age : np.sum([1 if age2==age else 0 for age2 in ages]) for age in ages}
        print ""
        print "   score max:",max(scores)
        print ""
        print "   age max:",max(ages)
        print "   age mean:",np.mean(ages)
        print "   repartition:",dicAge
        print ""
            
    def run(self):
        for _ in range(self.nbTotalStep):
            self.processStep()
            if self.pop[0].probaEvolution > self.scoreMax:
                self.scoreMax = self.pop[0].probaEvolution
                print self.pop[0].nature, self.pop[0].mutations
            print self.pop[0].probaEvolution
        print self.pop[0].parameters
        self.saveResults()
#             try:
#                 a = input()
#             except:
#                 pass
      
    def setCodeNAF(self, codeNAF):
        self.codeNAF = codeNAF[-5:]
        (_, self.keywordSet, self.dicWordWeight) = KeywordSubset.importTrainedSubset(subsetname="codeNAF_"+str(self.codeNAF), path=Constants.pathCodeNAF)    

    def saveResults(self):
        dic = self.pop[0].parameters
        dfNew = pd.DataFrame.from_dict(data = dic,orient = "index")
        dfNew.columns = ['nbChr'+str(len(self.pop))+'-nbStep'+str(self.nbTotalStep)] 
        os.chdir(Constants.pathCodeNAF+"/../")
        df = pd.DataFrame.from_csv("resultsAlgoGenetique.csv",sep=";")
        df = df.join(dfNew,rsuffix="-"+str(len(df.columns)),sort=True)
        df.sort_index(inplace=True)
#         df.to_csv("resultsAlgoGenetique.csv",sep=";")
        
def crossOver(chrom1, chrom2):
    params = chrom1.parameters.keys()
    ind = random.sample(params,random.randint(0,len(chrom1.parameters)))
    chromo3 = Chromosome()
    chromo4 = Chromosome()
    chromo3.nature = "enfant"
    chromo4.nature = "enfant"
    if random.random()>0.3:
        param3 = {key : (chrom1.parameters[key] if key in ind else chrom2.parameters[key]) for key in params}
        param4 = {key : (chrom2.parameters[key] if key in ind else chrom1.parameters[key]) for key in params}
    else:
        param3 = {key : (0.5*(chrom1.parameters[key]+chrom2.parameters[key]) if key in ind else chrom2.parameters[key]) for key in params}
        param4 = {key : (0.5*(chrom1.parameters[key]+chrom2.parameters[key]) if key in ind else chrom1.parameters[key]) for key in params}
        chromo3.nature += " modifié"
        chromo4.nature += " modifié"
    chromo3.parameters = param3
    chromo4.parameters = param4
    return [chromo3, chromo4]

def generateInitialPop(n):
    pop = [Chromosome(KeywordTraining.generateRandomParameters(),nature="random") for _ in range(n)]
    return pop

        