# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''

import codecs
import time
import IOFunctions
from main import TextProcessing
 
def analyseMotsCles():
    [keywords,_] = IOFunctions.importKeywords()
    doublons = {}
    doublonsAccents = {}
    doublonsPluriel = {}
    doublonsAutres = {}
    compt = IOFunctions.Compt(keywords,1)
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

