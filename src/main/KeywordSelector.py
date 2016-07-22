# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''
''' Extraction and Suggestion functions'''
''' Main pipeline functions '''

import codecs
from operator import itemgetter
import os
import time
import random

from nltk.corpus import stopwords
import nltk.stem.snowball

import GraphLearning, IOFunctions, UtilsConstants
import numpy as np


def pipeline(descriptions, nbMot = 20, printGraph = False):
    '''
    Pipeline function taking as input a dataframe with rows 'codeNAF' and 'description'
    and giving as output a list of keywords for each description in the dataframe
    -- IN:
    descriptions : list of array [description(string),codeNaf(string)]
    nbMot : number of returned keywords, (int) default : 5
    -- OUT:
    keywords : list of lists of keywords [[string],[string], ...]
    '''
    # checking validity of inputs
    try:
        for a in descriptions:
            a[0]
            a[1]
    except:
        print "error : invalid input, format error."
    # importing graph and keywords
    os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
    graph = IOFunctions.importGraph("graphcomplet")
    keywordSet, dicWordWeight = IOFunctions.importKeywords()
    keywords = []
    i = 0
    os.chdir(UtilsConstants.pathCodeNAF+"/graphtest")
    for line in descriptions:
        keywordlist, origins, _ = selectKeyword(line[1],line[0], graph, keywordSet, dicWordWeight, localKeywords=False, n=nbMot, toPrint=True)
        keywords.append(keywordlist)
        if printGraph:
            os.chdir(UtilsConstants.pathCodeNAF+"/graphtest")
            IOFunctions.saveGexfFile("graph_test_"+str(i)+".gexf", graph, keywords = keywordlist, origins = origins)
        i+=1
    return keywords

def pipelineTest():
    print "DEBUT TEST PIPELINE"
    os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
    graph = IOFunctions.importGraph("graphcomplet")
    print "   graph importé"
    keywordSet, _ = IOFunctions.importKeywords()
    print "   mots-clés importés"
    entreprises = IOFunctions.extractSubset(n=10)
    print "   entreprises importées"
    print ""
    i=0
    for i in range(len(entreprises)):
        line = entreprises[i]
        selectKeyword(line[1], line[0], graph, keywordSet, True, 20, True)
        while True:
            try:
                ipt = input("test de mot clé ?")
            except:
                break
            extractFromDescription(line[1], {ipt:UtilsConstants.tokenizeAndStemmerize(ipt)}, {}, toPrint=True)
        try:
            ipt = input("nouvelle description ?")
        except:
            break
        
def selectKeyword(description, codeNAF, graph = None, keywordSet = None, dicWordWeight = None, localKeywords = False, n=50, steps = 3, toPrint = False):
    '''
    function that takes a description and a codeNAF and returns a list of suggested keywords
    the recquired inputs are also the graph (for step 3) and the keywordSet (for step 1)
    an additional input is the number of returned keywords
    -- IN
    description : string describing the description (string)
    codeNAF : string representing the code NAF (string)
    graph : graph of keywords (GraphProcessing.GraphKeyword)
    keywordSet : dictionary of keywords with stems for values {keyword (str): [stems (str)]}
    -- OUT
    keywordsList : array of keywords, in order of importance ([string])
    origins : array of array of integers ([ [int, int, ...], ...])
    '''
    ## STEP 0 = Initializing
    if toPrint:
        print description
    origin = {}
    if localKeywords:
        keywordSet, dicWordWeight = IOFunctions.importKeywords(codeNAF)
    elif keywordSet is None or dicWordWeight is None:
        keywordSet, dicWordWeight = IOFunctions.importKeywords()
    if graph is None:
        # importing graph and keywords
        os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
        graph = IOFunctions.importGraph("graphcomplet")
    ## STEP 1 = Extracting only from description
    if steps>=1:
        keywordFromDesc = extractFromDescription(description, keywordSet, dicWordWeight,toPrint=False)
        if toPrint:
            print "from desc:"
            UtilsConstants.printSortedDic(keywordFromDesc)
            print ""
        for key in keywordFromDesc:
            origin[key]=[1]
    else:
        keywordFromDesc = {}
            
    ## STEP 3 = Extracting from Graph
    if steps >=3:
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
    keywords = mergingKeywords(keywordFromDesc, keywordFromGraph, graph)
    if toPrint:
        print "merging:"
        UtilsConstants.printSortedDic(keywords)
        print ""
        print ""
    origins = [origin[key] for key in keywords]
    values = [keywordFromDesc[key] if 1 in origin[key] else keywordFromGraph[key] for key in keywords]
    return keywords, origins, values

    
