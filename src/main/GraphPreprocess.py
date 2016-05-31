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

'''
 === Graph Description ===
- graphNodes V : dic{id, [name, genericite, dic{NAF:value}]}

- graphEdges E : dic{(id1,id2),[value,nbOccurence]}
'''

def addEdgeValue(id1, id2, value, graphEdges):
    '''
    function that add the value 'value' to the edge between the nodes 1 and 2
    -- IN
    id1 : id of the first node (int)
    id2 : id of the second node (int)
    value : the value to add to the edge (float)
    -- OUT
    graphEdges : the dic of edges
    '''
    try:
        i = int(id1)
        j = int(id2)
        v = float(value)
    except:
        return
    if i>j:
        (i,j) = (j,i)
    if not((i,j) in graphEdges):
        graphEdges[(i,j)] = [0,0]
    graphEdges[(i,j)][0] += v
    graphEdges[(i,j)][1] += 1
    return graphEdges
    
def addNodeValues(name, dicIdNodes, graphNodes, codeNAF="", valueNAF=0, genericity = 0):
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
    dicIdNodes : dic of nodes id
    graphNodes : graph of nodes  
    '''
    try:
        v = float(valueNAF)
        g = float(genericity)
    except:
        return
    if not(name in dicIdNodes):
        dicIdNodes[name] = len(dicIdNodes)
        graphNodes[dicIdNodes[name]] = [name, 0, {}]
    if codeNAF != "":
        if not(codeNAF in graphNodes[dicIdNodes[name]][2]):
            graphNodes[dicIdNodes[name]][2][codeNAF] = 0
        graphNodes[dicIdNodes[name]][2][codeNAF] += v
    if genericity>0:
        graphNodes[dicIdNodes[name]][1] = g
    return (dicIdNodes, graphNodes)

def extractDescription(desc,codeNAF,
                       keywords, dicWordWeight, 
                       dicIdNodes, graphNodes, graphEdges,
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
    dicIdNodes :
    graphNodes :
    graphEdges :
    -- OUT
    dicIdNodes :
    graphNodes :
    graphEdges :
    '''
    listKeywords = TextProcessing.extractKeywordsFromString(desc,keywords, dicWordWeight, french_stopwords, stem)
    for k in listKeywords:
        (dicIdNodes, graphNodes) = addNodeValues(k, dicIdNodes, graphNodes,codeNAF=codeNAF, valueNAF=listKeywords[k])
    for k in listKeywords:
        for k1 in listKeywords:
            if k!=k1:
                # on calcule la valeur de l'arrête entre i et j
                edgeValue = listKeywords[k]+listKeywords[k1]
                graphEdges = addEdgeValue(dicIdNodes[k], dicIdNodes[k1], edgeValue,graphEdges)
    return (dicIdNodes,graphNodes,graphEdges)

def generateWordWeight(keywords):
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

def graphPostTreatment0(graphNodes, graphEdges):
    # removing useless edges
    print "=== post treatment of graph"
    print "- removing little edges",
    thresholdEdge = 1.0
    toremove = []
    for edge in graphEdges:
        if 3.0*graphEdges[edge][0]/graphEdges[edge][1]<thresholdEdge:
            toremove.append(edge)
    print "... done :",len(toremove),"edges removed -",100.0*len(toremove)/len(graphEdges),"%"
    for edge in toremove:
        del graphEdges[edge]
    nbEdgeToKeep = 3
    dicRowToKeep = {}
    dicNodeEdges = {}
    print "- keeping only",str(nbEdgeToKeep),"edges by node",
    for edge in graphEdges:
        if edge[0] not in dicNodeEdges:
            dicNodeEdges[edge[0]] = []            
        dicNodeEdges[edge[0]].append(edge)
        if edge[1] not in dicNodeEdges:
            dicNodeEdges[edge[1]] = []            
        dicNodeEdges[edge[1]].append(edge)
    for node in dicNodeEdges:
        for _ in range(min(nbEdgeToKeep,len(dicNodeEdges[node]))):
            maxiVal = 0
            maxiEdge = None
            for edge in dicNodeEdges[node]:
                if 3.0*graphEdges[edge][0]/graphEdges[edge][1]>maxiVal:
                    maxiVal = 3.0*graphEdges[edge][0]/graphEdges[edge][1]
                    maxiEdge = edge
            dicRowToKeep[maxiEdge] = 1
            dicNodeEdges[node].remove(maxiEdge)
    graphEdges2 = {}
    for edge in dicRowToKeep:
        graphEdges2[edge] = graphEdges[edge]
    print "... done :",len(graphEdges)-len(graphEdges2),"edges removed -",100.0*(len(graphEdges)-len(graphEdges2))/len(graphEdges),"%"
    graphEdges = graphEdges2
    return (graphNodes, graphEdges)

