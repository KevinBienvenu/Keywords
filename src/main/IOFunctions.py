# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''
''' functions '''

from HTMLParser import HTMLParser
import codecs
from operator import itemgetter
import os
import time
import urllib
from nltk.corpus import stopwords
import nltk.stem.snowball
import unidecode, re
import pandas as pd


import Constants
from GraphProcessing import GraphKeyword, Node, Edge



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
            tab = line[:-1].split(sep)
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
        comprend = tokenizeAndStemmerize(comprend[0])
    if len(comprendpas)>0:
        comprendpas = tokenizeAndStemmerize(comprendpas[0])
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

''' Auxiliary text processing functions'''

def preprocessString(srctxt):
    '''
    function transforming str and unicode to string without accent
    or special characters, writable in ASCII
    '''
    try:
        srctxt = unicode(srctxt,"utf8")
    except:
        pass
    return unidecode.unidecode(srctxt).lower()

def tokenizeAndStemmerize(srctxt, 
                keepComa = False, 
                french_stopwords = set(stopwords.words('french')),
                stem = nltk.stem.snowball.FrenchStemmer(),
                method = "stem"):
    '''
    NLP function that transform a string into an array of stemerized tokens
    The punctionaction, stopwords and numbers are also removed as long as words shorter than 3 characters
    -- IN:
    srctxt : the string text to process (string)
    keepComa : boolean that settles if the process should keep comas/points during the process (boolean) default=false
    french_stopwords : set of french stop_words
    stem : stemmerizer
    -- OUT:
    stems : array of stemerized tokens (array[token]) 
    '''
    srctxt = preprocessString(srctxt)
    srctxt = re.sub(r" \(([a-z]| )*\)","",srctxt)
    srctxt = re.sub(r"-"," ",srctxt)
    tokens = nltk.word_tokenize(srctxt,'french')
    tokens = [token for token in tokens if (keepComa==True and (token=="." or token==",")) \
                                            or (len(token)>1 and token not in french_stopwords)]
    stems = []
    for token in tokens:
        try:
            # removing numbers
            float(token)
        except:
            if token[0:2]=="d'":
                token = token[2:]
            if len(token)>2:
                if method=="stem":
                    stems.append(stem.stem(token)) 
            if len(token)==1 and keepComa==True:
                stems.append(token)        
    return stems
                        
''' subset creation and saving '''

def extractSubset(codeNAF="", n=0, path=None, toPrint=False):
    '''
    function that extract one subset from the database
    by default it extracts the whole content of the database,
    however it's possible to choose a particular codeNAF or a maximal length.
    -- IN:
    codeNAF : string containing the code NAF *optional (str) default= ""
        (-> let to "" if no filter according to the code NAF is wanted)
    n : size of the desired extract *optional (int) default = 0
        (-> let to 0 to extract the whole subset)
    '''
    startTime= time.time()
    if path is None:
        path = Constants.pathCodeNAF
    if codeNAF=="":
        if n==0:
            subsetname = "graphcomplet"
        else:
            subsetname = "graphcomplet_size_"+str(n)
    else:
        if n==0:
            subsetname = "subset_NAF_"+str(codeNAF)
        else:
            subsetname = "subset_NAF_"+str(codeNAF)
            
    os.chdir(Constants.pathAgreg)
    if toPrint:
        print "== Extracting random subset of size",n,"for codeNAF:",codeNAF
    csvfile = pd.read_csv("descriptions.csv", usecols=['codeNaf', 'description'])
    csvfile = csvfile[csvfile.description.notnull()]
    csvfile = csvfile[csvfile.codeNaf.notnull()]
    if codeNAF!="":
        csvfile = csvfile[csvfile.codeNaf.str.contains(codeNAF)==True]
    if toPrint:
        print " done"
        print "sampling...",
    if n>0 and len(csvfile)>0:
        csvfile = csvfile.sample(min(n,len(csvfile)))
    if toPrint:
        print " done"
        print "extracting entreprises...",
    entreprises=[[line[0],line[1]] for line in csvfile.values]
    if toPrint:
        print " done:",len(entreprises),"entreprises selected"         
    os.chdir(path)
    if subsetname not in os.listdir("."):
        os.mkdir("./"+subsetname)
    os.chdir("./"+subsetname)
    with open("subset_entreprises.txt","w") as fichier:
        i=0
        for entreprise in entreprises:
            fichier.write(""+str(i)+"_"+str(entreprise[0])+"_")
            fichier.write(entreprise[1])
            fichier.write("\n")
    if toPrint:
        print "done in:",
        Constants.printTime(startTime)
    
