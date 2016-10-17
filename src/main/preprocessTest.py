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
from main import KeywordSelector
import warnings


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
        dicWordWeight = UtilsConstants.importDicWordWeight(IOFunctions.importKeywords())
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
        dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
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
    testing the GraphProcessing module and the graphComplet
    '''
#     def testExistenceAndValidityGraph(self):
#         listeCodeNAF = IOFunctions.importListCodeNAF()
#         keywords = IOFunctions.importKeywords()
#         os.chdir(UtilsConstants.pathCodeNAF)
#         i = 0
#         for codeNAF in listeCodeNAF:
#             i+=1
#             if not("subset_NAF_"+codeNAF in os.listdir(".")):
#                 warnings.warn("please compute the graph preprocessing step before validating this test")
#                 return
#             if i%1==0:
#                 os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"subset_NAF_"+codeNAF))
#                 graph = IOFunctions.importGraph("subset_NAF_"+codeNAF)
#                 n = len(graph.graphNodes)
#                 for node in graph.graphNodes.values():
#                     self.assertTrue(node.id<n)
#                     self.assertTrue(node.name in keywords)
#                     self.assertTrue(len(node.neighbours)>0)
#                     self.assertTrue(codeNAF in node.dicNAF)
#                     self.assertEqual(node.size, sum(node.dicNAF.values()))
#                 for edge in graph.graphEdges:
#                     self.assertTrue(edge[0] in graph.graphNodes)
#                     self.assertTrue(edge[1] in graph.graphNodes)
#                     self.assertTrue(graph.graphEdges[edge].value>0.0)
#         if not("graphcomplet" in os.listdir(".")):
#             warnings.warn("please compute the graph preprocessing step before validating this test")
#             return
#         os.chdir(UtilsConstants.pathCodeNAF)
#         graph = IOFunctions.importGraph("graphcomplet")
#         n = len(graph.graphNodes)
#         for node in graph.graphNodes:
#             self.assertTrue(node.id<n)
#             self.assertTrue(node.name in keywords)
#             self.assertTrue(len(node.neighbours)>0)
#             self.assertTrue(codeNAF in node.dicNAF)
#             self.assertEqual(node.size, sum(node.dicNAF.values()))
#         for edge in graph.graphEdges:
#             self.assertTrue(edge[0] in graph.graphNodes)
#             self.assertTrue(edge[1] in graph.graphNodes)
#             self.assertTrue(graph.graphEdges[edge].value>0.0)
        
    '''
    testing the keywordSelector module
    '''
    def testPipeline(self):
        try:
            os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
            graph = IOFunctions.importGraph("graphcomplet")  
        except:
            return
        # check error cases
        entreprises = [["0111Z"]]
        self.assertEqual({}, KeywordSelector.pipeline(entreprises))
        entreprises = [["Description aléatoire d'une entreprise"]]
        self.assertEqual({}, KeywordSelector.pipeline(entreprises))
        # check equality cases
        entreprises = [["1211"+str(i),"0111Z","Agriculture"+str(i)] for i in range(2)]
        a = KeywordSelector.pipeline(entreprises)
        self.assertEqual(len(a), 2)
        # check nbMot behavior
        keywords = IOFunctions.importKeywords()
        description = ""
        for kw in keywords.keys()[:20]:
            description += kw+" "
        self.assertTrue(len(KeywordSelector.pipeline([["321213","0111Z",description]], 5)["321213"])<=5)
      
    # Step 1
  
    def testDeleteKeywords(self):
        keywords = IOFunctions.importKeywords()
        os.chdir(UtilsConstants.pathKeywords)
        with codecs.open("keywords.txt","a","utf8") as fichier:
            fichier.write("test mot cle\r\n")
        for codeNAF in random.sample(IOFunctions.importListCodeNAF(),10):
            try:
                os.chdir(os.chdir(UtilsConstants.pathCodeNAF,"subset_NAF_"+codeNAF))
                with codecs.open("keywords.txt","a","utf8") as fichier:
                    fichier.write("test mot cle")
            except:
                pass
        KeywordSelector.deleteKeyword(["test mot cle"])
        self.assertEqual(keywords, IOFunctions.importKeywords())
        for codeNAF in random.sample(IOFunctions.importListCodeNAF(),10):
            try:
                os.chdir(os.chdir(UtilsConstants.pathCodeNAF,"subset_NAF_"+codeNAF))
                self.assertTrue("test mot cle" not in IOFunctions.importKeywords(codeNAF = codeNAF))
            except:
                pass
        
    def testPreprocessExtraction(self):
        keywords = ["achat de produits","vente de produit","produits informatiques","informatique"]
        keywords = {kw : UtilsConstants.tokenizeAndStemmerize(kw) for kw in keywords}
        dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
        a = KeywordSelector.preprocessExtraction(UtilsConstants.tokenizeAndStemmerize("achat et vente de produits"), keywords, dicWordWeight, {})
        self.assertEqual(len(a[0]),3)
        for kw in a[0]:
            self.assertEqual(keywords[kw], a[0][kw])
        a = KeywordSelector.preprocessExtraction(UtilsConstants.tokenizeAndStemmerize("achat d'informatique"), keywords, dicWordWeight, {})
        self.assertEqual(len(a[0]),2)
        for kw in a[0]:
            self.assertEqual(keywords[kw], a[0][kw])
        a = KeywordSelector.preprocessExtraction(UtilsConstants.tokenizeAndStemmerize("carottes"), keywords, dicWordWeight, {})
        self.assertEqual(len(a[0]),0)
                  
    def testIsMatch(self):
        slug1 = "test"
        slug2 = "test2"
        self.assertTrue(not KeywordSelector.isMatch(slug1, slug2))
        slug2 = "test"
        self.assertTrue(KeywordSelector.isMatch(slug1, slug2))
        equivalence ={"test":["test","test2"],"test2":["test","test2"]}
        slug2 = "test2"
        self.assertEqual(KeywordSelector.isMatch(slug1, slug2, equivalence),0.9)
        slug2 = "test3"
        self.assertTrue(not KeywordSelector.isMatch(slug1, slug2, equivalence))
#         slug1 = "azertyuiop"
#         slug2 = "azertyuio"
#         self.assertEqual(KeywordSelector.isMatch(slug1, slug2),0.8)
#         slug2 = "azertuiop"
#         self.assertEqual(KeywordSelector.isMatch(slug1, slug2),0.8)
 
    def testExtractFromDescription(self):
        keywords = ["achat de produits","vente de produit","produits informatiques","informatique"]
        keywords = {kw : UtilsConstants.tokenizeAndStemmerize(kw) for kw in keywords}
        dicWordWeight = UtilsConstants.importDicWordWeight(keywords)
        description = ""
        result = KeywordSelector.extractFromDescription(description, keywords, dicWordWeight, {})
        self.assertTrue(isinstance(result,dict))
        self.assertEqual(len(result),0)
        description = "achat de produits"
        result = KeywordSelector.extractFromDescription(description, keywords, dicWordWeight, {})
        self.assertTrue(isinstance(result,dict))
        self.assertEqual(len(result),1)
        self.assertTrue("achat de produits" in result)
        a = result["achat de produits"]
        description = "produits d'achat"
        result = KeywordSelector.extractFromDescription(description, keywords, dicWordWeight, {}, booleanMatchParfait=False)
        self.assertTrue(isinstance(result,dict))
        self.assertEqual(len(result),0)
       
    # step 3
  
    def testExtractFromGraph(self):
        try:
            os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
            graph = IOFunctions.importGraph("graphcomplet")  
        except:
            return
        self.assertEqual(KeywordSelector.extractPotentielNodes(graph, {}), [])
        node = graph.graphNodes[graph.graphNodes.keys()[0]]
        dicKeywords = {node.name:1.0}
        nodes = KeywordSelector.extractPotentielNodes(graph, dicKeywords)
        for potentielNode in nodes:
            self.assertTrue(graph.graphNodes[potentielNode].getSize()>0)
        n = 1
        self.assertTrue(len(KeywordSelector.extractPotentielNodes(graph, dicKeywords, n, n))<2*n)
        self.assertEqual(KeywordSelector.extractFromGraph(graph, {}, {}),{})
        potentielNodes = [graph.graphNodes[i].name for i in KeywordSelector.extractPotentielNodes(graph, dicKeywords)]
        dicKw = KeywordSelector.extractFromGraph(graph, dicKeywords, UtilsConstants.importDicWordWeight(IOFunctions.importKeywords()))
        for kw in dicKw:
            self.assertTrue(kw in potentielNodes)
            self.assertTrue(dicKw[kw]<=1.0 and dicKw[kw]>0.0)
        
    # step 4
    def testMergingKeywords(self):
        try:
            os.chdir(os.path.join(UtilsConstants.pathCodeNAF,"graphcomplet"))
            graph = IOFunctions.importGraph("graphcomplet")  
        except:
            return
        nodes = [graph.graphNodes[i] for i in graph.graphNodes.keys()[:10]]
        keywordsFromDesc = {nodes[i].name:1.0 for i in range(5)}
        keywordsFromGraph = {nodes[5+i].name:1.0 for i in range(5)}
        merg = KeywordSelector.mergingKeywords(keywordsFromDesc, keywordsFromGraph, graph, codeNAF="")
        self.assertTrue(len(merg)<=int(UtilsConstants.parametersStep04["nbMaxMotsCles"]))
        for kw in merg:
            self.assertTrue(kw in keywordsFromDesc or kw in keywordsFromGraph)
            self.assertTrue(merg[kw]>0 and merg[kw]<=1.0)
        keywordsFromDesc = {}
        keywordsFromGraph = {}
        merg = KeywordSelector.mergingKeywords(keywordsFromDesc, keywordsFromGraph, graph, codeNAF="0111Z")
        self.assertTrue(len(merg)<=int(UtilsConstants.parametersStep04["nbMaxMotsCles"]))
        defaultkw = IOFunctions.importDefaultKeywords("0111Z")
        for kw in merg:
            self.assertTrue(kw in defaultkw)
            self.assertTrue(merg[kw]>0 and merg[kw]<=1.0)
        merg = KeywordSelector.mergingKeywords(keywordsFromDesc, keywordsFromGraph, graph, codeNAF="")
        self.assertEqual(len(merg),0)
        
    # comparator algorithm
    def testComparator02(self):
        list1 = ["distribution de programmes"]
        list2 = ["distribution","programme"]
        self.assertTrue(KeywordSelector.compareKeywords02(list1,list2)==1.0)
        list2 = ["distribution"]
        self.assertTrue(KeywordSelector.compareKeywords02(list1,list2)>0.0)
        self.assertTrue(KeywordSelector.compareKeywords02(list1,list2)<1.0)
        list1 = ["distribution de programmes","yaourts aux fruits rouges"]
        list2 = ["distribution","programme","fruit","bleus"]
        self.assertTrue(KeywordSelector.compareKeywords02(list1,list2)>0.0)
        self.assertTrue(KeywordSelector.compareKeywords02(list1,list2)<1.0)
        list1 = ["imprimerie"]
        list2 = ["imprimante"]
        self.assertTrue(KeywordSelector.compareKeywords02(list1,list2)==1.0)
        list1 = ["roger"]
        list2 = ["banane"]
        self.assertTrue(KeywordSelector.compareKeywords02(list1,list2)==0.0)
        
            
        
        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()