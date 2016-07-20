# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''

import codecs
import os
import time
import urllib

import Constants, IOFunctions
from main import KeywordSelector


def analyseMotsCles():
    [keywords,_] = IOFunctions.importKeywords()
    doublons = {}
    doublonsAccents = {}
    doublonsPluriel = {}
    doublonsAutres = {}
    compt = Constants.Compt(keywords,1)
    nbAccent = 0
    nbPluriel = 0
    nbAutres = 0
    for keyword1 in keywords:
        compt.updateAndPrint()
        for keyword2 in keywords:
            if keyword1==keyword2:
                continue
            if keywords[keyword1]==keywords[keyword2]: 
                if keyword2 not in doublons:
                    suggest = "??"
                    if IOFunctions.preprocessString(keyword1)==IOFunctions.preprocessString(keyword2):
                        # problème d'accent
                        if IOFunctions.preprocessString(keyword1)==keyword1:
                            suggest = keyword2
                        if IOFunctions.preprocessString(keyword2)==keyword2:
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
            
def motsClesRemoveDoublons():
    [keywords,_] = IOFunctions.importKeywords()
    doublons = []
    compt = Constants.Compt(keywords,1)
    print "longueur initiale mots clés:",len(keywords)
    print ""
    for keyword1 in keywords:
        compt.updateAndPrint()
        flag = False
        for keywordset in doublons:
            if keywords[keywordset[0]]==keywords[keyword1]: 
                flag = True
                break
        if flag:
            keywordset.append(keyword1)
        else:
            doublons.append([keyword1])
    print "nombre de mots-clés uniques:",len(doublons)
    for d in doublons:
        if len(d)==1:
            continue
        flag = False
        while not flag:
            for k in d:
                print k,
            print "   ",
            try:
                a = int(input())
                if a <len(d):
                    for i in range(len(d)):
                        if i==a:
                            continue
                        del keywords[d[i]]
                    flag = True
            except:
                pass
    print "longueur finale mots clés:",len(keywords)
    IOFunctions.saveKeywords(keywords, Constants.path+"/motscles", "keywordsNew.txt")
      
def motsClesRemoveSolo():
    [keywords,_] = IOFunctions.importKeywords()
    solos = []
    compt = Constants.Compt(keywords,1)
    print "longueur initiale mots clés:",len(keywords)
    print ""
    for keyword1 in keywords:
        compt.updateAndPrint()
        if len(keyword1.split(" "))==1:
            solos.append(keyword1)
            
    print "nombre de mots-clés uniques:",len(solos)
    with codecs.open("solo.txt","w","utf8") as fichier:
        for d in solos:
            fichier.write(d+"\n")

def motsClesHandleSolo():
    solos = []
    [keywords,_] = IOFunctions.importKeywords()
    print "longueur initiale mots clés:",len(keywords)
    with codecs.open("solo.txt","r","utf8") as fichier:
        for line in fichier:
            solos.append(line[:-1])
    print "nombre de mots-clés uniques:",len(solos)
    while len(solos)>0:
        a = solos.pop(0)
        print a
        try:
            b=input()
            del keywords[a]
            IOFunctions.saveKeywords(keywords, Constants.path+"/motscles", "keywordsNew.txt")
        except:
            pass
        with codecs.open("solo.txt","w","utf8") as fichier:
            for d in solos:
                fichier.write(d+"\n")   
           
def isDifferencePluriel(kw1, kw2):
    k1 = IOFunctions.preprocessString(kw1).split(" ")       
    k2 = IOFunctions.preprocessString(kw2).split(" ")
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
      
def findExamples():
    entreprises = IOFunctions.extractSubset(n=100)
    keywordSet, _ = IOFunctions.importKeywords()
#     entreprises = [['a','élevage de brebis, chèvres']]
#     keywordSet = {"élevage de chèvres":[u'elevag',u'chevr']}
    for i in range(2,7):
        print i
        Constants.step01_seuilOrdre = i
        for e in entreprises:
            KeywordSelector.extractFromDescription(e[1], keywordSet, {},toPrint=False)

def importCodeNAF():
    listCodeNAF = IOFunctions.importListCodeNAF()
    dic = {
           "&Agrave":"À",
           "&agrave;":"à",
            "&Acirc;":"Â",
            "&acirc;":"â",
            "&Ccedil;":"Ç",
            "&ccedil;":"ç",
            "&Egrave;":"È",
            "&egrave;":"è",
            "&Eacute;":"É",
            "&eacute;":"é",
            "&Ecirc;":"Ê",
            "&ecirc;":"ê",
            "&Euml;":"Ë",
            "&euml;":"ë",
            "&Icirc;":"Î",
            "&icirc;":"î",
            "&Iuml;":"Ï",
            "&iuml;":"ï",
            "&Ocirc;":"Ô",
            "&ocirc;":"ô",
            "&OElig;":"Œ",
            "&oelig;":"œ",
            "&Ugrave;":"Ù",
            "&ugrave;":"ù",
            "&Ucirc;":"Û",
            "&ucirc;":"û",
            "&Uuml;":"Ü",
            "&uuml;":"ü",
            "&#376;":"Ÿ",
            "&yuml;":"ÿ",
            "&rsquo;":"'"}
    finalNAFdic = {}
    for codeNAF in listCodeNAF:
        print codeNAF,        
        url = "http://www.insee.fr/fr/methodes/default.asp?page=nomenclatures/naf2008/n5_"+str(codeNAF[0:2])+"."+str(codeNAF[2:]).lower()+".htm"
        page = urllib.urlopen(url)
        for line in page:
            s = "Sous-classe " + str(codeNAF[0:2])+"."+str(codeNAF[2:])
            e = "</h1>"
            if s in line and e in line:
                l = line[line.index(s)+len(s):line.index(e)]
                for d in dic:
                    while d in l:
                        l = l.replace(d,dic[d])
                l = l.decode("utf8")        
                print l
                finalNAFdic[codeNAF] = l
                break
    os.chdir(Constants.pathCodeNAF)
    IOFunctions.saveDict(finalNAFdic, "listeCodeNAF.txt", "_")


def fonctionEstimationTemps():
    # Estimation substep 0
    timer = {}
    timerpercent = {}
    for n in [20,200,100,50]:
        timer[n] = [0,0,0]
        startTime = time.time()
        KeywordSelector.pipelineGraph(n, 100, [True,False,False])
        timer[n][0] = time.time() - startTime
        startTime = time.time()
        KeywordSelector.pipelineGraph(n, 100, [False,True,False])
        timer[n][1] = time.time() - startTime
        startTime = time.time()
        KeywordSelector.pipelineGraph(n, 100, [False,False,True])
        timer[n][1] = time.time() - startTime
        print n,timer[n]
    timerpercent[100] = timer[50][2]
    for percent in [50,75]:
        startTime = time.time()
        KeywordSelector.pipelineGraph(n, percent, [False,False,True])
        timerpercent[percent] = time.time() - startTime
        print percent, timerpercent[percent]
    
    print "résultats"
    print ""
    print timer
    print ""
    print timerpercent
    

# os.chdir(Constants.pathCodeNAF)
# with codecs.open("listeCodeNAF.txt","w","utf8") as fichier:
#     for f in os.listdir("."):
#         if "subset_NAF_" in f:
#             fichier.write(f[f.index("subset_NAF_")+len("subset_NAF_"):]+"\r\n")
# 
# importCodeNAF()