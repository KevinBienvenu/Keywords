# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''
from networkx.algorithms.minors import equivalence_classes
''' Extraction and Suggestion functions'''
''' Main pipeline functions '''

import codecs
from operator import itemgetter
import os

from nltk.corpus import stopwords
import nltk.stem.snowball

import GraphLearning, IOFunctions, Constants
import numpy as np


def pipeline(descriptions, nbMot = 20, printGraph = True):
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
    os.chdir(os.path.join(Constants.pathCodeNAF,"graphcomplet"))
    graph = IOFunctions.importGraph("graphcomplet")
    keywordSet, _ = IOFunctions.importKeywords()
    keywords = []
    i = 0
    os.chdir(Constants.pathCodeNAF+"/graphtest")
    for line in descriptions:
        keywordlist, origins = selectKeyword(line[1],line[0], graph, keywordSet, True, nbMot, toPrint=True)
        keywords.append(keywordlist)
        if printGraph:
            os.chdir(Constants.pathCodeNAF+"/graphtest")
            IOFunctions.saveGexfFile("graph_test_"+str(i)+".gexf", graph, keywords = keywordlist, origins = origins)
        i+=1
    return keywords

def pipelineTest():
    print "DEBUT TEST PIPELINE"
    os.chdir(os.path.join(Constants.pathCodeNAF,"graphcomplet"))
    graph = IOFunctions.importGraph("graphcomplet")
    print "   graph importé"
    keywordSet, _ = IOFunctions.importKeywords()
    print "   mots-clés importés"
#     entreprises = IOFunctions.extractSubset(n=10)
    entreprises = [
                   ["","conseil en marketing, tracteur en marketing"]
                   ]
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
            extractFromDescription(line[1], {ipt:IOFunctions.tokenizeAndStemmerize(ipt)}, {}, toPrint=True)
        try:
            ipt = input("nouvelle description ?")
        except:
            break
        
def selectKeyword(description, codeNAF, graph, keywordSet, localKeywords = False, n=50, toPrint = False):
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
    dicWordWeight = {}
    origin = {}
    if localKeywords:
        keywordSet, _ = IOFunctions.importKeywords(codeNAF)
    ## STEP 1 = Extracting only from description
    keywordFromDesc = extractFromDescription(description, keywordSet, dicWordWeight,toPrint=False)
    if toPrint:
        print "from desc:"
        IOFunctions.printSortedDic(keywordFromDesc)
        print ""
    for key in keywordFromDesc:
        origin[key]=[1]
        
    ## STEP 3 = Extracting from Graph
    keywordFromGraph = extractFromGraph(graph,keywordFromDesc)
#     if toPrint:
#         print "from graph:"
#         IOFunctions.printSortedDic(keywordFromGraph)
#         print ""
#         print ""
    for key in keywordFromGraph:
        origin[key]=[3]
        
    ## STEP 4 = Merging and Selecting
    keywords = mergingKeywords(keywordFromDesc, keywordFromGraph)
    return keywords, origin

    
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
    os.chdir(os.path.join(Constants.path,"motscles"))
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
        mots = IOFunctions.tokenizeAndStemmerize(keyword, keepComa=False, stem = stem, method="")
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


''' STEP 01 - EXTRACTION FROM DESC '''     
def extractFromDescription(string, 
                              keywords, 
                              dicWordWeight,
                              equivalences = {},
                              french_stopwords = set(stopwords.words('french')),
                              stem = nltk.stem.snowball.FrenchStemmer(),
                              parameters = {},
                              parameterList = None,
                              toPrint=False,
                              preprocessedString = None,
                              n=10):
    '''
    function that returns a list of keywords out of a description
    -- IN
    string : the string from which we extract the keywords (str)
    keywords : the list of keywords to extract (dic{str:[tokens]})
    toPrint : boolean that settles if the function must print the results (boolean) default=False
    -- OUT
    dic : dic of keywords which values are the importance of the keyword (dic{str:float})
    '''
    # initializing parameters
    if parameterList is None:
        if parameters == {}:
            parameters = Constants.parameters
        parameterList = [parameters]
    dic = [{} for _ in parameterList]
    # initializing description
    if preprocessedString is None:
        stemmedDesc = IOFunctions.tokenizeAndStemmerize(string,keepComa=True, french_stopwords=french_stopwords, stem=stem)
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
                                            parameters = parameter, 
                                            equivalences = equivalences, 
                                            dicWordWeight = dicWordWeight,
                                            toPrint=toPrint)
            if v>0.05 and b:
                dic[nParam][keyword] = v
            nParam += 1
    for i in range(len(parameterList)):
        l = dic[i].items()
        l.sort(key=itemgetter(1),reverse=True)
        dic[i] = {li[0]:li[1] for li in l[:min(n,len(l))]}
    if len(dic)==1:
        dic = dic[0]
    return dic
 
