# -*- coding: utf-8 -*-
'''
Created on 14 avr. 2016

@author: Kevin Bienvenu
'''

import nltk
import codecs
from nltk.corpus import stopwords


def computeTokens():
    # chargement des stopwords fran�ais
    french_stopwords = set(stopwords.words('french'))
    # initialisation du vecteur final
    motscles = []
    ####
    # Fichier des pages jaunes
    ####
    with codecs.open("../../mots-cles-pj.txt",'r',"utf-8") as openfile:
        lines = openfile.readlines()
        print "nombre de lignes à traiter dans le fichier pj:",len(lines)
        for line in lines:
            if len(line)>3:
                tokens = nltk.word_tokenize(line[4:].lower(),'french')
                tokens = [token for token in tokens if len(token)>1 and token not in french_stopwords]
                motscles += tokens          
    #####
    # Fichier naf
    #####
    codeNafDict = {}
    with codecs.open("../../mots-cles-naf.txt",'r',"utf-8") as openfile:
        lines = openfile.readlines()
        print "nombre de lignes à traiter dans le fichier naf:",len(lines)
        for line in lines:
            if len(line)>3:
                tokens = nltk.word_tokenize(line[11:].lower(),'french')
                tokens = [token for token in tokens if len(token)>1 and token not in french_stopwords]
                codeNafDict[line[4:10]] = tokens
                motscles += tokens 
    #####
    # fichier kompass
    #####
    kompassCategoryDict = {}
    kompasSubCategoryToCategoryDict = {}
    lastkey = ""
    with codecs.open("../../mots-cles-kompass.txt","r","utf-8") as openfile:
        lines = openfile.readlines()
        print "nombre de lignes à traiter dans le fichier kompass:",len(lines)
        for line in lines:
            if len(line)>3:
                if line[0:8]=="        ":
                    kompassCategoryDict[lastkey].append(line[8:len(line)-1])
                    kompasSubCategoryToCategoryDict[line[8:len(line)-1]] = lastkey
                if line[0:4]=="    ":
                    lastkey = line[4:len(line)-1]
                    kompassCategoryDict[lastkey] = []
                tokens = nltk.word_tokenize(line[8:].lower(),'french')
                tokens = [token for token in tokens if len(token)>1 and token not in french_stopwords]
                motscles += tokens 
    # enlever les doublons
    motscles = list(set(motscles))
    toremove = []
    # simplifier les mots présents
    for mot in motscles:
        if mot[0:len(mot)-1] in motscles:
            toremove.append(mot)       
    for mot in toremove:
        motscles.remove(mot)
    
    #####
    # saving mots clés
    #####
    print "nombre de tokens:",len(motscles)
    with codecs.open("../../tokens.txt",'w','utf-8') as openfile:
        for mot in motscles:
            openfile.write(mot+"\n")


computeTokens()        

# import codecs
# 
# with codecs.open("../../mots-cles-kompass.txt","r","utf-8") as openfile:
#     lines = openfile.readlines()
# with codecs.open("../../mots-cles-kompass.txt","w","utf-8") as openfile:
#     for line in lines:
#         openfile.write(line)

            
            
            
            
            
            