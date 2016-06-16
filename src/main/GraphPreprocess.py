# -*- coding: utf-8 -*-
'''
Created on 27 avr. 2016

@author: Kévin Bienvenu
'''

from operator import itemgetter
import operator
import os

import Constants
import IOFunctions
import KeywordSubset
import TextProcessing
import pandas as pd


path = Constants.path
pathAgreg = Constants.pathAgreg
pathSubset = Constants.pathSubset


''' functions of graph handling '''

class GraphKeyword():
    '''
     === Graph Description ===
    - graphNodes V : dic{id (int): [name (str), genericite (float), dic{NAF (str) :value (float)}]}
    
    - graphEdges E : dic{(id1 (int), id2 (int)),[value (float), nbOccurence (int)]}
    
    - dicIdNodes : dic{name (str) : id (int)}
    '''
    
    ''' construction and import/export'''
    def __init__(self, name="untitled_graph"):
        try:
            self.name = str(name)
        except:
            self.name = "untitled_graph"
        self.graphNodes = {}
        self.graphEdges = {}
        self.dicIdNodes = {}
    
    def addEdgeValue(self, id0, id1, value):
        '''
        function that add the value 'value' to the edge between the nodes 1 and 2
        -- IN
        id0 : id of the first node (int)
        id1 : id of the second node (int)
        value : the value to add to the edge (float)
        -- OUT
        returns nothing
        '''
        try:
            i = int(id0)
            j = int(id1)
            if i>j:
                (i,j) = (j,i)
            v = float(value)
        except:
            print "failure in adding new edge :"
            print "id0", id0
            print "id1", id1
            print "value",value
            return
        if not((i,j) in self.graphEdges):
            self.graphEdges[(i,j)] = Edge(i,j)
        self.graphEdges[(i,j)].value += v
        self.graphEdges[(i,j)].nbOccurence += 1
    
    def addNodeValues(self, name, codeNAF="", valueNAF=0, genericity = 0):
        '''
        function that change the node 'name'
        if the node doesn't exist 
            it is created
        if the codeNAF is different than ""
            if the node doesn't have a value for codeNAF, 
                it is set to zero
            add the value 'valueNAF' to the codeNAF
        if the genericity is different than 0
            the node get this genericity
        -- IN
        name : name of the node to change (str)
        codeNAF : name of the codeNAF to change (str) default = ""
        value : value to add to the code NAF (float) default = 0
        genericity : value to set to the genericity (float) default = 0
        -- OUT
        the function returns nothing  
        '''
        try:
            v = float(valueNAF)
            g = float(genericity)
        except:
            return
        if not(name in self.dicIdNodes):
            self.dicIdNodes[name] = len(self.dicIdNodes)
            self.graphNodes[self.dicIdNodes[name]] = Node(self.dicIdNodes[name], name)
        if codeNAF != "":
            if not(codeNAF in self.graphNodes[self.dicIdNodes[name]].dicNAF):
                self.graphNodes[self.dicIdNodes[name]].dicNAF[codeNAF] = 0
            self.graphNodes[self.dicIdNodes[name]].dicNAF[codeNAF] += v
        if genericity>0:
            self.graphNodes[self.dicIdNodes[name]].genericity = g

    def extractKeywordRelationFromDescription(self,
                                              desc,codeNAF,
                                              keywords, dicWordWeight, 
                                              french_stopwords,
                                              stem ):
        '''
        function that extracts the content of a description and fills the graph.
        extraction of the keywords ?
        -- IN
        desc : the description to extract (str)
        codeNAF : the corresponding codeNAF (str)
        keywords : global dic of keywords
        dicWordWeight : global dic of word weight
        -- OUT
        the function returns nothing
        '''
        stemmedDesc = TextProcessing.nltkprocess(desc,True,french_stopwords,stem)
        listKeywords = TextProcessing.extractKeywordsFromString(desc,keywords, dicWordWeight,preprocessedString=stemmedDesc)
        tabOccurences = {}
        for k in listKeywords:
            self.addNodeValues(k, codeNAF=codeNAF, valueNAF=listKeywords[k])
            tabOccurences[k] = TextProcessing.getOccurencesKeywordInDescription(keywords[k], stemmedDesc)
        listMainKeywords = listKeywords.items()
        listMainKeywords.sort(key=itemgetter(1),reverse=True)
        listMainKeywords = [a[0] for a in listMainKeywords[:min(6,len(listMainKeywords))]]
        for k in listMainKeywords:
            for k1 in listMainKeywords:
                if k!=k1:
    #                 coef = len(tabOccurences[k])
    #                 for slug in tabOccurences[k]:
    #                     if slug in tabOccurences[k1]:
    # #                         coef+=dicWordWeight[slug]
    #                         coef -=1
                    # on calcule la valeur de l'arrête entre i et j
    #                 edgeValue = (listKeywords[k]+listKeywords[k1])/(1+coef)
                    edgeValue = 1
                    self.addEdgeValue(self.dicIdNodes[k], self.dicIdNodes[k1], edgeValue)  

    def generateWordWeight(self, keywords):
        '''
        function that generates a dic of word used in keywords and computes their weights.
        The more a word is present in keywords, the heavier it will weight.
        -- IN:
        keywords: dic of keywords (dic{str:[tokens]})
        -- OUT:
        dicWordWeight : dic of words and their weight (dic{str:int})
        '''
        dicWordWeight = {}
        for keywordstems in keywords.values():
            for word in keywordstems:
                if not(word in dicWordWeight):
                    dicWordWeight[word] = 0
                dicWordWeight[word] += 1
        return dicWordWeight

    def removeLonelyNodes(self):
        '''
        function that remove all nodes from graphNodes that
        aren't connected by any edge
        '''          
        toKeepNodes = {}
        for edge in self.graphEdges:
            toKeepNodes[edge[0]] = 1
            toKeepNodes[edge[1]] = 1
        toRemoveNodes = []
        for node in self.graphNodes:
            if not(node in toKeepNodes):
                toRemoveNodes.append(node)
        for node in toRemoveNodes:
            del self.graphNodes[node]