def importSubset(subsetname, path=Constants.pathSubset):
    '''
    function that imports a previously computed subset 
    and puts it into the array entreprises
    -- IN:
    filename : the name of the subset to import (string)
    -- OUT:
    entreprises : array containing info about the entreprise (array) [siren,naf,desc]
    keywords : dic of keywords
    '''
    # importing file
    os.chdir(path)
    if not(subsetname in os.listdir(".")):
        print "non-existing subset"
        return (None,None,None)
    os.chdir("./"+subsetname)
    entreprises = []
    with open("subset_entreprises.txt","r") as fichier:
        for line in fichier:
            entreprises.append(line.split("_"))
    entreprises.sort(key=itemgetter(1),reverse=True)
    return entreprises

def importTrainedSubset(subsetname, path=Constants.pathSubset):
    '''
    function that imports a previously computed subset 
    and puts it into the array entreprises
    -- IN:
    filename : the name of the subset to import (string)
    -- OUT:
    entreprises : array containing info about the entreprise (array) [siren,naf,desc]
    keywords : dic of keywords
    '''
    # importing file
    os.chdir(path)
    if not(subsetname in os.listdir(".")):
        print "non-existing subset"
        return (None,None,None)
    os.chdir("./"+subsetname)
    entreprises = []
    with open("trained_entreprises.txt","r") as fichier:
        for line in fichier:
            entreprises.append(line.split("_"))
            entreprises[2] = entreprises[2].split("=")
    return entreprises

''' functions about saving and importing keywords'''

def importKeywords(codeNAF = ""):
    '''
    function that imports the keywords for a given codeNAF
    if the given codeNAF is "" (default) the extracted file is motscles/mots-cles.txt
    the function then put them in the dictionary 'keywords', which values are the tokenized keywords
    and also returns the dicWordWeight, containing stems frequencies.
    -- IN:
    path : path of the file to load (path) default = None
    name : name of the file (str) default = "keywords.txt"
    -- OUT:
    keywords : the dictionary containing the keywords {keyword (str): [stems (str)]}
    dicWordWeight : the dictionary containing stems and their frequencies {stems (str): freq (int)}
    '''
    keywords = {}
    dicWordWeight = {}
    if codeNAF == "":
        path = os.path.join(Constants.path,"motscles")
    else:
        path = os.path.join(Constants.pathCodeNAF,"subset_NAF_"+str(codeNAF[-5:]))
    try:
        os.chdir(path)
        if not ("keywords.txt" in os.listdir(".")):
            print "file not found"
            return [{},{}]
    except:
        print "directory not found :",path
        os.chdir(os.path.join(Constants.path,"motscles"))
    with codecs.open("keywords.txt","r","utf-8") as fichier:
        for line in fichier:
            i = -2
            if len(line)>1:
                tokens = tokenizeAndStemmerize(line[:i])
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
            fichier.write(keyword+"\r\n")
            
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
           
def getSuggestedKeywordsByNAF(codeNAF):
    keywords = []
    try:
        os.chdir(Constants.pathCodeNAF+"/subset_NAF_"+str(codeNAF))
        with open("keywords.txt","r") as fichier:
            for line in fichier:
                keywords.append(line[:-1])
    except:
        pass
    return keywords



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

