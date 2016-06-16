# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

from HTMLParser import HTMLParser
import codecs
from operator import itemgetter
import time
import urllib
import os

import unidecode
import TextProcessing 
import Constants
from GraphPreprocess import GraphKeyword
import GraphPreprocess

''' functions '''

def saveDict(dic,filename,sep="-"):
    with codecs.open(filename,'w','utf-8') as fichier:
        for item in dic.items():
            try:
                int(item[0])
                fichier.write(str(item[0]))
            except:
                fichier.write(item[0])
            fichier.write(sep)
            try:
                int(item[1])
                fichier.write(str(item[1]))
            except:
                fichier.write(item[1])
            fichier.write("\n")
            
def importArray(filename):
    arr = []
    with codecs.open(filename,"r","utf8") as fichier:
        for line in fichier:
            arr.append(line[:-1])
    return arr;

def importDict(filename,sep="-"):
    dic = {}
    with codecs.open(filename,'r','utf-8') as fichier:
        for line in fichier:
            tab = line.split(sep)
            s = tab[0]
            for i in range(1,len(tab)-1):
                s+=tab[i]
            dic[s] = tab[-1]
    return dic
   
def printSortedDic(dic, nprint=0):      
    '''
    function that print a dic sorted according to its values
    if the parameter nprint in given and non zero, print only the nprint greatest values
    -- IN:
    dic : dic which values must be int or float (dic{object:float})
    nprint : number of values to print (int) default=0
    -- OUT:
    the function returns nothing
    '''
    l = dic.items()
    l.sort(key=itemgetter(1),reverse=True)
    imax = nprint
    if imax==0:
        imax = len(l)
    for i in range(min(imax,len(l))):
        print l[i][0],l[i][1]
       
def extractNAFDesc(codeNAF):
    page = urllib.urlopen("http://www.insee.fr/fr/methodes/default.asp?page=nomenclatures/naf2008/n5_"+codeNAF+".htm")
    s = page.read().decode("iso8859_1")
    s = HTMLParser().unescape(s)
    toComprend = True
    comprend = []
    comprendpas = []
    pair = 1
    while s.find("<tr>")!=-1:
        if pair%2==0:
            s1 = s[s.find("<tr>")+4:s.find("</tr>")]
            while s1.find("<td>")!=-1:
                if toComprend:
                    comprend.append(s1[s1.find("<td>")+4:s1.find("</td>")])
                else:
                    comprendpas.append(s1[s1.find("<td>")+4:s1.find("</td>")])
                s1 = s1[s1.find("</td>")+6:]
        else:
            s1 = s[s.find("<tr>")+4:s.find("</tr>")]
            toComprend = not("pas" in s1)  
        s = s[s.find("</tr>")+6:]
        pair+=1
    if len(comprend)>0:
        comprend = TextProcessing.nltkprocess(comprend[0])
    if len(comprendpas)>0:
        comprendpas = TextProcessing.nltkprocess(comprendpas[0])
    return (codeNAF,comprend,comprendpas)
                    
def getNbResultBing(searchword, toPrint=False):
    while searchword.find(" ")!=-1:
        searchword = searchword[:searchword.find(" ")]+"+"+searchword[searchword.find(" ")+1:]
    while searchword.find(",")!=-1:
        searchword = searchword[:searchword.find(",")]+searchword[searchword.find(",")+1:]
    url = ("https://www.bing.com/search?q="+searchword)
    print url
    s = "-1"
    if toPrint:
        print "requete bing:",searchword,"-",
    try:
        page = urllib.urlopen(url)
        for line in page:
            i = line.find(" results<")
            if i!=-1:
                s = line[i-13:i]
                s = s[s.find(">")+1:]
                while s.find(",")!=-1:
                    s = s[:s.find(",")]+s[s.find(",")+1:]
    except:
        print "erreur"
        pass
    if toPrint:
        print int(s),"résultats"
    return int(s)

def getGrammNatureViaInternet(searchword):
    try:
        word = unidecode.unidecode(unicode(searchword,"utf8"))
    except:
        word = searchword
    url = ("http://www.le-dictionnaire.com/definition.php?mot="+word)
    result = []
    try:
        page = urllib.urlopen(url)
        for line in page:
            if "arial-14-orange-b" in line:
                ind = line.find(">")
                string = line[ind+1:]
                ind = string.find("<")
                string = string[:ind]
                test = string.split(" ")[0]
                if test in ['Nom','Adjectif','Verbe','Adverbe'] and not(test in result):
                    result.append(test)
    except:
        pass
    if len(result)==0:
        # on teste d'autres possibilités
        if word[-1] == "s":
            result = getGrammNatureViaInternet(word[:-1])
    return result

''' functions about graph saving and importing'''
                   
