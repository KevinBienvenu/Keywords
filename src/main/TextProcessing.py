# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

import codecs
import re
from nltk.corpus import stopwords
import nltk.stem.snowball
import unidecode
import Constants

exceptList = ['art','btp','vin','pli','cms','son','bai']

def extractFromTxt(filename,toDisplay = False):
    '''
    function that extract text from a textfile and return an array of strings
    '''
    with codecs.open(filename,'r','utf-8') as fichier:
        lines = []
        if toDisplay:
            print "reading file",filename
        for line in fichier:
            lines.append(line)
        if toDisplay:
            print "...done"
    return lines

def tokenizeFromArrayOfTxt(array, toDisplay=False):
    lines = []
    percent = 1
    total = len(array)
    i = 0
    for stri in array:
#         if i>10:
#             break
        i+=1
        if toDisplay and 100.0*i/total>percent:
            print percent,".",
            if percent%10==0:
                print ""
            percent+=1
        if str(stri[0])!="nan":
            lines.append(nltkprocess(str(stri[0]).decode("utf-8")))
    return lines

def transformString(srctxt):
    '''
    function transforming str and unicode to string without accent
    or special characters, writable in ASCII
    '''
    try:
        srctxt = unicode(srctxt,"utf8")
    except:
        pass
    return unidecode.unidecode(srctxt).lower()

def nltkprocess(srctxt, 
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
    srctxt = transformString(srctxt)
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
     
def computeDictToken(lines, dictToken = {}):  
    for line in lines:
        for word in line:
            if not(word in dictToken):
                dictToken[word] = 0
            dictToken[word] += 1
    toRemove = []
    for entry in dictToken.items():
        if entry[1]<=2:
            toRemove.append(entry[0])
            continue
        for c in entry[0]:
            try:
                int(c)
                toRemove.append(entry[0])
            except:
                continue
    for toR in toRemove:
        if toR in dictToken.keys():
            del dictToken[toR]
    return dictToken

def extractKeywordsFromString(string, 
                              keywords, 
                              dicWordWeight,
                              french_stopwords = set(stopwords.words('french')),
                              stem = nltk.stem.snowball.FrenchStemmer(),
                              parameters = {},
                              parameterList = None,
                              toPrint=False,
                              preprocessedString = None):
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
        stemmedDesc = nltkprocess(string,keepComa=True, french_stopwords=french_stopwords, stem=stem)
    else :
        stemmedDesc = preprocessedString
    # checking all keywords from the set
    for keyword in keywords:
        if keyword=='.' or keyword==",":
            continue
        nParam = 0
        for parameter in parameterList:
            v = getProbKeywordInDescription(keyword = keyword, 
                                            slugs = keywords[keyword], 
                                            stemmedDesc = stemmedDesc, 
                                            parameters = parameter, 
                                            dicWordWeight = dicWordWeight)
            if v>0:
                dic[nParam][keyword] = v
            nParam += 1
    if toPrint and len(dic)==1:
        print "Analyzing string:"
        print "   ",string
        print ""
    if len(dic)==1:
        dic = dic[0]
    return dic
                         
def getProbKeywordInDescription(keyword, slugs, stemmedDesc, parameters, dicWordWeight={}):
    '''
    function that determine the importance of the keyword in the string
    according to the following rules and parameters:
    leave parameters and pop as default to have default parameters
    '''
    toPrint = False
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
            if isMatch(keywordslug, descslug):  
                # Match !
                v += resolveMatch(parameters, nSlug, coeff, nbMot, nbComa, nbTotalMot, nbTotalComa, pos, toPrint)
                pos[nSlug].append(nbMot)
            nbMot+=1
        if len(pos[nSlug])==0:
            # No Match !
            v -= parameters['N']*coeff
        nSlug+=1
    return 1.0*v/len(slugs) 

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
    

''' Defining features for keyword extraction '''

def isMatch(keywordslug, descslug):
    '''
    Matching function for slugs from both keyword and description
    '''
    return (keywordslug == descslug 
            or (len(keywordslug)>4 and keywordslug in descslug) 
            or (len(descslug)>4 and descslug in keywordslug))
   
def resolveMatch(parameters, nSlug, coefSlug, nbMot, nbComa, nbTotalMot, nbTotalComa, pos, toPrint):
    if toPrint:
        print "   match:",nbMot
    # feature 1 : about commas
    coefComa = extractFeature1_AboutComas(parameters, nbComa, nbTotalComa, toPrint)
    # feature 2 : place in the description
    coefPlace = extractFeature2_AboutPlace(parameters, nbMot, nbTotalMot, toPrint)
    # features 3 : slugs next to other slugs
    coefNextTo = extractFeature3_AboutSlugProximity(parameters, nSlug, nbMot, pos, toPrint)
    # computing final result
    return (coefSlug+coefNextTo)*coefPlace*coefComa

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
        if nbMot-1 in pos[k] or nbMot-2 in pos[k]:
            coefNextTo += parameters['J']
    if toPrint:
        print "      coefNextTo :",coefNextTo  
    return coefNextTo               
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    