''' STEP 00 - KEYWORDS CLEANING '''

def statsAboutKeywords():
    keywords, dicWordWeight = IOFunctions.importKeywords()
    print "== keywords imported"
    print ""
    print "total keywords :",len(keywords)
    print "total slugs : ",len(dicWordWeight)
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
    
    seuilTaille = 29
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
    
    print "keywords egaux par equivalence"
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
    keywords, dicWordWeight = IOFunctions.importKeywords()
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

def deleteKeyword(keywords):
    '''
    function that deletes keywords from the database
    the keywords must be removed in every graph and list of keywords
    -- IN:
    keywords : dic or list of keywords to remove (must be iterable)
    '''
    print "== Suppression des mots-clés",keywords
    compt = UtilsConstants.Compt(range(732),1)
    for codeNAF in IOFunctions.importListCodeNAF().keys()+[""]:
        compt.updateAndPrint()
        previousKeywords, _ = IOFunctions.importKeywords(codeNAF)
        name = "subset_NAF_"+codeNAF if codeNAF!="" else "graphcomplet"
        if name == "graphcomplet":
            os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
        graph = IOFunctions.importGraph(name)
        for keyword in keywords:
            if keyword in previousKeywords:
                del previousKeywords[keyword]
            if keyword in graph.dicIdNodes:
                identity = graph.dicIdNodes[keyword]
                del graph.dicIdNodes[keyword]
                del graph.graphNodes[identity]
                toRemoveEdge = []
                for edge in graph.graphEdges:
                    if identity in edge:
                        toRemoveEdge.append(edge)
                for edge in toRemoveEdge:
                    del graph.graphEdges[edge]
        IOFunctions.saveGraph(graph)
        if name == "graphcomplet":
            os.chdir(os.path.join(UtilsConstants.path,"motscles"))
        IOFunctions.saveKeywords(previousKeywords, ".", "keywords.txt")
        
    

''' STEP 01 - EXTRACTION FROM DESC '''     
def extractFromDescription(string, 
                              keywords, 
                              dicWordWeight,
                              equivalences = {},
                              french_stopwords = set(stopwords.words('french')),
                              stem = nltk.stem.snowball.FrenchStemmer(),
                              parametersStep01 = {},
                              parameterList = None,
                              toPrint=False,
                              preprocessedString = None,
                              n=20):
    '''
    function that returns a list of keywords out of a description
    -- IN
    string : the string from which we extract the keywords (str)
    keywords : the list of keywords to extract (dic{str:[tokens]})
    toPrint : boolean that settles if the function must print the results (boolean) default=False
    -- OUT
    dic : dic of keywords which values are the importance of the keyword (dic{str:float})
    '''
    # initializing parametersStep01
    if parameterList is None:
        if parametersStep01 == {}:
            parametersStep01 = UtilsConstants.parametersStep01
        parameterList = [parametersStep01]
    dic = [{} for _ in parameterList]
    # initializing description
    if preprocessedString is None:
        stemmedDesc = UtilsConstants.tokenizeAndStemmerize(string,keepComa=True, french_stopwords=french_stopwords, stem=stem)
    else :
        stemmedDesc = preprocessedString
    # checking all keywords from the set
    for keyword in keywords:
        if toPrint:
            print "trying to match",keyword
            print "slugs:",keywords[keyword]
        if keyword=='.' or keyword==",":
            continue
        nParam = 0
        for parameter in parameterList:
            v, b = getProbKeywordInDescription(keyword = keyword, 
                                            slugs = keywords[keyword],
                                            stemmedDesc = stemmedDesc, 
                                            parametersStep01 = parameter, 
                                            equivalences = equivalences, 
                                            dicWordWeight = dicWordWeight,
                                            toPrint=toPrint)
            if v>0.00 and b:
                dic[nParam][keyword] = v
            nParam += 1
    for i in range(len(parameterList)):
        l = dic[i].items()
        l.sort(key=itemgetter(1),reverse=True)
        dic[i] = {li[0]:li[1] for li in l[:min(n,len(l))]}
    if len(dic)==1:
        dic = dic[0]
    return dic
 
