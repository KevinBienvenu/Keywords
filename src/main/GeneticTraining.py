# -*- coding: utf-8 -*-
'''
Created on 6 juin 2016

@author: Kévin Bienvenu

Class describing the behavior of a genetic algorithm
this is an abstract class and cannot be used by itself,
as many functions must be completed or overwritten.

There is also the class Chromosome in this module that is the elementary
piece for the genetic process.
'''
from operator import itemgetter
import os
import random

import UtilsConstants
import pandas as pd


class Chromosome():
    '''
    Class representing one member of the global population for the genetic training.
    '''
    def __init__(self, parameters={}, nature = ""):
        '''
        initializing the Chromosome.
        the only input data are the parameters, that should change from one chromosome to the other
        and that represents the genetic material of the chromosome. Here
        parameters is a dictionary with string as keys and float as values.
        -- IN
            parameters : dictionary of the genetic material of the chromosome (dic{parameterName(string) : parameterValue(float)}) default = {}
            nature: string that describes the origin of the chromosome, useful for debugging but not necessary for the process to run
        '''
        self.parameters = parameters
        self.probaEvolution = 0.0
        self.probaBonus = 0.0
        self.evaluated = False
        self.age = 0
        self.nature = nature
        self.mutations = []
            
    def toPrint(self):
        '''
        printing function that displays the parameters of the chromosome.
        '''
        print self.parameters

