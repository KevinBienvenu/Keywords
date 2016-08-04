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

import GeneticTraining, IOFunctions, KeywordSelector, UtilsConstants
from main import UtilsConstants


class GeneticKeywords01(GeneticTraining.GeneticProcess):
    '''
    Class holding the behaviour of the step 01 learning:
    each chromosome contain parameters of an evaluation function
    that extract keywords out of a description (string).
    The evaluation is performed using comparison to a manually extracted keywords list.
    '''
    def __init__(self, nbDesc=0, nbChromo = 100, nbTotalStep = 100, toPrint=True):
        '''
        initializing the genetic process.
        the additional parameter is the number of description to perform the evaluation step on.
        By default the evaluation is performed on the whole training set.
        -- IN
            nbDesc : number of descriptions (int) default = 0
                (-> let 0 to perform on the whole training set)
            nbChromo : cf. GeneticProcess
            nbTotalStep : cf. GeneticProcess
        '''
        self.toPrint = toPrint
        self.name = "Step01Genetic"
        if self.toPrint:
            print "================================="
            print "= Genetic algorithm for step 01 ="
            print "================================="
            print ""
        # setting the evaluation ready
        self.codeNAF = ""
        self.descriptions = {}
        self.french_stopwords = set(stopwords.words('french'))
        self.stem = nltk.stem.snowball.FrenchStemmer()
        self.scoreMax = 0 
        # importing entreprises
        entreprises = []
        os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
        with open("trainingStep1.txt","r") as fichier:
            for line in fichier:
                entreprises.append(line.split("_"))
                entreprises[-1][-1] = [UtilsConstants.preprocessString(a) for a in entreprises[-1][-1].split("=")[:-1]]
        # importing keywords and equivalences         
        self.keywordSet = IOFunctions.importKeywords()
        self.dicWordWeight = UtilsConstants.importDicWordWeight()
        self.equivalences = IOFunctions.importSlugEquivalence()
        if nbDesc>0:
            entreprises = random.sample(entreprises, min(len(entreprises),nbDesc))
        self.descriptions = {s[0]:[UtilsConstants.tokenizeAndStemmerize(s[0],
                                                               keepComa=True,
                                                               french_stopwords=self.french_stopwords,
                                                               stem=self.stem),
                                   s[1]] 
                             for s in entreprises}
        # intializing the genetic process
        GeneticTraining.GeneticProcess.__init__(self, nbChromo, nbTotalStep, toPrint)

    ''' overriden methods '''
    def generateRandomParam(self, param): 
        '''
        function that settles the generation of new parameters for the chromosome
        It is possible here to change the range of exploration by selecting
        different bounds for the random choice over the parameters.
        '''
        return random.uniform(0.0,2.0)
        
    def evaluatePop(self):  
        '''
        evaluating the chromosome using the manually keywords extractions
        '''
        compt = UtilsConstants.Compt(self.descriptions, 10)
        for chromo in self.pop:
            if chromo.evaluated:
                continue
            chromo.score = []
            chromo.normalisationFunction = lambda x : x
        for desc in self.descriptions.values():
            # for each description we perform the evaluation of the chromosomes
            if self.toPrint:
                compt.updateAndPrint()
            dicKw = KeywordSelector.extractFromDescription(string = None, 
                                                           keywords = self.keywordSet, 
                                                           dicWordWeight = self.dicWordWeight,
                                                           equivalences = self.equivalences,
                                                           booleanMatchParfait = True,
                                                           french_stopwords = self.french_stopwords,
                                                           stem = self.stem,
                                                           parametersStep01 = [chromo.parameters for chromo in self.pop if not chromo.evaluated],
                                                           normalisationFunction= [chromo.normalisationFunction for chromo in self.pop if not chromo.evaluated],
                                                           toPrint=False,
                                                           preprocessedString = desc[0])

            for tupleChromoDic in zip([chromo for chromo in self.pop if not chromo.evaluated] , dicKw):
                if len(tupleChromoDic[1])==0:
                    tupleChromoDic[0].score.append(0.0)    
                else:    
                    l = tupleChromoDic[1].items()
                    l.sort(key=itemgetter(1), reverse=True)           
                    tupleChromoDic[0].score.append(self.matchingKeywordList(desc[1],[UtilsConstants.preprocessString(a[0]) for a in l]))    
        # performing the mean over the whole set of scores
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
            print "len(set1)=0 :",list1,list2
            return 0.0
        if len(set2) == 0:
            print "len(set2)=0 :",list1,list2
            return 0.0
        l = len(set1 & set2)
        if l == 0:
            print "len(l)=0 :",list1,list2
            return 0.0
        # nombre de mot retrouvés
        coef1 = 1.0*l/len(set1)
        # gestion de l'ordre
        coef2 = 1.0-1.0*sum([abs(list1.index(kw)-list2.index(kw)) if kw in list2 else l for kw in list1])/(l*l)
        score = coef1*coef2
        return score
    
    def generateRandomParameters(self):
        keys = ["freqSlugGamma",
                "freqSlugAlpha",
                "placeSecondTier",
                "nbCommaGamma",
                "placeDernierTier",
                "placePremierTier",
                "nbCommaAlpha",
                "placeMot0",
                "placeMot1",
                "placeMot2",
                "coefProxi",
                "placeMot-1"]
        return {key : self.generateRandomParam(key) for key in keys}    
      
       
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            