def getProbKeywordInDescription(keyword, slugs, stemmedDesc, parametersStep01, equivalences={}, dicWordWeight={}, toPrint = False):
    '''
    function that determine the importance of the keyword in the string
    according to the following rules and parametersStep01:
    leave parametersStep01 and pop as default to have default parametersStep01
    '''
    v=0.0
    pos = [[] for _ in slugs]
    pos.append([])
    nSlug=0
    nbTotalComa = len([token for token in stemmedDesc if token==","])
    nbTotalMot = len(stemmedDesc)
    booleanMatchParfait = True
    # looking for special stem in description
    for i in range(len(stemmedDesc)):
        # checking the 'non' token in description => pos[-1]
        if stemmedDesc[i]=="non":
            pos[-1].append(i)
    for keywordslug in slugs:
        if toPrint:
            print "  ", keywordslug
        # feature 0 : valeur initiale
        coeff = extractFeature0_InitialValue(parametersStep01, keywordslug, dicWordWeight, toPrint)
        nbMot=0
        nbComa = 0
        vt = 0
        for descslug in stemmedDesc:
            if descslug==",":
                # updating comas number
                nbComa += 1
            if descslug==".":
                nbComa = 0
            im = isMatch(keywordslug, descslug, equivalences, toPrint)
            if im<UtilsConstants.parametersMatchStep01["seuilMatch"]:
                im = 0
            coeff2 = coeff * im
            if coeff2>0:  
                # Match !
                rm = resolveMatch(parametersStep01, nSlug, coeff2, nbMot, nbComa, nbTotalMot, nbTotalComa, pos, toPrint)
                booleanMatchParfait = booleanMatchParfait and (rm[1] or nSlug==0)
                vt = max(vt,rm[0])
                pos[nSlug].append(nbMot)
            if descslug!="," and descslug!=".":
                nbMot+=1
        if len(pos[nSlug])==0:
            # No Match !
            vt = -UtilsConstants.normalisationFunction(2*coeff)
            booleanMatchParfait = False
        v += vt
        nSlug+=1
        if toPrint:
            print "score du slug :",vt
            print ""
    if len(slugs)==1 and abs(v-UtilsConstants.normalisationFunction(UtilsConstants.valMaxUnique))<0.01:
        v = 1
    if toPrint:
        print ""
        print "SCORE FINAL =",1.0*v
        print ""
    return 1.0*v/len(slugs), booleanMatchParfait

def isMatch(slug1, slug2,  equivalences={}, toPrint = False):
    '''
    Matching function for slugs from both keyword and description
    '''
    if (str(slug1) == str(slug2)):
        return 1.0
    if slug1 in equivalences and slug2 in equivalences[slug1]:
        return 0.9
    if abs(len(slug1)-len(slug2))==1:
        if len(slug1)>9:
            for i in range(len(slug1)):
                if slug1[:i]+slug1[i+1:]==slug2:
                    return 0.8
        if len(slug2)>9:
            for i in range(len(slug2)):
                if slug2[:i]+slug2[i+1:]==slug1:
                    return 0.8
    return 0
   
