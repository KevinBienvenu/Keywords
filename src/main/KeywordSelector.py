# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''
from main import GraphProcessing
''' Extraction and Suggestion functions'''

from operator import itemgetter
import os
from nltk.corpus import stopwords
import nltk.stem.snowball

import GraphLearning, IOFunctions, Constants


''' Main pipeline functions '''
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
        keywordlist, origins = selectKeyword(line[0],line[1], graph, keywordSet, nbMot)
        keywords.append(keywordlist)
        if printGraph:
            os.chdir(Constants.pathCodeNAF+"/graphtest")
            IOFunctions.saveGexfFile("graph_test_"+str(i)+".gexf", graph, keywords = keywordlist, origins = origins)
        i+=1
    return keywords
        
def selectKeyword(description, codeNAF, graph, keywordSet, localKeywords = False, n=50):
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
    dicWordWeight = {}
    origin = {}
    if localKeywords:
        keywordSet, _ = IOFunctions.importKeywords(codeNAF)
    ## STEP 1 = Extracting only from description
    keywordFromDesc = extractFromDescription(description, keywordSet, dicWordWeight,toPrint=False)
    print keywordFromDesc
    ## STEP 2 = Extracting only from codeNAF
    keywordFromNAF = IOFunctions.getSuggestedKeywordsByNAF(codeNAF)
    # merging previous dictionaries
    dicKeywords = {}
    for key in keywordFromDesc:
        dicKeywords[key] = keywordFromDesc[key]
        origin[key] = [1]
    coef = 2.0
    for key in keywordFromNAF:
        if not(key in dicKeywords):       
            coef=max(1.0,coef*0.95)
            continue
        origin[key].append(2)
        dicKeywords[key] *= coef
        coef=max(1.0,coef*0.95)
    ## STEP 3 = Extracting from Graph
    keywordFromGraph = extractFromGraph(graph,dicKeywords)
    print keywordFromGraph
    # merging last dice
    for key in keywordFromGraph:
        if not(key in dicKeywords):
            dicKeywords[key] = 0
            origin[key] = []
        dicKeywords[key] = keywordFromGraph[key]
        origin[key].append(3)
        
    ## STEP 4 = Printing / Returning
    l = dicKeywords.items()
    l.sort(key=itemgetter(1),reverse=True)
    return {k[0]:k[1] for k in l[:min(n,len(l))]},[origin[k[0]] for k in l[:min(n,len(l))]]

''' STEP 01 - EXTRACTION FROM DESC '''     
def extractFromDescription(string, 
                              keywords, 
                              dicWordWeight,
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
    if toPrint:
        print "analaysing :",string
        print stemmedDesc
    # checking all keywords from the set
    for keyword in keywords:
        if toPrint:
            print "trying to match",keyword
            print "slugs:",keywords[keyword]
        if keyword=='.' or keyword==",":
            continue
        nParam = 0
        for parameter in parameterList:
            v = getProbKeywordInDescription(keyword = keyword, 
                                            slugs = keywords[keyword], 
                                            stemmedDesc = stemmedDesc, 
                                            parameters = parameter, 
                                            dicWordWeight = dicWordWeight,
                                            toPrint=toPrint)
            if v>0.1:
                dic[nParam][keyword] = v
                if toPrint:
                    print parameter,":",keyword
            nParam += 1
    for i in range(len(parameterList)):
        l = dic[i].items()
        l.sort(key=itemgetter(1),reverse=True)
        dic[i] = {li[0]:li[1] for li in l[:min(n,len(l))]}
    if len(dic)==1:
        dic = dic[0]
    return dic
 
def getProbKeywordInDescription(keyword, slugs, stemmedDesc, parameters, dicWordWeight={}, toPrint = False):
    '''
    function that determine the importance of the keyword in the string
    according to the following rules and parameters:
    leave parameters and pop as default to have default parameters
    '''
    if toPrint:
        print "== Get Prob of",keyword,"in",stemmedDesc
    v=0.0
    pos = [[]]
    nSlug=0
    nbTotalComa = len([token for token in stemmedDesc if token==","])
    nbTotalMot = len(stemmedDesc)
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
            coeff2 = coeff * isMatch(keywordslug, descslug, toPrint)
            if toPrint:
                print descslug, keywordslug, coeff2
            if coeff2>0:  
                # Match !
                vt += resolveMatch(parameters, nSlug, coeff2, nbMot, nbComa, nbTotalMot, nbTotalComa, pos, toPrint)
                pos[nSlug].append(nbMot)
            nbMot+=1
        if len(pos[nSlug])==0:
            # No Match !
            v -= Constants.normalisationFunction(parameters['N']*coeff)
        else:
            v += vt
        nSlug+=1
    return 1.0*v/len(slugs) 

def isMatch(slug1, slug2, toPrint = False):
    '''
    Matching function for slugs from both keyword and description
    '''
    if (str(slug1) == str(slug2)):
        if toPrint:
            print "match !", slug1, slug2
        return 1.0
    if (slug1[:-1]==slug2 or slug2[:-1]==slug1):
        if toPrint:
            print "moyen match !", slug1, slug2
        return 1.0
    if abs(len(slug1)-len(slug2))==1:
        if len(slug1)>9:
            for i in range(len(slug1)):
                if slug1[:i]+slug1[i+1:]==slug2:
                    return 0.9
        if len(slug2)>9:
            for i in range(len(slug2)):
                if slug2[:i]+slug2[i+1:]==slug1:
                    return 0.9
    if ((len(slug1)>5 and slug1 == slug2[:min(len(slug2),len(slug1))]) 
         or (len(slug2)>5 and slug2 == slug1[:min(len(slug2),len(slug1))])):
        if toPrint:
            print "petit match !", slug1, slug2
        return 0.3
    return 0
   
def resolveMatch(parameters, nSlug, coefSlug, nbMot, nbComa, nbTotalMot, nbTotalComa, pos, toPrint):
    if toPrint:
        print "   match:",nbMot
    # feature 1 : about commas
    coefComa = extractFeature1_AboutComas(parameters, nbComa, nbTotalComa, toPrint)
    # feature 2 : place in the description
    coefPlace = extractFeature2_AboutPlace(parameters, nbMot, nbTotalMot, toPrint)
    # feature 3 : slugs next to other slugs
    coefNextTo = extractFeature3_AboutSlugProximity(parameters, nSlug, nbMot, pos, toPrint)
    # computing final result
    return Constants.normalisationFunction((coefSlug+coefNextTo)*coefPlace*coefComa)

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
    for k in range(nSlug):
        for i in range(nbMot):
            if i in pos[k]:
                coefNextTo = parameters['J']
    if toPrint:
        print "      coefNextTo :",coefNextTo  
    return coefNextTo               
   
   
''' STEP 02 - CREATION OF GRAPH '''    
def buildFromDescription(self,stemmedDesc,codeNAF,keywords, dicWordWeight):
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
    listKeywords = extractFromDescription(_,keywords, dicWordWeight,preprocessedString=stemmedDesc)
    for k in listKeywords:
        self.addNodeValues(k, codeNAF=codeNAF, valueNAF=listKeywords[k])
    listMainKeywords = listKeywords.items()
    listMainKeywords.sort(key=itemgetter(1),reverse=True)
    listMainKeywords = [a[0] for a in listMainKeywords[:min(6,len(listMainKeywords))]]
    for k in listMainKeywords:
        for k1 in listMainKeywords:
            if k!=k1:
                edgeValue = 1
                self.addEdgeValue(self.dicIdNodes[k], self.dicIdNodes[k1], edgeValue)  

                    
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
    print ""
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
                  
              
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
        
        