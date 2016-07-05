# -*- coding: utf-8 -*-
'''
Created on 6 juin 2016

@author: Kévin Bienvenu

Class GeneticKeywords01
herited from Genetic Process

handles the learning of the step 01 : extracting keywords from graph
'''

from operator import itemgetter
import os, random, nltk
from nltk.corpus import stopwords

import GeneticTraining, IOFunctions, KeywordSelector


class GeneticKeywords01(GeneticTraining.GeneticProcess):
    '''
    Class holding the behaviour of the step 01 learning:
    each chromosome contain parameters of an evaluation function
    that extract keywords out of a description (string).
    The evaluation is performed using comparison to an actual and manually extracted keywords list.
    '''
    def __init__(self, nbDesc=0, nbChromo = 100, nbTotalStep = 100, toPrint=True):
        self.toPrint = toPrint
        self.name = "Step01Genetic"
        if self.toPrint:
            print "================================="
            print "= Genetic algorithm for step 01 ="
            print "================================="
            print ""
        # on prépare l'évaluation
        self.codeNAF = ""
        self.descriptions = {}
        self.french_stopwords = set(stopwords.words('french'))
        self.stem = nltk.stem.snowball.FrenchStemmer()
        self.scoreMax = 0 
        entreprises = []
        os.chdir(os.path.join(GeneticTraining.Constants.path,"preprocessingData"))
        with open("trainingSet.txt","r") as fichier:
            for line in fichier:
                entreprises.append(line.split("_"))
                entreprises[-1][-1] = entreprises[-1][-1].split("=")[:-1]           
        self.keywordSet, self.dicWordWeight = IOFunctions.importKeywords()
        if nbDesc>0:
            entreprises = random.sample(entreprises, min(len(entreprises),nbDesc))
        self.descriptions = {s[1]:[IOFunctions.tokenizeAndStemmerize(s[1],
                                                                        keepComa=True,
                                                                        french_stopwords=self.french_stopwords,
                                                                        stem=self.stem),
                                   s[2],
                                   s[0]] 
                             for s in entreprises}
        # on génére le genetic process
        GeneticTraining.GeneticProcess.__init__(self, nbChromo, nbTotalStep, toPrint)

    ''' méthodes overidée '''
    def generatePop(self, n):
        pop = [GeneticTraining.Chromosome(self.generateRandomParameters(),nature="random") for _ in range(n)]
        return pop

    def generateRandomParam(self, param): 
        if param == 'A':
            return 0.02  
        elif param == 'B':
            return 2.5  
        elif param == 'C':
            return 0.06
        elif param == "D":
            return 0.0
        elif param == 'E':
            return 0.0
        elif param == 'F':
            return random.uniform(0.0,2.0)
        elif param == "G":
            return random.uniform(0.0,1.0)
        elif param == 'H':
            return random.uniform(0.0,1.0)
        elif param == "J":
            return random.uniform(0.0,1.0)
        elif param == "N":
            return 4.0
        elif param == "I0":
            return random.uniform(3.0,5.0)
        elif param == "I1":
            return random.uniform(3.0,5.0)
        elif param == "I2":
            return random.uniform(1.0,3.0)
        elif param == "I-1":
            return random.uniform(0.5,2.5)
        else:
            return random.uniform(0.0,5.0)
        
    def evaluatePop(self):  
        compt = IOFunctions.Compt(self.descriptions, 10)
        params = []
        for chromo in self.pop:
            if chromo.evaluated:
                continue
            params.append(chromo.parameters)
            chromo.score = [] 
        for desc in self.descriptions.values():
            if self.toPrint:
                compt.updateAndPrint()
            if desc[2] != self.codeNAF:
                self.setCodeNAF(desc[2])
            dicKw = KeywordSelector.extractFromDescription(string = None, 
                                                           keywords = self.keywordSet, 
                                                           dicWordWeight = self.dicWordWeight,
                                                           french_stopwords = self.french_stopwords,
                                                           stem = self.stem,
                                                           parameterList = params,
                                                           toPrint=False,
                                                           preprocessedString = desc[0])
            k=0
            for i in range(len(self.pop)):
                if self.pop[i].evaluated:
                    continue
                l = dicKw[k].items()
                l.sort(key=itemgetter(1),reverse=True)
                if len(l)==0:
                    self.pop[i].score.append(0.0)    
                else:               
                    self.pop[i].score.append(self.matchingKeywordList(desc[1],[l[j][0] for j in range(len(l))]))    
                k+=1
            if not k==len(dicKw):
                print "problème"
        for chromo in self.pop:
            if chromo.evaluated:
                continue
            chromo.probaEvolution = (sum(chromo.score)/len(chromo.score))
            del chromo.score
 
    ''' méthodes auxiliaires ''' 
            
    def matchingKeywordList(self, list1, list2):
        '''
        function that returns a score between 0 and 1
        according on how much two list look like each other
        non-symmetric function ! 
        list1 : keywords to match
        list2 : keywords provided by the algorithm to test
        -- ALGO
        score = coef1 * coef 2
        coef1 = len(list1) / len(list1 && list2)
        coef2 = 1 / (max(list1 in list2) - len(list1))
        -- CAS PARFAIT:
        tous les mots sont présents et en tête:
        coef1 = 1, coef2 = 1
        score = 1
        '''
        set1 = set(list1)
        set2 = set(list2)
        if len(set1) == 0:
            print "petit souci"
            return 0.0
        if len(set2) == 0:
            return 0.0
        l = len(set1 & set2)
        coef1 = 1.0*l/len(set1)
        if l>0:
            indsum = 0
            indnb = 0
            for i in range(len(list2)):
                if list2[i] in list1:
                    indsum += i+1
                    indnb += 1
            indnb = (indnb+1)*indnb/2
            coef2 = 1.0*indnb/indsum
        else:
            coef2 = 0.0
        score = coef1*coef2
        score = -score*(score-2.0)
        return score
    
    def generateRandomParameters(self):
        keys = ['A','B','C','D','E','F','G','H',
                'I0','I1','I2','I-1',
                'J','N']
        return {key : self.generateRandomParam(key) for key in keys}    
      
    def setCodeNAF(self, codeNAF):
        self.codeNAF = codeNAF[-5:]
        self.keywordSet, self.dicWordWeight = IOFunctions.importKeywords(codeNAF)
     
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            