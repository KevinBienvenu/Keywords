# -*- coding: utf-8 -*-
'''
Created on 26 avr. 2016

@author: Kévin Bienvenu
'''

import codecs
import os
import numpy as np

import IOFunctions
import TextProcessing
import Constants


path = Constants.path
pathAgreg = Constants.pathAgreg
pathSubset = Constants.pathSubset


# importing code NAF
def extractingNAFKeyWordsFromInternet():
    codeNAFs = {}
    with codecs.open("mots-cles-naf.txt","r",encoding="utf-8") as fichier:
        for line in fichier:
            codeNAFs[line.split(" ")[4]] = line[11:]
             
    with codecs.open("mots-cles-naf-preprocess.txt","w",encoding="utf-8") as fichier:
        j=0
        percent = 10
        total = len(codeNAFs)
        for codeNAF in codeNAFs:
            j+=1
            if 100.0*j/total>percent:
                print percent,"% -",
                percent+=10
            (_,comprend, comprendpas) = IOFunctions.extractNAFDesc(codeNAF)
            ennonce = TextProcessing.nltkprocess(codeNAFs[codeNAF])
            fichier.write(codeNAF)
            fichier.write("$")
            for i in range(len(ennonce)):
                fichier.write(ennonce[i])
                if i<len(ennonce)-1:
                    fichier.write(",")
            fichier.write("$")
            for i in range(len(comprend)):
                fichier.write(comprend[i])
                if i<len(comprend)-1:
                    fichier.write(",")
            fichier.write("$")
            for i in range(len(comprendpas)):
                fichier.write(comprendpas[i])
                if i<len(comprendpas)-1:
                    fichier.write(",")
            fichier.write("$")
            fichier.write("\n")

def processingNAFKeyWords():
    with codecs.open("mots-cles-naf-preprocess.txt","r",encoding="utf-8") as fichier:
        dic = {}
        codeNAFs = {}
        for line in fichier:
            tab = line[:-1].split("$")
            codeNAFs[tab[0]] = [tab[1].split(","),tab[2].split(","),tab[3].split(",")]
            for word in tab[1].split(","):
                if not(word in dic):
                    dic[word] = 0
                dic[word] += 1
            for word in tab[2].split(","):
                if not(word in dic):
                    dic[word] = 0
                dic[word] += 1
            for word in tab[3].split(","):
                if not(word in dic):
                    dic[word] = 0
                dic[word] += 1
    #     print len(dic)
    #     dic= sorted(dic.items(), key=operator.itemgetter(1),reverse=True)
    #     for i in range(len(dic)):
    #         print dic[i][0],dic[i][1]
    
    
    with codecs.open("mots-cles-naf-preprocess2.txt","w",encoding="utf-8") as fichier:
        for codeNAF in codeNAFs:
            for mot in codeNAFs[codeNAF][2]:
                if mot in codeNAFs[codeNAF][0] or mot in codeNAFs[codeNAF][1]:
                    try:
                        codeNAFs[codeNAF][0].remove(mot)
                    except:
                        pass
                    try:
                        codeNAFs[codeNAF][1].remove(mot)
                    except:
                        pass
            codeNAFs[codeNAF][0] = np.unique(codeNAFs[codeNAF][0])
            codeNAFs[codeNAF][1] = np.unique(codeNAFs[codeNAF][1])
            codeNAFs[codeNAF][2] = np.unique(codeNAFs[codeNAF][2])
            fichier.write(codeNAF)
            fichier.write("$")
            for i in range(len(codeNAFs[codeNAF][0])):
                if codeNAFs[codeNAF][0][i] in dic \
                    and dic[codeNAFs[codeNAF][0][i]]>1 \
                    and dic[codeNAFs[codeNAF][0][i]]<200:
                    fichier.write(codeNAFs[codeNAF][0][i])
                    if i<len(codeNAFs[codeNAF][0])-1:
                        fichier.write(",")
            fichier.write("$")
            for i in range(len(codeNAFs[codeNAF][1])):
                if codeNAFs[codeNAF][1][i] in dic \
                    and dic[codeNAFs[codeNAF][1][i]]>1 \
                    and dic[codeNAFs[codeNAF][1][i]]<200:
                    fichier.write(codeNAFs[codeNAF][1][i])
                    if i<len(codeNAFs[codeNAF][1])-1:
                        fichier.write(",")
            fichier.write("$")
            for i in range(len(codeNAFs[codeNAF][2])):
                if codeNAFs[codeNAF][2][i] in dic \
                    and dic[codeNAFs[codeNAF][2][i]]>1 \
                    and dic[codeNAFs[codeNAF][2][i]]<200:
                    fichier.write(codeNAFs[codeNAF][2][i])
                    if i<len(codeNAFs[codeNAF][2])-1:
                        fichier.write(",")
            fichier.write("$")
            fichier.write("\n")
    
def pipelineNAF():
#     extractingNAFKeyWordsFromInternet()
    processingNAFKeyWords()
  
os.chdir(path)  
pipelineNAF()    

# print IOFunctions.extractNAFDesc("17.29Z")