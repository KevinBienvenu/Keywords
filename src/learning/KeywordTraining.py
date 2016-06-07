# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''
''' Extraction and Suggestion functions'''

import codecs
from operator import itemgetter
import os
import random

import nltk
from nltk.corpus import stopwords

from main import TextProcessing,IOFunctions,Constants


def suggestKeyword(description, codeNAF, graph, keywordSet, n=30):
    '''
    function that takes a description and a codeNAF and returns a list of suggested keywords
    -- IN
    description : string describing the description (string)
    codeNAF : string representing the code NAF (string)
    -- OUT
    keywordsList : array of keywords, in order of importance ([string])
    '''
    ## STEP 0 = Initializing
    [graphNodes, graphEdges, dicIdNodes] = graph
    dicWordWeight = {}
    origin = {}
    ## STEP 1 = Extracting only from description
    keywordFromDesc = TextProcessing.extractKeywordsFromString(description, keywordSet, dicWordWeight,toPrint= False)
    ## STEP 2 = Extracting only from codeNAF
    keywordFromNAF = IOFunctions.getSuggestedKeywordsByNAF(codeNAF)
    # merging previous dictionaries
    dicKeywords = {}
    for key in keywordFromDesc:
        dicKeywords[key] = keywordFromDesc[key]
        origin[key] = [1]
    coef = 2.0
    for key in keywordFromNAF:
        if not(key in dicKeywords):       
            coef=max(1.0,coef*0.95)
            continue
        origin[key].append(2)
        dicKeywords[key] *= coef
        coef=max(1.0,coef*0.95)
    ## STEP 3 = Extracting from Graph
    keywordFromGraph = extractFromGraph(graphNodes,graphEdges,dicIdNodes,dicKeywords)
    # merging last dice
    for key in keywordFromGraph:
        if not(key in dicKeywords):
            dicKeywords[key] = 0
            origin[key] = []
        dicKeywords[key] = keywordFromGraph[key]
        origin[key].append(3)
        
    ## STEP 4 = Printing / Returning
    l = dicKeywords.items()
    l.sort(key=itemgetter(1),reverse=True)
    return [k[0] for k in l[:min(n,len(l))]],[origin[k[0]] for k in l[:min(n,len(l))]]
    
def extractFromGraph(graphNodes, graphEdges, dicIdNodes, dicKeywords, n=10):
    '''
    function that extract extra keywords from a graph 

    pour rappel :
    - graphNodes V : dic{id, [name, genericite, dic{NAF:value}]}
    - graphEdges E : dic{(id1,id2),[value,nbOccurence]}
    '''
    # on parcourt toutes les arrêtes:
    potentielNodes = {}
#     print graphEdges
    for edge in graphEdges:
        # si le premier noeud fait partie des sélectionnés
        if edge[0] in graphNodes and graphNodes[edge[0]][0] in dicKeywords:
            # et que le second n'en fait pas partie
            if edge[1] in graphNodes and not(graphNodes[edge[1]][0] in dicKeywords):
                # on l'ajoute au dic s'il n'y est pas déjà
                if not(graphNodes[edge[1]][0] in potentielNodes):
                    potentielNodes[graphNodes[edge[1]][0]] = [0.0,0]
                # on met à jour sa valeur dans le dictionnaire
                potentielNodes[graphNodes[edge[1]][0]][0] += dicKeywords[graphNodes[edge[0]][0]]
                potentielNodes[graphNodes[edge[1]][0]][1] += 1
        # même chose pour le cas symétrique
        elif edge[1] in graphNodes and graphNodes[edge[1]][0] in dicKeywords:
            if edge[0] in graphNodes and not(graphNodes[edge[0]][0] in dicKeywords):
                if not(graphNodes[edge[0]][0] in potentielNodes):
                    potentielNodes[graphNodes[edge[0]][0]] = [0.0,0]
                potentielNodes[graphNodes[edge[0]][0]][0] += dicKeywords[graphNodes[edge[1]][0]]
                potentielNodes[graphNodes[edge[0]][0]][1] += 1
    for key in potentielNodes:
        potentielNodes[key] = potentielNodes[key][0]/(2+potentielNodes[key][1])
    # on extrait les n plus gros
    l = potentielNodes.items()
    l.sort(key=itemgetter(1),reverse=True)
    return {k[0]:k[1] for k in l[:min(n,len(l))]}
    
''' Auxiliary functions for the training software'''
       
def pickNewRow(interface):
    codeNAF = "nan"
    for line in interface.csvclean.sample(1).itertuples():
        # extracting info
        description = line[3].decode("utf8")
        codeNAF = line[2]
        lastIndex = line[0]
    keywords,origins = suggestKeyword(description, codeNAF, interface.graph, interface.keywordSet)
    interface.codeNAF = codeNAF
    interface.desc = description
    interface.lastIndex = lastIndex
    interface.keywords = keywords
    interface.origins = origins
    interface.vkeywords = []
    
