# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''
from learning.GraphLearning import Step3Classifier
''' Extraction and Suggestion functions'''

import codecs
from operator import itemgetter
import os

from learning import GeneticKeywords03
from main import IOFunctions, Constants, TextProcessing
import pandas as pd

def pipeline(descriptions, nbMot = 20, printGraph = False):
    '''
    Pipeline function taking as input a dataframe with rows 'codeNAF' and 'description'
    and giving as output a list of keywords for each description in the dataframe
    -- IN:
    descriptions : pd.DataFrame with columns 'codeNaf' and 'description' at least
    nbMot : number of returned keywords, (int) default : 5
    -- OUT:
    keywords : list of lists of keywords [[string],[string], ...]
    '''
    # checking validity of inputs
    try:
        _ = descriptions.codeNaf
        _ = descriptions.description
    except:
        print "error : invalid input, missing columns"
    # importing graph and keywords
    os.chdir(os.path.join(Constants.pathCodeNAF,"graphcomplet"))
    graph = IOFunctions.importGraph("graphcomplet")
    keywordSet, _ = IOFunctions.importKeywords()
    keywords = []
    i = 0
    os.chdir(Constants.pathCodeNAF+"/graphtest")
    for line in descriptions[["codeNaf","description"]].values:
        keywords.append(suggestKeyword(line[1],line[0], graph, keywordSet, nbMot)[0])
        if printGraph:
            IOFunctions.saveGexfFile("graph_test_"+str(i)+".gexf", graph, keywords = keywords[-1])
        i+=1
    return keywords
        
    

def suggestKeyword(description, codeNAF, graph, keywordSet, localKeywords = False, n=50):
    '''
    function that takes a description and a codeNAF and returns a list of suggested keywords
    the recquired inputs are also the graph (for step 3) and the keywordSet (for step 1)
    an additional input is the number of returned keywords
    -- IN
    description : string describing the description (string)
    codeNAF : string representing the code NAF (string)
    graph : graph of keywords (GraphProcessing.GraphKeyword)
    keywordSet : dictionary of keywords with stems for values {keyword (str): [stems (str)]}
    -- OUT
    keywordsList : array of keywords, in order of importance ([string])
    origins : array of array of integers ([ [int, int, ...], ...])
    '''
    ## STEP 0 = Initializing
    dicWordWeight = {}
    origin = {}
    if localKeywords:
        keywordSet, _ = IOFunctions.importKeywords(codeNAF)
    ## STEP 1 = Extracting only from description
    keywordFromDesc = TextProcessing.extractKeywordsFromString(description, keywordSet, dicWordWeight,toPrint=False)
    print keywordFromDesc
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
    keywordFromGraph = extractFromGraph(graph,dicKeywords)
    print keywordFromGraph
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
    
def extractFromGraph(graph, dicKeywords, classifier=Step3Classifier()):
    '''
    function that extracts extra keywords from a graph 

    pour rappel :
    - graphNodes V : dic{id, [name, genericite, dic{NAF:value}]}
    - graphEdges E : dic{(id1,id2),[value,nbOccurence]}
    '''
    # on parcourt toutes les arrêtes:
    potentielNodes = {}
    print ""
    for name in dicKeywords:
        node = graph.getNodeByName(name)
        if node is None:
            continue
        node.state = 1
        for neighbour in node.neighbours:
            if not(neighbour.name in dicKeywords):
                if not(neighbour.id in potentielNodes):
                    potentielNodes[neighbour.id] = [0.0,0]
                potentielNodes[neighbour.id][0] += dicKeywords[name]
                potentielNodes[neighbour.id][1] += 1
    for key in potentielNodes:
        potentielNodes[key] = potentielNodes[key][0]*potentielNodes[key][1]
    # on extrait les n plus gros
    l = potentielNodes.items()
    l.sort(key=itemgetter(1),reverse=True)
    potentielNodes = [k[0] for k in l[:min(50,len(l))]]
    X = []
    for key in potentielNodes:
        graph.computeNodeFeatures(graph.graphNodes[key].name)
        X.append([graph.graphNodes[key].features[keyFeatures] for keyFeatures in GeneticKeywords03.globalParam])
    Y = classifier.predict(X)
    result = {}
    for a in zip(potentielNodes, Y):
        if a[1]==1:
            result[graph.graphNodes[a[0]].name] = 1
    return result
    
