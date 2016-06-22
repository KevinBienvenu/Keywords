# -*- coding: utf-8 -*-
'''
Created on 21 juin 2016

@author: Kévin Bienvenu
'''
import math
from operator import add
import os
import random

from learning import GeneticTraining, GraphLearning
from learning.GeneticTraining import GeneticProcess, Chromosome
from main import Constants, IOFunctions
import numpy as np
import pandas as pd


globalParam = ['nbVoisins','nbVoisins1','propSumVoisins1','propVoisins1','size','sumVoisins','sumVoisins1']
globalKeyParam = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'phi']

class GeneticKeywords03(GeneticProcess):
    '''
    Class holding the behaviour of the step 01 learning:
    each chromosome contain parameters of an evaluation function
    that extract keywords out of a description (string).
    The evaluation is performed using comparison to an actual and manually extracted keywords list.
    '''
    def __init__(self, nbDesc=0, nbChromo = 100, nbTotalStep = 100, toPrint=True):
        self.toPrint = toPrint
        self.name = "Step03Genetic"
        if self.toPrint:
            print "================================="
            print "= Genetic algorithm for step 03 ="
            print "================================="
            print ""
        # on prépare l'évaluation
        self.codeNAF = ""
        self.features = {}
        self.scoreMax = 0 
        os.chdir(os.path.join(Constants.path,"preprocessingData"))
        self.df = pd.DataFrame.from_csv("trainingStep3.csv", sep=";")
        nbYPos = len(self.df.loc[self.df.Y==1])
        if nbYPos<len(self.df)/2:
            indexToKeep = list(self.df.loc[self.df.Y==1].index.values) + list(random.sample(self.df.loc[self.df.Y==0].index.values, nbYPos))
        self.df= self.df.loc[indexToKeep]
        self.df[globalParam] = self.df[globalParam].apply(lambda s : s/max(s))
        GeneticProcess.__init__(self, nbChromo, nbTotalStep, toPrint)

    ''' méthodes overidée '''
    def generatePop(self, n):
        pop = [Chromosome(self.generateRandomParameters(),nature="random") for _ in range(n)]
        return pop

    def generateRandomParam(self, param): 
        # dealing with special cases
        if param in ['nbVoisins1_epsilon',
                     'nbVoisins_phi',
                     'propSumVoisins1_alpha',
                     'propSumVoisins1_beta',
                     'propSumVoisins1_delta',
                     'propSumVoisins1_epsilon',
                     'propSumVoisins1_phi',
                     'propVoisins1_beta',
                     'propVoisins1_phi',
                     'sumVoisins1_phi',
                     'sumVoisins_phi',
                     'nbVoisins_beta',
                     'propVoisins1_epsilon',
                     'size_beta']:
            return 0
        
        if random.random()>1.0/(len(globalKeyParam)-1):
            return 0
        else:
            return random.random()*2.0-1.0
        
    def evaluatePop(self):  
        compt = IOFunctions.Compt(range(len(self.pop)/2) if self.nStep>0 else self.pop,10)
        for chromo in self.pop:
            if chromo.evaluated:
                continue
            compt.updateAndPrint()
            chromo.probaEvolution = self.evaluateFunctionValue(chromo)
            chromo.evaluated = True
            
 
    ''' méthodes auxiliaires ''' 
     
    def generateRandomParameters(self):
        keys = []
        for param in globalParam:
            keys += [param+"_"+key for key in globalKeyParam]
        return {key : self.generateRandomParam(key) for key in keys}    
      
    def evaluateFunctionValue(self, chromo):
        scores = [0.0]*len(self.df)
        for param in chromo.parameters: 
            tab = param.split("_")
            scores = map(add, scores, self.df[tab[0]].apply(evaluateParam, args=[tab[1], chromo.parameters[param]]).values)
        df = pd.DataFrame(data={"label":self.df.Y.apply(lambda x : 1 if x else -1), "scores":scores})
#         variances = [np.var(df.loc[df.label==1].scores.values),np.var(df.loc[df.label==-1].scores.values)]
#         moyennes = [np.mean(df.loc[df.label==1].scores.values),np.mean(df.loc[df.label==-1].scores.values)]
#         moyenne = (moyennes[0]*variances[0]+moyennes[1]*variances[1])/(variances[0]+variances[1])
        moyenne2 = computeOptimalReduit(df)
        score = evaluateNombre(df, moyenne2)
        return score;
    
def computeOptimalReduit(df):
    mini = min(df.scores.values)
    maxi = max(df.scores.values)
    while maxi-mini>1:
        test = (mini+maxi)/2.0
        score = evaluateNombre(df, test)
        score1 = evaluateNombre(df, test+1)
        if score>score1:
            maxi = test
        else:
            mini = test
    return mini
        
    
def evaluateNombre(df, nombre):
    return int(1000.0*np.sum(df.apply((lambda s,y=nombre: (1+np.sign(s.scores-nombre)*s.label)/2), 'columns'))/len(df))/10.0
    
def evaluateParam(v, paramKey, paramValue):  
    if paramKey=="alpha":
        return paramValue*v
    elif paramKey=="beta":
        return paramValue*math.sqrt(v)
    elif paramKey=="gamma":
        return paramValue/(0.001+v)
    elif paramKey=="delta":
        return paramValue*(1.0-v)
    elif paramKey=="epsilon":
        return paramValue*math.sqrt(1.0-v)
    elif paramKey=="phi":
        return paramValue/(0.001+(1.0-v))      