def saveGraph(graph):
    ''' 
    function that stores one graph in the current directory
    -- IN:
    graph : the graph to store (Graph)
    filename : the root name for the file to store (str)
    '''
    # saving nodes
    with codecs.open(graph.name+"_nodes.txt","w","utf-8") as fichier:
        for node in graph.graphNodes.values():
            fichier.write(str(node.id) \
                          +"_"+node.name \
                          +"_"+str(node.genericity) \
                          +"_")
            for codeNAF in node.dicNAF:
                fichier.write(str(codeNAF)+"-"+str(node.dicNAF[codeNAF]))
                fichier.write(",")
            fichier.write("\n")
    # saving edges
    with codecs.open(graph.name+"_edges.txt","w","utf-8") as fichier:
        for node in graph.graphEdges:
            fichier.write(str(node[0])+"_" \
                          +str(node[1])+"_" \
                          +str('%.2f' %graph.graphEdges[node].value) \
                          +"_"+str(graph.graphEdges[node].nbOccurence)+"\n")

def importGraph(filename):
    '''
    function that imports a complete graph, including graphNodes and graphEdges
    the os path must be settle in the subset file
    -- IN:
    subsetname: name of the subset from which import the graph (str)
    --OUT:
    graph: imported graph (GraphKeyword)
    '''
    graph = GraphKeyword(filename)
    if not(filename+"_nodes.txt" in os.listdir(".")):
        print "non-existing graphNodes"
        return graph
    if not(filename+"_edges.txt" in os.listdir(".")):
        print "non-existing graphEdges"
        return graph
    # importing nodes
    with codecs.open(filename+"_nodes.txt","r","utf-8") as fichier:
        flag = False
        for line in fichier:
            flag = not flag
            if flag:
                totalLine = ""
            totalLine += line[:-1]
            if not flag:
                tab = totalLine.split("_")
                graph.dicIdNodes[tab[1]] = int(tab[0])
                graph.graphNodes[int(tab[0])] = GraphPreprocess.Node(graph.dicIdNodes[tab[1]], tab[1])
                graph.graphNodes[int(tab[0])].genericity = float(tab[2])
                for element in tab[3].split(','):
                    tab1 = element.split("-")
                    if len(tab1)>1:
                        graph.graphNodes[int(tab[0])].dicNAF[str(tab1[0])] = float(tab1[1])
    # importing edges
    with codecs.open(filename,"r","utf-8") as fichier:
        for line in fichier:
            if len(line)>3:
                tab = line.split("_")
                graph.graphEdges[(int(tab[0]),int(tab[1]))] = GraphPreprocess.Edge(int(tab[0]),int(tab[1]))
                graph.graphEdges[(int(tab[0]),int(tab[1]))].value = float(tab[2])
                graph.graphEdges[(int(tab[0]),int(tab[1]))].nbOccurence = int(tab[3])
    return graph
     
def saveGexfFile(filename, graph, thresoldEdge=0.0):
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
        for node in graph.graphNodes.values():
            fichier.write("<node id=\"")
            fichier.write(str(node.id))
            fichier.write("\" label=\"")
            fichier.write(node.name.replace("&","et"))
            fichier.write("\">\n")
            fichier.write("<viz:size value=\"")
            fichier.write(str(sum(node.dicNAF.values())))
            fichier.write("\"/>\n")
            fichier.write("</node>")
        fichier.write("</nodes>\n")
        # writing edges
        fichier.write("<edges>\n")
        i=0
        for edge in graph.graphEdges.values():
            if edge.value>thresoldEdge:
                fichier.write("<edge id=\"")
                fichier.write(str(i))
                fichier.write("\" source=\"")
                fichier.write(str(edge.id0))
                fichier.write("\" target=\"")
                fichier.write(str(edge.id1))
                fichier.write("\" type=\"undirected\" weight=\"")
                fichier.write(str(edge.value))
                fichier.write("\"/>\n")
                i+=1
        fichier.write("</edges>\n")
        fichier.write("</graph>\n")
        fichier.write("</gexf>")

def saveGexfFileNaf(filename, graph, codeNAF):
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
        concernedNodes = []
        for node in graph.graphNodes:
            if codeNAF in graph.graphNodes[node][2]:
                concernedNodes.append(node)
                fichier.write("<node id=\"")
                fichier.write(str(node))
                fichier.write("\" label=\"")
                fichier.write(graph.graphNodes[node][0].replace("&","et"))
                fichier.write("\">\n")
                fichier.write("<viz:size value=\"")
                fichier.write(str(graph.graphNodes[node][2][codeNAF]))
                fichier.write("\"/>\n")
                fichier.write("</node>")
        fichier.write("</nodes>\n")
        # writing edges
        fichier.write("<edges>\n")
        i=0
        selectedEdges = []
        maxEdge = 0
        for edge in graph.graphEdges:
            if int(edge[0]) in concernedNodes and int(edge[1]) in concernedNodes:
                selectedEdges.append(edge)
                if 3.0*graph.graphEdges[edge][0]/graph.graphEdges[edge][1]>maxEdge:
                    maxEdge = 3.0*graph.graphEdges[edge][0]/graph.graphEdges[edge][1]
        for edge in selectedEdges:
