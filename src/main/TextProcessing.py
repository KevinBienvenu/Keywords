# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

''' Performing keywords extraction - Etape 1 '''

from operator import itemgetter
import re

from nltk.corpus import stopwords
import nltk.stem.snowball
import unidecode

import Constants


def extractKeywordsFromString(string, 
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
        stemmedDesc = tokenizeAndStemmerize(string,keepComa=True, french_stopwords=french_stopwords, stem=stem)
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
            if v>0.15:
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

def getOccurencesKeywordInDescription(slugs, stemmedDesc):
    '''
    function returning the slugs that match in the stemmed description
    '''
    tab = {}
    nSlug = 0
    for keywordslug in slugs:
        for descslug in stemmedDesc:
            if isMatch(keywordslug, descslug):
                tab[keywordslug]=True
        nSlug+=1
    return tab
 
''' Auxiliary text processing functions ''' 

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
                v += resolveMatch(parameters, nSlug, coeff2, nbMot, nbComa, nbTotalMot, nbTotalComa, pos, toPrint)
                pos[nSlug].append(nbMot)
            nbMot+=1
        if len(pos[nSlug])==0:
            # No Match !
            v -= Constants.normalisationFunction(parameters['N']*coeff)
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

''' Defining features for keyword extraction - Etape 1'''

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
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    