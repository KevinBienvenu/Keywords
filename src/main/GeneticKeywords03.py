# -*- coding: utf-8 -*-
'''
Created on 21 juin 2016

@author: Kévin Bienvenu
'''
import codecs
from operator import add
import os
import random

import GeneticTraining, IOFunctions, Constants
import numpy as np
import pandas as pd


globalKeyParam = ['alpha', 'gamma', 'delta', 'phi']

class GeneticKeywords03(GeneticTraining.GeneticProcess):
    '''
    Class holding the behaviour of the step 01 learning:
    each chromosome contain parametersStep01 of an evaluation function
    that extract keywords out of a description (string).
    The evaluation is performed using comparison to an actual and manually extracted keywords list.
    '''
    def __init__(self, nbDesc=0, nbChromo = 100, nbTotalStep = 100, toPrint=True):
        self.toPrint = toPrint
        self.name = "Step03Genetic"
        if self.toPrint:
            print ""
            print "================================="
            print "= Genetic algorithm for step 03 ="
            print "================================="
            print ""
        # on prépare l'évaluation
        self.codeNAF = ""
        self.features = {}
        self.scoreMax = 0 
        os.chdir(os.path.join(GeneticTraining.Constants.path,"preprocessingData"))
        self.df = pd.DataFrame.from_csv("trainingStep3.csv", sep=";")
#         nbYPos = len(self.df.loc[self.df.Y==1])
#         if nbYPos<len(self.df)/2:
#             indexToKeep = list(self.df.loc[self.df.Y==1].index.values) + list(random.sample(self.df.loc[self.df.Y==0].index.values, nbYPos))
#         self.df= self.df.loc[indexToKeep]
        self.globalParams = list(self.df.columns)
        self.globalParams.remove('Y')
        self.df[self.globalParams] = self.df[self.globalParams].apply(lambda s : s/max(s))
        GeneticTraining.GeneticProcess.__init__(self, nbChromo, nbTotalStep, toPrint)

    ''' méthodes overidée '''
    def generatePop(self, n):
        pop = [GeneticTraining.Chromosome(self.generateRandomParameters(),nature="random") for _ in range(n)]
        return pop

    def generateRandomParam(self, param): 
        # dealing with known cases
        dic = {
#                'nbVoisins_alpha' : 0.16,
#                'nbVoisins_gamma' : 0.4,
#                'nbVoisins_phi' : 0,
#                'nbVoisins1_gamma' : 0.25,
#                'nbVoisins1_phi' : -0.28,
#                'sumVoisins_phi' : 0,
#                'sumVoisins1_gamma' : -0.33,
#                'sumVoisins1_phi' : 0,
#                'propVoisins1_gamma' : -0.3,
#                'propVoisins1_phi' : 0,
#                'propSumVoisins1_alpha' : 0,
#                'propSumVoisins1_gamma' : -0.45,
#                'propSumVoisins1_delta' : 0,
#                'propSumVoisins1_phi' : 0,
#                'size_alpha' : 0,
#                'size_delta' : 0,
#                'size_gamma' : -0.07,
#                'size_phi' : -0.23
               }
        if param in dic:
            return dic[param]
        if random.random()>1.0/(len(globalKeyParam)-1):
            return 0
        else:
            return random.random()*2.0-1.0
        
    def evaluatePop(self):  
        compt = Constants.Compt(range(len(self.pop)/2) if self.nStep>0 else self.pop,10)
        for chromo in self.pop:
            if chromo.evaluated:
                continue
            if self.toPrint:
                compt.updateAndPrint()
            chromo.probaEvolution, chromo.probaBonus = self.evaluateFunctionValue(chromo)
            chromo.evaluated = True
            
 
    ''' méthodes auxiliaires ''' 
     
    def generateRandomParameters(self):
        keys = []
        for param in self.globalParams:
            keys += [param+"_"+key for key in globalKeyParam]
        return {key : self.generateRandomParam(key) for key in keys}    
      
    def evaluateFunctionValue(self, chromo):
        scores = [0.0]*len(self.df)
        for param in chromo.parameters: 
            tab = param.split("_")
            scores = map(add, scores, self.df[tab[0]].apply(evaluateParam, args=[tab[1], chromo.parameters[param]]).values)
        df = pd.DataFrame(data={"label":self.df.Y.apply(lambda x : 1 if x else -1), "scores":scores})
        moyenne2 = computeOptimalReduit(df)
        return evaluateNombre(df, moyenne2), moyenne2
    
class GeneticClassifier():
    
    def __init__(self, nbChromo=0, nbTotalStep=0, parameters = GeneticTraining.Constants.parametersGraphLearning, filename=""):
        if nbChromo>0 and nbTotalStep>0:
            self.nbChromo = nbChromo
            self.nbTotalStep = nbTotalStep
        if filename == "":
            self.parameters = parameters
        else:
            self.parameters = {}
            sep="="
            with codecs.open(filename,'r','utf-8') as fichier:
                flag = False
                for line in fichier:
                    if not flag:
                        self.threshold = float(line)
                        flag = True
                    else:
                        tab = line[:-1].split(sep)
                        s = tab[0]
                        for i in range(1,len(tab)-1):
                            s+=tab[i]
                        self.parameters[s] = tab[-1]

    def predict(self, X):
        scores = [sum([evaluateParam(X[i][param[0]/4], 
                                     param[1].split("_")[1], 
                                     self.parameters[param[1]]) 
                       for param in zip(range(len(self.parameters)),self.parameters.keys())])
                  for i in range(len(X))]
        return [min(1,max(0,(score-self.threshold)/20+0.5)) for score in scores]

    def fit(self, XTrain, Ytrain, toPrint=False):
        geneticProcess = GeneticKeywords03(nbChromo = self.nbChromo, nbTotalStep = self.nbTotalStep, toPrint=toPrint)
        geneticProcess.run() 
        self.parameters = geneticProcess.pop[0].parameters
        self.threshold = geneticProcess.pop[0].probaBonus
        
    def save(self, filename="Genetic.gen"):
        with codecs.open(filename,'w','utf-8') as fichier:
            fichier.write(str(self.threshold)+"\r\n")
            for item in self.parameters.items():
                try:
                    int(item[0])
                    fichier.write(str(item[0]))
                except:
                    fichier.write(item[0])
                fichier.write("=")
                try:
                    int(item[1])
                    fichier.write(str(item[1]))
                except:
                    fichier.write(item[1])
                fichier.write("\r\n")


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
    a = int(1000.0*np.sum(df.apply((lambda s,y=nombre: (1+np.sign(s.scores-nombre)*s.label)/2), 'columns'))/len(df))/10.0
    b = int(1000.0*np.sum(df.apply((lambda s,y=nombre: (1+np.sign(s.scores-nombre))*(1+s.label)/4.0), 'columns'))/len(df))/10.0
    return a
    
def evaluateParam(v, paramKey, paramValue):  
    if paramKey=="alpha":
        return float(paramValue)*v
    elif paramKey=="gamma":
        return float(paramValue)/(0.001+v)
    elif paramKey=="delta":
        return float(paramValue)*(1.0-v)
    elif paramKey=="phi":
        return float(paramValue)/(0.001+(1.0-v))    
    

   
