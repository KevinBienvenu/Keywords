# -*- coding: utf-8 -*-
'''
Created on 26 mai 2016

@author: Kévin Bienvenu
'''

from main import TextProcessing, GraphPreprocess, IOFunctions

def suggestKeyword(description, codeNAF):
    '''
    function that takes a description and a codeNAF and returns a list of suggested keywords
    -- IN
    description : string describing the description (string)
    codeNAF : string representing the code NAF (string)
    -- OUT
    keywordsList : array of keywords, in order of importance ([string])
    '''
    ## STEP 0 = Initializing
    [graphNodes, graphEdges] = IOFunctions.importGraph("graphcomplet")
    keywords = IOFunctions.importKeywords()
    dicWordWeight = IOFunctions.importDict("dicWordWeight.txt")
    ## STEP 1 = Extracting only from description
    keywordFromDesc = TextProcessing.extractKeywordsFromString(description, keywords, dicWordWeight, False)
    ## STEP 2 = Extracting only from codeNAF
    
    # merging previous dictionaries
    dicKeywords = {}
    for key in keywordFromDesc:
        dicKeywords[key] = keywordFromDesc[key]
    for key in keywordFromNAF:
        if not(key in dicKeywords):
            dicKeywords[key] = 0
        dicKeywords[key] += keywordFromNAF[key]
            
    
    ## STEP 3 = Extracting from Graph
    keywordFromGraph = extractFromGraph(graphNodes,graphEdges,dicKeywords)
    
    # merging last dice
    for key in keywordFromGraph:
        dicKeywords[key] = keywordFromGraph[key]
        
    ## STEP 4 = Printing / Returning
    IOFunctions.printSortedDic(dicKeywords, 15)
    
def extractFromGraph(graphNodes, graphEdges, dicKeywords):
    '''
    function that extract extra keywords from a graph 
    '''
    