# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''

import codecs
import gc
import os
import time

import Constants
import GraphPreprocess
import IOFunctions, KeywordSubset
from main import TextProcessing
import pandas as pd


def createDescDatabase():
    print ""
    os.chdir(Constants.pathAgreg)
    fileNameVec = ['BRep_Step2_0_1000000.csv', 
               'BRep_Step2_1000000_2000000.csv', 
               'BRep_Step2_2000000_3000000.csv',
              'BRep_Step2_3000000_4000000.csv', 
              'BRep_Step2_4000000_5000000.csv', 
              'BRep_Step2_5000000_6000000.csv',
              'BRep_Step2_6000000_7000000.csv', 
              'BRep_Step2_7000000_8000000.csv', 
              'BRep_Step2_8000000_9176180.csv']
    db = pd.DataFrame(columns=['codeNAF','description','keywords'])
    for filename in fileNameVec:
        csvfile = pd.read_csv(filename, usecols=['codeNAF','description','keywords'])
        csvfile = csvfile[csvfile.description.notnull()]
        db = pd.concat([db,csvfile],copy=False)
        print len(db)
    db.to_csv("descriptions.csv", compression="bz2")
    
def createListNAF():
    os.chdir(Constants.path+"/archives")
    codeNAFs = []
    with open("mots-cles-naf.txt") as fichier:
        for line in fichier:
            if len(line)<2:
                continue
            codeNAFs.append(str(line[4:6])+str(line[7:10]))
    with open("listeCodeNAF.txt","w") as fichier:
        for codeNAF in codeNAFs:
            fichier.write(codeNAF+"\n")
            print codeNAF
        print ""
        print "... done :",len(codeNAFs),"printed"
              
def extractAllNAF():
    os.chdir(Constants.path+"/motscles")
    codeNAFs = []
    with open("listeCodeNAF.txt","r") as fichier:
        for line in fichier:
            codeNAFs.append(line[:-1])
    [graphNodes, _, _] = IOFunctions.importGraph("graphcompet")
    os.mkdir("./codeNAFs")
    os.chdir("./codeNAFs")
    print "== extracting codeNAFs"
    for codeNAF in codeNAFs:
        print codeNAF
        keywordFromNAF = GraphPreprocess.extractKeywordsFromNAF(codeNAF, graphNodes)
        with open("codeNAF_"+codeNAF+".txt", "w") as fichier:
            for keyword in keywordFromNAF:
                fichier.write(keyword+"\n")
    print " ... done"
    
def computeNAFSubsets():
    print "=== Computing subsets for all code NAF"
    print " - extracting list of codeNAF",
    codeNAFs = []
    os.chdir(Constants.pathCodeNAF)   
    with open("listeCodeNAF.txt","r") as fichier:
        for line in fichier:
            codeNAFs.append(line[:-1])
    n=20
    os.chdir(Constants.pathAgreg)
    fileNameVec = ['BRep_Step2_0_1000000.csv', 
               'BRep_Step2_1000000_2000000.csv', 
               'BRep_Step2_2000000_3000000.csv',
              'BRep_Step2_3000000_4000000.csv', 
              'BRep_Step2_4000000_5000000.csv', 
              'BRep_Step2_5000000_6000000.csv',
              'BRep_Step2_6000000_7000000.csv', 
              'BRep_Step2_7000000_8000000.csv', 
              'BRep_Step2_8000000_9176180.csv']
    entreprises = {}
    for codeNAF in codeNAFs:
        entreprises[codeNAF] = []
    print "... done"
    print " - extracting entreprises"
    for brepFile in fileNameVec:
        print "   ",brepFile
        csvfile = pd.read_csv(brepFile, usecols=['siren','codeNaf', 'description'])
        csvfile = csvfile[csvfile.description.notnull()]
        compt = IOFunctions.initProgress(codeNAFs,1)
        for codeNAF in codeNAFs:
            compt = IOFunctions.updateProgress(compt)
            csvfile2 = csvfile[csvfile.codeNaf.str.contains(codeNAF)==True]
            i=0
            for line in csvfile2.itertuples():
                entreprises[codeNAF].append([line[1],line[2],line[3]]) 
                i+=1
                if i>=n:
                    break  
    del csvfile
    del csvfile2
    gc.collect() 
    print "... done"   
    print ""
    print " - writing done subsets"  
    os.chdir(Constants.pathCodeNAF)
    compt = IOFunctions.initProgress(codeNAFs)
    for codeNAF in codeNAFs:
        compt = IOFunctions.updateProgress(compt)
        subsetname = "codeNAF_"+codeNAF
        if subsetname not in os.listdir("."):
            os.mkdir("./"+subsetname)
        os.chdir("./"+subsetname)
        with open("subset_entreprises.txt","w") as fichier:
            for entreprise in entreprises[codeNAF]:
                fichier.write(""+str(entreprise[0]))
                fichier.write("_"+str(entreprise[1])+"_")
                fichier.write(entreprise[2])
                fichier.write("\n")
        keywords = KeywordSubset.createKeywords(entreprises[codeNAF], subsetname, Constants.pathCodeNAF)
    #     printKeywordsSubset(entreprises = entreprises, keywords = keywords)
        dicWordWeight = GraphPreprocess.generateWordWeight(keywords)
        IOFunctions.saveDict(dicWordWeight, "dicWordWeight.txt")
        os.chdir("../")
    