#             if codeNAF in graphNodes[int(edge[0])][2] or codeNAF in graphNodes[int(edge[1])][2] :
            if 3.0*graph.graphEdges[edge][0]/graph.graphEdges[edge][1]>=3.5*maxEdge/5.0:
                fichier.write("<edge id=\"")
                fichier.write(str(i))
                fichier.write("\" source=\"")
                fichier.write(str(edge[0]))
                fichier.write("\" target=\"")
                fichier.write(str(edge[1]))
                fichier.write("\" type=\"undirected\" weight=\"")
                fichier.write(str(3.0*graph.graphEdges[edge][0]/graph.graphEdges[edge][1]))
                fichier.write("\"/>\n")
                i+=1
        fichier.write("</edges>\n")
        fichier.write("</graph>\n")
        fichier.write("</gexf>")
        
def getSuggestedKeywordsByNAF(codeNAF):
    keywords = []
    os.chdir(Constants.pathCodeNAF+"/codeNAF_"+str(codeNAF))
    with open("keywordSuggest.txt","r") as fichier:
        for line in fichier:
            keywords.append(line[:-1])
    return keywords
 
''' functions about saving and importing keywords'''

def importKeywords(path = None, filename ="keywords.txt"):
    '''
    function that imports the keywords out of a file given by pathArg
    (the path must contain a file named keywords.txt
    if the given path is None (default) the extracted file is motscles/mots-cles.txt
    the function then put them in the dictionary 'keywords', which values are the tokenized keywords
    -- IN:
    path : path of the file to load (path) default = None
    name : name of the file (str) default = "keywords.txt"
    -- OUT:
    keywords : the dictionary containing the keywords
    '''
    keywords = {}
    dicWordWeight = {}
    if path is None:
        path = Constants.path+"/motscles"
    try:
        os.chdir(path)
        if not (filename in os.listdir(".")):
            print "file not found :", filename
            return [{},{}]
    except:
        print "directory not found :",path
        return [{},{}]
    with codecs.open(filename,"r","utf-8") as fichier:
        for line in fichier:
            i = -2
            if line[-3]==" ":
                i=-3
            if len(line)>1:
                tokens = TextProcessing.nltkprocess(line[:i])
                if len(tokens)>0:
                    keywords[line[:i]] = tokens
                else:
                    continue
    for keywordSlugs in keywords.values():
        for slug in keywordSlugs:
            if not (slug in dicWordWeight):
                dicWordWeight[slug]=0
            dicWordWeight[slug]+=1
    return [keywords, dicWordWeight]
     
def saveKeywords(keywords, path = None, filename = "keywords.txt"):  
    '''
    function that saves the list of keywords under the file named filenamed
    at the location specified by path.
    The input object keywords should be a dictionary containing the keywords as indexes.
    -- IN
    keywords : dic containing keywords to print as indexes (dic)
    path : path to save the file (str) default = None (-> in this case the path will be constant.path+"/motscles")
    filename : name of the file to save (str) default = "keywords.txt"
    -- OUT
    the function returns nothing
    '''
    if path is None:
        path = Constants.path+"/motscles"
    os.chdir(path)
    with codecs.open(filename,"w","utf8") as fichier:
        for keyword in keywords:
            fichier.write(keyword+"\n")
            
def importListCodeNAF():
    '''
    function that returns the list of codeNAF
    located in the pathCodeNAF
    -- IN:
    the function takes no argument
    -- OUT:
    codeNAFs : list of all codeNAF ([str])
    '''
    os.chdir(Constants.pathCodeNAF)
    codeNAFs = []
    with open("listeCodeNAF.txt","r") as fichier:
        for line in fichier:
            codeNAFs.append(line[:-1])
    return codeNAFs
           
''' function about progress printing '''

class Compt():
    ''' class which implements the compt object, 
    which main purpose is printing progress
    '''
    def __init__(self, completefile, p=10, printAlone=True):
        self.i = 0
        self.total = len(completefile)
        self.percent = p
        self.deltaPercent = p
        self.printAlone = printAlone

    def updateAndPrint(self):
        self.i+=1
        if 100.0*self.i/self.total >= self.percent:
            print self.percent,"%",
            self.percent+=self.deltaPercent
            if (self.deltaPercent==1 and self.percent%10==1) \
                or (self.deltaPercent==0.1 and ((int)(self.percent*10))%10==0) \
                or (self.i==self.total) \
                or not self.printAlone:
                    print ""
              
                    
def printTime(startTime):
    totalTime = (time.time()-startTime)
    hours = (int)(totalTime/3600)
    minutes = (int)((totalTime-3600*hours)/60)  
    seconds = (int)(totalTime%60)
    print "time : ",hours,':',minutes,':',seconds
                  
                    
                    
                    
                    
                    
                    
                    
                    
                    
                