# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

import codecs
import os

import  Constants
import IOFunctions
import KeywordSubset

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

<<<<<<< HEAD
# KeywordSubset.extractSubset(toPrint=True)

GraphPreprocess.extractGraphFromSubset("graphcomplet", Constants.pathCodeNAF)
=======
        
>>>>>>> 5f2b3af3ee6b9f885ae8c072803991484494dd33


<<<<<<< HEAD
# KeywordSubset.computeAllNAFGraph()
=======
# # create example
# IOFunctions.extractGraphFromSubset("subset_NAF_0111Z", Constants.pathCodeNAF)


## Create all keywords
#IOFunctions.extractKeywordsFromGraph("subset_NAF_0111Z", Constants.pathCodeNAF)



# Create for all NAF codes
KeywordSubset.createAllNAFSubset(200)

#KeywordSubset.computeAllNAFGraph()
>>>>>>> 5f2b3af3ee6b9f885ae8c072803991484494dd33
