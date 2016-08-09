# -*- coding: utf-8 -*-
'''
Created on 19 avr. 2016

@author: Kévin Bienvenu
'''

import codecs
import os
import random
import unittest

from nltk.corpus import stopwords

import UtilsConstants, IOFunctions


class TestKeywords(unittest.TestCase):
    '''
    tests for the folders and files integrity
    '''
    def testEnvironVariables(self):
        ''' checking existence of the environ variables '''
        for variable in ["PATH_GOOGLE_DRIVE","PATH_KEYWORDS"]:
            self.assertTrue(os.environ.has_key(variable), "environ variable missing : "+variable)
    
    def testFolderStructure(self):
        ''' checking folder existence '''
        for path in [UtilsConstants.path, 
                     UtilsConstants.pathAgreg, 
                     UtilsConstants.pathClassifiers,
                     UtilsConstants.pathCodeNAF,
                     UtilsConstants.pathConstants,
                     UtilsConstants.pathKeywords]:
            os.chdir(path)
    
    def testMotsClesFolderIntegrity(self):
        ''' checking integrity of folder motscles '''
        os.chdir(UtilsConstants.pathKeywords)
        for filename in ["equivalences.txt",
                         "keywords.txt"]:
            self.assertTrue(filename in os.listdir("."), "missing file "+filename)
            with codecs.open(filename,"r","utf8") as fichier:
                for _ in fichier:
                    pass
    
    def testConstantFilesIntegrity(self):
        os.chdir(UtilsConstants.pathConstants)
        for filename in ["blacklistStep04.txt",
                         "parametersMatchStep01.txt",
                         "parametersStep01.txt",
                         "parametersStep03.txt",
                         "parametersStep04.txt"]:
            self.assertTrue(filename in os.listdir("."), "missing file "+filename)
            with codecs.open(filename,"r","utf8") as fichier:
                for _ in fichier:
                    pass   
    
    def testIsPresentListCodeNAF(self):
        os.chdir(UtilsConstants.pathCodeNAF)
        filename = "listeCodeNAF.txt"
        self.assertTrue(filename in os.listdir("."), "missing file "+filename)
        with codecs.open(filename,"r","utf8") as fichier:
            for _ in fichier:
                pass
        listeCodeNAF = IOFunctions.importListCodeNAF()
        self.assertEqual(len(listeCodeNAF), 732, "error : wrong size of list code NAF file : "+str(len(listeCodeNAF)))         
      
    '''
    testing the UtilsConstant module
    '''
    
    def testImportAndSaveDictFloat(self):
        os.chdir(UtilsConstants.path)
        dic = {}
        for a in ['A','B','C','D']:
            dic[a] = float(1.2 + random.random())
        UtilsConstants.saveDict(dic,"dicTest.txt")
        dic2 = UtilsConstants.importDict("dicTest.txt")
        self.assertEqual(dic,dic2)
        os.remove("dicTest.txt")
        
    def testImportAndSaveDictInt(self):
        os.chdir(UtilsConstants.path)
        dic = {'A' : 12, 'B': 13,'C':14}
        UtilsConstants.saveDict(dic,"dicTest.txt")
        dic2 = UtilsConstants.importDict("dicTest.txt")
        self.assertEqual(dic,dic2)
        os.remove("dicTest.txt")

    def testImportAndSaveDictMisc(self):
        os.chdir(UtilsConstants.path)
        dic = {'A' : 'a', 'B': 'B','C':'a1'}
        UtilsConstants.saveDict(dic,"dicTest.txt")
        dic2 = UtilsConstants.importDict("dicTest.txt")
        self.assertEqual(dic,dic2)        
        os.remove("dicTest.txt")
    
    def testPreprocessString(self):
        srctxt = "test"
        self.assertEqual(UtilsConstants.preprocessString(srctxt),"test")
        srctxt = "testé"
        self.assertEqual(UtilsConstants.preprocessString(srctxt),"teste")
        srctxt = "éèàüôïŒ"
        self.assertEqual(UtilsConstants.preprocessString(srctxt),"eeauoioe")
        srctxt = "AzZa"
        self.assertEqual(UtilsConstants.preprocessString(srctxt),"azza")
        srctxt = u"testunicode"
        self.assertEqual(UtilsConstants.preprocessString(srctxt),"testunicode")
        
    def testTokenStemmer(self):
        srctxt = "boulangerie"
        self.assertEqual(UtilsConstants.tokenizeAndStemmerize(srctxt),[u"boulanger"])
        srctxt = "la boulangerie demeure dans le 16ème arrondissement"
        self.assertEqual(UtilsConstants.tokenizeAndStemmerize(srctxt),[u'boulanger', u'demeur', u'16em', u'arrond'])
        srctxt = "j'allais au devant d'énormes problèmes"
        self.assertEqual(UtilsConstants.tokenizeAndStemmerize(srctxt),[u"j'all", u'dev', u'enorm', u'problem'])
        srctxt = "pourquoi diable faut-il persister dans cette voie périlleuse"
        self.assertEqual(UtilsConstants.tokenizeAndStemmerize(srctxt),[u'pourquoi', u'diabl', u'faut', u'persist', u'cet', u'voi', u'perill'])
        srctxt = "au 12 de la en pour non mais donc"
        self.assertEqual(UtilsConstants.tokenizeAndStemmerize(srctxt),[u'non',u'donc'])
        srctxt = ""
        for word in stopwords.words('french'):
            srctxt += word + " "
        self.assertEqual(UtilsConstants.tokenizeAndStemmerize(srctxt),[])
    
    def testImportDicWordWeight(self):
        dicWordWeight = UtilsConstants.importDicWordWeight()
        for slug in dicWordWeight:
            self.assertTrue(int(dicWordWeight[slug]), "slug frequency not integer")
            self.assertTrue(dicWordWeight[slug]>0, "slug frequency not positive")
    
    '''
    testing IOFunctions
    '''
    def testExtractSubset(self):
        os.chdir(UtilsConstants.pathAgreg)
        self.assertTrue("descriptions.csv" in os.listdir("."))
        self.assertEqual(len(IOFunctions.extractSubset("ABD")),0)
        IOFunctions.extractSubset("0111Z", 10)
    
    def testImportExportSubset(self):
        entreprises = IOFunctions.extractAndSaveSubset("0111Z", 10, UtilsConstants.path, False)
        os.chdir("..")
        self.assertTrue("subset_NAF_0111Z" in os.listdir("."))
        entreprises2 = IOFunctions.importSubset("subset_NAF_0111Z", UtilsConstants.path)
        self.assertEqual(len(entreprises),len(entreprises2))
        self.assertEqual(set([a[1] for a in entreprises]),set([a[1] for a in entreprises2]))
        os.chdir("..")
        os.remove("subset_NAF_0111Z/subset_entreprises.txt")
        os.rmdir("subset_NAF_0111Z")
        
    def testImportSubsetSorted(self):
        IOFunctions.extractAndSaveSubset("", 20, UtilsConstants.path, False)
        os.chdir("..")
        entreprises2 = IOFunctions.importSubset("graphcomplet_size_20", UtilsConstants.path)
        codeNAF = [a[0] for a in entreprises2]
        codeNAF2 = list(codeNAF)
        codeNAF2.sort()
        self.assertEqual(codeNAF, codeNAF2)
        os.chdir("..")
        os.remove("graphcomplet_size_20/subset_entreprises.txt")
        os.rmdir("graphcomplet_size_20")
     
    def testImportKeywords(self):
        keywords = IOFunctions.importKeywords()
        dicWordWeight = UtilsConstants.importDicWordWeight()
        for keyword in keywords:
            self.assertTrue(len(keywords[keyword])>0)
            self.assertEqual(keywords[keyword],UtilsConstants.tokenizeAndStemmerize(keyword))
            for slug in keywords[keyword]:
                self.assertTrue(slug in dicWordWeight)
        
    def testImportExportKeywords(self):
        keywords = IOFunctions.importKeywords()
        IOFunctions.saveKeywords(keywords, UtilsConstants.pathKeywords, "keywords2.txt")
        keywords2 = IOFunctions.importKeywords(filename="keywords2.txt")
        os.remove("keywords2.txt")
        self.assertEqual(keywords, keywords2)
    
    def testSlugEquivalence(self):
        equivalences = IOFunctions.importSlugEquivalence()
        for eq in equivalences:
            for eq1 in equivalences[eq]:
                self.assertTrue(eq1 in equivalences)
    
    def testListCodeNAF(self):
        listeCodeNAF = IOFunctions.importListCodeNAF()
        self.assertEqual(732,len(listeCodeNAF))
        for codeNAF in listeCodeNAF:
            self.assertTrue(len(codeNAF)==5)
            self.assertTrue(len(listeCodeNAF[codeNAF])>0)
        
        
    '''
    testing the keywordSelector module
    '''
    def testCleaningMethod(self):
        keywords = IOFunctions.importKeywords()
        
      
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()