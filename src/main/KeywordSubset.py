# -*- coding: utf-8 -*-
'''
Created on 10 mai 2016

@author: Kévin Bienvenu
'''

from operator import itemgetter
import numpy as np
import pandas as pd
import codecs
import os
import IOFunctions
import TextProcessing
import GraphPreprocess
import Constants

path = Constants.path
pathAgreg = Constants.pathAgreg
pathSubset = Constants.pathSubset

def extractRandomSubset(n=10, subsetname="extrait_entreprises"):
    os.chdir(pathAgreg)
    print "== Extracting random subset of size",n
    fileNameVec = ['BRep_Step2_0_1000000.csv', 
               'BRep_Step2_1000000_2000000.csv', 
               'BRep_Step2_2000000_3000000.csv',
              'BRep_Step2_3000000_4000000.csv', 
              'BRep_Step2_4000000_5000000.csv', 
              'BRep_Step2_5000000_6000000.csv',
              'BRep_Step2_6000000_7000000.csv', 
              'BRep_Step2_7000000_8000000.csv', 
              'BRep_Step2_8000000_9176180.csv']
    entreprises = []
    if n<9:
        for i in range(n):
            brepFile = fileNameVec[np.random.randint(0,9)]
            csvfile = pd.read_csv(brepFile, usecols=['siren','codeNaf', 'description'])
            csvfile = csvfile[csvfile.description.notnull()]
            line = csvfile.iloc[np.random.randint(0,len(csvfile))]
            entreprises.append([line[0],line[1],line[2]])
            print str(i+1)+"/"+str(n)
    else:
        ndiv = (int)(n/9)
        j = 0
        for i in range(n):
            if i%ndiv==0:
                brepFile = fileNameVec[j]
                j = min(j+1,8)
                csvfile = pd.read_csv(brepFile, usecols=['siren','codeNaf', 'description'])
                csvfile = csvfile[csvfile.description.notnull()]
                print str(j)+"/"+str(9)   
            line = csvfile.iloc[np.random.randint(0,len(csvfile))]
            entreprises.append([line[0],line[1],line[2]])
    os.chdir(pathSubset)
    i=0
    if subsetname not in os.listdir("."):
        os.mkdir("./"+subsetname)
    os.chdir("./"+subsetname)
    with open("subset_entreprises.txt","w") as fichier:
        for entreprise in entreprises:
            fichier.write(""+str(entreprise[0]))
            fichier.write("_"+str(entreprise[1])+"_")
            fichier.write(entreprise[2])
            fichier.write("\n")
    keywords = createKeywords(entreprises, subsetname)
#     printKeywordsSubset(entreprises = entreprises, keywords = keywords)
    dicWordWeight = GraphPreprocess.generateWordWeight(keywords)
    IOFunctions.saveDict(dicWordWeight, "dicWordWeight.txt")

def extractSubsetFromCodeNAF(codeNAF, n=10):
    subsetname = "extrait_NAF_"+codeNAF
    os.chdir(pathAgreg)
    print "== Extracting random subset of size",n,"for codeNAF:",codeNAF
    fileNameVec = ['BRep_Step2_0_1000000.csv', 
               'BRep_Step2_1000000_2000000.csv', 
               'BRep_Step2_2000000_3000000.csv',
              'BRep_Step2_3000000_4000000.csv', 
              'BRep_Step2_4000000_5000000.csv', 
              'BRep_Step2_5000000_6000000.csv',
              'BRep_Step2_6000000_7000000.csv', 
              'BRep_Step2_7000000_8000000.csv', 
              'BRep_Step2_8000000_9176180.csv']
    entreprises = []
    if n<100:
        for i in range(n):
            l = 0
            while l==0:
                brepFile = fileNameVec[np.random.randint(0,9)]
                csvfile = pd.read_csv(brepFile, usecols=['siren','codeNaf', 'description'])
                csvfile = csvfile[csvfile.description.notnull()]
                csvfile = csvfile[csvfile.codeNaf.str.contains(codeNAF)==True]
                l = len(csvfile)
            line = csvfile.iloc[np.random.randint(0,len(csvfile))]
            entreprises.append([line[0],line[1],line[2]])
            print str(i+1)+"/"+str(n)
    else:
        for brepFile in fileNameVec:
            print ".",
            csvfile = pd.read_csv(brepFile, usecols=['siren','codeNaf', 'description'])
            csvfile = csvfile[csvfile.description.notnull()]
            csvfile = csvfile[csvfile.codeNaf.str.contains(codeNAF)==True]
            i=0
            for line in csvfile.itertuples():
                entreprises.append([line[1],line[2],line[3]]) 
                i+=1
                if i>=int(n/9):
                    break
    print "... done:",len(entreprises),"entreprises selected"         
    os.chdir(Constants.pathCodeNAF)
    i=0
    if subsetname not in os.listdir("."):
        os.mkdir("./"+subsetname)
    os.chdir("./"+subsetname)
    with open("subset_entreprises.txt","w") as fichier:
        for entreprise in entreprises:
            fichier.write(""+str(entreprise[0]))
            fichier.write("_"+str(entreprise[1])+"_")
            fichier.write(entreprise[2])
            fichier.write("\n")
    keywords = createKeywords(entreprises, subsetname)
