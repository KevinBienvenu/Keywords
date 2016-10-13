# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu

Module that specifies the behaviour of the different steps
of the main algorithm.
- Main pipeline function
- preprocessing : keywords cleaning
- preprocessing : creation of graph
- Step 1 : extraction from description
- Step 3 : extraction from graph
- Step 4 : merging keywords 
'''


''' Main pipeline functions '''

import codecs
from operator import itemgetter
import operator
import os
import random
import time

from nltk.corpus import stopwords
import nltk.stem.snowball

import GraphLearning, IOFunctions, UtilsConstants
import numpy as np


def pipeline(descriptions, nbMot = 5, printGraph = False, toPrint = False):
    '''
    Pipeline function taking as input an array of entreprises containing the codeNAF and description
    and giving as output a list of keywords for each description.
    -- IN:
    descriptions : list of array [[codeNaf(string),description(string)], ...]
    nbMot : maximal number of returned keywords, (int) default : 20
    printGraph : boolean that settles if the function has to print the graphs for the descriptions (boolean) default = False
        those graphs will only contain the selected keywords and display them according to their relevance and origins
        they will be saved in the subfolder "graphtest", in pathCodeNAF.
    -- OUT:
    keywords : list of lists of keywords [[string],[string], ...]
    '''
    # checking validity of inputs
    try:
        for a in descriptions:
            a[0]
            a[1]
            a[2]
    except:
        if toPrint:
            print "error : invalid input, format error."
        return {}
    # importing graph and keywords
    try:
        os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
        graph = IOFunctions.importGraph("graphcomplet")
    except:
        print "veuillez calculer le graph complet avant de lancer le pipeline"
        return
    keywordSet = IOFunctions.importKeywords()
    dicWordWeight = UtilsConstants.importDicWordWeight(keywordSet)
    equivalences = IOFunctions.importSlugEquivalence()
    keywords = {}
    i = 0
    os.chdir(UtilsConstants.pathCodeNAF+"/graphtest")
    compt = UtilsConstants.Compt(descriptions,0.1)
    for line in descriptions:
        keywordlist, origins, _ = selectKeyword(line[2],line[1], graph, keywordSet, dicWordWeight, equivalences, localKeywords=False, n=nbMot, toPrint=toPrint)
        keywords[line[0]] = {"keyword_"+str(i) : keywordlist[i] for i in range(len(keywordlist))}
        if printGraph:
            os.chdir(UtilsConstants.pathCodeNAF+"/graphtest")
            IOFunctions.saveGexfFile("graph_test_"+str(i)+".gexf", graph, keywords = keywordlist, origins = origins)
        i+=1
        compt.updateAndPrint()
    return keywords

def pipelineTest(n = 1000):
    '''
    Fonction de travail, disparaîtra dans la version finale
    (ou à faire disparaître si c'est déjà la version finale et que j'ai oublié :) )
    '''
    print "DEBUT TEST PIPELINE"
    keywordSet = IOFunctions.importKeywords()
    dicWordWeight = UtilsConstants.importDicWordWeight(keywordSet)
    equivalences = IOFunctions.importSlugEquivalence()
    print "   mots-clés importés"
    entreprises = IOFunctions.extractSubset(n = n)
    print "   entreprises importées"
    print ""
    nbNoKw = 0
    for i in range(len(entreprises)):
        line = entreprises[i]
        a = selectKeyword(description = line[1], 
                          codeNAF = line[0], 
                          graph = None, 
                          keywordSet = keywordSet, 
                          dicWordWeight = dicWordWeight, 
                          equivalences = equivalences, 
                          localKeywords = True, 
                          n = 20, 
                          steps = 1, 
                          toPrint = False)[0]
        if len(a)==0:
            print line[1]
            nbNoKw+=1
    print ""
    print ""
    print "proportion d'entreprises sans keywords :",100.0*nbNoKw/n,"%"

def selectKeyword(description, codeNAF, graph = None, keywordSet = None, dicWordWeight = None, equivalences = {}, localKeywords = False, n=50, steps = 3, toPrint = False):
    '''
    
    === MAIN FUNCTION FOR KEYWORD EXTRACTION ===
    
    function that takes a description and a codeNAF and returns a list of suggested keywords.
    the recquired inputs are also the graph (for step 3) and the keywordSet (for step 1)
    an additional input is the maximal number of returned keywords.
    -- IN
    description : string describing the description (string)
    codeNAF : string representing the code NAF (string)
    graph : graph of keywords (GraphProcessing.GraphKeyword)
    keywordSet : dictionary of keywords with stems for values {keyword (str): [stems (str)]}
    dicWordWeight: the dictionary of the frequencies of the stems in keywordSet {stem (str) : freq (int)}
    equivalences : dictionary of the equivalences (dic)
    localKeywords : boolean that settles if the used keywords are the global one or the one corresponding to the codeNAF (boolean) default = False
        (-> if True, the algorithm will import the keywords in the corresponding codeNAF folder and therefore there is no need to specifiy the keywordSet and dicWordWeight)
    n : maximal number of returned keywords (int) default = 50
    steps: the higher step to perform in the algorithm, if 0 no step will be performed, if 4 all will be.
    toPrint : boolean that settles if the function must print the results or not (boolean) default = False
    -- OUT
    keywords : array of keywords, in order of importance ([string])
    origins : array of array of integers ([ [int, int, ...], ...])
    values : array of values corresponding to the notes of the different keywords (between 0 and 1)
    '''
    ## STEP 0 = Initializing
    if toPrint:
        print description
    origin = {}
    if localKeywords:
        keywordSet = IOFunctions.importKeywords(codeNAF)
    elif keywordSet is None or dicWordWeight is None:
        keywordSet = IOFunctions.importKeywords()
    if dicWordWeight is None:
        dicWordWeight = UtilsConstants.importDicWordWeight(keywordSet)
    if graph is None and steps>1:
        # importing graph and keywords
        os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
        graph = IOFunctions.importGraph("graphcomplet")
    ## STEP 1 = Extracting only from description
    flag = False
    try:
        flag = str(description)!="nan"
    except:
        flag = True
    if steps>=1 and flag:
        # extracting from description
        keywordFromDesc = extractFromDescription(string = description, 
                                                 keywords = keywordSet,
                                                 dicWordWeight = dicWordWeight, 
                                                 equivalences = equivalences, 
                                                 booleanMatchParfait=True, 
                                                 toPrint=False)
        # if none is found, we forget the constraint on the perfect match 
        if len(keywordFromDesc)==0:
            keywordFromDesc = extractFromDescription(string = description, 
                                                     keywords = keywordSet,
                                                     dicWordWeight = dicWordWeight, 
                                                     equivalences = equivalences, 
                                                     booleanMatchParfait=False, 
                                                     toPrint=False)   
        # if still none is found, we search over all keywords (and not just local ones)
        if localKeywords and len(keywordFromDesc)==0:
            keywordSet = IOFunctions.importKeywords()
            keywordFromDesc = extractFromDescription(string = description, 
                                                     keywords = keywordSet,
                                                     dicWordWeight = dicWordWeight, 
                                                     equivalences = equivalences, 
                                                     booleanMatchParfait=False, 
                                                     toPrint=False) 
        # eventually we try the orthographic correction (using yahoo)
        if len(keywordFromDesc)==0 and len(description)<50:
            description2 = IOFunctions.correctionOrthographeYahoo(description)
            if description2.lower() != description.lower():
#                 print " = description corrigée :", description,"- en -", description2
                description = description2
                keywordFromDesc = extractFromDescription(string = description, 
                                                     keywords = keywordSet,
                                                     dicWordWeight = dicWordWeight, 
                                                     equivalences = equivalences, 
                                                     booleanMatchParfait=False, 
                                                     toPrint=False) 
        if toPrint:
            print "from desc:"
            UtilsConstants.printSortedDic(keywordFromDesc)
            print ""
        for key in keywordFromDesc:
            origin[key]=[1]
    else:
        keywordFromDesc = {}
            
    ## STEP 3 = Extracting from Graph
    if steps >=3 and keywordFromDesc != {}:
        keywordFromGraph = extractFromGraph(graph,keywordFromDesc, codeNAF, n=10)
        if toPrint:
            print "from graph:"
            UtilsConstants.printSortedDic(keywordFromGraph)
            print ""
            print ""
        for key in keywordFromGraph:
            origin[key]=[3]
    else:
        keywordFromGraph = {}
        
    ## STEP 4 = Merging and Selecting
    if steps >=4:
        keywords = mergingKeywords(keywordFromDesc, keywordFromGraph, graph, codeNAF=codeNAF)
        if toPrint:
            print "merging:"
            UtilsConstants.printSortedDic(keywords)
            print ""
            print ""
        origins = [origin[key] for key in keywords]
        values = [keywordFromDesc[key] if 1 in origin[key] else keywordFromGraph[key] for key in keywords]
    else:
        keywords = keywordFromDesc.keys()+keywordFromGraph.keys()
        origins = [0] * len(keywords)
        values = [0] * len(keywords)
    return keywords[:min(n,len(keywords))], origins[:min(n,len(origins))], values[:min(n,len(values))]
 

''' PREPROCESSING - KEYWORDS CLEANING '''

def cleanKeyword(toPrint = False, varProgress = None):
    """
    function that cleans the keywords list
    by removing equal and equivalent keywords.
    -- IN
        toPrint : boolean that settles if the function must print its results (boolean) default = False
    """
    print "=== Fonction de nettoyage de la liste de mots-clés"
    keywords = IOFunctions.importKeywords()
    equivalences = IOFunctions.importSlugEquivalence()
    newKeywords = {}
    print "   taille originale:",len(keywords)
    for keyword in keywords:
        if keyword.lower() in newKeywords:
            print keyword
        newKeywords[keyword.lower()] = keywords[keyword]
    ''' suppression des doublons purs'''
    doublons = set()
    toRemove = []
    for keyword1 in keywords:
        s = "+".join(keywords[keyword1])
        if s in doublons:
            toRemove.append(keyword1)
        else:
            doublons.add(s)
    for w in toRemove:
        del keywords[w]
    ''' suppression des doublons par equivalence'''
    toRemove = []
    for kw1 in keywords:
        for kw2 in keywords:
            if kw1>=kw2:
                continue
            slugs1 = keywords[kw1]
            slugs2 = keywords[kw2]
            flag = len(slugs1)==len(slugs2) 
            i = 0
            while flag and i<len(slugs1):
                flag = slugs1[i]==slugs2[i] or slugs1[i] in equivalences and slugs2[i] in equivalences[slugs1[i]]
                i+=1
            if i == len(slugs1) and flag:
                toRemove.append(kw2)
    for w in toRemove:
        del keywords[w]
    print "longueur finale de la liste de mots clés:",len(keywords)
    IOFunctions.saveKeywords(keywords)
      
def statsAboutKeywords():
    """
    Function that prints stats about keywords,
    without modifying the content of the lists.
    """
    keywords = IOFunctions.importKeywords()
    dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
    print "== mots-clés importés"
    print ""
    print "nombre total de mots-clés :",len(keywords)
    print "nombre total de slugs : ",len(dicWordWeight)
    print ""
    print ""
    
    nbKwPerSlugNb = []
    for slugs in keywords.values():
        n = len(slugs)
        while len(nbKwPerSlugNb)<=n:
            nbKwPerSlugNb.append(0)
        nbKwPerSlugNb[n]+=1
    print "répartition des slugs :"
    print "  nb Slug     nb Keywords"
    for i in range(1,len(nbKwPerSlugNb)):
        print "    ",str(i),"    :    ",str(nbKwPerSlugNb[i])
    print ""
    
    print "répartition des fréquences :"
    freqs = ["1  ","3  ","5  ","10 ","30 ","50 ","100","300","500","+  "]
    nbSlugPerFreq = [0]*(len(freqs))
    bigFreq = []
    seuilBigFreq = 50
    for slug,freq in dicWordWeight.items():
        i = 0
        while i<len(freqs)-1 and int(freqs[i])<freq:
            i+=1
        nbSlugPerFreq[i]+=1
        if freq>seuilBigFreq:
            bigFreq.append(slug)
    print "  freq     nb Slug"
    for l in zip(freqs,nbSlugPerFreq):
        print "  ",str(l[0]),"  :   ",str(l[1])
    print ""
    
    print "slugs à grosse fréquence : (>"+str(seuilBigFreq)+")"
    l = len(bigFreq)
    bigFreq.sort()
    for slug in zip(bigFreq[:l/3],bigFreq[l/3:2*l/3],bigFreq[2*l/3:]):
        print " ",slug[0]," ; ",slug[1]," ; ",slug[2]
    print ""
    
        
    seuilMidFreq = 50
    print "keywords dont tous les slugs sont à grosse fréquence : (>"+str(seuilMidFreq)+")"
    curiousKw = []
    for keyword, slugs in keywords.items():
        flag = True
        for slug in slugs:
            if dicWordWeight[slug]<seuilMidFreq:
                flag = False
                break
        if flag:
            curiousKw.append(keyword)
    l = len(curiousKw)
    curiousKw.sort()
    for kws in zip(curiousKw[:l/3],curiousKw[l/3:2*l/3],curiousKw[2*l/3:]):
        print " ",kws[0]," ; ",kws[1]," ; ",kws[2] 
    print ""
        
    print "keywords avec slugs multiples :"
    for keyword, slugs in keywords.items():
        if len(np.unique(slugs)) <len(slugs):
            print "  ",keyword
    print ""
    
    seuilTaille = 25
    largeKw = [] 
    for keyword in keywords:
        if len(keyword)>seuilTaille:
            largeKw.append(keyword) 
    l = len(largeKw)
    largeKw.sort()
    print "keywords de grande longueur : (>"+str(seuilTaille)+") :",l  
    for kws in zip(largeKw[:l/3],largeKw[l/3:2*l/3],largeKw[2*l/3:]):
        print " ",kws[0]," ; ",kws[1]," ; ",kws[2] 
    print ""  
    
    
    seuilTaille = 4
    smallKw = [] 
    for keyword in keywords:
        if len(keyword)<=seuilTaille:
            smallKw.append(keyword) 
    l = len(smallKw)
    smallKw.sort()
    print "keywords de grande longueur : (>"+str(seuilTaille)+") :",l  
    for kws in zip(smallKw[:l/3],smallKw[l/3:2*l/3],smallKw[2*l/3:]):
        print " ",kws[0]," ; ",kws[1]," ; ",kws[2] 
    print ""  

    caract = ",.;:*?!&"
    specialKw = []
    for keyword in keywords:
        for c in caract:
            if c in keyword:
                specialKw.append(keyword)
    l = len(specialKw)
    print "keywords avec caractères spéciaux :",l
    for kws in zip(specialKw[:l/3],specialKw[l/3:2*l/3],specialKw[2*l/3:]):
        print " ",kws[0]," ; ",kws[1]," ; ",kws[2] 
    print "" 
     
    print "keywords de plus de cinq mots :"
    for keyword in keywords:
        if len(keyword.split(" ")) >=5 :
            print keyword
            
    print ""
    
    equivalences = IOFunctions.importSlugEquivalence()
    
    print "keywords égaux par equivalence"
    for kw1 in keywords:
        for kw2 in keywords:
            if kw1==kw2:
                continue
            slugs1 = keywords[kw1]
            slugs2 = keywords[kw2]
            flag = len(slugs1)==len(slugs2)
            i = 0
            while flag and i<len(slugs1):
                flag = slugs1[i]==slugs2[i] or slugs1[i] in equivalences and slugs2[i] in equivalences[slugs1[i]]
                i+=1
            if i == len(slugs1) and flag:
                print kw1," -- ",kw2
            
def computeSlugEquivalence():
    """
    function that analyses the keywords list and the simplifications rules
    written in the simplification.txt file to create a list of equivalence.
    The list is stored in the equivalence.txt file and contains all classes
    of equivalence for the slugs.
    """
    keywords = IOFunctions.importKeywords()
    dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
    print "== keywords imported"
    print ""
    print "total keywords :",len(keywords)
    print "total slugs : ",len(dicWordWeight)
    print ""
    print ""
    os.chdir(os.path.join(UtilsConstants.path,"motscles"))
    equivalences = []
    print "REGLES EN VIGUEUR"
    with codecs.open("simplification.txt","r","utf8") as fichier:
        flag = True
        for line in fichier:
            i=0
            if flag:
                flag = False
                i = 1
            print line[i:-2]
            equivalences.append(line[i:-2].split(";"))

    similaires = []
    for slug in dicWordWeight:
        for slug1 in dicWordWeight:
            if slug==slug1 or slug[0]!=slug1[0]:
                continue
            for eq in equivalences:
                l = [len(eqi[1:]) if eq[0][0] else len(eqi) for eqi in eq]
                flag = False
                radical = ""
                for z in zip(eq, l):
                    if slug[-z[1]:] == z[0][1:]:
                        flag = True
                        radical = slug[:-z[1]]
                        break
                if not flag or (len(radical)<5 and u'*age' in eq):
                    continue
                for z in zip(eq, l):
                    if radical == slug1[:len(slug1)-z[1]] and slug1[len(slug1)-z[1]:len(slug1)] == z[0][1:]:
                        for si in similaires:
                            if slug in si:
                                if slug1 not in si:
                                    si.append(slug1)
                                break
                            if slug1 in si:
                                if slug not in si:
                                    si.append(slug)
                                break
                        else:
                            similaires.append([slug,slug1])
                        break
    print ""
    print "Nombre de classes d'équivalence:"
    print len(similaires)
    print ""
    exemples = [[] for _ in similaires]
    stem = nltk.stem.snowball.FrenchStemmer()
    for keyword in keywords:
        mots = UtilsConstants.tokenizeAndStemmerize(keyword, keepComa=False, stem = stem, method="")
        stems = [stem.stem(mot) for mot in mots]
        j=0
        for si in similaires:
            for s in si:
                if s in stems:
                    if mots[stems.index(s)] not in exemples[j]:
                        exemples[j].append(mots[stems.index(s)])
                        break
            j+=1
    
    for si in zip(similaires,exemples):
        print si[0],si[1]  
        
    exceptions = [u'chal',u'moul',u'frais',u'detect',u'chass',u'regl',u'plac',u'bouch']
    
    with codecs.open("equivalences.txt","w","utf8") as fichier:
        for si in similaires:
            flag = False
            for exe in exceptions:
                if exe in si:
                    flag = True
                    break
            if flag:
                continue
            for s in si:
                fichier.write(s+";")
            fichier.write("\r\n")     

def deleteKeyword(keywords, varProgress = None, toPrint = False):
    '''
    function that deletes keywords from the database
    the keywords must be removed in every graph and list of keywords
    -- IN:
    keywords : list keyword to remove ([string])
    '''
    if toPrint:
        print "== Suppression des mots-clés",keywords
    compt = UtilsConstants.Compt(range(732),1, varProgress = varProgress)
    for codeNAF in IOFunctions.importListCodeNAF().keys()+[""]:
        if not (varProgress is None) or toPrint:
            compt.updateAndPrint()
        try:
            if codeNAF!="":
                os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"subset_NAF_"+str(codeNAF[-5:])))
        except:
            continue
        previousKeywords = IOFunctions.importKeywords(codeNAF)
        graph = None
        flag = False
        for keyword in keywords:
            if keyword in previousKeywords:
                del previousKeywords[keyword]
                if not flag:
                    flag = True
                    name = "subset_NAF_"+codeNAF if codeNAF!="" else "graphcomplet"
                    try:
                        if name == "graphcomplet":
                            os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
                    except:
                        continue
                    graph = IOFunctions.importGraph(name)
                    
                graph.deleteNode(keyword)
        if flag:
            if not(graph is None):
                IOFunctions.saveGraph(graph)
            if name == "graphcomplet":
                os.chdir(os.path.join(UtilsConstants.path,"motscles"))
            IOFunctions.saveKeywords(previousKeywords, ".", "keywords.txt")
        
def printMotsClesCourant():
    """
    function that print the 300 most used keywords in the graph.
    --WARNING
    the graphcomplet must have been computed before this function can be used.
    """
    print "Analyse des mots-clés les plus utilisés"
    try:
        os.chdir(UtilsConstants.pathCodeNAF+"/graphcomplet")
    except:
        print "   => Le graphe complet n'a pas été créé, abandon."
        return
    graph = IOFunctions.importGraph("graphcomplet")
    keywords = { name : sum(graph.getNodeByName(name).dicNAF.values()) for name in graph.dicIdNodes}
    degree = {name : len(graph.getNodeByName(name).neighbours) for name in graph.dicIdNodes}
    l = keywords.items()
    l.sort(key=itemgetter(1),reverse=True)
    print "  = 300 plus grands mots clés"
    for keyword in l[:300]:
        print "   ",keyword
    print ""
    l = degree.items()
    l.sort(key=itemgetter(1),reverse=True)
    print "  = 300 mots clés les plus connectés "
    for keyword in l[:300]:
        print "   ",keyword
    print ""
 
    
''' PREPROCESSING - CREATION OF GRAPH '''    
def extractGraphFromSubset(subsetname, 
                           path = UtilsConstants.pathCodeNAF, 
                           localKeywords = False, 
                           percent = 100,
                           keywords = None,
                           dicWordWeight = None,
                           equivalences = None, 
                           toPrint = False):
    '''
    function that computes a graph (ie. dicIdNodes, graphNodes, graphEdges)
    out of a subset file, containing a 'keywords.txt' and a 'subsey_entreprises.txt' file
    -- IN:
    subsetname : name of the subset (string)
    -- OUT:
    graph : graph object containing the following attributes:
        dicIdNodes : dic of id of the nodes
        graphNodes : dic of the nodes
        graphEdges : dic of the edges
    '''
    if toPrint:
        print "== Extracting graph from subset:",subsetname
    if toPrint:
        print "- importing subset",
    entreprises = IOFunctions.importSubset(subsetname, path)
    if toPrint:
        print "... done"
    if entreprises is None or len(entreprises) == 0:
        return
    graph = IOFunctions.GraphKeyword("graph_"+str(subsetname))
    if toPrint:
        print "- analyzing entreprises"
    french_stopwords = set(stopwords.words('french')),
    stem = nltk.stem.snowball.FrenchStemmer()
    # importing keywords and dicwords weight
    #     here, we also keep the global keywords for the keywords may change and become local.
    if keywords is None:
        keywords = IOFunctions.importKeywords()
        dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
        equivalences = IOFunctions.importSlugEquivalence()
    # computing dicslug 
    dicSlug = {dic : [] for dic in dicWordWeight}
    for keyword in keywords:
        dicSlug[keywords[keyword][0]].append(keyword)
    if localKeywords:
        globalKeywords = dict(keywords)
    else:
        globalKeywords = None
    
    currentNAF = ""
    if percent<100 and percent>0:
        entreprises = random.sample(entreprises, int(len(entreprises)*percent/100))
    # extracting information from the data
    compt = UtilsConstants.Compt(entreprises, 0.1 if subsetname=="graphcomplet" else 10)
    for entreprise in entreprises:
        if localKeywords and currentNAF != entreprise[0]:
            currentNAF = entreprise[0]
            if currentNAF!="nan" and "keywords.txt" in os.listdir(UtilsConstants.pathCodeNAF+"/subset_NAF_"+currentNAF):
                keywords = IOFunctions.importKeywords(currentNAF)
            else: 
                keywords = IOFunctions.importKeywords()
        stemmedDesc = UtilsConstants.tokenizeAndStemmerize(entreprise[1],True,french_stopwords,stem)
        buildFromDescription(stemmedDesc = stemmedDesc, 
                             codeNAF = entreprise[0], 
                             keywords = keywords, 
                             graph = graph, 
                             dicWordWeight = dicWordWeight, 
                             globalKeywords = globalKeywords, 
                             equivalences = equivalences, 
                             dicSlug = dicSlug,
                             description = entreprise[1])
        compt.updateAndPrint()
    graph.removeLonelyNodes()
    keywordsGraph = []
    for node in graph.graphNodes.values():
        keywordsGraph.append(node.name) 
    if toPrint:
        print "... done"
        print "- saving graphs",
    os.chdir(path+"/"+subsetname)
    IOFunctions.saveGraph(graph)
#     IOFunctions.saveGexfFile("graph.gexf", graph)
    IOFunctions.saveKeywords(keywordsGraph, path+"/"+subsetname, "keywords.txt")
    if toPrint:
        print "... done"
    return graph

def buildFromDescription(stemmedDesc,
                         codeNAF,
                         keywords, 
                         graph, 
                         dicWordWeight, 
                         globalKeywords = None, 
                         equivalences = None,
                         dicSlug = None, 
                         description = ""):
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
    listKeywords = extractFromDescription(None,keywords, dicWordWeight,preprocessedString=stemmedDesc, equivalences=equivalences, dicSlug = dicSlug)
    if len(listKeywords)==0 and globalKeywords is not None:
        print "pas ok"
        listKeywords = extractFromDescription(None,globalKeywords, dicWordWeight,preprocessedString=stemmedDesc, equivalences=equivalences, dicSlug = dicSlug)
    for k in listKeywords:
        graph.addNodeValues(k, codeNAF=codeNAF, valueNAF=listKeywords[k])
    l = listKeywords.items()
    l.sort(key=itemgetter(1),reverse=True)
    l = l[:5]
    for k in l:
        for k1 in l:
            if k[0]!=k1[0]:
                edgeValue = k[1]*k1[1]
                graph.addEdgeValues(graph.dicIdNodes[k[0]], graph.dicIdNodes[k1[0]], edgeValue)  
     
def pipelineGraph(n, percent=100, steps = [True, True, True]):
    '''
    function that builds the complete graph
    the pipeline is composed of three substeps:
    - substep 0 : sample each code NAF with n entreprises and compute the corresponding subsets
    - substep 1 : compute local graph and keywords for each code NAF, using the previously computed subsets
    - substep 2 : using only local keywords, compute the complete graph over the selected percentage of entreprises
    -- IN:
        n : size of the sample for the code NAF subset (int)
        percent : percent of entreprises used for the computation of the graph (float) default=100
        steps : array of boolean of size 3, defining which steps to perform ([boolean, boolean, boolean]) default=[True,True,True]
    -- OUT:
        the function returns nothing
    '''
    # COMPUTING GRAPH
    print "COMPUTING COMPLETE GRAPH PIPELINE"
    print ""

    path = UtilsConstants.pathCodeNAF
    codeNAFs = IOFunctions.importListCodeNAF()
        
    # Step 0 : creating subset for all NAF
    if(steps[0]):
        startTime = time.time()
        print "Step 0 : creating subset for all NAF"
        compt = UtilsConstants.Compt(codeNAFs, 1, True)
        for codeNAF in codeNAFs:
            compt.updateAndPrint()
            IOFunctions.extractAndSaveSubset(codeNAF, n, path = path, toPrint=False)
        UtilsConstants.printTime(startTime)
        print ""
    
    if(steps[1] or steps[2]):
        keywords = IOFunctions.importKeywords()
        dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
        equivalences = IOFunctions.importSlugEquivalence()
        
    # Step 1 : computing graph and keywords for all code NAF, using keywords from Step 0-1
    if(steps[1]):
        startTime = time.time()
        print "Step 1 : computing graph and keywords for all code NAF, using all keywords"
        i = 0
        for codeNAF in codeNAFs:
            print codeNAF,"- "+str(i)+"/732"
            i+=1
            extractGraphFromSubset(subsetname = "subset_NAF_"+codeNAF, 
                                   path = path,
                                   localKeywords=False,
                                   keywords = keywords,
                                   dicWordWeight = dicWordWeight,
                                   equivalences = equivalences,
                                   toPrint = False)
        UtilsConstants.printTime(startTime)
        print ""
        
    # Step 2 : compute complete graph using local keywords
    if(steps[2]):
        startTime = time.time()
        print "Step 2 : compute complete graph using local keywords"
        # checking if the subset exists
        if not("graphcomplet" in os.listdir(UtilsConstants.pathCodeNAF)):
            print "- creating subset for the graphcomplet"
            IOFunctions.extractAndSaveSubset()
        extractGraphFromSubset(subsetname = "graphcomplet", 
                               path = path, 
                               localKeywords = False, 
                               keywords = keywords,
                               dicWordWeight = dicWordWeight,
                               equivalences = equivalences,
                               percent = percent, 
                               toPrint = True)
        UtilsConstants.printTime(startTime)
        print ""  
        
    # Step 3 : compute all default keywords for each NAF using graphcomplet
    if(steps[2]):
        computeKeywordsForNAF() 
 
def computeKeywordsForNAF():
    '''
    function that computes the list of the 20 most used keywords
    by code NAF to add them in the algorithm if no keyword is selected
    in step 1 2 and 3.
    the "defaultKeywords.txt" files are stored in the same subset folders than the NAF samples.
    --IN
    the function takes no argument
    --OUT
    the function returns nothing
    '''
    os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
    graph = IOFunctions.importGraph("graphcomplet",edges = False)
    for codeNAF in IOFunctions.importListCodeNAF():
        keywords = {node.name:node.dicNAF[codeNAF] for node in graph.graphNodes.values() if codeNAF in node.dicNAF}
        l = keywords.items()
        l.sort(key=itemgetter(1),reverse=True)
        if len(l)>0:
            s = max(keywords.values())
        keywords = {li[0] : li[1]/s for li in l[:20]}
        os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"subset_NAF_"+codeNAF))
        UtilsConstants.saveDict(keywords, filename="defaultKeywords.txt", sep="_")
         

''' STEP 01 - EXTRACTION FROM DESC '''     
def extractFromDescription(string, 
                           keywords = None, 
                           dicWordWeight = None,
                           equivalences = None,
                           booleanMatchParfait = True,
                           french_stopwords = set(stopwords.words('french')),
                           stem = nltk.stem.snowball.FrenchStemmer(),
                           parametersStep01 = UtilsConstants.parametersStep01,
                           normalisationFunction = UtilsConstants.normalisationFunction,
                           dicSlug = None,
                           toPrint=False,
                           preprocessedString = None):
    '''
    function that returns a list of keywords out of a description
    the function takes a dic of parameters as an input.
    -- IN
        string : the string from which we extract the keywords (str)
        keywords : *optional - the list of keywords to extract (dic{str:[tokens]}) default = None
            # obtained by 'keywords = IOFunctions.importKeywords()'
        dicWordWeight : *optional - the dictionary containing slug weights (dic{str:int}) default = None
            # obtained by 'dicWordWeight = UtilsConstants.importDicWordWeight()'
        equivalences : *optional - the dictionary containing classes of equivalence (dic{str:[str]})
            # obtained by 'equivalences = IOFunctions.importSlugEquivalence()'
        booleanMatchParfait: boolean that settles if we discard keywords that aren't match perfectly (boolean) default = True
            # reminder - a match is perfect according to the function isMatch()
        french_stopwords : *optional - the set of stopwords for the french language, can be precomputed and passed as an argument or not (set)
        stem : *optional - stemmerize provided by the nltk library, can be precomputed and passed as an argument or not
        parametersStep01 : *optional - dictionary of parameters used for the matching analysis
            # obtained by 'UtilsConstants.parametersStep01
            -> it is also possible to give as input an array of such dictionary (useful for the genetic algorithm)
        toPrint : *optional - boolean that settles if the function must print the results (boolean) default=False
        preprocessingString : *optional - array of tokens containing the preprocessed String ([unicode]) default=None
    -- OUT
        dic : dic of keywords which values are the importance of the keyword (dic{str:float})
    '''
    # initializing keywords, dicWordWeight and equivalences
    if keywords is None:
        keywords = IOFunctions.importKeywords()
    if dicWordWeight is None:
        dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
    if equivalences is None:
        equivalences = IOFunctions.importSlugEquivalence()
    # initializing description
    if preprocessedString is None:
        preprocessedString = UtilsConstants.tokenizeAndStemmerize(string,keepComa=True, french_stopwords=french_stopwords, stem=stem)
    # creating set of keywords to check
    keywords, tableMatch = preprocessExtraction(preprocessedString = preprocessedString, 
                                                keywords = keywords, 
                                                dicWordWeight = dicWordWeight, 
                                                equivalences = equivalences, 
                                                dicSlug = dicSlug,
                                                toPrint = toPrint)
    dicResults = {}
    posSpecial = { key : set([i for i, x in enumerate(preprocessedString) if x == key]) for key in ["non",".",","]}
    for keyword in keywords:
        if toPrint:
            print "trying to match",keyword
            print "slugs:",keywords[keyword]
        if keyword=='.' or keyword==",":
            continue
        v, b = getProbKeywordInDescription(keyword = keyword, 
                                              slugs = keywords[keyword],
                                              stemmedDesc = preprocessedString, 
                                              parametersStep01 = parametersStep01,
                                              normalisationFunction = normalisationFunction, 
                                              equivalences = equivalences, 
                                              dicWordWeight = dicWordWeight,
                                              tableMatch = tableMatch,
                                              posSpecial = posSpecial,
                                              toPrint=toPrint)
        if b:
            dicResults[keyword] = v
    # handling the output
    if isinstance(parametersStep01, dict):
        # only one parameters set to test : usual case
        return dicResults
    else:
        # list of parameters to tests : genetic algorithm or multiple parameters set
        finalDic = []
        for i in range(len(parametersStep01)):
            finalDic.append({kw : dicResults[kw][i] for kw in dicResults})
        return finalDic
    
def preprocessExtraction(preprocessedString,
                         keywords = None, 
                         dicWordWeight = None,
                         equivalences = None,
                         dicSlug = None,
                         toPrint=False):
    '''
    function that preprocess the string and the global list of keywords to extract only those which might be found in
    the description.
    -- IN
        preprocessingString : array of tokens containing the preprocessed String ([unicode]) default=None
        keywords : *optional - the list of keywords to extract (dic{str:[tokens]}) default = None
            # obtained by 'keywords = IOFunctions.importKeywords()'
        dicWordWeight : *optional - the dictionary containing slug weights (dic{str:int}) default = None
            # obtained by 'dicWordWeight = UtilsConstants.importDicWordWeight()'
        equivalences : *optional - the dictionary containing classes of equivalence (dic{str:[str]})
            # obtained by 'equivalences = IOFunctions.importSlugEquivalence()'
        french_stopwords : *optional - the set of stopwords for the french language, can be precomputed and passed as an argument or not (set)
        stem : *optional - stemmerize provided by the nltk library, can be precomputed and passed as an argument or not
        toPrint : *optional - boolean that settles if the function must print the results (boolean) default=False
    -- OUT
        KeywordSet : the dictionary of keywords to be used in the rest of the pipeline (dic{keyword(str):[slugs(str)]}) (for this description)
    '''
    # initializing keywords, dicWordWeight and equivalences
    if keywords is None:
        keywords = IOFunctions.importKeywords()
    if dicWordWeight is None:
        dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
    if equivalences is None:
        equivalences = IOFunctions.importSlugEquivalence()
    # computing the dictionary linking slugs and keywords
    if dicSlug is None:
        dicSlug = {dic : [] for dic in dicWordWeight}
        for keyword in keywords:
            dicSlug[keywords[keyword][0]].append(keyword)
    # creating the set of keywords to check
    keywordSet = {}
    tableMatch = [{} for _ in preprocessedString]
    i=0
    for descslug in preprocessedString:
        # updating comas number
        if descslug=="," or descslug==".":
            i += 1
            continue
        for kwslug in dicSlug:
            value = isMatch(descslug, kwslug, equivalences, toPrint)
            if value>0:
                # we then check all keywords starting with this slug
                for keyword in dicSlug[kwslug]:   
                    keywordSet[keyword] = keywords[keyword] 
                tableMatch[i][kwslug] = value
        i += 1
    return keywordSet, tableMatch  
    
def getProbKeywordInDescription(keyword, 
                                string = "",
                                stemmedDesc = None, 
                                slugs = None, 
                                parametersStep01 = UtilsConstants.parametersStep01,
                                equivalences = None, 
                                dicWordWeight = None,  
                                tableMatch = None,
                                posSpecial = None,
                                normalisationFunction=UtilsConstants.normalisationFunction, 
                                toPrint = False):
    '''
    function that determines the importance of the keyword in the string
    according to the following rules and parametersStep01:
    leave parametersStep01 and pop as default to have default parametersStep01
    -- IN
        keyword : the keyword to analyze (str)
        slugs : the slugs in the keyword to analyze ([slug(str)])
            # obtained as the value of the key 'keyword' in the dictionary 'keywords'
        stemmedDesc : the tokennized description ([stem(str)])
        parametersStep01 : the dictionary containing the parameters of the step 01 (dic{parameter(str) : value(int)})
            # it is also possible to give an array of dictionaries (useful for genetic algorithm)
        normalisationFunction : the associated normalisation function for the parameters
        equivalences : the dictionary containing the equivalences
        dicWordWeight : the dictionary containing the frequencies for the slugs (dic{slug(str):freq(int)})
        toPrint : boolean that settles if the results must be print *optional (boolean) default = False
    '''
    # initializing keywords, dicWordWeight and equivalences
    if dicWordWeight is None:
        keywords = IOFunctions.importKeywords()
        dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
    if slugs is None:
        slugs = UtilsConstants.tokenizeAndStemmerize(keyword)
    if equivalences is None:
        equivalences = IOFunctions.importSlugEquivalence()
    # initializing description
    if stemmedDesc is None:
        stemmedDesc = UtilsConstants.tokenizeAndStemmerize(string,keepComa=True)
        
    pos = [[] for _ in slugs]
    nSlug=0
    nbTotalMot = len(stemmedDesc)
    b = True
    if isinstance(parametersStep01,dict):
        parametersStep01 = [parametersStep01]
        normalisationFunction = [normalisationFunction]
    v=[0.0]*len(parametersStep01)
    # looking for special stem in description
    if posSpecial is None:
        posSpecial = {"non":set(), ".":set(), ",":set()}
        for key in posSpecial:
            for i in range(len(stemmedDesc)):
            # checking the 'non','.' and ',' token in description
                if stemmedDesc[i]==key:
                    posSpecial[key].add(i)
    for keywordslug in slugs:
        if toPrint:
            print "  ", keywordslug
        # feature 0 : valeur initiale
        coeff = [extractFeature0_InitialValue(p, keywordslug, dicWordWeight, toPrint) for p in parametersStep01]
        nbMot=0
        nbComa = 0
        vt = [0]*len(parametersStep01)
        b1 = False
        for descslug in stemmedDesc:
            if descslug==",":
                # updating comas number
                nbComa += 1
            if descslug==".":
                nbComa = 0
            # performing the test to match
            if tableMatch is None:
                im = isMatch(keywordslug, descslug, equivalences, toPrint)
            else:
                im = tableMatch[nbMot][keywordslug] if keywordslug in tableMatch[nbMot] else 0.0
            if im<UtilsConstants.parametersMatchStep01["seuilMatch"]:
                im = 0
            if im>0:  
                coeff2 = [c * im for c in coeff]
                # Match !
                rm = [resolveMatch(parametersStep01 = p[0], 
                                   nSlug = nSlug, 
                                   coefSlug = p[1], 
                                   nbMot = nbMot, 
                                   nbComa = nbComa, 
                                   nbTotalMot = nbTotalMot,  
                                   pos = pos,
                                   posSpecial = {"non":[], ".":[], ",":[]},
                                   normalisationFunction = UtilsConstants.normalisationFunction,
                                   toPrint = toPrint)
                      for p in zip(parametersStep01,coeff2, normalisationFunction)]
                b1 = b1 or rm[0][1]
                vt = [max(vt1[0],vt1[1][0]) for vt1 in zip(vt,rm)]
                pos[nSlug].append(nbMot)
            nbMot+=1
        if len(pos[nSlug])==0:
            # No Match !
            v = [0.0] * len(parametersStep01)
            b = False
            break
        b = b and b1
        v = map(operator.add, v, vt)
        nSlug+=1
        if toPrint:
            print "score du slug :",vt
            print ""
    v = map(operator.div,v,[len(slugs)]*len(v))
    b = b
    if len(v) ==1:
        v = v[0]
    if toPrint:
        print ""
        print "SCORE FINAL =",v
        print ""
    return v, b

def isMatch(slug1, slug2,  equivalences=None, toPrint = False):
    '''
    Matching function for slugs from both keyword and description
    returns the value of the match
    -- IN:
        slug1 : first slug/stem to match
        slug2 : second slug/stem to match
            # the function is totally symmetric
        equivalences : the dictionary for equivalence for stems (dic{stem(str):[stem(str]})
        toPrint : boolean that settles if the results must be printed (boolean) default = False
    -- OUT:
        float : the result of the match:
            1.0 : perfect match
            0.9 : match via equivalence
            0.8 : match via modification of 1 letter in one stem (only if the stem's lenght is above 9)
            0.0 : else
    '''
    # importing equivalences
    if equivalences is None:
        print "oups !"
        equivalences = IOFunctions.importSlugEquivalence()
        
    if (str(slug1) == str(slug2)):
        return 1.0
    try:
        if slug1 in equivalences and slug2 in equivalences[slug1]:
            return 0.9
    except:
        pass
#     if abs(len(slug1)-len(slug2))==1:
#         if len(slug1)>6:
#             for i in range(len(slug1)):
#                 if slug1[:i]+slug1[i+1:]==slug2:
#                     return 0.8
#         if len(slug2)>6:
#             for i in range(len(slug2)):
#                 if slug2[:i]+slug2[i+1:]==slug1:
#                     return 0.8
    return 0
   
def resolveMatch(parametersStep01, 
                 nSlug, 
                 coefSlug, 
                 nbMot, 
                 nbComa, 
                 nbTotalMot,  
                 pos,
                 posSpecial = {"non":[], ".":[], ",":[]},
                 normalisationFunction = UtilsConstants.normalisationFunction,
                 toPrint = False):
    '''
    function that resolves the match knowing all the parameters
    pivot function between all the 'extractFeatures' functions
    -- IN
        parametersStep01 : parameters for the step 01 contained in UtilsConstant (dic)
        nSlug : number of the slug inside the keyword (int)
        nbComa : number of comas before the slug is match
        nbTotalMot : total number of words in the description
        nbTotalComa : total number of coma in the description
        pos : position of the previous matches
        normalisationFunction : the normalisation function for the match to return a result between 0 and 1
        toPrint : boolean that settles if the results must be printed (boolean) default = False
    '''
    if toPrint:
        print "   match !"
    # feature 1 : about commas
    coefComa = extractFeature1_AboutComas(parametersStep01, nbComa, nbTotalComa = len(posSpecial[","]), toPrint = toPrint)
    # feature 2 : place in the description
    coefPlace = extractFeature2_AboutPlace(parametersStep01, nbMot, nbTotalMot, toPrint)
    # feature 3 : slugs next to other slugs
    if nSlug==0:
        coefNextTo = parametersStep01['coefProxi']/2.0
    else:
        coefNextTo = extractFeature3_AboutSlugProximity(parametersStep01, nSlug, nbMot, pos, posSpecial, toPrint)
    # computing final result
    score = (coefSlug+coefNextTo)*coefPlace*coefComa
    score = normalisationFunction(score)
    if toPrint:
        print "     => score =",score
    return score, coefNextTo>0

def extractFeature0_InitialValue(parametersStep01, keywordslug, dicWordWeight, toPrint):
    '''
    function that returns the initial value of a keyword slug
    according to parametersStep01 and a dicWordWeight.
    '''
    try:
        coeff = parametersStep01['freqSlugAlpha']*int(dicWordWeight[keywordslug]) \
                + parametersStep01['freqSlugGamma']/int(dicWordWeight[keywordslug])           
    except:
        coeff = 0.5
    if toPrint:
        print "   valeur initiale:",coeff
    return coeff

def extractFeature1_AboutComas(parametersStep01, nbComa, nbTotalComa, toPrint):
    '''
    function that returns the coma coefficient in keyword extraction
    '''
    coefComa = parametersStep01['nbCommaAlpha']*nbComa \
                + parametersStep01['nbCommaGamma']/(1.0+nbComa) 
    if toPrint:
        print "      coefComa :",coefComa
    return coefComa

def extractFeature2_AboutPlace(parametersStep01, nbMot, nbTotalMot, toPrint):
    '''
    function that returns the place coefficient in keyword extraction
    '''
    coefPlace = 0.0
    if nbMot<6:
        coefPlace = parametersStep01['placePremierTier']
    else:
        fracPlace = 1.0*nbMot/nbTotalMot
        if fracPlace<0.33:
            coefPlace += parametersStep01['placePremierTier']
        elif fracPlace<0.66:
            coefPlace += parametersStep01['placeSecondTier']
        else:
            coefPlace += parametersStep01['placeDernierTier']
        
    if "placeMot"+str(nbMot) in parametersStep01:
        coefPlace *= parametersStep01["placeMot"+str(nbMot)] 
    elif "placeMot"+str(nbMot-nbTotalMot) in parametersStep01:                    
        coefPlace *= parametersStep01["placeMot"+str(nbMot-nbTotalMot)]   
    if toPrint:
        print "      coefPlace :",coefPlace
    return coefPlace
                    
def extractFeature3_AboutSlugProximity(parametersStep01, nSlug, nbMot, pos, posSpecial, toPrint):
    '''
    function that returns the place coefficient in keyword extraction
    '''
    coefNextTo = 0
    i = nbMot
    j = int(UtilsConstants.parametersMatchStep01["seuilOrdre"])
    value = parametersStep01['coefProxi']
    while j>=0 and i>=0:
        # check if "non" is not just before our match, if so we cancel the search
        if i==nbMot-1 and i in posSpecial["non"]:
            coefNextTo = 0
            break
        # check if there is no "." between our match and the previous match, if so we cancel the search
            break
        if i in posSpecial["."]:
            coefNextTo = 0
        # check if there is "," between our match and the previous one, if so we reduce the value
        if i in posSpecial[","]:
            value*=0.9
            j+=1
        # check for slug proximity
        if i in pos[nSlug-1]:
            coefNextTo = value
            break
        i-=1
        j-=1
        
        
    if toPrint:
        print "      coefNextTo :",coefNextTo  
    return coefNextTo               
   
         
''' STEP 03 - EXTRACTION FROM GRAPH '''    
def extractPotentielNodes(graph, dicKeywords, n = 0):
    '''
    function that returns the surrounding nodes of the selected keywords in the graph.
    We will then perform the prediction algorithm on these potentiel keywords.
    -- IN:
        graph : the complete graph (graph)
        dicKeywords : dictionary of the previously seletec keywords (dic{keyword(string):value(float)})
        n : maximal number of keywords in the final output of the function (int)
    -- OUT
        potentielNodes : array of potentiel keywords, classed by values. (array[keywords(string)])
    '''
    # on parcourt toutes les arrêtes:
    potentielNodes = {}
    maxEdge = 0
    for i in graph.graphNodes:
        graph.graphNodes[i].state = 0
    for name in dicKeywords:
        if not(graph.getNodeByName(name) is None):
            maxEdge = max(maxEdge, max(graph.getNodeByName(name).neighbours.values()))
    for name in dicKeywords:
        node = graph.getNodeByName(name)
        if node is None:
            continue
        node.state = 1
        for neighbour in node.neighbours:
            if not(neighbour.name in dicKeywords):
                if not(neighbour.id in potentielNodes):
                    potentielNodes[neighbour.id] = [0.0,0]
                potentielNodes[neighbour.id][0] += dicKeywords[name]*node.neighbours[neighbour]/maxEdge
                potentielNodes[neighbour.id][1] += 1
    for key in potentielNodes:
        potentielNodes[key] = potentielNodes[key][0]
    l = potentielNodes.items()
    l.sort(key=itemgetter(1),reverse=True)
    potentielNodes = [li[0] for li in l[: (min(len(l),n) if n>0 else len(l))]]
    return potentielNodes

def extractFromGraph(graph, dicKeywords, codeNAF = "", classifier=GraphLearning.Step3Classifier(), n=0):
    '''
    function that extracts extra keywords from the graph according
    to the relationships with the previously selected keywords.
    the choice is made by a clssifier trained in the graph learning module.
    -- IN
        graph : the complete graph to perform the algorithm on (graph)
        dicKeywords : the dictionary containing the previously selected keywords and their values (dic{keyword(string):value(float)})
        codeNAF : the codeNAF of the description, used to compute the propCodeNAF features in the nodes. (string) default=""
            -> if not defined, the correspondng feature will be 0 in all nodes
        classifier : the trained classifier that will select nodes (classifier)
        n : maximum number of extracted keywords (int) default=0
            -> let 0 to set no limit to the number of extracted keywords
    -- OUT
        result : dictionary of keywords and their value between 0 and 1 (dic{keyword(string):value(float)})
    '''
    potentielNodes = extractPotentielNodes(graph, dicKeywords, 50)
    X = []
    result = {}
    if len(potentielNodes)>0:
        columns = []
        for key in potentielNodes:
            graph.computeNodeFeatures(graph.graphNodes[key].name, dicKeywords, codeNAF)
            if len(columns)==0:
                columns = graph.graphNodes[potentielNodes[0]].features.keys()
                columns.sort()           
            X.append([graph.graphNodes[key].features[keyFeatures] 
                      for keyFeatures in columns])
        Y = classifier.predict(X)
        for a in zip(potentielNodes, Y):
            if a[1]>0.5:
                result[graph.graphNodes[a[0]].name] = (a[1]-0.5)*2.0
    if n>0:
        l = result.items()
        l.sort(key=itemgetter(1),reverse=True)
        result = {li[0]:li[1]*UtilsConstants.parametersStep04["coefficientStep3"] for li in l[:min(len(l),n)]}
    return result
      
                  
''' STEP 04 - MERGING KEYWORDS '''  
def mergingKeywords(keywordsFromDesc, keywordsFromGraph, graph, codeNAF, keywordsFromStep2 = {}): 
    keywords = dict(keywordsFromDesc.items())
    keywords.update(keywordsFromGraph)
    if len(keywords)==0:
        keywords = IOFunctions.importDefaultKeywords(codeNAF)
    # Initializing, computing note Step 01/03
    keywords = { k[0] : [k[1],0.0,0.0] for k in keywords.items()}
    # Computing note place dans graph
    maxNode = 0
    for name in keywords:
        if name in graph.dicIdNodes:
            keywords[name][1] = sum([1 
                                     for neighbour in graph.getNodeByName(name).neighbours.items() 
                                     if neighbour[0].name in keywords ])
        maxNode = max(keywords[name][1],maxNode)
    if maxNode>0:
        for name in keywords:
            keywords[name][1] /= maxNode
    # Computing relation sémantique
    stems = {}
    french_stopwords = set(stopwords.words('french'))
    stem = nltk.stem.snowball.FrenchStemmer()
    for name in keywords:
        stems[name] = UtilsConstants.tokenizeAndStemmerize(name, False, french_stopwords, stem)
    maxNode = 0
    minNode = 0
    for name in keywords:
        for name2 in keywords:
            if name==name2:
                continue
            a = set(stems[name])
            b = set(stems[name2]) 
            if len(a & b) == 0:
                keywords[name][2]+=UtilsConstants.parametersStep04["coeffSemantIfDifferent"]
            else:
                if len(a-b)==0:
                    keywords[name][2]+=UtilsConstants.parametersStep04["coeffSemantIfInclus"]
                elif len(b-a)==0:
                    keywords[name][2]+=UtilsConstants.parametersStep04["coeffSemantIfContient"]
                else:
                    keywords[name][2]+=UtilsConstants.parametersStep04["coeffSemantIfIntersection"]*(1.0 if name>=name2 else -1.0)
        maxNode = max(keywords[name][2],maxNode)
        minNode = min(keywords[name][2],minNode)
    for name in keywords:
        keywords[name][2] = 1.0*(keywords[name][2]-minNode)/(maxNode-minNode) if maxNode!=minNode else 0.5
    # merging
    weights = [UtilsConstants.parametersStep04["weightScoreStep13"],UtilsConstants.parametersStep04["weightPlaceGraph"],UtilsConstants.parametersStep04["weightSemantique"]]
    for name in keywords:
        keywords[name] = sum([a[0]*a[1] for a in zip(keywords[name],weights)])/sum(weights)
    l = keywords.items()
    l.sort(key=itemgetter(1),reverse=True)
    kw = [li[0] for li in l]
    # suppression finales des doublons
    representedStems = []
    toRemove = []
    for name in kw:
        if stems[name] in UtilsConstants.blacklistStep04.values():
            toRemove.append(name)
            continue            
        flag = True
        for st in stems[name]:
            if not(st in representedStems):
                representedStems.append(st)
                flag = False
        if flag or keywords[name]<0.4:
            toRemove.append(name)
            continue
        for name2 in kw:
            if name!=name2 and len(set(stems[name])-set(stems[name2]))==0:
                toRemove.append(name)
    for tr in toRemove:
        if tr in kw:
            kw.remove(tr)
    # on détermine le nombre de keywords à sortir
    n = int(UtilsConstants.parametersStep04["nbMaxMotsCles"])
    keywords = {k : keywords[k] for k in kw[:min(n,len(keywords))]}
    return keywords
    
''' GLOBAL PIPELINE '''
def compareKeywords(keywordsList1, keywordsList2):  
    '''
    function that takes two list of keywords as an imput and return a note 
    according to the lists similarities. 
    The main use of the function is to evaluate the current pipeline with a training set.
    -- IN 
        keywordsList1 : list of desired keywords ([keywords(string)])
        keywordsList2 : list of obtained keywords ([keywords(string)])
    -- OUT
        note : float between 0 and 1 that evaluates the similarities between both the lists.
    '''   
    if keywordsList1==[] or keywordsList2==[]:
        return 0.0
    set1 = set(keywordsList1)
    set2 = set(keywordsList2)
    note = 1.0*len(set1 & set2)/min(len(set1),len(set2)) 
    note -= 0.5*len(set1 - set2)/len(set1)
    note -= 0.5*len(set2 - set1)/len(set2)
    return (1.0+note)/2.0   

 
  
        