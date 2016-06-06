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

    
    def mutation(self):
        while random.random()<0.2:
            r = random.randint(0,len(self.parameters)-1)
            param = self.parameters.keys()[r]
            self.parameters[param] = KeywordTraining.generateRandomParam(param)
            
    def toPrint(self):
        print self.parameters

class TrainingSet():
    def __init__(self, codeNAF, nbDesc=1, nbChromo = 100, nbTotalStep = 100):
        # on prépare l'entraînement
        self.descriptions = {}
        self.nStep = 0
        self.nbTotalStep = nbTotalStep
        self.nbAjoutRandom = 2
        self.french_stopwords = set(stopwords.words('french'))
        self.stem = nltk.stem.snowball.FrenchStemmer()
        (entreprises, self.keywordSet, self.dicWordWeight) = KeywordSubset.importTrainedSubset(subsetname="codeNAF_"+str(codeNAF), path=Constants.pathCodeNAF)
        sample = random.sample(entreprises, nbDesc)
        self.descriptions = {s[1]:[TextProcessing.nltkprocess(s[1],
                                                        keepComa=True,
                                                        french_stopwords=self.french_stopwords,
                                                        stem=self.stem),s[2]] for s in sample}
        self.pop = generateInitialPop(nbChromo)

    def evaluationStep(self):
        # on associe à chaque chromosome son score
        compt = IOFunctions.initProgress(self.pop, 10)
        for chromo in self.pop:
            compt = IOFunctions.updateProgress(compt)
            chromo.probaEvolution = KeywordTraining.evaluateChromosome(chromo, 
                                                                       self.descriptions, 
                                                                       self.keywordSet, 
                                                                       self.dicWordWeight,
                                                                       self.french_stopwords,
                                                                       self.stem
                                                                       )    
            
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
        for i in range(len(self.pop)/2-self.nbAjoutRandom):
            [chromo1, chromo2] = crossOver(self.pop[2*i], self.pop[2*i+1])
            chromo1.mutation()
            chromo2.mutation()
            self.pop.append(chromo1)
            self.pop.append(chromo2)
        self.pop = self.pop + generateInitialPop(self.nbAjoutRandom*2)
    
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
    if random.random()>0.3:
        param3 = {key : (chrom1.parameters[key] if key in ind else chrom2.parameters[key]) for key in params}
        param4 = {key : (chrom2.parameters[key] if key in ind else chrom1.parameters[key]) for key in params}
    else:
        param3 = {key : ((chrom1.parameters[key]+chrom2.parameters[key])/2 if key in ind else chrom2.parameters[key]) for key in params}
        param4 = {key : ((chrom2.parameters[key]+chrom1.parameters[key])/2 if key in ind else chrom1.parameters[key]) for key in params} 
    return [Chromosome(parameters=param3),Chromosome(parameters=param4)]

def generateInitialPop(n):
    pop = [Chromosome(KeywordTraining.generateRandomParameters()) for _ in range(n)]
    return pop


        