class Node():
    '''
    === Node description: 
    id (int)
    name (str)
    genericity (float)
    dicNAF (dic{codeNAF(str) : value (float)}
    '''
    def __init__(self, id, name):
        self.id = id
        self.name= name
        self.genericity = 0.0
        self.dicNAF = {}

class Edge():
    '''
    === Edge description:
    id0 (int)
    id1 (int)
    value (float)
    nbOccurence (int)
    '''
    def __init__(self, id0, id1):
        self.id0 = id0
        self.id1 = id1
        self.value = 0.0
        self.nbOccurence = 0

''' other functions '''

def extractKeywordsFromNAF(codeNAF, graph, number = 10):
    '''
    experimental function that return the 10 first keywords for a particular codeNAF
    '''
    nodes = {}
    for node in graph.graphNodes:
        if codeNAF in graph.graphNodes[node][2]:
            nodes[graph.graphNodes[node][0]]=graph.graphNodes[node][2][codeNAF]
    dic= sorted(nodes.items(), key=operator.itemgetter(1),reverse=True)
    return dic[:min(number,len(dic))]

def extractGraphFromSubset(subsetname, path = Constants.pathSubset):
    '''
    function that computes a graph (ie. dicIdNodes, graphNodes, graphEdges)
    out of a subset file, containing a 'keywords.txt' and a 'subsey_entreprises.txt' file
    -- IN:
    subsetname : name of the subset (string)
    -- OUT:
    dicIdNodes : dic of id of the nodes
    graphNodes : dic of the nodes
    graphEdges : dic of the edges
    '''
    print "== Extracting graph from subset:",subsetname
    print "- importing subset",
    (entreprises,keywords,dicWordWeight) = KeywordSubset.importSubset(subsetname, path)
    print "... done"
    if entreprises is None:
        return
    graph = GraphKeyword("graph_"+str(subsetname))
    print "- analyzing entreprises"
    compt = IOFunctions.Compt(entreprises, 10)
    # creating stemmerizer and stopwords
    from nltk.corpus import stopwords
    import nltk.stem.snowball
    french_stopwords = set(stopwords.words('french')),
    stem = nltk.stem.snowball.FrenchStemmer()
    # extracting information from the data
    for entreprise in entreprises:
        compt.updateAndPrint()
        graph.extractKeywordRelationFromDescription(entreprise[2],entreprise[1], 
                                                    keywords, dicWordWeight, 
                                                    french_stopwords, stem)
    graph.removeLonelyNodes()
    print "... done"
    print "- saving graphs",
    os.chdir(path+"/"+subsetname)
#     with open("edges_values.txt","w") as fichier:
#         for edge in graphEdges:
#             fichier.write(str(graphEdges[edge][0])+"\n")
    IOFunctions.saveGraph(graph)
    IOFunctions.saveGexfFile("graph.gexf", graph)
    print "... done"
    return graph
     
    




    