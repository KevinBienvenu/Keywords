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
import IOFunctions

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
                elif method=="gram":
                    stems.append(IOFunctions.getGrammNatureViaInternet(token))
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
    if parameterList is None:
        if parameters == {}:
            parameters = {'A':1.0/200,'B':1.0,
                          'C':1.0/5.0,'D':1.0,'E':1.0,
                          'F':1.0,'G':0.5,'H':0.8,
                          'I0':2.0,
                          'I1':2.0,
                          'I-1':2.0,
                          'J':1.0,
                          'N':0.5}
            print "vaneau"
        parameterList = [parameters]
    dic = [{} for _ in parameterList]
    if preprocessedString is None:
        stemmedDesc = nltkprocess(string,keepComa=True, french_stopwords=french_stopwords, stem=stem)
    else :
        stemmedDesc = preprocessedString
    for keyword in keywords:
        if keyword=='.' or keyword==",":
            continue
        v = getProbKeywordInDescription(keyword = keyword, 
                                        tokens = keywords[keyword], 
                                        stemmedDesc = stemmedDesc, 
                                        parameterList = parameterList, 
                                        dicWordWeight = dicWordWeight)
        for i in range(len(dic)):
            if v[i]>0:
                dic[i][keyword] = v[i]
    if toPrint and len(dic)==1:
        print "Analyzing string:"
        print "   ",string
        print ""
        IOFunctions.printSortedDic(dic[0], 10)
    if len(dic)==1:
        dic = dic[0]
    return dic
                         
def getProbKeywordInDescription(keyword, tokens, stemmedDesc, parameterList, dicWordWeight={}):
    '''
    function that determine the importance of the keyword in the string
    according to the following rules and parameters:
    leave parameters and pop as default to have default parameters
    '''
    toPrint = False
    if toPrint:
        print keyword
        print stemmedDesc
    v=[0]*len(parameterList)
    pos = [[]]
    nSlug=0
    rlp = range(len(parameterList))
    nbTotalComa = len([token for token in stemmedDesc if token==","])
    for keywordslug in tokens:
        if toPrint:
            print "  ", keywordslug
        try:
            # feature 0 : valeur initiale
            coeff = [parameters['A']*int(dicWordWeight[keywordslug])
                     + parameters['B']/int(dicWordWeight[keywordslug])
#                      + (parameters['K0'] if nSlug==0 else 1.0)
#                      + (parameters['K1'] if nSlug==1 else 1.0)
#                      + (parameters['K2'] if nSlug==2 else 1.0)
#                      + (parameters['L']*len(tokens))
#                      + (parameters['M']/len(tokens))
                     for parameters in parameterList]
            
        except:
            coeff = [0.5]*len(parameterList)
        if toPrint:
            print "   valeur initiale:",coeff
        j=0
        nbTotalMot = len(stemmedDesc)
        nbComa = 0
        coefNextTo = [0.0]*len(parameterList)
        pos.append([])
        coefPlace = [0.0]*len(parameterList)
        for s in stemmedDesc:
            if s==",":
                nbComa += 1
            if (keywordslug == s 
                or (len(keywordslug)>4 and keywordslug in s) 
                or (len(s)>4 and s in keywordslug)):  
                if toPrint:
                    print "   match:",j
                # feature 1 : about commas
                coefComa = [parameters['C']*nbComa
                            +parameters['D']/(1.0+nbComa)
                            +parameters['E']/(1.0+abs(nbComa-nbTotalComa/2.0)) 
                            for parameters in parameterList]
                if toPrint:
                    print "      coefComa :",coefComa
                # feature 2 : place in the description
                fracPlace = 1.0*j/nbTotalMot
                if fracPlace<0.33:
                    coefPlace = [coefPlace[i] + parameterList[i]['F'] for i in rlp]
                elif fracPlace<0.66:
                    coefPlace = [coefPlace[i] + parameterList[i]['G'] for i in rlp]
                else:
                    coefPlace = [coefPlace[i] + parameterList[i]['H'] for i in rlp]
                if "I"+str(j) in parameters:
                    coefPlace = [coefPlace[i] * parameterList[i]["I"+str(j)] for i in rlp]
                elif "I"+str(j-nbTotalMot) in parameters:                    
                    coefPlace = [coefPlace[i] * parameterList[i]["I"+str(j-nbTotalMot)] for i in rlp]
                if toPrint:
                    print "      coefPlace :",coefPlace
                # features 3 : slugs next to other slugs
                for k in range(nSlug):
                    if j-1 in pos[k] or j-2 in pos[k]:
                        coefNextTo = [coefNextTo[i] + parameterList[i]['J'] for i in rlp]
                if toPrint:
                    print "      coefNextTo :",coefNextTo
                v = [v[i]+(coeff[i]+coefNextTo[i])*coefPlace[i]*coefComa[i] for i in rlp]
                if toPrint:
                    print "      v :",v
                pos[nSlug].append(j)
            j+=1
        if len(pos[nSlug])==0:
            v = [v[i] - parameterList[i]['N']*coeff[i] for i in rlp]
        nSlug+=1
    v = [1.0*a/len(tokens) for a in v]
    return v

    