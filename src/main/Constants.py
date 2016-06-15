# -*- coding: utf-8 -*-
'''
Created on 12 mai 2016

@author: Kévin Bienvenu
'''

import os

user = os.path.dirname(os.path.abspath(__file__)).split("\\")[2]


path = os.path.join("C:/","Users",user,"Documents","GitHub","Keywords")
pathAgreg = os.path.join("C:/","Users",user,"Google Drive","Camelia Tech","Donnees entreprise","Agregation B Reputation")
pathSubset = os.path.join("C:/","Users",user,"Documents","GitHub","Keywords","subsets")
pathCodeNAF = os.path.join("C:/","Users",user,"Documents","GitHub","Keywords","preprocessingData","codeNAF")


parameters = {'A':0.02,
              'B':2.5,
              'C':0.06,
              'D':0.0,
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