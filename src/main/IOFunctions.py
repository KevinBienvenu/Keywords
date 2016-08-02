# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu

Functions dealing with file as input and output.
Particularly the import and saving of subsets, keywords and graphs
The module is cut into three parts, one for each of the examples enumerated above.
'''

''' subset creation and saving '''

import codecs
from operator import itemgetter
import os
import re
import time
import urllib

from GraphProcessing import GraphKeyword, Node, Edge
import UtilsConstants
import pandas as pd


def extractAndSaveSubset(codeNAF="", n=0, path=UtilsConstants.pathCodeNAF, toPrint=False):
    '''
    function that extract a subset from the database then save it in a file.
    by default it extracts the whole content of the database,
    however it's possible to choose a particular codeNAF or a size.
    -- IN:
    codeNAF : string containing the code NAF *optional (str) default= ""
        (-> let "" if no filter according to the code NAF is wanted)
    n : size of the desired extract *optional (int) default = 0
        (-> let 0 to extract the whole subset)
    path : the path were to save the extracted subset *optional (str) default=UtilsConstants.pathCodeNAF
    toPrint : boolean that settles if information must be displayed (boolean) default = False
    -- OUT:
    the function returns True if everything went fine, False else.
    '''
    startTime= time.time()
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
    entreprises = extractSubset(codeNAF, n, path, toPrint)        
    try:
        os.chdir(path)
    except:
        if toPrint:
            "non existing path in subset extraction -aborting"
        return False
    if subsetname not in os.listdir("."):
        os.mkdir("./"+subsetname)
    os.chdir("./"+subsetname)
    with open("subset_entreprises.txt","w") as fichier:
        i=0
        for entreprise in entreprises:
            try:
                fichier.write(""+str(i)+"_"+str(entreprise[0])+"_")
                fichier.write(entreprise[1])
                fichier.write("\n")
            except:
                "error in subset saving - codeNAF:",codeNAF,"n:",n,"entreprise :",entreprise
                return False
            i+=1
    if toPrint:
        print "done in:",
        UtilsConstants.printTime(startTime)
    if "subset_entreprises.txt" in os.listdir("."):
        return True
    else: 
        return False

def extractSubset(codeNAF="", n=0, path=UtilsConstants.pathCodeNAF, toPrint=False):
    '''
    function that extract a subset from the database
    by default it extracts the whole content of the database,
    however it's possible to choose a particular codeNAF or a maximal size.
    -- IN:
    codeNAF : string containing the code NAF *optional (str) default= ""
        (-> let "" if no filter according to the code NAF is wanted)
    n : size of the desired extract *optional (int) default = 0
        (-> let 0 to extract the whole subset)
    path : the path were to save the extracted subset *optional (str) default=UtilsConstants.pathCodeNAF
    toPrint : boolean that settles if information must be displayed (boolean) default = False
    -- OUT:
    '''     
    try:
        os.chdir(UtilsConstants.pathAgreg)
    except:
        print "Non-existing path : pathAgreg -aborting"
        return []
    if toPrint:
        print "== Extracting random subset of size",n,"for codeNAF:",codeNAF
    if not("descriptions.csv" in os.listdir(".")):
        print "Impossible to find the file descriptions.csv -aborting"
        return []
    # retrieving the csv file containing descriptions
    csvfile = pd.read_csv("descriptions.csv", usecols=['codeNaf', 'description'])
    # applying basic criteria over the description and codeNAF
    csvfile = csvfile[csvfile.description.notnull()]
    csvfile = csvfile[csvfile.codeNaf.notnull()]
    if codeNAF!="":
        csvfile = csvfile[csvfile.codeNaf.str.contains(codeNAF)==True]
    if toPrint:
        print " done"
    # sampling according to the input size n
        print "sampling...",
    if n>0 and len(csvfile)>0:
        csvfile = csvfile.sample(min(n,len(csvfile)))
    if toPrint:
        print " done"
        print "extracting entreprises...",
    entreprises=csvfile.values
    if toPrint:
        print " done:",len(entreprises),"entreprises selected"         
    return entreprises
    
def importSubset(subsetname, path=UtilsConstants.pathCodeNAF):
    '''
    function that imports a previously computed subset 
    and puts it into the array entreprises.
    The resulting entreprises are sorted by codeNAF
    -- IN:
    subsetname : the name of the subset to import (string)
    path : the path were the subset is located *optional (string) default: UtilsConstants.pathSubset
    -- OUT:
    entreprises : array containing info about the entreprise (array) [[siren,naf,desc]]
    '''
    # importing file
    os.chdir(path)
    if not(subsetname in os.listdir(".")):
        print "non-existing subset"
        return []
    os.chdir("./"+subsetname)
    entreprises = []
    with open("subset_entreprises.txt","r") as fichier:
        for line in fichier:
            entreprises.append(line.split("_"))
    entreprises.sort(key=itemgetter(1),reverse=True)
    return entreprises


''' keywords saving and importing '''

def importKeywords(codeNAF = "", filename="keywords.txt"):
    '''
    function that imports the keywords for a given codeNAF
    if the given codeNAF is "" (default) the extracted file is motscles/mots-cles.txt
    the function then put them in the dictionary 'keywords', which values are the tokenized keywords
    and also returns the dicWordWeight, containing stems frequencies.
    -- IN:
    codeNAF : codeNAF of the keywords to extract *optional (str) default = ""
        (-> let "" to get the full set of keywords, stored in motscles/mots-cles.txt)
    filename : the name of the file of keywords to import (str) ('keywords.txt' or 'specialkeywords.txt') default = "keywords.txt"
    -- OUT:
    keywords : the dictionary containing the keywords {keyword (str): [stems (str)]}
    dicWordWeight : the dictionary containing stems and their frequencies {stems (str): freq (int)}
    '''
    keywords = {}
    dicWordWeight = {}
    if codeNAF == "":
        path = os.path.join(UtilsConstants.path,"motscles")
    else:
        path = os.path.join(UtilsConstants.pathCodeNAF,"subset_NAF_"+str(codeNAF[-5:]))
    try:
        os.chdir(path)
        if not (filename in os.listdir(".")):
            print "file not found"
            return [keywords, dicWordWeight]
    except:
        print "directory not found :",path
        os.chdir(os.path.join(UtilsConstants.path,"motscles"))
    with codecs.open(filename,"r","utf-8") as fichier:
        for line in fichier:
            i = -2
            if len(line)>1:
                tokens = UtilsConstants.tokenizeAndStemmerize(line[:i])
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
     
def saveKeywords(keywords, path = UtilsConstants.path+"/motscles", filename = "keywords.txt"):  
    '''
    function that saves the list of keywords under the file named filename
    at the location specified by path.
    The input object keywords should be a dictionary containing the keywords as indexes.
    NB : It could also be a list or a set of keywords.
    -- IN
    keywords : dic containing keywords to print as indexes (dic)
    path : path to save the file (str) default = None 
        (-> in this case the path will be constant.path+"/motscles")
    filename : name of the file to save (str) default = "keywords.txt"
    -- OUT
    the function returns True if everything went fine, False else.
    '''
    os.chdir(path)
    try:
        l = keywords.keys()
    except:
        l = list(keywords)
    l.sort()
    with codecs.open(filename,"w","utf8") as fichier:
        for keyword in l:
            try:
                fichier.write(keyword+"\r\n")
            except:
                print "Problem in the writing of the file 'keywords' for the keyword:",keyword
                return False
    if filename in os.listdir("."):
        return True
    else:
        return False

def importSlugEquivalence():
    '''
    Function that imports the file equivalence.txt located in the keywords path
        and stores the equivalences in a dictionary.
    Those equivalence are used for the slug matching during step 01.
    For instance 'boulanger' and 'boulangerie' are one of those equivalences.
    For each member of the equivalence, there is one entry in the dictionary where the corresponding
        value is an array containing all the other members of the equivalence.
    -- IN
    The function takes no argument
    -- OUT
    equivalences : dictionary containing the equivalences ({slug : [slug1, slug2...]}) 
    '''
    path = UtilsConstants.pathKeywords
    os.chdir(path)   
    equivalences = {}
    if not("equivalences.txt" in os.listdir(".")):
        print "non-existing file 'equivalences.txt"
        return equivalences
    with codecs.open("equivalences.txt","r","utf-8") as fichier:
        for line in fichier:
            tab = line[:-2].split(";")
            for t in tab:
                if not t in equivalences:
                    equivalences[t] = []
            equivalences[t] += tab
    return equivalences
    
def importListCodeNAF():
    '''
    function that returns the list of codeNAF
    located in the pathCodeNAF
    -- IN:
    the function takes no argument
    -- OUT:
    codeNAFs : list of all codeNAF ([str])
    '''
    os.chdir(UtilsConstants.pathCodeNAF)
    codeNAFs = UtilsConstants.importDict("listeCodeNAF.txt","_")
    del codeNAFs[" "]
    return codeNAFs


''' functions about graph saving and importing'''
                   
def saveGraph(graph):
    ''' 
    function that stores one graph in the current directory.
    This is done by creating two files one for the nodes, and one for the edges.
    The name used to save the graph is the one contained in the graph attributes.
    -- IN:
    graph : the graph to store (Graph
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
    graph = GraphKeyword("graph_"+filename)
    if not("graph_"+filename+"_nodes.txt" in os.listdir(".")):
        print "non-existing graphNodes:",filename
        return graph
    if not("graph_"+filename+"_edges.txt" in os.listdir(".")):
        print "non-existing graphEdges:",filename
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
                    graph.graphNodes[int(tab[0])].neighbours[graph.getNode(int(tab[1]))] = float(tab[2])
                    graph.graphNodes[int(tab[1])].neighbours[graph.getNode(int(tab[0]))] = float(tab[2])
    return graph
     
def saveGexfFile(filename, graph, thresoldEdge=0.0, codeNAF="", keywords = None, origins = None):
    '''
    Function that saves the graph under a .gexf file
    to allow a further visualisation using the free software Gephi.
    -- IN
    filename : name of the file to save the graph (str)
    graph : complete graph object to save (graph)
    thresholdEdge : threshold under which the edges are not displayed (float) default = 0.0
        (does not change the graph, only let the visualisation be lighter and easier)
    codeNAF : only the keywords containing this codeNAF value are printed (string) default = ""
        (-> let "" to delete the filter over the codeNAF)
    keywords : list or dic selected keywords to display ([] or {}) default = None
        (-> let None to display all the keywords)
    origins : dic linking all the keywords to an integer reflecting their origin ({keyword(str) : origin(int)}
        (-> only used if keywords is set)
    -- OUT
    the function returns True if everything went fine, False else.
    '''
    with codecs.open(filename,"w","utf-8") as fichier:
        try:
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
                if (keywords is None and codeNAF=="") \
                    or ((codeNAF=="" or codeNAF in node.dicNAF) \
                        and ((keywords is None) or node.name in keywords)):
                    fichier.write("<node id=\"")
                    fichier.write(str(node.id))
                    fichier.write("\" label=\"")
                    fichier.write(node.name.replace("&","et"))
                    fichier.write("\">\n")
                    r,g,b = node.color
                    if not(keywords is None) and node.name in keywords:
                        size = int(10*keywords[node.name])
                        if origins[node.name][0] == 1:
                            r,g,b = 0,0,255
                        else:
                            r,g,b = 255,120,0
                    elif node.size == 0:
                        if (codeNAF!="" and codeNAF in node.dicNAF):
                            size = node.dicNAF[codeNAF]
                        else:
                            size = sum(node.dicNAF.values())
                    else:
                        size = node.size              
                    fichier.write("<viz:color r=\""+str(r)+"\" g=\""+str(g)+"\" b=\""+str(b)+"\" a=\"0.9\"/>\n")
                    fichier.write("<viz:size value=\""+str(size)+"\"/>\n")
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
        except:
            print "Error during the saving of the graph under .gexf format"
            False
    return True
        
def updateDescriptionFail(description):
    os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
    with codecs.open("descriptionsFails.txt","a","utf8") as fichier:
        fichier.write(description)
        fichier.write("\r\n")

''' function about internet '''

def correctionOrthographeYahoo(searchword):
    result = searchword
    while searchword.find(" ")!=-1:
        searchword = searchword[:searchword.find(" ")]+"+"+searchword[searchword.find(" ")+1:]
    url = ("https://fr.search.yahoo.com/search?q="+searchword)
    dic = {"&Agrave":"À",
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
            "&rsquo;":"'",
            "&#39;":"'"}
    try:
        exceptions = ["Annonce","Annonces","Aide"]
        for _ in range(3):
            page = urllib.urlopen(url)
        for line in page:
            i = line.find("relatives")
            if i!=-1:
                s = line[i+16:line[i+16:].find("</b>")+i+16]
                for d in dic:
                    while d in s:
                        s = s.replace(d,dic[d])
                if not s in exceptions:
                    result = s
            i = line.find("résultats")
            if i!=-1:
                s = line[i+20:line[i+20:].find("</a>")+i+20]
                while "\">" in s:
                    s = s[s.find("\">")+2:]
                s = re.sub(r"\<([a-z]| |/)*\>","",s)
                for d in dic:
                    while d in s:
                        s = s.replace(d,dic[d])
                if not s in exceptions:
                    result = s
    except:
        pass
    return result.lower()
                    
                    
                    
                    
                    
                    
                    
                