def resolveMatch(parametersStep01, nSlug, coefSlug, nbMot, nbComa, nbTotalMot, nbTotalComa, pos, toPrint):
    if toPrint:
        print "   match !"
    # feature 1 : about commas
    coefComa = extractFeature1_AboutComas(parametersStep01, nbComa, nbTotalComa, toPrint)
    # feature 2 : place in the description
    coefPlace = extractFeature2_AboutPlace(parametersStep01, nbMot, nbTotalMot, toPrint)
    # feature 3 : slugs next to other slugs
    if nSlug==0:
        coefNextTo = parametersStep01['coefProxi']/2
    else:
        coefNextTo = extractFeature3_AboutSlugProximity(parametersStep01, nSlug, nbMot, pos, toPrint)
    # computing final result
    score = UtilsConstants.normalisationFunction((coefSlug+coefNextTo)*coefPlace*coefComa)
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
    coefPlace = 0
    if nbMot<10:
        coefPlace = 1.0
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
                    
def extractFeature3_AboutSlugProximity(parametersStep01, nSlug, nbMot, pos, toPrint):
    '''
    function that returns the place coefficient in keyword extraction
    '''
    coefNextTo = 0
    for i in range(nbMot-int(UtilsConstants.parametersMatchStep01["seuilOrdre"]),nbMot):
        if coefNextTo>0 and i in pos[-1]:
            coefNextTo = 0
        if i in pos[nSlug-1]:
            coefNextTo = parametersStep01['coefProxi']
        
    if toPrint:
        print "      coefNextTo :",coefNextTo  
    return coefNextTo               
   
   
''' STEP 02 - CREATION OF GRAPH '''    
def extractGraphFromSubset(subsetname, path = UtilsConstants.pathSubset, localKeywords = False, percent = 100, toPrint = False):
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
        print "- importing subset",
    entreprises = IOFunctions.importSubset(subsetname, path)
    if toPrint:
        print "... done"
    if entreprises is None:
        return
    graph = IOFunctions.GraphKeyword("graph_"+str(subsetname))
    if toPrint:
        print "- analyzing entreprises"
    compt = UtilsConstants.Compt(entreprises, 1)
    french_stopwords = set(stopwords.words('french')),
    stem = nltk.stem.snowball.FrenchStemmer()
    [keywords,dicWordWeight] = IOFunctions.importKeywords()
    [globalKeywords,globaldicWordWeight] = IOFunctions.importKeywords()
    equivalences = IOFunctions.importSlugEquivalence()
    currentNAF = ""
    if percent<100 and percent>0:
        entreprises = random.sample(entreprises, int(len(entreprises)*percent/100))
    # extracting information from the data
    for entreprise in entreprises:
        if toPrint:
            compt.updateAndPrint()
        if localKeywords and currentNAF != entreprise[1]:
            currentNAF = entreprise[1]
            if currentNAF!="nan" and "keywords.txt" in os.listdir(UtilsConstants.pathCodeNAF+"/subset_NAF_"+currentNAF):
                [keywords,dicWordWeight] = IOFunctions.importKeywords(currentNAF)
            else: 
                [keywords,dicWordWeight] = IOFunctions.importKeywords()
        stemmedDesc = UtilsConstants.tokenizeAndStemmerize(entreprise[2],True,french_stopwords,stem)
        buildFromDescription(stemmedDesc, entreprise[1], keywords, graph, dicWordWeight, globalKeywords, globaldicWordWeight, equivalences, entreprise[2])
    graph.removeLonelyNodes()
    keywordsGraph = []
    for node in graph.graphNodes.values():
        keywordsGraph.append(node.name) 
    if toPrint:
        print "... done"
        print "- saving graphs",
    os.chdir(path+"/"+subsetname)
    IOFunctions.saveGraph(graph)
    IOFunctions.saveGexfFile("graph.gexf", graph)
    IOFunctions.saveKeywords(keywordsGraph, path+"/"+subsetname, "keywords.txt")
    if toPrint:
        print "... done"
        return graph

