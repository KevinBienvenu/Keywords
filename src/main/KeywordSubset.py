# -*- coding: utf-8 -*-
'''
Created on 10 mai 2016

@author: Kévin Bienvenu
'''

import pandas as pd
import os, time
import IOFunctions
import Constants
import GraphPreprocess

''' subset creation and saving '''

def extractSubset(codeNAF="", n=0, path=None, toPrint=False):
    '''
    function that extract one subset from the database
    by default it extracts the whole content of the database,
    however it's possible to choose a particular codeNAF or a maximal length.
    -- IN:
    codeNAF : string containing the code NAF *optional (str) default= ""
        (-> let to "" if no filter according to the code NAF is wanted)
    n : size of the desired extract *optional (int) default = 0
        (-> let to 0 to extract the whole subset)
    '''
    startTime= time.time()
    if path is None:
        path = Constants.pathCodeNAF
    if codeNAF=="":
        if n==0:
            subsetname = "graphcomplet"
        else:
            subsetname = "graphcomplet_size_"+str(n)
    else:
        if n==0:
            subsetname = "subset_NAF_"+str(codeNAF)
        else:
            subsetname = "subset_NAF_"+str(codeNAF)
            
    os.chdir(Constants.pathAgreg)
    if toPrint:
        print "== Extracting random subset of size",n,"for codeNAF:",codeNAF
    csvfile = pd.read_csv("descriptions.csv", usecols=['codeNaf', 'description'])
    csvfile = csvfile[csvfile.description.notnull()]
    if codeNAF!="":
        csvfile = csvfile[csvfile.codeNaf.str.contains(codeNAF)==True]
    if toPrint:
        print " done"
        print "sampling...",
    if n>0 and len(csvfile)>0:
        csvfile = csvfile.sample(min(n,len(csvfile)))
    if toPrint:
        print " done"
        print "extracting entreprises...",
    entreprises=[[line[0],line[1]] for line in csvfile.values]
    if toPrint:
        print " done:",len(entreprises),"entreprises selected"         
    os.chdir(path)
    if subsetname not in os.listdir("."):
        os.mkdir("./"+subsetname)
    os.chdir("./"+subsetname)
    with open("subset_entreprises.txt","w") as fichier:
        i=0
        for entreprise in entreprises:
            fichier.write(""+str(i)+"_"+str(entreprise[0])+"_")
            fichier.write(entreprise[1])
            fichier.write("\n")
    if toPrint:
        "done in:",
        IOFunctions.printTime(startTime)
    
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
    if "keywords.txt" in os.listdir("."):
        [keywords,dicWordWeight] = IOFunctions.importKeywords(path+"/"+subsetname)
    else:
        [keywords,dicWordWeight] = IOFunctions.importKeywords()
    return (entreprises, keywords, dicWordWeight)

def importTrainedSubset(subsetname, path=Constants.pathSubset):
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
    try:
        with open("trained_entreprises.txt","r") as fichier:
            for line in fichier:
                entreprises.append(line.split("_"))
                entreprises[-1][-1] = entreprises[-1][-1].split("=")[:-1]
    except:
        pass
    [keywords,dicWordWeight] = IOFunctions.importKeywords(path+"/"+subsetname, name ="keywordSuggest.txt")
    return (entreprises, keywords, dicWordWeight)

''' script function '''

def createAllNAFSubset(n=100):
    '''
    script function that creates the subset of size n
    for each codeNAF and save them in the folder preprocessingData/codeNAF
    -- IN
    n : size of the subset for each code NAF
    -- OUT
    the function returns nothing (script function)
    '''
    # step 0 : importing list of codeNAF
    codeNAFs =IOFunctions.importListCodeNAF()
    # step 1 : creating all subsets
    compt = IOFunctions.Compt(codeNAFs, 1, False)
    for codeNAF in codeNAFs:
        compt.updateAndPrint()
        extractSubset(codeNAF, n, path = Constants.pathCodeNAF, toPrint=True)

def computeAllNAFGraph():
    codeNAFs =IOFunctions.importListCodeNAF()
    compt = IOFunctions.Compt(codeNAFs, 1, False)
    for codeNAF in codeNAFs:
        compt.updateAndPrint()
        GraphPreprocess.extractGraphFromSubset("subset_NAF_"+codeNAF, Constants.pathCodeNAF)
        