def getProbKeywordInDescription(keyword, slugs, stemmedDesc, parameters, equivalences={}, dicWordWeight={}, toPrint = False):
    '''
    function that determine the importance of the keyword in the string
    according to the following rules and parameters:
    leave parameters and pop as default to have default parameters
    '''
    v=0.0
    pos = [[]]
    nSlug=0
    nbTotalComa = len([token for token in stemmedDesc if token==","])
    nbTotalMot = len(stemmedDesc)
    booleanMatchParfait = True
    for keywordslug in slugs:
        if toPrint:
            print "  ", keywordslug
        # feature 0 : valeur initiale
        coeff = extractFeature0_InitialValue(parameters, keywordslug, dicWordWeight, toPrint)
        pos.append([])
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
            if im<Constants.step01_seuilMatch:
                im = 0
            coeff2 = coeff * im
            if coeff2>0:  
                # Match !
                rm = resolveMatch(parameters, nSlug, coeff2, nbMot, nbComa, nbTotalMot, nbTotalComa, pos, toPrint)
                booleanMatchParfait = booleanMatchParfait and (rm[1] or nSlug==0)
                vt = max(vt,rm[0])
                pos[nSlug].append(nbMot)
            if descslug!="," and descslug!=".":
                nbMot+=1
        if len(pos[nSlug])==0:
            # No Match !
            vt = -Constants.normalisationFunction(parameters['N']*coeff)
            booleanMatchParfait = False
        v += vt
        nSlug+=1
        if toPrint:
            print "score du slug :",vt
            print ""
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
   
def resolveMatch(parameters, nSlug, coefSlug, nbMot, nbComa, nbTotalMot, nbTotalComa, pos, toPrint):
    if toPrint:
        print "   match !"
    # feature 1 : about commas
    coefComa = extractFeature1_AboutComas(parameters, nbComa, nbTotalComa, toPrint)
    # feature 2 : place in the description
    coefPlace = extractFeature2_AboutPlace(parameters, nbMot, nbTotalMot, toPrint)
    # feature 3 : slugs next to other slugs
    coefNextTo = extractFeature3_AboutSlugProximity(parameters, nSlug, nbMot, pos, toPrint)
    # computing final result
    score = Constants.normalisationFunction((coefSlug+coefNextTo)*coefPlace*coefComa)
    if toPrint:
        print "     => score =",score
    return score, coefNextTo>0

def extractFeature0_InitialValue(parameters, keywordslug, dicWordWeight, toPrint):
    '''
    function that returns the initial value of a keyword slug
    according to parameters and a dicWordWeight.
    '''
    try:
        coeff = parameters['A']*int(dicWordWeight[keywordslug]) \
                + parameters['B']/int(dicWordWeight[keywordslug])           
    except:
        coeff = 0.5
    if toPrint:
        print "   valeur initiale:",coeff
    return coeff

def extractFeature1_AboutComas(parameters, nbComa, nbTotalComa, toPrint):
    '''
    function that returns the coma coefficient in keyword extraction
    '''
    coefComa = parameters['C']*nbComa \
                + parameters['D']/(1.0+nbComa) \
                + parameters['E']/(1.0+abs(nbComa-nbTotalComa/2.0)) 
    if toPrint:
        print "      coefComa :",coefComa
    return coefComa

def extractFeature2_AboutPlace(parameters, nbMot, nbTotalMot, toPrint):
    '''
    function that returns the place coefficient in keyword extraction
    '''
    coefPlace = 0
    if nbMot<10:
        coefPlace = 1.0
    else:
        fracPlace = 1.0*nbMot/nbTotalMot
        if fracPlace<0.33:
            coefPlace += parameters['F']
        elif fracPlace<0.66:
            coefPlace += parameters['G']
        else:
            coefPlace += parameters['H']
        
    if "I"+str(nbMot) in parameters:
        coefPlace *= parameters["I"+str(nbMot)] 
    elif "I"+str(nbMot-nbTotalMot) in parameters:                    
        coefPlace *= parameters["I"+str(nbMot-nbTotalMot)] 
        
    if toPrint:
        print "      coefPlace :",coefPlace
    return coefPlace
                    
