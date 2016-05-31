# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''

from operator import itemgetter
import os

from main import TextProcessing, GraphPreprocess, IOFunctions, Constants
import pandas as pd


def suggestKeyword(description, codeNAF):
    '''
    function that takes a description and a codeNAF and returns a list of suggested keywords
    -- IN
    description : string describing the description (string)
    codeNAF : string representing the code NAF (string)
    -- OUT
    keywordsList : array of keywords, in order of importance ([string])
    '''
    ## STEP 0 = Initializing
    [graphNodes, graphEdges, dicIdNodes] = IOFunctions.importGraph("graphcomplet")
    keywords = IOFunctions.importKeywords()
    dicWordWeight = {}
    ## STEP 1 = Extracting only from description
    keywordFromDesc = TextProcessing.extractKeywordsFromString(description, keywords, dicWordWeight, False)
    ## STEP 2 = Extracting only from codeNAF
    keywordFromNAF = IOFunctions.getSuggestedKeywordsByNAF(codeNAF)
    
    # merging previous dictionaries
    dicKeywords = {}
    for key in keywordFromDesc:
        dicKeywords[key] = keywordFromDesc[key]
    coef = 2.0
    for key in keywordFromNAF:
        if not(key in dicKeywords):       
            coef=max(1.0,coef*0.95)
            continue
        dicKeywords[key] *= coef
        coef=max(1.0,coef*0.95)
    
    ## STEP 3 = Extracting from Graph
    keywordFromGraph = extractFromGraph(graphNodes,graphEdges,dicIdNodes,dicKeywords)
    
    # merging last dice
    for key in keywordFromGraph:
        dicKeywords[key] = keywordFromGraph[key]
        
    ## STEP 4 = Printing / Returning
    IOFunctions.printSortedDic(dicKeywords, 30)
    
def extractFromGraph(graphNodes, graphEdges, dicIdNodes, dicKeywords, n=10):
    '''
    function that extract extra keywords from a graph 

    pour rappel :
    - graphNodes V : dic{id, [name, genericite, dic{NAF:value}]}
    - graphEdges E : dic{(id1,id2),[value,nbOccurence]}
    '''
    # on parcourt toutes les arrêtes:
    potentielNodes = {}
    for edge in graphEdges:
        # si le premier noeud fait partie des selectionnés
        if graphNodes[edge[0]][0] in dicKeywords:
            # et que le second n'en fait pas partie
            if not(graphNodes[edge[1]][0] in dicKeywords):
                # on l'ajoute au dic s'il n'y est pas déjà
                if not(graphNodes[edge[1]][0] in potentielNodes):
                    potentielNodes[graphNodes[edge[1]][0]] = 0
                # on met à jour sa valeur dans le dictionnaire
                potentielNodes[graphNodes[edge[1]][0]] += dicKeywords[graphNodes[edge[0]][0]]
        # même chose pour le cas symétrique
        elif graphNodes[edge[1]][0] in dicKeywords:
            if not(graphNodes[edge[0]][0] in dicKeywords):
                if not(graphNodes[edge[0]][0] in potentielNodes):
                    potentielNodes[graphNodes[edge[0]][0]] = 0
                potentielNodes[graphNodes[edge[0]][0]] += dicKeywords[graphNodes[edge[1]][0]]
    # on extrait les n plus gros
    l = potentielNodes.items()
    l.sort(key=itemgetter(1),reverse=True)
    return {k : dicKeywords[k] for k in l[:min(n,len(l))]}
    

def trainingProcess():
    print "=== Training Process ==="
    print ""
    os.chdir(Constants.path+"/preprocessingData")
    indexToDrop = []
    with open("processedRows.txt","r") as fichier:
        for line in fichier:
            try:
                indexToDrop.append(int(line[:-1]))
            except:
                pass
    os.chdir(Constants.pathAgreg)
    csvdesc = pd.read_csv("descriptions.csv")
    total = len(csvdesc)
    csvdesc.drop(indexToDrop,inplace=True)
    print "  ",len(indexToDrop),"rows already processed (",100.0*len(indexToDrop)/total,"%)"
    print "       ...",len(csvdesc),"to go !"
    print ""
    print "=="
    print ""
    flag = True
    os.chdir(Constants.path+"/preprocessingData")
    while flag:
        for line in csvdesc.sample(1).itertuples():
            print "= description :"
            print line
            print line[2]
            keywords = suggestKeyword(line[2], line[1])
            ncolumns = 3
            frac = len(keywords)/ncolumns
            for i in range(frac):
                for j in range(ncolumns):
                    print i+j*frac,":",keywords[i+j*frac],"  "
            print ""
            print "suggesting keywords ?"
            print "   (numbers separated by commas)"
            inputkey = input("=>")
            tab = [keywords[int(a)] for a in inputkey.split(",")]
            print ""
            print "validated keywords:",tab
            print ""
            lastIndex = line[0]
            with open("processedRows.txt","wb") as fichier:
                fichier.write(str(line[0])+"\n")
            
            with open("trainingSet.txt","wb") as fichier:
                fichier.write(str(line[1]+"_"+str(line[2])+"_"))
                for keyword in keywords:
                    fichier.write(keyword+"=")
                fichier.write("\n")
        csvdesc.drop(lastIndex)
        print ""
        inputkey = input("continue ? (y/n)")
        if inputkey=="n":
            flag=False
    print " END OF THE SESSION"
    print "  ",len(indexToDrop),"rows already processed (",100.0*len(indexToDrop)/total,"%)"
    print "       ...",len(csvdesc),"to go !"
    
    