def buildFromDescription(stemmedDesc,codeNAF,keywords, graph, dicWordWeight, globalKeywords, globaldicWordWeight, equivalences = {}, description = ""):
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
    listKeywords = extractFromDescription(None,keywords, dicWordWeight,preprocessedString=stemmedDesc, equivalences=equivalences)
    if len(listKeywords)==0:
        listKeywords = extractFromDescription(None,globalKeywords, globaldicWordWeight,preprocessedString=stemmedDesc, equivalences=equivalences)
    if len(listKeywords)==0:
        IOFunctions.updateDescriptionFail(description)
    for k in listKeywords:
        graph.addNodeValues(k, codeNAF=codeNAF, valueNAF=listKeywords[k])
    l = listKeywords.items()
    l.sort(key=itemgetter(1),reverse=True)
    l = l[:5]
    for k in l:
        for k1 in l:
            if k[0]!=k1[0]:
                edgeValue = k[1]*k1[1]
                graph.addEdgeValue(graph.dicIdNodes[k[0]], graph.dicIdNodes[k1[0]], edgeValue)  
     
def pipelineGraph(n, percent=100, steps = [True, True, True]):
    
    # COMPUTING GRAPH
    print "COMPUTING COMPLETE GRAPH PIPELINE"
    print ""
    return

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
        
    # Step 1 : computing graph and keywords for all code NAF, using keywords from Step 0-1
    if(steps[1]):
        startTime = time.time()
        print "Step 1 : computing graph and keywords for all code NAF, using all keywords"
        compt = UtilsConstants.Compt(codeNAFs, 1, True)
        for codeNAF in codeNAFs:
            compt.updateAndPrint()
            extractGraphFromSubset("subset_NAF_"+codeNAF, path)
        UtilsConstants.printTime(startTime)
        print ""
        
    # Step 2 : compute complete graph using local keywords
    if(steps[2]):
        startTime = time.time()
        print "Step 2 : compute complete graph using local keywords"
        subsetname = "graphcomplet"
        localKeywords = True
        extractGraphFromSubset(subsetname, path, localKeywords, percent, toPrint=True)
        UtilsConstants.printTime(startTime)
        print ""   
        
                      
''' STEP 03 - EXTRACTION FROM GRAPH '''    
def extractPotentielNodes(graph, dicKeywords, n = 0):
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
    if n>0:
        l = potentielNodes.items()
        l.sort(key=itemgetter(1),reverse=True)
        potentielNodes = [li[0] for li in l[:min(len(l),n)]]
    else:
        potentielNodes = potentielNodes.keys()
    return potentielNodes

def extractFromGraph(graph, dicKeywords, codeNAF = "", classifier=GraphLearning.Step3Classifier(), n=0):
    '''
    function that extracts extra keywords from a graph 

    pour rappel :
    - graphNodes V : dic{id, [name, genericite, dic{NAF:value}]}
    - graphEdges E : dic{(id1,id2),[value,nbOccurence]}
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
                result[graph.graphNodes[a[0]].name] = (a[1]-0.5)*2
    if n>0:
        l = result.items()
        l.sort(key=itemgetter(1),reverse=True)
        result = {li[0]:li[1]*UtilsConstants.parametersStep04["coefficientStep3"] for li in l[:min(len(l),n)]}
    return result
      
                  
''' STEP 04 - MERGING KEYWORDS '''  
def mergingKeywords(keywordsFromDesc, keywordsFromGraph, graph): 
    keywords = dict(keywordsFromDesc.items())
    keywords.update(keywordsFromGraph)
    # Initializing, computing note Step 01/03
    keywords = { k[0] : [k[1],0.0,0.0] for k in keywords.items()}
    # Computing note place dans graph
    maxNode = 0
    for name in keywords:
        for neighbour in graph.getNodeByName(name).neighbours.items():
            if neighbour[0].name in keywords:
                keywords[name][1] += neighbour[1]
        maxNode = max(keywords[name][1],maxNode)
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
        kw.remove(tr)
    # on détermine le nombre de keywords à sortir
    n = int(UtilsConstants.parametersStep04["nbMaxMotsCles"])
    keywords = {k : keywords[k] for k in kw[:min(n,len(keywords))]}
    return keywords
             
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
        
        