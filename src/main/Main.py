# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''
from main import KeywordSubset, Constants, GraphPreprocess

codeNAF = "6201Z"

GraphPreprocess.extractGraphFromSubset("codeNAF_"+codeNAF, Constants.pathCodeNAF)

