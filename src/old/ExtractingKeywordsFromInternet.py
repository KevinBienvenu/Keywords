# -*- coding: utf-8 -*-
'''
Created on 29 avr. 2016

@author: Kévin Bienvenu
'''


import HTMLParser
import os
import ssl
import string
import urllib

from mmain.Utilsimport tokenizeAndStemmerize
import numpy as np


def getNbResultBing(searchword, toPrint=False):
    while searchword.find(" ")!=-1:
        searchword = searchword[:searchword.find(" ")]+"+"+searchword[searchword.find(" ")+1:]
    while searchword.find(",")!=-1:
        searchword = searchword[:searchword.find(",")]+searchword[searchword.find(",")+1:]
    url = ("https://www.bing.com/search?q="+searchword)
    print url
    s = "-1"
    if toPrint:
        print "requete bing:",searchword,"-",
    try:
        page = urllib.urlopen(url)
        for line in page:
            i = line.find(" results<")
            if i!=-1:
                s = line[i-13:i]
                s = s[s.find(">")+1:]
                while s.find(",")!=-1:
                    s = s[:s.find(",")]+s[s.find(",")+1:]
    except:
        print "erreur"
        pass
    if toPrint:
        print int(s),"résultats"
    return int(s)

def extractNAFDesc(codeNAF):
    page = urllib.urlopen("http://www.insee.fr/fr/methodes/default.asp?page=nomenclatures/naf2008/n5_"+codeNAF+".htm")
    s = page.read().decode("iso8859_1")
    s = HTMLParser().unescape(s)
    toComprend = True
    comprend = []
    comprendpas = []
    pair = 1
    while s.find("<tr>")!=-1:
        if pair%2==0:
            s1 = s[s.find("<tr>")+4:s.find("</tr>")]
            while s1.find("<td>")!=-1:
                if toComprend:
                    comprend.append(s1[s1.find("<td>")+4:s1.find("</td>")])
                else:
                    comprendpas.append(s1[s1.find("<td>")+4:s1.find("</td>")])
                s1 = s1[s1.find("</td>")+6:]
        else:
            s1 = s[s.find("<tr>")+4:s.find("</tr>")]
            toComprend = not("pas" in s1)  
        s = s[s.find("</tr>")+6:]
        pair+=1
    if len(comprend)>0:
        comprend = tokenizeAndStemmerize(comprend[0])
    if len(comprendpas)>0:
        comprendpas = tokenizeAndStemmerize(comprendpas[0])
    return (codeNAF,comprend,comprendpas)
                    

def importKeywordHelloPro():
    keywords = []
    for letter in list(string.ascii_lowercase):
        print "============================="
        print "letter :", letter
        print "============================="
        i = 1
        flag = True
        templen = len(keywords)
        while flag:
            url = "http://www.hellopro.fr/definition/definition-et-glossaire-"+letter+"-"+str(i)+".html"
            page = urllib.urlopen(url)
            for line in page:
                if line[:10]=="<li><b><a ":
                    keywords.append(line[line.find('">')+2:line.find("</a>")])
                    print keywords[-1]
            page.close()
            i+=1
            flag = len(keywords)!=templen
            templen = len(keywords)
    path = "C:/Users/Utilisateur/Documents/GitHub/MotsCles"
    os.chdir(path)
    with open("mots-cles-hellopro.txt","w") as fichier:
        for keyword in keywords:
            fichier.write(keyword+"\n")
    return keywords

def importKeywordHelloProPhoto():
    url = "http://www.hellopro.fr/liste-photo.html"
    page = urllib.urlopen(url)
    flag = False
    for line in page:
        if flag:
            s = line
            break
        if "<div class=\"arbo\">" in line:
            flag = True
    page.close()
    hierarchy = 1
    lastFlag = [""]*10
    path = "C:/Users/Utilisateur/Documents/GitHub/MotsCles"
    os.chdir(path)
    with open("mots-cles-helloprophoto.txt","w") as fichier:
        while s.find(">")!=-1:
            a = s.find(">")
            block = s[:a+1]
            s = s[a+1:]
            if block[1:5]=="<div":
                hierarchy += 1
            if block[1:6]=="</div":
                hierarchy -= 1
            if block[-4:]=="</a>":
                keyword = block[:-4]
                lastFlag[hierarchy] = keyword
                fichier.write(keyword+"_")
                for i in list(reversed(range(1,hierarchy))):
                    fichier.write(lastFlag[i]+"_")
                fichier.write("\n")
                print keyword

