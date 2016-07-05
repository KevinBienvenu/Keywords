# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''

''' Extraction and Suggestion functions'''

from operator import itemgetter
import os
from nltk.corpus import stopwords
import nltk.stem.snowball

import GraphLearning, IOFunctions, Constants


''' Main pipeline functions '''
def pipeline(descriptions, nbMot = 20, printGraph = False):
    '''
    Pipeline function taking as input a dataframe with rows 'codeNAF' and 'description'
    and giving as output a list of keywords for each description in the dataframe
    -- IN:
    descriptions : pd.DataFrame with columns 'codeNaf' and 'description' at least
    nbMot : number of returned keywords, (int) default : 5
    -- OUT:
    keywords : list of lists of keywords [[string],[string], ...]
    '''
    # checking validity of inputs
    try:
        _ = descriptions.codeNaf
        _ = descriptions.description
    except:
        print "error : invalid input, missing columns"
    # importing graph and keywords
    os.chdir(os.path.join(Constants.pathCodeNAF,"graphcomplet"))
    graph = IOFunctions.importGraph("graphcomplet")
    keywordSet, _ = IOFunctions.importKeywords()
    keywords = []
    i = 0
    os.chdir(Constants.pathCodeNAF+"/graphtest")
    for line in descriptions[["codeNaf","description"]].values:
        keywords.append(selectKeyword(line[1],line[0], graph, keywordSet, nbMot)[0])
        if printGraph:
            os.chdir(Constants.pathCodeNAF+"/graphtest")
            IOFunctions.saveGexfFile("graph_test_"+str(i)+".gexf", graph, keywords = keywords[-1])
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
    for key in keywordFromDesc:
        origin[key]=[1]
        
    ## STEP 3 = Extracting from Graph
    keywordFromGraph = extractFromGraph(graph,keywordFromDesc)
    print keywordFromGraph
    for key in keywordFromGraph:
        origin[key]=[3]
        
    ## STEP 4 = Merging and Selecting
    keywords = mergingKeywords(keywordFromDesc, keywordFromGraph)
    return keywords

    
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
def extractGraphFromSubset(subsetname, path = Constants.pathSubset, localKeywords = False):
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
    print "== Extracting graph from subset:",subsetname
    print "- importing subset",
    entreprises = IOFunctions.importSubset(subsetname, path)
    print "... done"
    if entreprises is None:
        return
    graph = IOFunctions.GraphKeyword("graph_"+str(subsetname))
    print "- analyzing entreprises"
    compt = Constants.Compt(entreprises, 1)
    french_stopwords = set(stopwords.words('french')),
    stem = nltk.stem.snowball.FrenchStemmer()
    [keywords,dicWordWeight] = IOFunctions.importKeywords()
    currentNAF = ""
    # extracting information from the data
    for entreprise in entreprises:
        compt.updateAndPrint()
        if localKeywords and currentNAF != entreprise[1]:
            currentNAF = entreprise[1]
            if currentNAF!="nan" and "keywords.txt" in os.listdir(Constants.pathCodeNAF+"/subset_NAF_"+currentNAF):
                [keywords,dicWordWeight] = IOFunctions.importKeywords(currentNAF)
            else: 
                [keywords,dicWordWeight] = IOFunctions.importKeywords()
        stemmedDesc = IOFunctions.tokenizeAndStemmerize(entreprise[2],True,french_stopwords,stem)
        buildFromDescription(stemmedDesc, entreprise[1], keywords, graph, dicWordWeight)
    graph.removeLonelyNodes()
    print "... done"
    print "- saving graphs",
    os.chdir(path+"/"+subsetname)
#     with open("edges_values.txt","w") as fichier:
#         for edge in graphEdges:
#             fichier.write(str(graphEdges[edge][0])+"\n")
    IOFunctions.saveGraph(graph)
    IOFunctions.saveGexfFile("graph.gexf", graph)
    print "... done"
    return graph

def buildFromDescription(stemmedDesc,codeNAF,keywords, graph, dicWordWeight):
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
    listKeywords = extractFromDescription(None,keywords, dicWordWeight,preprocessedString=stemmedDesc)
    for k in listKeywords:
        graph.addNodeValues(k, codeNAF=codeNAF, valueNAF=listKeywords[k])
    listMainKeywords = listKeywords.items()
    listMainKeywords.sort(key=itemgetter(1),reverse=True)
    listMainKeywords = [a[0] for a in listMainKeywords[:min(6,len(listMainKeywords))]]
    for k in listMainKeywords:
        for k1 in listMainKeywords:
            if k!=k1:
                edgeValue = 1
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
      
                  
''' STEP 04 - MERGING KEYWORDS '''  
def mergingKeywords(keywordsFromDesc, keywordsFromGraph): 
    keywords = {}
    for k in keywordsFromDesc:
        keywords[k] = keywordsFromDesc[k]
    for k in keywordsFromGraph:
        keywords[k] = keywordsFromGraph[k]
    return keywords
             
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
        
        