def computeNAFgraphs():
    print "=== Computing graphs for all code NAF"
    codeNAFs = []
    os.chdir(Constants.pathCodeNAF)   
    with open("listeCodeNAF.txt","r") as fichier:
        for line in fichier:
            codeNAFs.append(line[:-1])
    for codeNAF in codeNAFs:
        print "extracting code NAF",codeNAF,
        (_,graphNodes,_) = GraphPreprocess.extractGraphFromSubset("codeNAF_"+codeNAF, Constants.pathCodeNAF)
        print "... done"
        print "   number of keywords:",len(graphNodes)
        keywords = GraphPreprocess.extractKeywordsFromNAF(codeNAF, graphNodes, 200)
        os.chdir(Constants.pathCodeNAF+"/codeNAF_"+codeNAF)
        with codecs.open("keywordSuggest.txt","w","utf8") as fichier:
            for keyword in keywords:
                fichier.write(keyword[0]+"\n")
        print "   final number of keywords:",len(keywords)
               
def extractCompleteGraphUsingNAFKeywords():
    '''
    function that computes a graph (ie. dicIdNodes, graphNodes, graphEdges)
    out of a subset file, containing a 'keywords.txt' and a 'subset_entreprises.txt' file
    
    -- IN:
    subsetname : name of the subset (string)
    -- OUT:
    dicIdNodes : dic of id of the nodes
    graphNodes : dic of the nodes
    graphEdges : dic of the edges
    '''
    print "== Extracting complete graph from subset:"
    print "- importing subset",
    (entreprises,_,dicWordWeight) = KeywordSubset.importSubset("graphcomplet", Constants.pathSubset)
    print "... done"
    if entreprises is None:
        return
    graphNodes = {}
    graphEdges = {}
    dicIdNodes = {}
    print "- analyzing entreprises"
    compt = 0
    localcompt = 0
    # creating stemmerizer and stopwords
    from nltk.corpus import stopwords
    import nltk.stem.snowball
    french_stopwords = set(stopwords.words('french')),
    stem = nltk.stem.snowball.FrenchStemmer()
    for entreprise in entreprises:
        localcompt += 1
        compt += 1
        print ".",
        if localcompt%30==0:
            localcompt=0
            print "   ",'%.3f' % (100.0*compt/len(entreprises)),"%"
        if entreprise[1]=="nan":
            continue
        keywords = IOFunctions.importKeywords(Constants.pathCodeNAF+"/codeNAF_"+entreprise[1],"keywordSuggest.txt");
        (dicIdNodes,graphNodes,graphEdges) = GraphPreprocess.extractDescription(entreprise[2],entreprise[1], 
                                                                keywords, dicWordWeight, 
                                                                dicIdNodes, graphNodes, graphEdges,
                                                                french_stopwords, stem)
        os.chdir("..")
#     (graphNodes, graphEdges) = GraphPreprocess.graphPostTreatment1(graphNodes, graphEdges)
    print "... done"
    print "- saving graphs",
    os.chdir(Constants.pathSubset+"/"+"graphcomplet")
    IOFunctions.saveGraphEdge(graphEdges, "graphEdges.txt")
    IOFunctions.saveGraphNode(graphNodes, "graphNodes.txt")
    IOFunctions.saveGexfFile("graph.gexf", graphNodes, graphEdges)
    print "... done"
         
def analyseMotsCles():
    [keywords,_] = IOFunctions.importKeywords()
    doublons = {}
    doublonsAccents = {}
    doublonsPluriel = {}
    doublonsAutres = {}
    compt = IOFunctions.initProgress(keywords,1)
    nbAccent = 0
    nbPluriel = 0
    nbAutres = 0
    for keyword1 in keywords:
        compt = IOFunctions.updateProgress(compt)
        for keyword2 in keywords:
            if keyword1==keyword2:
                continue
            if keywords[keyword1]==keywords[keyword2]: 
                if keyword2 not in doublons:
                    suggest = "??"
                    if TextProcessing.transformString(keyword1)==TextProcessing.transformString(keyword2):
                        # problème d'accent
                        if TextProcessing.transformString(keyword1)==keyword1:
                            suggest = keyword2
                        if TextProcessing.transformString(keyword2)==keyword2:
                            suggest = keyword1                         
                        doublonsAccents[nbAccent] = [keyword1,keyword2,suggest]
                        nbAccent += 1
                    elif isDifferencePluriel(keyword1, keyword2):
                        # problème de pluriel
                        doublonsPluriel[nbPluriel] = [keyword1, keyword2, suggest]
                        nbPluriel += 1
                    else:
                        # autres problèmes
                        doublonsAutres[nbAutres] = [keyword1, keyword2, suggest]
                        nbAutres += 1
                    doublons[keyword1] = keyword2
                    doublons[keyword2] = keyword1
    with codecs.open("doublonsKeywords.csv",'w','utf-8') as fichier:
        fichier.write("keyword1;keyword2;suggestion\n")
        fichier.write("# doublons dus aux accents\n")
        for item in doublonsAccents.values():
            fichier.write(item[0]+";"+item[1]+";"+item[2]+"\n")
        fichier.write("# doublons dus aux pluriels\n")
        for item in doublonsPluriel.values():
            fichier.write(item[0]+";"+item[1]+";"+item[2]+"\n")
        fichier.write("# doublons dus au reste\n")
        for item in doublonsAutres.values():
            fichier.write(item[0]+";"+item[1]+";"+item[2]+"\n")

