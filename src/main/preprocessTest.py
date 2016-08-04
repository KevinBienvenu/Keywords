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

from main import UtilsConstants, IOFunctions


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
    
    '''
    testing the keywordSelector module
    '''
    def testCleaningMethod(self):
        keywords = IOFunctions.importKeywords()
        
      
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()