def graphPostTreatment1(graphNodes, graphEdges):
    toPrint = False
    (graphNodes, graphEdges) = graphPostTreatmentEdges(graphNodes, graphEdges)
    dicNodeEdges = {}
    dicNodeDegre = {}
    dicEdgeState = {}
    nbEdgeToKeep = 10
    if toPrint: 
        print "- keeping only",str(nbEdgeToKeep),"edges by node",
    for edge in graphEdges:
        if edge[0] not in dicNodeEdges:
            dicNodeEdges[edge[0]] = []            
        dicNodeEdges[edge[0]].append(edge)
        if edge[1] not in dicNodeEdges:
            dicNodeEdges[edge[1]] = []            
        dicNodeEdges[edge[1]].append(edge)
#         graphEdges[edge] = [graphEdges[edge][0]/graphEdges[edge][1], graphEdges[edge][0]/graphEdges[edge][1]]
        graphEdges[edge] = [graphEdges[edge][0], graphEdges[edge][0]]
        dicEdgeState[edge] = "waiting"
    nodes = {}
    for node in graphNodes:
        nodes[node] = sum(graphNodes[node][2].values())
        dicNodeDegre[node] = 0
    l = nodes.items()
    l.sort(key=itemgetter(1),reverse=True)
    if toPrint: 
        print ""
    for nodel in l:
        node = nodel[0]
        if toPrint: 
            print "studying node",node,"   :",nodes[node]
        # handling the case of a lonely node (no neighbours)
        if not(node in dicNodeEdges):
            if toPrint: 
                print "lonely node"
            continue
        if toPrint: 
            print "nombre d'arrêtes restantes:",len(dicNodeEdges[node])
        n = nbEdgeToKeep
        toremove = []
        for edge in dicNodeEdges[node]:
            if toPrint: 
                print "  edge linking",int(edge[0]),"to",int(edge[1]) 
                print "      value of",int(edge[0]),":",nodes[int(edge[0])]," - ",int(edge[1]),":",nodes[int(edge[1])]
            # checking for previously settled edges
            if dicEdgeState[edge]=="validated":
                n-=1
                toremove.append(edge)
                if toPrint: 
                    print " === Existing edge !!! restantes:",n
            # removing deleted edges
            elif dicEdgeState[edge]=="deleted":
                toremove.append(edge)             
        for edge in toremove:
            dicNodeEdges[node].remove(edge)
        if n==0:
            continue
        if n<0:
            if toPrint: 
                print "problème: un noeud a trop d'arrêtes",n,node
                continue
        i=0
        if toPrint: 
            print ""
            print "arrêtes à valider:",n
        while i < n:
            if len(dicNodeEdges[node])==0:
                if toPrint: 
                    print "stop because no edge left"
                break
            maxvalue = 0
            maxedge = None
            for edge in dicNodeEdges[node]:
                # conditions to keep an edge:
                #   edge value must be superior to the current edge value
                #   destination node must not be overloaded
                #   destination node must not have an edge to an already connected node with bigger value
                if graphEdges[edge][0]>maxvalue and graphEdges[edge][1]>maxvalue \
                and dicNodeDegre[int(edge[1])]<nbEdgeToKeep and dicNodeDegre[int(edge[0])]<nbEdgeToKeep:
                    maxvalue = graphEdges[edge][0]
                    maxedge = edge
            if maxvalue==0 and i==0:
                if toPrint: 
                    print "have to complete because no edge were left"
                i=n
#                 for edge in dicNodeEdges[node]:
#                 # removing already completed nodes
#                     if dicNodeDegre[int(edge[0])]<3 and dicNodeDegre[int(edge[1])]<3 and graphEdges[edge][1]>maxvalue:
#                         maxvalue = graphEdges[edge][1]
#                         maxedge = edge
            if maxedge==None:
                break
            dicNodeEdges[node].remove(maxedge)
            if toPrint: 
                print " _ - _- _- Edge kept:",maxedge,graphEdges[maxedge][0]
            dicEdgeState[maxedge] = "validated"
            # increasing degre of concerned nodes
            dicNodeDegre[int(maxedge[0])] +=1
            dicNodeDegre[int(maxedge[1])] +=1      
            i+=1
        for edge in dicNodeEdges[node]:
            graphEdges[edge][0] = 0
            dicEdgeState[edge] = "deleted"
        if toPrint: 
            print "putting",len(dicNodeEdges[node]),"edges to 0"
        if toPrint: 
            try:
                input("press Enter")
            except SyntaxError:
                pass
    # removing edges with 0 values
    toremove = []
    for edge in graphEdges:
        if dicEdgeState[edge] == "deleted":
            toremove.append(edge)
    print "removing",len(toremove),"over",len(graphEdges)
    for edge in toremove:
        del graphEdges[edge]
    return (graphNodes,graphEdges)
                