def isDifferencePluriel(kw1, kw2):
    k1 = TextProcessing.transformString(kw1).split(" ")       
    k2 = TextProcessing.transformString(kw2).split(" ")
    for i in range(len(k1)):
        try:
            if k1[i]==k2[i]:
                continue
            if k1[i][-1]=="s" and k1[i][:-1]==k2[i]:
                continue
            if k2[i][-1]=="s" and k2[i][:-1]==k1[i]:
                continue
            return False
        except:
            continue
    return True

def makeGraphLaurent():
           

    # graphNodes = {str name : int value}
    graphNodes = {}
    
    # dicIdNodes = {str name : int id}
    dicIdNodes = {}
    
    # graphEdges = {str name(name1_name2) : int value}
    graphEdges = {}
    
    idNode = 0
    with codecs.open("","r","utf8") as fichier:
        for line in fichier:
            tab = line.split(" ");
            # on parcourt les noeuds et les ajoute si nécessaire
            for keyword1 in tab:
                if not(keyword1 in graphNodes):
                    graphNodes[keyword1] = 0
                    dicIdNodes[keyword1] = idNode
                    idNode += 1
                graphNodes[keyword1] += 1
                # on reparcourt les noeuds pour créer les arrêtes
                for keyword2 in tab:
                    if keyword1==keyword2:
                        continue
                    if keyword1 < keyword2:
                        if not(keyword1+"_"+keyword2 in graphEdges):
                            graphEdges[keyword1+"_"+keyword2] = 0
                        graphEdges[keyword1+"_"+keyword2] += 1
                    else:
                        if not(keyword2+"_"+keyword1 in graphEdges):
                            graphEdges[keyword2+"_"+keyword1] = 0
                        graphEdges[keyword2+"_"+keyword1] += 1
    
    # saving gexf file
    filename = "graphOutput.csv"
    with codecs.open(filename,"w","utf-8") as fichier:
        # writing header
        fichier.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        fichier.write("<gexf xmlns=\"http://www.gexf.net/1.2draft\" \
                        xmlns:viz=\"http://www.gexf.net/1.2draft/viz\" \
                        version=\"1.2\">\n")
        fichier.write("<meta lastmodifieddate=\""+time.strftime('%d/%m/%y',time.localtime())+"\">\n")
        fichier.write("<creator>Kevin Bienvenu</creator>\n")
        fichier.write("<description>A subset graph file</description>\n")
        fichier.write("</meta>\n")
        # writing graph
        fichier.write("<graph>\n")
        # writing nodes
        fichier.write("<nodes>\n")
        for node in graphNodes:
            fichier.write("<node id=\"")
            fichier.write(str(dicIdNodes[node]))
            fichier.write("\" label=\"")
            fichier.write(node.replace("&","et"))
            fichier.write("\">\n")
            fichier.write("<viz:size value=\"")
            fichier.write(str(graphNodes[node]))
            fichier.write("\"/>\n")
            fichier.write("</node>")
        fichier.write("</nodes>\n")
        # writing edges
        fichier.write("<edges>\n")
        i=0
        for edge in graphEdges:
            if graphEdges[edge][0]>0:
                fichier.write("<edge id=\"")
                fichier.write(str(i))
                fichier.write("\" source=\"")
                fichier.write(str(dicIdNodes[edge.split("_")[0]]))
                fichier.write("\" target=\"")
                fichier.write(str(dicIdNodes[edge.split("_")[1]]))
                fichier.write("\" type=\"undirected\" weight=\"")
                fichier.write(str(graphEdges[edge]))
                fichier.write("\"/>\n")
                i+=1
        fichier.write("</edges>\n")
        fichier.write("</graph>\n")
        fichier.write("</gexf>")  

def cleanKeyword():
    [keywords, _ ] = IOFunctions.importKeywords()
    i=0
    newKeywords = {}
    print "taille originale:",len(keywords)
    for keyword in keywords:
        if keyword.lower() in newKeywords:
            print keyword
        newKeywords[keyword.lower()] = keywords[keyword]
    print "nouvelle taille:",len(newKeywords)
    with codecs.open("keywordsClean.txt","w","utf8") as fichier:
        for keyword in keywords:
            fichier.write(keyword+"\n")
         
analyseMotsCles()