def extractFeature3_AboutSlugProximity(parameters, nSlug, nbMot, pos, toPrint):
    '''
    function that returns the place coefficient in keyword extraction
    '''
    coefNextTo = 0
    for i in range(nbMot-Constants.step01_seuilOrdre,nbMot):
        if i in pos[nSlug-1]:
            coefNextTo = parameters['J']
            break;
    if toPrint:
        print "      coefNextTo :",coefNextTo  
    return coefNextTo               
   
   
''' STEP 02 - CREATION OF GRAPH '''    
def extractGraphFromSubset(subsetname, path = Constants.pathSubset, localKeywords = False, toPrint = False):
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
    compt = Constants.Compt(entreprises, 1)
    french_stopwords = set(stopwords.words('french')),
    stem = nltk.stem.snowball.FrenchStemmer()
    [keywords,dicWordWeight] = IOFunctions.importKeywords()
    [globalKeywords,globaldicWordWeight] = IOFunctions.importKeywords()
    equivalences = IOFunctions.importSlugEquivalence()
    currentNAF = ""
    # extracting information from the data
    for entreprise in entreprises:
        if toPrint:
            compt.updateAndPrint()
        if localKeywords and currentNAF != entreprise[1]:
            currentNAF = entreprise[1]
            if currentNAF!="nan" and "keywords.txt" in os.listdir(Constants.pathCodeNAF+"/subset_NAF_"+currentNAF):
                [keywords,dicWordWeight] = IOFunctions.importKeywords(currentNAF)
            else: 
                [keywords,dicWordWeight] = IOFunctions.importKeywords()
        stemmedDesc = IOFunctions.tokenizeAndStemmerize(entreprise[2],True,french_stopwords,stem)
        buildFromDescription(stemmedDesc, entreprise[1], keywords, graph, dicWordWeight, globalKeywords, globaldicWordWeight, equivalences)
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

def buildFromDescription(stemmedDesc,codeNAF,keywords, graph, dicWordWeight, globalKeywords, globaldicWordWeight, equivalences = {}):
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
    for k in listKeywords:
        graph.addNodeValues(k, codeNAF=codeNAF, valueNAF=listKeywords[k])
    for k in listKeywords:
        for k1 in listKeywords:
            if k!=k1:
                edgeValue = listKeywords[k]*listKeywords[k1]
                graph.addEdgeValue(graph.dicIdNodes[k], graph.dicIdNodes[k1], edgeValue)  
     
                 
''' STEP 03 - EXTRACTION FROM GRAPH '''    
def extractFromGraph(graph, dicKeywords, classifier=GraphLearning.Step3Classifier()):
    '''
    function that extracts extra keywords from a graph 

    pour rappel :
    - graphNodes V : dic{id, [name, genericite, dic{NAF:value}]}
    - graphEdges E : dic{(id1,id2),[value,nbOccurence]}
    '''
    # on parcourt toutes les arrêtes:
    potentielNodes = {}
    for name in dicKeywords:
        node = graph.getNodeByName(name)
        if node is None:
            continue
        node.state = 1
        for neighbour in node.neighbours:
            if not(neighbour.name in dicKeywords):
                if not(neighbour.id in potentielNodes):
                    potentielNodes[neighbour.id] = [0.0,0]
                potentielNodes[neighbour.id][0] += dicKeywords[name]
                potentielNodes[neighbour.id][1] += 1
    for key in potentielNodes:
        potentielNodes[key] = potentielNodes[key][0]*potentielNodes[key][1]
    # on extrait les n plus gros
    l = potentielNodes.items()
    l.sort(key=itemgetter(1),reverse=True)
    potentielNodes = [k[0] for k in l[:min(50,len(l))]]
    X = []
    for key in potentielNodes:
        graph.computeNodeFeatures(graph.graphNodes[key].name)
        X.append([graph.graphNodes[key].features[keyFeatures] 
                  for keyFeatures in ['nbVoisins','nbVoisins1','propSumVoisins1','propVoisins1','size','sumVoisins','sumVoisins1']])
    Y = classifier.predict(X)
    result = {}
    for a in zip(potentielNodes, Y):
        if a[1]==1:
            result[graph.graphNodes[a[0]].name] = 1
    return result
      
                  
''' STEP 04 - MERGING KEYWORDS '''  
def mergingKeywords(keywordsFromDesc, keywordsFromGraph): 
    keywords = {}
    for k in keywordsFromDesc:
        keywords[k] = keywordsFromDesc[k]
    for k in keywordsFromGraph:
        keywords[k] = keywordsFromGraph[k]
    return keywords
             
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
        
        