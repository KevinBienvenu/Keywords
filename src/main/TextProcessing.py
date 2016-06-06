# -*- coding: utf-8 -*-
'''
Created on 25 avr. 2016

@author: Kévin Bienvenu
'''

import codecs
from nltk.corpus import stopwords
import nltk.stem.snowball
import unidecode
import warnings
import IOFunctions
import math

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

def nltkprocess(srctxt, 
                keepComa = False, 
                french_stopwords = set(stopwords.words('french')),
                stem = nltk.stem.snowball.FrenchStemmer()):
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
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tokens = nltk.word_tokenize(srctxt.lower(),'french')
    except:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tokens = nltk.word_tokenize(srctxt.lower().decode("utf8"),'french')
        except:    
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tokens = nltk.word_tokenize(unidecode.unidecode(srctxt).lower(),'french')
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
            if len(token)>3 or token in exceptList or token[:2]=="th":
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        stems.append(stem.stem(token[:-1])) 
                except:
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            stems.append(stem.stem(token[:-1].decode("utf8")))
                    except:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            stems.append(stem.stem(unidecode.unidecode(token[:-1])))
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
    dic = {}
    if preprocessedString is None:
        stemmedDesc = nltkprocess(string,keepComa=True, french_stopwords=french_stopwords, stem=stem)
    else :
        stemmedDesc = preprocessedString
    for keyword in keywords:
        if keyword=='.' or keyword==",":
            continue
        v = getProbKeywordInDescription(keyword, keywords[keyword], stemmedDesc, dicWordWeight, parameters)
        if v>0.00:
            dic[keyword[:-1]] = v
    if toPrint:
        print "Analyzing string:"
        print "   ",string
        print ""
        IOFunctions.printSortedDic(dic, 10)
    return dic
                         
def getProbKeywordInDescription(keyword, tokens, stemmedDesc, dicWordWeight={}, parameters = {}):
    '''
    function that determine the importance of the keyword in the string
    according to the following rules and parameters:
    
    '''
    toPrint = False
    if toPrint:
        print keyword
        print stemmedDesc
    v=0
    pos = [[]]
    i=0
    if parameters == {}:
        parameters = {'A':1.0/200,'B':1.0,
                      'C':1.0/5.0,'D':1.0,'E':1.0,
                      'F':1.0,'G':0.5,'H':0.8,
                      'I0':2.0,
                      'I1':2.0,
                      'I-1':2.0,
                      'J':1.0,
                      'N':0.5}
    nbTotalComa = len([token for token in stemmedDesc if token==","])
    for keywordslug in tokens:
        if toPrint:
            print "  ", keywordslug
        if keywordslug in dicWordWeight:
            # feature 0 : valeur initiale
            coeff = parameters['A']*int(dicWordWeight[keywordslug])+parameters['B']/int(dicWordWeight[keywordslug])
        else:
            coeff = 0.5
        if toPrint:
            print "   valeur initiale:",coeff
        j=0
        nbTotalMot = len(stemmedDesc)
        nbComa = 0
        coefNextTo = 0.0
        pos.append([])
        coefPlace = 0.0
        for s in stemmedDesc:
            if s==",":
                nbComa += 1
            if keywordslug == s:  
                if toPrint:
                    print "   match:",j
                # feature 1 : about commas
                coefComa = parameters['C']*nbComa 
                coefComa += parameters['D']/(1.0+nbComa) 
                coefComa += parameters['E']/(1.0+abs(nbComa-nbTotalComa/2.0))
                if toPrint:
                    print "      coefComa :",coefComa
                # feature 2 : place in the description
                fracPlace = 1.0*j/nbTotalMot
                if fracPlace<0.33:
                    coefPlace += parameters['F']
                elif fracPlace<0.66:
                    coefPlace += parameters['G']
                else:
                    coefPlace += parameters['H']
                if "I"+str(j) in parameters:
                    coefPlace*=parameters["I"+str(j)]
                elif "I"+str(j-nbTotalMot) in parameters:                    
                    coefPlace*=parameters["I"+str(j-nbTotalMot)]
                if toPrint:
                    print "      coefPlace :",coefPlace
                # features 3 : slugs next to other slugs
                for k in range(i):
                    if j-1 in pos[k] or j-2 in pos[k]:
                        coefNextTo += parameters['J']
                if toPrint:
                    print "      coefNextTo :",coefNextTo
                v+=(coeff+coefNextTo)*coefPlace*coefComa
                if toPrint:
                    print "      v :",v
                pos[i].append(j)
            j+=1
        if len(pos[i])==0:
            v-=parameters['N']*coeff
        i+=1
    v = 1.0*v/len(tokens)
    return v

    