''' Auxiliary functions for the training software'''
       
def pickNewRow(interface):
    codeNAF = "nan"
    for line in interface.csvclean.sample(1).itertuples():
        # extracting info
        description = line[3].decode("utf8")
        codeNAF = line[2]
        lastIndex = line[0]
    keywords,origins = suggestKeyword(description, codeNAF, interface.graph, interface.keywordSet, True)
#     # on met à jour la couleur des noeuds dans le graphe
#     for i in range(len(origins)):
#         if keywords[i] in interface.graph.dicIdNodes:
#             color = 0
#             if 3 in origins[i]:
#                 color = 3
#             elif 1 in origins[i]:
#                 color = 1
#             interface.graph.graphNodes[interface.graph.dicIdNodes[keywords[i]]].setColor(color)
#     os.chdir(Constants.pathCodeNAF+"/../")
#     IOFunctions.saveGexfFile("graphTraining.gexf", interface.graph)
    if interface.currentStep.get()==3:        
        interface.keywords = []
        for i in range(len(origins)):
            if 3 in origins[i]:
                interface.keywords.append(keywords[i])
        interface.origins = [[3]] * len(interface.keywords)
    else:
        interface.origins = origins
        interface.keywords = keywords
    interface.codeNAF = codeNAF
    interface.desc = description
    interface.lastIndex = lastIndex
    interface.vkeywords = []
    
def saveRow(interface):
    os.chdir(Constants.pathCodeNAF)
    os.chdir("..")
    with open("processedRows.txt","a") as fichier:
        fichier.write(str(interface.lastIndex)+"\n")
    interface.indexToDrop=[interface.lastIndex]
    interface.csvdesc.drop(interface.indexToDrop,inplace=True)
    interface.csvclean.drop(interface.indexToDrop,inplace=True)
    interface.indexToDrop = []
    if interface.currentStep.get()==1:
        # text processing step / saving list of selected keywords
        with codecs.open("trainingSet.txt","a",'utf8') as fichier:
            fichier.write(str(interface.codeNAF)+"_"+interface.desc+"_")
            for keyword in interface.vkeywords:
                fichier.write(keyword+"=")
            fichier.write("\n")
        os.chdir(Constants.pathCodeNAF+"/subset_NAF_"+str(interface.codeNAF))
        with codecs.open("trained_entreprises.txt","a","utf8") as fichier:
            fichier.write(str(interface.codeNAF)+"_"+interface.desc+"_")
            for keyword in interface.keywords:
                fichier.write(keyword+"=")
            fichier.write("\n")
    elif interface.currentStep.get()==3:
        # graph interpolation step / saving rows in a panda dataframe
        for kw in interface.keywords:
            print kw
            interface.graph.computeNodeFeatures(kw)
            interface.graph.getNodeByName(kw).features["Y"] = kw in interface.vkeywords
        dicDF = {ft : [interface.graph.getNodeByName(kw).features[ft] 
                       for kw in interface.keywords] 
                 for ft in Constants.parametersGraph.keys()}
        os.chdir(Constants.pathCodeNAF+"/../")
        if not ("trainingStep3.csv" in os.listdir(".")):
            df = pd.DataFrame(columns=Constants.parametersGraph.keys())
        else:
            df = pd.DataFrame.from_csv("trainingStep3.csv",sep=";")
        df = pd.concat([df, pd.DataFrame.from_dict(dicDF)], ignore_index=True)
        df.to_csv("trainingStep3.csv",sep=";")

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
        [interface.keywordSet,interface.dicWordWeight] = IOFunctions.importKeywords(interface.criteres['codeNAF'][2])
    funNbMot = lambda x : len(x.split(" "))
    if interface.criteres['nbWordMin'][3]:
        test = test & (interface.csvdesc.description.apply(funNbMot)>int(interface.criteres['nbWordMin'][2]))
    if interface.criteres['nbWordMax'][3]:
        test = test & (interface.csvdesc.description.apply(funNbMot)<int(interface.criteres['nbWordMax'][2]))
    interface.csvclean = interface.csvdesc.copy()
    interface.csvclean.loc[~test] = None
    interface.csvclean.dropna(axis=0,how='any',inplace=True)
        

 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
        
        