def importGraph(filename, edges=True):
    '''
    function that imports a complete graph, including graphNodes and graphEdges
    the os path must be settle in the subset file
    -- IN:
    subsetname: name of the subset from which import the graph (str)
    /!\ must be in the correct sub-directory
    --OUT:
    graph: imported graph (GraphKeyword)
    '''
    graph = GraphKeyword(filename)
    if not("graph_"+filename+"_nodes.txt" in os.listdir(".")):
        print "non-existing graphNodes"
        return graph
    if not("graph_"+filename+"_edges.txt" in os.listdir(".")):
        print "non-existing graphEdges"
        return graph
    # importing nodes
    with codecs.open("graph_"+filename+"_nodes.txt","r","utf-8") as fichier:
        for line in fichier:
            if line[0]==u'\ufeff':
                tab = line[1:].split("_")
            else:
                tab = line.split("_")
            try:
                graph.dicIdNodes[tab[1]] = int(tab[0])
            except:
                print tab
                print line[0]
            graph.graphNodes[int(tab[0])] = Node(graph.dicIdNodes[tab[1]], tab[1])
            graph.graphNodes[int(tab[0])].genericity = float(tab[2])
            for element in tab[3].split(','):
                tab1 = element.split("-")
                if len(tab1)>1:
                    graph.graphNodes[int(tab[0])].dicNAF[str(tab1[0])] = float(tab1[1])
    # importing edges
    if edges:
        with codecs.open("graph_"+filename+"_edges.txt","r","utf-8") as fichier:
            for line in fichier:
                if len(line)>3:
                    tab = line.split("_")
                    graph.graphEdges[(int(tab[0]),int(tab[1]))] = Edge(int(tab[0]),int(tab[1]))
                    graph.graphEdges[(int(tab[0]),int(tab[1]))].value = float(tab[2])
                    graph.graphEdges[(int(tab[0]),int(tab[1]))].nbOccurence = int(tab[3])
                    graph.graphNodes[int(tab[0])].neighbours.append(graph.getNode(int(tab[1])))
                    graph.graphNodes[int(tab[1])].neighbours.append(graph.getNode(int(tab[0])))
    return graph
     
def saveGexfFile(filename, graph, thresoldEdge=0.0, keywords = None):
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
#             print [node.name], keywords
            if keywords is None or node.name in keywords:
                fichier.write("<node id=\"")
                fichier.write(str(node.id))
                fichier.write("\" label=\"")
                fichier.write(node.name.replace("&","et"))
                fichier.write("\">\n")
                fichier.write("<viz:color r=\""+str(node.color[0])+"\" g=\""+str(node.color[1])+"\" b=\""+str(node.color[2])+"\" a=\"0.9\"/>\n")
                fichier.write("<viz:size value=\"")
                if not(keywords is None) and node.name in keywords:
                    fichier.write(str(int(10*keywords[node.name])))
                elif node.size == 0:
                    fichier.write(str(sum(node.dicNAF.values())))
                else:
                    fichier.write(str(node.size))                
                fichier.write("\"/>\n")
                fichier.write("<viz:shape value=\""+node.shape+"\"/>")
                fichier.write("</node>")
        fichier.write("</nodes>\n")
        # writing edges
        fichier.write("<edges>\n")
        i=0
        for edge in graph.graphEdges.values():
            if edge.value>thresoldEdge \
            and (keywords is None \
                 or (graph.graphNodes[edge.id0].name in keywords \
                     and graph.graphNodes[edge.id1].name in keywords)):
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
                fichier.write("<viz:color r="+str(node.color[0])+"g="+str(node.color[1])+"b="+str(node.color[2])+"a=1.0/>\n")
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
 
def extractKeywordsFromGraph(subsetname, path = Constants.pathSubset):
    '''
    function that returns the list of keywords present in a graph of a subset.
    Therefore the function extractGraphFromSubset must be called before this one
    '''
    try:
        os.chdir(path+"/"+subsetname)
    except:
        print "subset not found :",subsetname
        return
    if not("graph_"+subsetname+"_nodes.txt" in os.listdir(".")):
        print "non-existing graphNodes"
        return
    keywords = []
    with codecs.open("graph_"+subsetname+"_nodes.txt","r","utf-8") as fichier:
        for line in fichier:
            if line[0]==u'\ufeff':
                tab = line[1:].split("_")
            else:
                tab = line.split("_")
            keywords.append(tab[1])
    saveKeywords(keywords, path+"/"+subsetname, "keywords.txt")
        



             
                    
                    
                    
                    
                    
                    
                    
                