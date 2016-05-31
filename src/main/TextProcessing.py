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

exceptList = ['art','btp','vin','pli','cms','son']

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
            if len(token)>3 or token in exceptList:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        stems.append(stem.stem(token[:-1])) 
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
                              french_stopwords,
                              stem, 
                              toPrint=False):
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
    stemmedDesc = nltkprocess(string,keepComa=True, french_stopwords=french_stopwords, stem=stem)
    for keyword in keywords:
        if keyword=='.' or keyword==",":
            continue
        v = getProbKeywordInDescription(keyword, keywords[keyword], stemmedDesc, dicWordWeight)
        if v>0.00:
            dic[keyword] = v
    if toPrint:
        print "Analyzing string:"
        print "   ",string
        print ""
        IOFunctions.printSortedDic(dic, 10)
    return dic
                         
def getProbKeywordInDescription(keyword, tokens, stemmedDesc, dicWordWeight):
    '''
    function that determine the importance of the keyword in the string
    '''
    v=0
    pos = [-1]*len(tokens)
    i=0
    for keywordslug in tokens:
        if keywordslug in dicWordWeight:
            coeff = 0.9+0.1/math.log10(1+float(dicWordWeight[keywordslug]))
        else:
            coeff = 1.0
        j=0
        flagComa = False
        for s in stemmedDesc:
            if len(s)==1:
                coeff*0.7
                flagComa=True
            if keywordslug == s:
                if flagComa==False and j+1<len(stemmedDesc) and len(stemmedDesc[j+1])==1:
                    v+=0.4
                for k in range(i):
                    if pos[k]!=-1 and pos[k]<j and (j-pos[k]>=1 or j-pos[k]<=i-k):
                        v+=1.0
                v+=coeff
                coeff*=0.5
                if pos[i]==-1:
                    pos[i] = j
            coeff*=0.99
            j+=1
        if pos[i]==-1:
            v-=0.5
        i+=1
    if v>0:
        v = 1.0*v/len(tokens)
    return v

    