def saveRow(interface):
    os.chdir(Constants.pathCodeNAF)
    os.chdir("..")
    with open("processedRows.txt","a") as fichier:
        fichier.write(str(interface.lastIndex)+"\n")
    interface.indexToDrop.append(interface.lastIndex)
    interface.csvdesc.drop(interface.indexToDrop,inplace=True)
    interface.csvclean.drop(interface.indexToDrop,inplace=True)
    interface.indexToDrop = []
    with codecs.open("trainingSet.txt","a",'utf8') as fichier:
        fichier.write(str(interface.codeNAF)+"_"+interface.desc+"_")
        for keyword in interface.keywords:
            fichier.write(keyword+"=")
        fichier.write("\n")
    os.chdir(Constants.pathCodeNAF+"/codeNAF_"+str(interface.codeNAF))
    with codecs.open("trained_entreprises.txt","a","utf8") as fichier:
        fichier.write(str(interface.codeNAF)+"_"+interface.desc+"_")
        for keyword in interface.keywords:
            fichier.write(keyword+"=")
        fichier.write("\n")

def signaleRow(interface):
    os.chdir(Constants.pathCodeNAF)
    os.chdir("..")
    interface.indexToDrop.append(interface.lastIndex)
    interface.csvdesc.drop(interface.indexToDrop,inplace=True)
    interface.csvclean.drop(interface.indexToDrop,inplace=True)
    interface.indexToDrop = []
    with codecs.open("signaledRows.txt","a",'utf8') as fichier:
        fichier.write(str(interface.codeNAF)+"_"+interface.desc)
        fichier.write("\n")
        
def getCsvWithCriteres(interface):
    ''' '''
    
    test = interface.csvdesc.codeNaf.notnull()
    if interface.criteres['codeNAF'][3]:
        test = test & interface.csvdesc.codeNaf.str.match(interface.criteres['codeNAF'][2])
        interface.keywordSet = IOFunctions.importKeywords(path = Constants.pathCodeNAF+"/codeNAF_"+interface.criteres['codeNAF'][2])
    funNbMot = lambda x : len(x.split(" "))
    if interface.criteres['nbWordMin'][3]:
        test = test & (interface.csvdesc.description.apply(funNbMot)>int(interface.criteres['nbWordMin'][2]))
    if interface.criteres['nbWordMax'][3]:
        test = test & (interface.csvdesc.description.apply(funNbMot)<int(interface.criteres['nbWordMax'][2]))
    interface.csvclean = interface.csvdesc.copy()
    interface.csvclean.loc[~test] = None
    interface.csvclean.dropna(axis=0,how='any',inplace=True)
        
''' Auxiliary function for the training algorithms'''  
        
def matchingKeywordList(list1, list2):
    '''
    function that returns a score between 0 and 1
    according on how much two list look like each other
    '''
    set1 = set(list1)
    set2 = set(list2)
    if len(set1) == 0:
        return 0.0
    if len(set2) == 0:
        print "petit souci"
        return 0.0
    score = 0.5*(1.0*len(set1 & set2)/len(set1)+1.0*len(set1 & set2)/len(set2))
    score = -score*(score-2.0)
    return score

def generateRandomParameters():
    keys = ['A','B','C','D','E','F','G','H',
            'I0','I1','I2','I3','I4','I-2','I-1',
            'J','N']
    return {key : generateRandomParam(key) for key in keys}    

def generateRandomParam(param): 
    if param == 'A':
        return random.uniform(0.0,1.0/30)  
    elif param == 'C':
        return random.uniform(0,1.0)
    elif param == 'J':
        return random.uniform(0,5.0)
    elif param == 'N':
        return random.uniform(0,5.0)
    elif param[0] == "I":
        return random.uniform(-1.0,5.0)
    else:
        return random.uniform(-1.0,3.0)

def evaluatePop(tSet):  
    compt = IOFunctions.initProgress(tSet.descriptions, 10)
    params = [chromo.parameters for chromo in tSet.pop]
    for chromo in tSet.pop:
        chromo.score = [] 
    for desc in tSet.descriptions.values():
        compt = IOFunctions.updateProgress(compt)
        dicKw = TextProcessing.extractKeywordsFromString(string = None, 
                                                         keywords = tSet.keywordSet, 
                                                         dicWordWeight = tSet.dicWordWeight,
                                                         french_stopwords = tSet.french_stopwords,
                                                         stem = tSet.stem,
                                                         parameterList = params,
                                                         toPrint=False,
                                                         preprocessedString = desc[0])
        for i in range(len(params)):
            l = dicKw[i].items()
            l.sort(key=itemgetter(1),reverse=True)
            tSet.pop[i].score.append(matchingKeywordList([l[j][0] for j in range(min(len(l),5))], desc[1]))    
    for chromo in tSet.pop:
        chromo.probaEvolution = (sum(chromo.score)/len(chromo.score)+max(chromo.score)+min(chromo.score))/3  
        del chromo.score
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
        
        