#     printKeywordsSubset(entreprises = entreprises, keywords = keywords)
    dicWordWeight = GraphPreprocess.generateWordWeight(keywords)
    IOFunctions.saveDict(dicWordWeight, "dicWordWeight.txt")
 
def extractWholeSubsetFromCodeNAF(codeNAF):
    subsetname = "extrait_NAF_"+codeNAF
    os.chdir(pathAgreg)
    print "== Extracting whole subset of codeNAf",codeNAF
    fileNameVec = ['BRep_Step2_0_1000000.csv', 
               'BRep_Step2_1000000_2000000.csv', 
               'BRep_Step2_2000000_3000000.csv',
              'BRep_Step2_3000000_4000000.csv', 
              'BRep_Step2_4000000_5000000.csv', 
              'BRep_Step2_5000000_6000000.csv',
              'BRep_Step2_6000000_7000000.csv', 
              'BRep_Step2_7000000_8000000.csv', 
              'BRep_Step2_8000000_9176180.csv']
    entreprises = []
    nb = 0
    for i in range(9):
        brepFile = fileNameVec[i]
        csvfile = pd.read_csv(brepFile, usecols=['siren','codeNaf', 'description'])
        csvfile = csvfile[csvfile.description.notnull()]
        csvfile = csvfile[csvfile.codeNaf.str.contains(codeNAF)==True]
        for line in csvfile.values:
            entreprises.append([line[0],line[1],line[2]])
        print "= File done..",brepFile
        print "    entreprises found :",str(len(entreprises)-nb)
        nb=len(entreprises)
    print ""
    print "final number of entreprises:",len(entreprises)
    os.chdir(pathSubset)
    i=0
    if subsetname not in os.listdir("."):
        os.mkdir("./"+subsetname)
    os.chdir("./"+subsetname)
    with open("subset_entreprises.txt","w") as fichier:
        for entreprise in entreprises:
            fichier.write(""+str(entreprise[0]))
            fichier.write("_"+str(entreprise[1])+"_")
            fichier.write(entreprise[2])
            fichier.write("\n")
    keywords = createKeywords(entreprises, subsetname)
#     printKeywordsSubset(entreprises = entreprises, keywords = keywords)
    dicWordWeight = GraphPreprocess.generateWordWeight(keywords)
    IOFunctions.saveDict(dicWordWeight, "dicWordWeight.txt")

def extractWholeSubset(subsetname="completeGraph"):
    os.chdir(pathAgreg)
    print "== Extracting whole subset of description"
    fileNameVec = ['BRep_Step2_0_1000000.csv', 
               'BRep_Step2_1000000_2000000.csv', 
               'BRep_Step2_2000000_3000000.csv',
              'BRep_Step2_3000000_4000000.csv', 
              'BRep_Step2_4000000_5000000.csv', 
              'BRep_Step2_5000000_6000000.csv',
              'BRep_Step2_6000000_7000000.csv', 
              'BRep_Step2_7000000_8000000.csv', 
              'BRep_Step2_8000000_9176180.csv']
    entreprises = []
    for brepFile in fileNameVec:
        print "     extracting",brepFile
        csvfile = pd.read_csv(brepFile, usecols=['siren','codeNaf', 'description'])
        csvfile = csvfile[csvfile.description.notnull()] 
        for line in csvfile.itertuples():
            entreprises.append([line[1],line[2],line[3]])
    print "... done"
    os.chdir(pathSubset)
    if subsetname not in os.listdir("."):
        os.mkdir("./"+subsetname)
    os.chdir("./"+subsetname)
    compt = IOFunctions.initProgress(entreprises,1)
    with open("subset_entreprises.txt","w") as fichier:
        for entreprise in entreprises:
            compt = IOFunctions.updateProgress(compt)
            fichier.write(""+str(entreprise[0]))
            fichier.write("_"+str(entreprise[1])+"_")
            fichier.write(entreprise[2])
            fichier.write("\n")
    os.chdir(Constants.path+"/motscles")
    # creating keywords file by copying global keywords file
    lines = []
    with open("keywords.txt","r") as fichier:
        for line in fichier:
            lines.append(line)
    os.chdir(pathSubset+"/"+subsetname)
    with open("keywords.txt","w") as fichier:
        for line in lines:
            fichier.write(line)
    keywords = IOFunctions.importKeywords(".")
    dicWordWeight = GraphPreprocess.generateWordWeight(keywords)
    IOFunctions.saveDict(dicWordWeight, "dicWordWeight.txt")
    
