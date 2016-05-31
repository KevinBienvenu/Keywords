# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''

import gc
import os

import Constants
import GraphPreprocess
import IOFunctions, KeywordSubset
import pandas as pd
import codecs


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
        
        
            