def importKeywordSpotAPartner():
    keywords = []
    for i in range(1,100):
        url = "https://spotapartner.com/public_company_profiles?category="+str(i)+"&onmap=false&search="
        context = ssl._create_unverified_context()
        page = urllib.urlopen(url, context=context)
        for line in page:
            if line[0:25]=="<span class='tag_simple'>":
                keywords.append(line[25:].split("|")[0])
    keywords = np.unique(keywords)
    path = "C:/Users/Utilisateur/Documents/GitHub/MotsCles"
    os.chdir(path)
    with open("mots-cles-spotapartner.txt","w") as fichier:
        for keyword in keywords:
            fichier.write(keyword+"\n")
            print keyword
    print len(keywords)
    return keywords
    
        
# keywords = importKeywordHelloPro()
# importKeywordHelloProPhoto()

def importKeywordPagesJaunes():
    keywords = []
    for i in range(1,12):
        url = "http://www.pagesjaunes.fr/activites/"+str(i)
        context = ssl._create_unverified_context()
        page = urllib.urlopen(url, context=context)
        for line in page:
            if line[-10:-1]=="</a></li>":
                keyword = line[line.find(">")+1+line[line.find(">")+1:].find(">")+1:-10]
                print keyword
                keywords.append(keyword)
    path = "C:/Users/Utilisateur/Documents/GitHub/MotsCles"
    os.chdir(path)
    with open("mots-cles-pagesjaunes.txt","w") as fichier:
        for keyword in keywords:
            fichier.write(keyword+"\n")
    print len(keywords)
    
def mergeMotsCles(filenames, exportname):
    print "=== MERGING"
    motscles = []
    motsclesfinaux = []
    for filename in filenames:
        print "   "+filename
        motscles.append([])
        with open("mots-cles-"+filename+".txt","r") as fichier:
            for line in fichier:
                motscles[-1].append(line[:-1].lower())
                motsclesfinaux.append(line[:-1].lower())
    print ""
    print "processing...",
    mc = np.unique(motsclesfinaux)
    motsclesfinaux = []
    mcStem = []
    print "stemmerizing",
    for mot in mc:
        stem = 0
        if not(stem in mcStem):
            mcStem.append(stem)
            motsclesfinaux.append(mot)
        else:
            print "mot en double:",mot
    print "done"
    print ""
    print "done"
    print ""
    with open(exportname, "w") as fichier:
        for motscle in motsclesfinaux:
            fichier.write(motscle+"\n")
    print "merging complete :",len(motsclesfinaux),"mots cles"
            
            
# path = "C:/Users/Utilisateur/Documents/GitHub/MotsCles/motscles/"
# os.chdir(path)
# filenames = ["hellopro","laurent","spotapartner","pagesjaunes"] 
# exportname = "mots-cles.txt" 
# 
# mergeMotsCles(filenames, exportname)

def cleanMotsCles(filename):
    '''
    function that cleans the keywords file according to criterias
    '''
    keywords = []
    with open(filename, "r") as fichier:
        for line in fichier:
            keywords.append(line[:-1])
    newKeywords = []
    for keyword in keywords:
        # criteria : maximum length
        maxlength = 30
        if len(keyword)>maxlength:
            continue
        # criteria : maximum number of words
        nbmaxword = 5
        if len(keyword.split(" "))>nbmaxword:
            continue
        # criteria : first word is 'autre' or 'entreprise'
        word = keyword.split(" ")[0]
        if word=="autre" or word=="autres" or word=="entreprise" or word=="entreprises":
            continue
        # criteria : remove double "mot-mot" and "mot mot"
        flag = False
        for keyword2 in newKeywords:
            if keyword2[:2]==keyword[:2]:
                if keyword.split(" ")==keyword2.split("-") or keyword2.split(" ")==keyword.split("-"):
                    flag=True
                    break 
        if flag:
            print "similar words :",keyword,"et",keyword2
            newKeywords.remove(keyword2)
        # criteria : remove plural if singular is present
        flag = False
        for keyword2 in newKeywords:
            if keyword2[:]==keyword[:-1]:
                flag=True
                break 
        if flag:
            print "plural words :",keyword,"et",keyword2
            continue

        # keyword accepted !
        newKeywords.append(keyword)
    with open(filename,"w") as fichier:
        for keyword in newKeywords:
            fichier.write(keyword)
            fichier.write("\n")
    print len(newKeywords)
    return newKeywords
        
 