class GeneticProcess():
    
    ''' initialization function '''
    def __init__(self, nbChromo = 100, nbTotalStep = 100, toPrint=True):
        '''
        Initializing the process.
        The parameters of a genetic process are the size of population described by nbChromo
        and the number of step in the process, represented by nbTotalStep.
        There is also a parameter that lead the printing behaviour.
        -- IN
            nbChromo : size of the population (int) default = 100
            nbTotalStep : number of steps (int) default = 100
            toPrint : boolean that settles if the function must print its results (boolean) default = True
        '''
        self.toPrint = toPrint
        # setting the training ready
        self.nStep = 0                      # number of the current step
        self.nbTotalStep = nbTotalStep      # total number of steps to perform
        self.nbAjoutRandom = nbChromo/10    # number of new chromosomes to add randomly at each iteration
        self.scoreMax = 0                   # we keep in memory the highest score among the chromosomes
        # creating initial population
        self.pop = self.generatePop(nbChromo)   # set containing all the chromosomes, at first is randomly generated
        if self.toPrint:
            print " nb Chromosomes :", len(self.pop)
            print " nb Etapes :", nbTotalStep
            print ""

    ''' to override '''
    # we here define the function to override
    # (non nécessaire mais bon, on oublie jamais vraiment le java, hein ?)
    def evaluatePop(self):
        '''
        function that attributes a score to each chromosome of the pop
        -> note that at each step, some chromosomes already posess a score from the previous step,
            there is no need to compute anew a score for them.
        '''
        pass  

    def generateRandomParam(self, param):
        '''
        function that generates random parameters for the chromosomes. 
        the function takes as an input the name of a parameter that should be a key of the 
        parameters dictionary in the chromosomes.
        -- IN
            param : name of the param to generate (string)
        '''
        pass 

    ''' main algorithm functions'''
    def generatePop(self, n):
        '''
        function that create an array of size n of new chromosomes
        '''
        pop = [Chromosome(self.generateRandomParameters(),nature="random") for _ in range(n)]
        return pop
    
    def evaluationStep(self):
        '''
        Step A : EVALUATION
        function that handles the evaluation step : it calls the evaluatePop method that
        should have been overwritten and marks the chromosomes as 'evaluated' and increase their age
        '''
        self.evaluatePop()
        for chromo in self.pop:
            chromo.evaluated = True
            chromo.age += 1
            
    def selectionStep(self):
        '''
        Step B : SELECTION
        during this step we only keep the first half of the chromosomes, destroying the others.
        '''
        l = {chromo : chromo.probaEvolution for chromo in self.pop}.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.pop = [l[i][0] for i in range(len(self.pop)/2)]
          
    def croisementStep(self):
        '''
        STEP C : CROSSING
        We create children from the remaining parents, and add some new randomly generated chromosomes
        '''
        # creating children
        parents = random.sample(self.pop, len(self.pop)-self.nbAjoutRandom)
        random.shuffle(parents)
        for i in range(len(parents)/2):
            # each pair of parents generates two children, distributing their genetic material
            [chromo1, chromo2] = [parents[2*i], parents[2*i+1]]
            # performing cross over
            params = chromo1.parameters.keys()
            ind = random.sample(params,random.randint(0,len(chromo1.parameters)))
            chromo3 = Chromosome()
            chromo4 = Chromosome()
            chromo3.nature = "child"
            chromo4.nature = "child"
            if random.random()>0.5:
                # first case : the material is split and distributed
                param3 = {key : (chromo1.parameters[key] if key in ind else chromo2.parameters[key]) for key in params}
                param4 = {key : (chromo2.parameters[key] if key in ind else chromo1.parameters[key]) for key in params}
            else:
                # second case : the material is split and mixed
                param3 = {key : (0.5*(chromo1.parameters[key]+chromo2.parameters[key]) if key in ind else chromo2.parameters[key]) for key in params}
                param4 = {key : (0.5*(chromo1.parameters[key]+chromo2.parameters[key]) if key in ind else chromo1.parameters[key]) for key in params}
                chromo3.nature += " -modified"
                chromo4.nature += " -modified"
            chromo3.parameters = param3
            chromo4.parameters = param4
            # handling mutation
            while random.random()<0.5:
                # with probability 1/2 the first child mutates
                r = random.randint(0,len(chromo3.parameters)-1)
                param = chromo3.parameters.keys()[r]
                chromo3.parameters[param] = self.generateRandomParam(param)
                chromo3.mutations.append(param)
            while random.random()<0.5:
                # with probability 1/2 the second child mutates
                r = random.randint(0,len(chromo4.parameters)-1)
                param = chromo4.parameters.keys()[r]
                chromo4.parameters[param] = self.generateRandomParam(param)
                chromo4.mutations.append(param)
            # adding resulting chromosome to pop
            self.pop.append(chromo3)
            self.pop.append(chromo4)
        self.pop = self.pop + self.generatePop(self.nbAjoutRandom)
       
    def processStep(self):
        ''' function that handles one complete step '''
        if self.toPrint:
            print "running step",self.nStep
        self.evaluationStep()
        self.selectionStep()
        self.croisementStep()
        self.nStep += 1
            
    def run(self):
        ''' running function for the genetic algorithm '''
        for _ in range(self.nbTotalStep):
            self.processStep()
            if self.toPrint:
                if self.pop[0].probaEvolution > self.scoreMax:
                    self.scoreMax = self.pop[0].probaEvolution
                    print self.pop[0].nature, self.pop[0].mutations
                print self.pop[0].probaEvolution,self.pop[0].probaBonus
        if self.toPrint:
            print self.pop[0].parameters
        self.saveResults()

    ''' méthodes de sauvegarde des résultats '''

    def saveResults(self):
        '''
        function that saves the results of the genetic algorithm in a file in the preprocessingData folder.
        The previous results aren't deleted, as the new as concatened to the old.
        This way several results are stored and observable in the same file.
        '''
        dic = self.pop[0].parameters
        dfNew = pd.DataFrame.from_dict(data = dic,orient = "index")
        dfNew.columns = ['nbChr'+str(len(self.pop))+'-nbStep'+str(self.nbTotalStep)+'-score:'+str(self.pop[0].probaEvolution)] 
        os.chdir(UtilsConstants.path+"/preprocessingData")
        df = pd.DataFrame.from_csv(self.name+"-results.csv",sep=";")
        if len(df)<len(dfNew):
            # on archive la vieille base
            df.to_csv(self.name+"-results(old).csv",sep=";")
            df = dfNew
        else:
            df = df.join(dfNew,rsuffix="-"+str(int(self.pop[0].probaEvolution))+"-"+str(len(df.columns)),sort=True)
        df.sort_index(inplace=True)
        df.to_csv(self.name+"-results.csv",sep=";")
        if(self.name == "Step01Genetic"):
            os.chdir(UtilsConstants.pathConstants)
            UtilsConstants.saveDict(dic,"parametersStep01.txt","_")
        elif(self.name == "Step03Genetic"):
            os.chdir(UtilsConstants.pathConstants)
            UtilsConstants.saveDict(dic,"parametersStep03.txt","_")
        
        