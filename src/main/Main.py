# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

import codecs
import os

import  Constants
import IOFunctions


# IOFunctions.extractSubset()
IOFunctions.extractGraphFromSubset("graphcomplet", Constants.pathCodeNAF, localKeywords=True)
# IOFunctions.extractKeywordsFromGraph("graphcomplet_size_5000", Constants.pathCodeNAF)


# kw = []
# os.chdir(Constants.path+"/motscles")
# with codecs.open("keywords.txt","r","utf8") as fichier:
#     for line in fichier:
#         print [line]
# with codecs.open("keywords.txt","r","utf8") as fichier:
#     for line in fichier:
#         a = line[:-1]
#         while a[-1]==" ":
#             a = a[:-1]
#         kw.append(a)
# with codecs.open("keywords.txt","w","utf8") as fichier:
#     for k in kw:
#         fichier.write(k+"\r\n")


# # create example
# IOFunctions.extractGraphFromSubset("subset_NAF_0111Z", Constants.pathCodeNAF)


# # Create all keywords
# os.chdir(Constants.pathCodeNAF)
# for directory in os.listdir("."):
#     if directory[0]=="s":
#         IOFunctions.extractKeywordsFromGraph(directory, Constants.pathCodeNAF)


# Create for all NAF codes
# KeywordSubset.createAllNAFSubset(200)
