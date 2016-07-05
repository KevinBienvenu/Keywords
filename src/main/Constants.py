# -*- coding: utf-8 -*-
'''
Created on 12 mai 2016

@author: Kévin Bienvenu
'''

import os, time
import numpy.linalg as lg
import numpy as np

user = os.path.dirname(os.path.abspath(__file__)).split("\\")[2]


path = os.path.join("C:/","Users",user,"Documents","GitHub","Keywords")
pathAgreg = os.path.join("C:/","Users",user,"Google Drive","Camelia Tech","Donnees entreprise","Agregation B Reputation")
pathSubset = os.path.join("C:/","Users",user,"Documents","GitHub","Keywords","subsets")
pathCodeNAF = os.path.join("C:/","Users",user,"Documents","GitHub","Keywords","preprocessingData","codeNAF")
pathClassifiers = os.path.join("C:/","Users",user,"Documents","GitHub","Keywords","preprocessingData","classifiers")

# About STEP 01
parameters = {'A':0.02,
              'B':2.5,
              'C':0.06,
              'D':1.0,
              'E':0.0,
              'F':1.4,
              'G':0.4,
              'H':0.8,
              'I0':4.0,
              'I1':4.0,
              'I2':2.0,
              'I-1':1.5,
              'J':0.7,
              'N':4.0}
# ABOUT STEP 01 NORMALISATION
valMax = (parameters['A']*165+parameters['B']/165+parameters['J'])*(parameters['F']*parameters["I0"])*(parameters['D'])/2.0
a = np.array([[valMax**3,valMax**2,valMax],[3*valMax**2,2*valMax, 1],[6*valMax,2,0]])
b = np.array([1,0,0])
normalisationParam = lg.solve(a,b)
normalisationFunction = lambda x : min(1.0,normalisationParam[-3]*x**3+normalisationParam[-2]*x*x+normalisationParam[-1]*x)

parametersGraph = {"nbVoisins1":0,
                   "nbVoisins":0,
                   "sumVoisins1":0.0,
                   "sumVoisins":0.0,
                   "propVoisins1":0.0,
                   "propSumVoisins1":0.0,
                   "size":0.0,
                   "Y":False}

thresholdGeneticLearning = 0.0

parametersGraphLearning = {
               'nbVoisins_alpha' : 0.16,
               'nbVoisins_gamma' : 0.4,
               'nbVoisins_delta' : 0.5,
               'nbVoisins_phi' : 0,
               'nbVoisins1_alpha' : 0,
               'nbVoisins1_gamma' : 0.25,
               'nbVoisins1_delta' : -0,
               'nbVoisins1_phi' : -0.28,
               'sumVoisins_alpha' : -0.73,
               'sumVoisins_gamma' : 0.85,
               'sumVoisins_delta' : 0,
               'sumVoisins_phi' : 0,
               'sumVoisins1_alpha' : -0.63,
               'sumVoisins1_gamma' : -0.33,
               'sumVoisins1_delta' : -0,
               'sumVoisins1_phi' : 0,
               'propVoisins1_alpha' : 0.02,
               'propVoisins1_gamma' : -0.3,
               'propVoisins1_delta' : -0.27,
               'propVoisins1_phi' : 0,
               'propSumVoisins1_alpha' : 0,
               'propSumVoisins1_gamma' : -0.45,
               'propSumVoisins1_delta' : 0,
               'propSumVoisins1_phi' : 0,
               'size_alpha' : 0,
               'size_delta' : 0,
               'size_gamma' : -0.07,
               'size_phi' : -0.23
               }

class Compt():
    ''' class which implements the compt object, 
    which main purpose is printing progress
    '''
    def __init__(self, completefile, p=10, printAlone=True):
        self.i = 0
        self.total = len(completefile)
        self.percent = p
        self.deltaPercent = p
        self.printAlone = printAlone

    def updateAndPrint(self):
        self.i+=1
        if 100.0*self.i/self.total >= self.percent:
            print self.percent,"%",
            self.percent+=self.deltaPercent
            if (self.deltaPercent==1 and self.percent%10==1) \
                or (self.deltaPercent==0.1 and ((int)(self.percent*10))%10==0) \
                or (self.i==self.total) \
                or not self.printAlone:
                    print ""
              
                    
def printTime(startTime):
    totalTime = (time.time()-startTime)
    hours = (int)(totalTime/3600)
    minutes = (int)((totalTime-3600*hours)/60)  
    seconds = (int)(totalTime%60)
    print "time : ",hours,':',minutes,':',seconds
                  
 