def importSubset(subsetname, path=Constants.pathSubset):
    '''
    function that imports a previously computed subset 
    and puts it into the array entreprises
    -- IN:
    filename : the name of the subset to import (string)
    -- OUT:
    entreprises : array containing info about the entreprise (array) [siren,naf,desc]
    keywords : dic of keywords
    '''
    # importing file
    os.chdir(path)
    if not(subsetname in os.listdir(".")):
        print "non-existing subset"
        return (None,None,None)
    os.chdir("./"+subsetname)
    entreprises = []
    with open("subset_entreprises.txt","r") as fichier:
        for line in fichier:
            entreprises.append(line.split("_"))
    keywords = IOFunctions.importKeywords(path+"/"+subsetname)
    dicWordWeight = IOFunctions.importDict("dicWordWeight.txt")
    return (entreprises, keywords, dicWordWeight)

def analyzeSubset(subsetname):
    # importing subset
    entreprises = importSubset(subsetname)
    # computing stats about codeNAF
    dicNAF1 = {}
    dicNAF2 = {}
    for entreprise in entreprises:
        naf1 = int(entreprise[1][:1])
        if not(naf1 in dicNAF1):
            dicNAF1[naf1] = 0
        dicNAF1[naf1]+=1
        naf2 = int(entreprise[1][:2])
        if not(naf2 in dicNAF2):
            dicNAF2[naf2] = 0
        dicNAF2[naf2]+=1
    l = dicNAF1.items()
    l.sort(key=itemgetter(1),reverse=True)
    l2 = dicNAF2.items()
    l2.sort(key=itemgetter(1),reverse=True)
    print l[:5]
    print l2[:5]

def createKeywords(entreprises,subsetname, path=Constants.pathSubset):
    '''
    function that import the keywords list and remove the unused one
    to create a restrictive list of used keywords
    -- IN:
    entreprises: the array containing the siren, naf and description of entreprises (array [[siren,naf,desc],..])
    -- OUT:
    keywords: dictionary of keywords which values are the tokenized keywords
    '''
    print "== Creating keywords for subset :",subsetname
    print ""
    print "- importing all keywords",
    # importing all keywords
    keywords = IOFunctions.importKeywords()
    print "... done"
    newKeywords = {}
    # extracting descriptions
    descriptions = [tab[2] for tab in entreprises]
    print "- analysing descriptions"
    print "   ",
    compt = IOFunctions.initProgress(descriptions, 10)
    from nltk.corpus import stopwords
    import nltk.stem.snowball
    french_stopwords = set(stopwords.words('french')),
    stem = nltk.stem.snowball.FrenchStemmer()
    for description in descriptions:
        compt = IOFunctions.updateProgress(compt)
        dic = TextProcessing.extractKeywordsFromString(description, keywords, {}, french_stopwords, stem) 
        for key in dic:
            newKeywords[key] = keywords[key]
            del keywords[key]
    print " ... done"
    os.chdir(path+"/"+subsetname)
    with codecs.open("keywords.txt","w","utf-8") as fichier:
        for keyword in newKeywords:
            fichier.write(keyword)
            fichier.write("\n")
    return newKeywords
        
def printKeywordsSubset(subsetname = "", entreprises=None, keywords=None):  
    if entreprises is None or keywords is None:  
        (entreprises, keywords) = importSubset("extrait1")
    for entreprise in entreprises:
        TextProcessing.extractKeywordsFromString(entreprise[2], keywords, True)