def graphPostTreatmentEdges(graphNodes, graphEdges):

        
    return (graphNodes, graphEdges)
            

''' experimental functions '''

def extractKeywordsFromNAF(codeNAF, graphNodes, number = 10):
    '''
    experimental function that return the 10 first keywords for a particular codeNAF
    '''
    nodes = {}
    for node in graphNodes:
        if codeNAF in graphNodes[node][2]:
            nodes[graphNodes[node][0]]=graphNodes[node][2][codeNAF]
    dic= sorted(nodes.items(), key=operator.itemgetter(1),reverse=True)
    return dic[:min(number,len(dic))]

def extractGraphFromCSV(filename,keywords):
    ''' 
    non generic function that extract description and keywords from csv file
    '''
    os.chdir(pathAgreg)
    db = pd.read_csv(filename,usecols=['codeNaf', 'description'])
    percent = 1
    i = 0
    total = len(db)
    graphNodes = {}
    graphEdges = {}
    dicIdNodes = {}
    for line in db.values:
        i+=1
        if 100.0*i/total>percent:
            print percent,"%",
            percent+=1
            if percent%10==0:
                print ""
        if str(line[1])!="nan":
            (dicIdNodes,graphNodes,graphEdges)=extractDescription(line[1],line[0],keywords,dicIdNodes,graphNodes,graphEdges)
        break
    return (dicIdNodes,graphNodes,graphEdges)

     



# keywords = importKeywords()
# 
# fileNameVec = ['BRep_Step2_0_1000000.csv', 
#                'BRep_Step2_1000000_2000000.csv', 
#                'BRep_Step2_2000000_3000000.csv',
#               'BRep_Step2_3000000_4000000.csv', 
#               'BRep_Step2_4000000_5000000.csv', 
#               'BRep_Step2_5000000_6000000.csv',
#               'BRep_Step2_6000000_7000000.csv', 
#               'BRep_Step2_7000000_8000000.csv', 
#               'BRep_Step2_8000000_9176180.csv']
# 
# for filename in fileNameVec:
#     print "extracting file:",filename
#     extractDescriptionFromCSV(filename, keywords)
# 
# os.chdir(path)
# IOFunctions.saveGraphNode(graphNodes, "graphNode.txt")
# IOFunctions.saveGraphEdge(graphEdges, "graphEdge.txt")

# graphNodes = IOFunctions.importGraphNode("vaneau_copy.txt")

# codeNAFs = []
# for node in graphNodes:
#     for codeNAF in graphNodes[node][2]:
#         if not codeNAF in codeNAFs:
#             codeNAFs.append(codeNAF)
#             
# print len(codeNAFs)
# print len(graphNodes)
# 
# 
# print extractKeywords("2059Z")

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
    graphNodes = {}
    graphEdges = {}
    dicIdNodes = {}
    print "- analyzing entreprises"
    compt = IOFunctions.initProgress(entreprises, 10)
    # creating stemmerizer and stopwords
    from nltk.corpus import stopwords
    import nltk.stem.snowball
    french_stopwords = set(stopwords.words('french')),
    stem = nltk.stem.snowball.FrenchStemmer()
    for entreprise in entreprises:
        compt = IOFunctions.updateProgress(compt)
        (dicIdNodes,graphNodes,graphEdges) = extractDescription(entreprise[2],entreprise[1], 
                                                                keywords, dicWordWeight, 
                                                                dicIdNodes, graphNodes, graphEdges,
                                                                french_stopwords, stem)
    (graphNodes, graphEdges) = graphPostTreatment1(graphNodes, graphEdges)
    print "... done"
    print "- saving graphs",
    os.chdir(path+"/"+subsetname)
    IOFunctions.saveGraphEdge(graphEdges, "graphEdges.txt")
    IOFunctions.saveGraphNode(graphNodes, "graphNodes.txt")
    IOFunctions.saveGexfFile("graph.gexf", graphNodes, graphEdges)
    print "... done"
    return (dicIdNodes,graphNodes,graphEdges)
     
    




    