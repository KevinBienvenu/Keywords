# -*- coding: utf-8 -*-
'''
Created on 6 juin 2016

@author: Kévin Bienvenu
'''
from operator import itemgetter
import random

import nltk
from nltk.corpus import stopwords

from learning import KeywordTraining
from main import IOFunctions, Constants, KeywordSubset, TextProcessing
import numpy as np


class Chromosome():
    def __init__(self, parameters={}, parents = None):
        self.parameters = parameters
        self.probaEvolution = 0.0
        self.evaluated = False
   
    def mutation(self):
        while random.random()<0.2:
            r = random.randint(0,len(self.parameters)-1)
            param = self.parameters.keys()[r]
            self.parameters[param] = KeywordTraining.generateRandomParam(param)
            
    def toPrint(self):
        print self.parameters

class TrainingSet():
    def __init__(self, codeNAF, nbDesc=0, nbChromo = 100, nbTotalStep = 100):
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
        (entreprises, self.keywordSet, self.dicWordWeight) = KeywordSubset.importTrainedSubset(subsetname="codeNAF_"+str(codeNAF), path=Constants.pathCodeNAF)
        if nbDesc>0:
            entreprises = random.sample(entreprises, min(len(entreprises),nbDesc))
        self.descriptions = {s[1]:[TextProcessing.nltkprocess(s[1],
                                                        keepComa=True,
                                                        french_stopwords=self.french_stopwords,
                                                        stem=self.stem),s[2]] for s in entreprises}
        self.pop = generateInitialPop(nbChromo)
        print " nb Chromosomes :", len(self.pop)
        print " nb Descriptions :", len(self.descriptions)
        print " nb Etapes :", nbTotalStep
        print ""

    def evaluationStep(self):
        KeywordTraining.evaluatePop(self)
        for chromo in self.pop:
            chromo.evaluated = True
            
    def selectionStep(self):
        # on sélectionne uniquement les meilleurs chromosomes
        l = {chromo : chromo.probaEvolution for chromo in self.pop}.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.pop = [l[i][0] for i in range(len(self.pop)/2)]
    
    def selectionStep2(self):
        # on sélectionne les survivants avec probabilités leurs scores:
        newPop = []
        for _ in range(len(self.pop)/2):
            valNorm = sum([chromo.probaEvolution for chromo in self.pop])
            r = random.random()
            for chromo in self.pop:
                r -= chromo.probaEvolution/valNorm
                if r<=0:
                    newPop.append(chromo)
                    break
            self.pop.remove(newPop[-1])
        self.pop = newPop
                 
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
        print "running step",self.nStep
        self.evaluationStep()
        self.printState()
        self.selectionStep()
        self.croisementStep()
        self.nStep += 1
        
    def printState(self):
        scores = [chromo.probaEvolution for chromo in self.pop]
        print "   max:",max(scores)
        print "   min:",min(scores)
        print "   mean:",np.mean(scores)
        print "     total pop:",len(self.pop)
            
    def run(self):
        for _ in range(self.nbTotalStep):
            self.processStep()
        print self.pop[0].parameters
#             try:
#                 a = input()
#             except:
#                 pass
            

def crossOver(chrom1, chrom2):
    params = chrom1.parameters.keys()
    ind = random.sample(params,random.randint(0,len(chrom1.parameters)))
    param3 = {key : (chrom1.parameters[key] if key in ind else chrom2.parameters[key]) for key in params}
    param4 = {key : (chrom2.parameters[key] if key in ind else chrom1.parameters[key]) for key in params}
    return [Chromosome(parameters=param3),Chromosome(parameters=param4)]

def generateInitialPop(n):
    pop = [Chromosome(KeywordTraining.generateRandomParameters()) for _ in range(n)]
    return pop


        