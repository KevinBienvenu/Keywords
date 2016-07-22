# -*- coding: utf-8 -*-
'''
Created on 14 juil. 2016

@author: Kévin Bienvenu
'''

from Tkinter import * 
from operator import itemgetter
import os
import time
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

import IOFunctions, KeywordSelector, GraphLearning, GeneticKeywords03, UtilsConstants

codeNAFs = IOFunctions.importListCodeNAF()

        
class InterfaceGraphique():
    def __init__(self):
        self.fenetreTk = Tk()
        self.fenetre = Label(self.fenetreTk)
        # import des images
        os.chdir(UtilsConstants.path+"/src/main/")
        self.images = {}
        self.images["intro"] = PhotoImage(file="keywords.gif")
        self.images["step01"] = PhotoImage(file="step01.gif")
        self.images["step02"] = PhotoImage(file="step02.gif")
        self.images["step03"] = PhotoImage(file="step03.gif")
        self.images["step04"] = PhotoImage(file="step04.gif")
        self.images["step01param"] = PhotoImage(file="step01param.gif")
        self.images["step03learning"] = PhotoImage(file="step03learning.gif")
        # parametres de la fenetre
        self.fenetreTk.title("Projet Mots-Clés")
        # base de données, keywords et graphe
        self.csvdesc = None
        self.csvclean = None
        self.graph = None
        self.keywords = {}
        self.dicWordWeight = {}
        self.equivalences = {}
        # gestion des ecrans
        self.ecrans = {}
        self.ecrans["EcranIntro"] = EcranIntro
        self.ecrans["EcranStep1"] = EcranStep1
        self.ecrans["EcranStep1Param"] = EcranStep1Param
        self.ecrans["EcranStep2"] = EcranStep2
        self.ecrans["EcranStep3"] = EcranStep3
        self.ecrans["EcranStep3Training"] = EcranStep3Training
        self.ecrans["EcranStep3Visu"] = EcranStep3Visu
        self.ecrans["EcranStep3Learning"] = EcranStep3Learning
        self.ecrans["EcranStep4"] = EcranStep4
        self.ecranCourant = None
        self.changerEcran("EcranIntro")
        w, h = self.fenetreTk.winfo_screenwidth(), self.fenetreTk.winfo_screenheight()
        self.fenetreTk.overrideredirect(1)
        self.fenetreTk.geometry("%dx%d+0+0" % (w, h))
        self.fenetreTk.focus_set() # <-- move focus to this widget
        self.fenetreTk.bind("<Escape>", lambda e: e.widget.quit())
        self.fenetreTk.mainloop()
        
    
    def changerEcran(self, ecran):    
        # on efface l'écran courant
        if not(self.ecranCourant is None):
            self.ecranCourant.hide()
        if ecran!="EcranStep2" and self.csvdesc is None:
            self.chargerBaseDeDonnees()
            self.chargerKeywords()
        if (ecran=="EcranStep3" or ecran=="EcranStep4") and self.graph is None:
            self.chargerGraph()
            self.step03classifier = GraphLearning.Step3Classifier()
        self.ecranCourant = self.ecrans[ecran](self)
        self.ecranCourant.display(padx = 20, pady = 1)
        self.fenetre.pack(fill = BOTH)
    
    def chargerBaseDeDonnees(self):
        os.chdir(UtilsConstants.pathAgreg)
        csvdesc = pd.read_csv("descriptions.csv")
        self.csvdesc=csvdesc
        self.csvclean = self.csvdesc.copy()
    
    def chargerKeywords(self):
        self.keywords, self.dicWordWeight = IOFunctions.importKeywords()
    
    def appliquerCritereBaseDeDonnees(self, criteres):
        test = self.csvdesc.codeNaf.notnull()
        if criteres['codeNAF'][3]:
            test = test & self.csvdesc.codeNaf.str.match(str(criteres['codeNAF'][2]))
        funNbMot = lambda x : len(x.split(" "))
        if criteres['nbWordMin'][3]:
            test = test & (self.csvdesc.description.apply(funNbMot)>=int(criteres['nbWordMin'][2]))
        if criteres['nbWordMax'][3]:
            test = test & (self.csvdesc.description.apply(funNbMot)<=int(criteres['nbWordMax'][2]))
        self.csvclean = self.csvdesc.copy()
        self.csvclean.loc[~test] = None
        self.csvclean.dropna(axis=0,how='any',inplace=True)
      
    def chargerGraph(self):
        os.chdir(UtilsConstants.pathCodeNAF+"/graphcomplet")
        # import nécessaires à l'extraction de description
        self.graph = IOFunctions.importGraph("graphcomplet")  
    
'''
Differents écrans
'''
class Ecran():
    def __init__(self, interface):
        self.interface = interface
        self.elements = []
    def display(self, **options):
        for element in self.elements:
            element.display(**options)  
    def hide(self):
        for element in self.elements:
            element.hide()
        self.elements = []
    def update(self):
#         for element in self.elements:
#             element.update()
#         self.interface.fenetre.pack_forget()
#         self.display()
        pass
            
class EcranIntro(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        # Titre + Image
        self.elements.append(Element(interface.fenetre,texte="Keyword Project Manager"))
        self.elements.append(Element(interface.fenetre,texte="un projet qui envoie du pâté !"))
        self.elements.append(Element(interface.fenetre,image=interface.images["intro"]))
        # boutons
        commands = [lambda a = "EcranStep1" : self.interface.changerEcran(a),
                    lambda a = "EcranStep2" : self.interface.changerEcran(a),
                    lambda a = "EcranStep3" : self.interface.changerEcran(a),
                    lambda a = "EcranStep4" : self.interface.changerEcran(a),
                    self.interface.fenetreTk.destroy
                    ]
        self.elements.append(PaneauBoutons(interface.fenetre, ["Step 1","Step 2","Step 3","Step 4","Quitter"], commands, relief=RAISED))

class EcranStep1(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        # Titre + Image
        self.elements.append(Element(interface.fenetre,texte="Step 01 : Extraction depuis la description"))
        self.elements.append(Element(interface.fenetre,image=interface.images["step01"]))
        # A Gestion des paramètres
        self.elements.append(Element(interface.fenetre,texte="A - Critères de sélection"))        
        self.elements.append(Criteres(interface.fenetre, 
                                      criteres=["codeNAF","nbWordMin","nbWordMax"], 
                                      textes = ["code NAF","nombre de mots minimal","nombre de mots maximal"]))
        self.elements.append(PaneauBoutons(interface.fenetre,["Appliquer"],[lambda x=0:(self.elements[3].functionEntryCritere(),interface.appliquerCritereBaseDeDonnees(self.elements[3].criteres))], relief = RAISED))
        # B Visualiser des exemples
        self.elements.append(Element(interface.fenetre,texte="B - Visualiser les exemples"))        
        self.elements.append(PaneauBoutons(interface.fenetre,["Visualiser"],[lambda ecran="EcranStep1Param":interface.changerEcran(ecran)], relief = RAISED))
        # C Autres
        self.elements.append(Element(interface.fenetre,texte="C - Autres"))        
        self.elements.append(PaneauBoutons(interface.fenetre,["Retour"],[lambda ecran="EcranIntro":interface.changerEcran(ecran)], relief = RAISED))
    
class EcranStep1Param(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        # Titre + Image
        self.parameters = UtilsConstants.parametersStep01
        self.elements.append(Element(interface.fenetre,texte="Step 01 : Analyse des paramètres"))
        self.elements.append(Element(interface.fenetre,image=interface.images["step01param"]))
        # Gestion des parametres
        self.elements.append(Criteres(interface.fenetre, criteres=self.parameters.keys(), textes=self.parameters.keys(), values=self.parameters.values()))
        # Entrer une description
        self.elements.append(ValeurEntree(interface.fenetre,"Description"))
        listcallback = [self.genererDescription, self.testerDescription, self.reinitParameters, UtilsConstants.saveConstants]
        self.elements.append(PaneauBoutons(interface.fenetre,["Générer une description","Tester la description","Reinitialiser les paramètres","Sauvegarder les paramètres"],listcallback))
        # proposition d'un mot clé
        self.elements.append(ValeurEntree(interface.fenetre,"Mot clé ?", taille = 50))
        self.elements.append(Element(interface.fenetre))
        self.scorePropMotCle = Label(self.elements[6].content, text="", width=200,height=2)
        self.scorePropMotCle['text'] = "score :"
        self.scorePropMotCle['text'] += " "*(100-len(self.scorePropMotCle['text']))
        self.scorePropMotCle.pack(fill = X)
        # mots clés
        self.elements.append(MotsCles(interface.fenetre,"Résultats", [], valueskeywords = []))
        # bouton retour
        self.elements.append(PaneauBoutons(interface.fenetre,["Retour"],[lambda ecran="EcranStep1":interface.changerEcran(ecran)], relief = RAISED))
    
    def genererDescription(self):
        for line in self.interface.csvclean.sample(1).itertuples():
            # extracting info
            description = line[3].decode("utf8")
        self.elements[3].l.set(description)
        
    def testerDescription(self):
        self.elements[2].functionEntryCritere()
        dic = KeywordSelector.extractFromDescription(self.elements[3].l.get(), 
                                                     self.interface.keywords, 
                                                     self.interface.dicWordWeight, 
                                                     self.interface.equivalences, 
                                                     parametersStep01 = {critere[1]:float(critere[2]) for critere in self.elements[2].criteres.values()},  
                                                     toPrint=False)
        if len(self.elements[5].l.get())>0:
            self.scorePropMotCle['text'] = "score : "+str(KeywordSelector.getProbKeywordInDescription(self.elements[5].l.get(), 
                                                                                                      UtilsConstants.tokenizeAndStemmerize(self.elements[5].l.get(), False), 
                                                                                                      UtilsConstants.tokenizeAndStemmerize(self.elements[3].l.get(), True), 
                                                                                                      {critere[1]:float(critere[2]) for critere in self.elements[2].criteres.values()}, 
                                                                                                      self.interface.equivalences, 
                                                                                                      self.interface.dicWordWeight, 
                                                                                                      False))
            self.scorePropMotCle['text'] += " "*(100-len(self.scorePropMotCle['text']))
        l = dic.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.elements[7].keywords = [li[0] for li in l]
        self.elements[7].valueskeywords = [li[1] for li in l]
        self.elements[7].update()
        
    def reinitParameters(self):
        UtilsConstants.loadConstants
        for key in UtilsConstants.parametersStep01:
            self.elements[2].criteresButton[self.elements[2].criteres[key][0]][2].delete(0, END)
            self.elements[2].criteresButton[self.elements[2].criteres[key][0]][2].insert(0, UtilsConstants.parametersStep01[key])

    
        
class EcranStep2(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        # Titre + Image
        self.elements.append(Element(interface.fenetre,texte="Step 02 : Création du Graph"))
        self.elements.append(Element(interface.fenetre,image=interface.images["step02"]))
        # Step 0 : Extracting subset for all NAF
        self.elements.append(Element(interface.fenetre))
        l = LabelFrame(self.elements[-1].content, text="SubStep 0 : Echantillonage des codeNAF")
        self.varStep0 = IntVar()
        self.checkbuttonStep0 = Checkbutton(l, text="Effectuer la substep 0", variable = self.varStep0)
        self.checkbuttonStep0.pack()
        self.critereStep0 = Criteres(l, ['n'],['taille des échantillons'],[200])
        self.critereStep0.display()
        self.tempsEstimeStep0 = Label(l, text="", width=200,height=2)
        self.tempsEstimeStep0['text'] = "temps estimé :"
        self.tempsEstimeStep0['text'] += " "*(100-len(self.tempsEstimeStep0['text']))
        self.tempsEstimeStep0.pack()
        l.pack()
        # Step 1 : Computing keyword for all NAF
        self.elements.append(Element(interface.fenetre))
        l = LabelFrame(self.elements[-1].content, text="SubStep 1 : Création des mots-clés des codeNAF")
        self.varStep1 = IntVar()
        self.checkbuttonStep1 = Checkbutton(l, text="Effectuer la substep 1", variable = self.varStep1)
        self.checkbuttonStep1.pack()
        self.tempsEstimeStep1 = Label(l, text="", width=200,height=2)
        self.tempsEstimeStep1['text'] = "temps estimé :"
        self.tempsEstimeStep1['text'] += " "*(100-len(self.tempsEstimeStep1['text']))
        self.tempsEstimeStep1.pack()
        l.pack()
        # Step 2 : Computing whole graph
        self.elements.append(Element(interface.fenetre))
        l = LabelFrame(self.elements[-1].content, text="SubStep 2 : Création du graphe complet")
        self.varStep2 = IntVar()
        self.checkbuttonStep2 = Checkbutton(l, text="Effectuer la substep 2", variable = self.varStep2)
        self.checkbuttonStep2.pack()
        self.critereStep2 = Criteres(l, ['percent'],['effectuer sur quel pourcent des entreprises'],[100])
        self.critereStep2.display()
        self.tempsEstimeStep2 = Label(l, text="", width=200,height=2)
        self.tempsEstimeStep2['text'] = "temps estimé :"
        self.tempsEstimeStep2['text'] += " "*(100-len(self.tempsEstimeStep2['text']))
        self.tempsEstimeStep2.pack()
        l.pack()
        listCallBack = [self.estimationTemps,
                        self.algorithmStep02,
                        lambda ecran = "EcranIntro" :interface.changerEcran(ecran)
                        ]
        self.elements.append(PaneauBoutons(interface.fenetre, ["Estimer le temps","Lancer l'algorithme*","Retour"], listCallBack))
        self.elements.append(Element(interface.fenetre, texte="*Lancer l'algorithme ferme la fenêtre et le reste du processus se déroule dans la console"))
        
    def algorithmStep02(self):
        steps = [self.varStep0.get()==1, self.varStep1.get()==1, self.varStep2.get()==1]
        n = int(self.critereStep0.criteres["n"][2]) if self.critereStep0.criteres["n"][3] else 100
        percent = int(self.critereStep2.criteres["percent"][2]) if self.critereStep2.criteres["percent"][2] else 100
        self.interface.fenetreTk.destroy()
        print n, percent, steps
        KeywordSelector.pipelineGraph(n, percent, steps)
    
    def estimationTemps(self):
        pass

class EcranStep3(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        # Titre + Image
        self.elements.append(Element(interface.fenetre,texte="Step 03 : Extraction depuis le graphe"))
        self.elements.append(Element(interface.fenetre,image=interface.images["step03"]))
        # A Critères
        self.elements.append(Element(interface.fenetre,texte="A - Critères de selection"))        
        self.elements.append(Criteres(interface.fenetre, 
                                      criteres=["codeNAF","nbWordMin","nbWordMax"], 
                                      textes = ["code NAF","nombre de mots minimal","nombre de mots maximal"]))
        # B Visualiser des exemples
        self.elements.append(Element(interface.fenetre,texte="B - Actions possibles"))        
        commands = [
                    lambda ecran="EcranStep3Training":interface.changerEcran(ecran), 
                    lambda ecran="EcranStep3Visu":interface.changerEcran(ecran), 
                    lambda ecran="EcranStep3Learning":interface.changerEcran(ecran)
                    ]
        self.elements.append(PaneauBoutons(interface.fenetre,["Améliorer le training","Visualiser des exemples","Effectuer le learning"],commands, relief = RAISED))
        # C Autres
        self.elements.append(Element(interface.fenetre,texte="C - Autres"))        
        self.elements.append(PaneauBoutons(interface.fenetre,["Retour"],[lambda ecran="EcranIntro":interface.changerEcran(ecran)], relief = RAISED))
    
class EcranStep3Training(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        self.elements.append(Element(interface.fenetre,texte="Step 03 : Ajout de résultats au training"))
        self.elements.append(ValeurEntree(interface.fenetre,"Description"))
        # mots clés
        self.elements.append(MotsCles(interface.fenetre,"Résultats Step 01", [], valueskeywords = []))
        self.elements.append(MotsCles(interface.fenetre,"Proposition Step 03", [], valueskeywords = [], tickable = True, nbMax = 50))
        # boutons
        self.elements.append(PaneauBoutons(interface.fenetre,["Nouvelle description","Valider la description"], [self.genererDescription, self.validerDescription]))
        self.elements.append(PaneauBoutons(interface.fenetre,["Retour"],[lambda ecran="EcranStep3":interface.changerEcran(ecran)], relief = RAISED))
        # notice
        self.elements.append(Element(interface.fenetre, texte="Step 03: A partir uniquement des mots clés sortis à la Step 01, sélectionner des mots-clés similaires. Mieux vaut trop que pas assez, à priori on a pas accès à la description."))
        self.genererDescription()
    
    def genererDescription(self):
        for line in self.interface.csvclean.sample(1).itertuples():
            # extracting info
            self.codeNAF = line[2]
            description = line[3].decode("utf8")
        self.elements[1].l.set(description)
        dicDesc = KeywordSelector.extractFromDescription(self.elements[1].l.get(), 
                                                         self.interface.keywords, 
                                                         self.interface.dicWordWeight, 
                                                         self.interface.equivalences, 
                                                         parametersStep01 = UtilsConstants.parametersStep01,  
                                                         toPrint=False)
        dicGraph = KeywordSelector.extractPotentielNodes(self.interface.graph,
                                                         dicDesc, 50)
        l = dicDesc.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.elements[2].keywords = [li[0] for li in l]
        self.elements[2].valueskeywords = [li[1] for li in l]
        self.elements[2].update()
        self.elements[3].keywords = [self.interface.graph.graphNodes[k].name for k in dicGraph]
        self.elements[3].valueskeywords = None
        self.elements[3].deselectAll()
        self.elements[3].update()
    
    def validerDescription(self):
        print self.elements[3].selectedKeyword
        # graph interpolation step / saving rows in a panda dataframe
        for kw in self.elements[3].keywords:
            self.interface.graph.computeNodeFeatures(kw, {l : 1 for l in self.elements[2].keywords}, self.codeNAF)
            self.interface.graph.getNodeByName(kw).features["Y"] = kw in self.elements[3].selectedKeyword
        dicDF = {ft : [self.interface.graph.getNodeByName(kw).features[ft] 
                       for kw in self.elements[3].keywords] 
                 for ft in UtilsConstants.parametersStep03}
        os.chdir(UtilsConstants.pathCodeNAF+"/../")
        if not("trainingStep3.csv" in os.listdir(".")):
            df = pd.DataFrame(columns=UtilsConstants.parametersStep03)
        else:
            df = pd.DataFrame.from_csv("trainingStep3.csv",sep=";")
        df = pd.concat([df, pd.DataFrame.from_dict(dicDF)], ignore_index=True)
        df.to_csv("trainingStep3.csv",sep=";")
        self.genererDescription()
        
class EcranStep3Visu(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        self.elements.append(Element(interface.fenetre,texte="Step 03 : Visualisation des résultats"))
        self.elements.append(ValeurEntree(interface.fenetre,"Description"))
        # mots clés
        self.elements.append(MotsCles(interface.fenetre,"Résultats Step 01", [], valueskeywords = []))
        self.elements.append(MotsCles(interface.fenetre,"Résultats Step 03", [], valueskeywords = [], nbMax = 20))
        # boutons
        self.elements.append(PaneauBoutons(interface.fenetre,["Visualiser un autre exemple","Retour"], [self.genererDescription,lambda ecran="EcranStep3":interface.changerEcran(ecran)]))
        # notice
        self.elements.append(Element(interface.fenetre, texte="Step 03: Les mots-clés sortis sont à proximité des mots-clés de la step 01 et ont obtenu les meilleures notes selon le modèle appris"))
        self.genererDescription()
        
    def genererDescription(self):
        for line in self.interface.csvclean.sample(1).itertuples():
            # extracting info
            self.codeNAF = line[2]
            description = line[3].decode("utf8")
        self.elements[1].l.set(description)
        dicDesc = KeywordSelector.extractFromDescription(self.elements[1].l.get(), 
                                                         self.interface.keywords, 
                                                         self.interface.dicWordWeight, 
                                                         self.interface.equivalences, 
                                                         parametersStep01 = UtilsConstants.parametersStep01,  
                                                         toPrint=False)
        dicGraph = KeywordSelector.extractFromGraph(self.interface.graph, dicDesc, self.codeNAF, self.interface.step03classifier, n=10)
        l = dicDesc.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.elements[2].keywords = [li[0] for li in l]
        self.elements[2].valueskeywords = [li[1] for li in l]
        self.elements[2].update()
        l = dicGraph.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.elements[3].keywords = [li[0] for li in l]
        self.elements[3].valueskeywords = [li[1] for li in l]
        self.elements[3].update()
        
class EcranStep3Learning(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        # Titre + Image
        self.elements.append(Element(interface.fenetre,texte="Step 03 : Apprentissage du modèle"))
        self.elements.append(Element(interface.fenetre,image=interface.images["step03learning"]))
        # Step 0 : training models
        self.elements.append(Element(interface.fenetre))
        l = LabelFrame(self.elements[-1].content, text="SubStep 0 : Training des modèles")
        #   Modele SVR
        self.varSVR = IntVar()
        self.checkbuttonSVR = Checkbutton(l, text="Support Vector Regressor", variable = self.varSVR)
        self.checkbuttonSVR.pack()
        self.critereSVR = Criteres(l, ['gamma'],['Paramètre gamma :'],[200])
        self.critereSVR.display()
        #   Modele Random Forest
        self.varRF = IntVar()
        self.checkbuttonRF = Checkbutton(l, text="Random Forest Regressor", variable = self.varRF)
        self.checkbuttonRF.pack()
        self.critereRF = Criteres(l, ['n_estimators'],["Nombre d'estimateur :"],[15])
        self.critereRF.display()
        #   Modele Génétique
        self.varGen = IntVar()
        self.checkbuttonGen = Checkbutton(l, text="Genetic Regressor", variable = self.varGen)
        self.checkbuttonGen.pack()
        self.critereGen = Criteres(l, ['nbChromo','nbTotalStep'],["Taille de population :","Nombre d'étapes :"],[100,100])
        self.critereGen.display()
        self.tempsEstime = Label(l, text="", width=200,height=2)
        self.tempsEstime['text'] = "temps estimé :"
        self.tempsEstime['text'] += " "*(100-len(self.tempsEstime['text']))
        self.tempsEstime.pack()
        l.pack()
        listCallBack = [self.estimationTemps,
                        self.algorithmStep03learning
                        ]
        self.elements.append(PaneauBoutons(interface.fenetre, ["Estimer le temps","Lancer le training*"], listCallBack))
        self.elements.append(Element(interface.fenetre, texte="*Lancer l'algorithme ferme la fenêtre et le reste du processus se déroule dans la console"))

        self.elements.append(PaneauBoutons(interface.fenetre, ["Retour"], [lambda ecran = "EcranStep3" :interface.changerEcran(ecran)]))
        
    def algorithmStep03learning(self):
        classifiers = []
        names = []
        if self.varSVR.get():
            self.critereSVR.functionEntryCritere()
            classifiers.append(SVR(kernel="rbf",gamma=float(self.critereSVR.criteres['gamma'][2])))
            names.append("SVR")
        if self.varRF.get():
            self.critereRF.functionEntryCritere()
            classifiers.append(RandomForestRegressor(n_estimators=int(self.critereRF.criteres['n_estimators'][2])))
            names.append("Random Forest")
        if self.varGen.get():
            self.critereGen.functionEntryCritere()
            classifiers.append(GeneticKeywords03.GeneticClassifier(nbChromo=int(self.critereGen.criteres['nbChromo'][2]),nbTotalStep=int(self.critereGen.criteres['nbTotalStep'][2])))
            names.append("Genetic")
        self.interface.fenetreTk.destroy()
        temps = time.time()
        GraphLearning.preprocessClassifiers(classifiers, names, nbPrise=1, toSave=True)
        UtilsConstants.printTime(temps)

    
    def estimationTemps(self):
        pass



class EcranStep4(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        self.elements.append(Element(interface.fenetre,texte="Step 04 : Merging step 01 et 03"))
        self.elements.append(Element(interface.fenetre,image=interface.images["step04"]))
        # critères
        self.elements.append(Element(interface.fenetre,texte="Paramètres de la step 04"))
        criteres = []
        values = []
        for key in UtilsConstants.parametersStep04:
            criteres.append(key)
            values.append(UtilsConstants.parametersStep04[key])
        self.elements.append(Criteres(interface.fenetre, criteres, criteres, values))
        # description
        self.elements.append(ValeurEntree(interface.fenetre,"Description"))
        # mots clés
        self.elements.append(MotsCles(interface.fenetre,"Résultats Step 01", [], valueskeywords = [], nbMax = 20))
        self.elements.append(MotsCles(interface.fenetre,"Résultats Step 03", [], valueskeywords = [], nbMax = 20))
        self.elements.append(MotsCles(interface.fenetre,"Résultats Finaux", [], valueskeywords = [], nbMax = 20))
        # boutons
        listcallbacks = [self.testerDescription,
                         self.genererDescription,
                         self.reinitParameters,
                         UtilsConstants.saveConstants,
                         lambda ecran="EcranStep3":interface.changerEcran(ecran)]
        self.elements.append(PaneauBoutons(interface.fenetre,["Tester la description","Visualiser un autre exemple","Réinitialiser les paramètres","Sauvegarder les paramètres","Retour"], listcallbacks))
        # notice
        self.elements.append(Element(interface.fenetre, texte="Step 04: Mots-clés définitifs obtenus à partir des step 01 et 03 "))
        self.genererDescription()
    
    def testerDescription(self):
        dicDesc = KeywordSelector.extractFromDescription(self.elements[4].l.get(), 
                                                         self.interface.keywords, 
                                                         self.interface.dicWordWeight, 
                                                         self.interface.equivalences, 
                                                         parametersStep01 = UtilsConstants.parametersStep01,  
                                                         toPrint=False)
        dicGraph = KeywordSelector.extractFromGraph(self.interface.graph, dicDesc, self.codeNAF, self.interface.step03classifier, n=10)
        dicMerge = KeywordSelector.mergingKeywords(dicDesc, dicGraph, self.interface.graph)
        l = dicDesc.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.elements[5].keywords = [li[0] for li in l]
        self.elements[5].valueskeywords = [li[1] for li in l]
        self.elements[5].update()
        l = dicGraph.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.elements[6].keywords = [li[0] for li in l]
        self.elements[6].valueskeywords = [li[1] for li in l]
        self.elements[6].update()
        l = dicMerge.items()
        l.sort(key=itemgetter(1),reverse=True)
        self.elements[7].keywords = [li[0] for li in l]
        self.elements[7].valueskeywords = [li[1] for li in l]
        self.elements[7].update()
        
    def genererDescription(self):
        # saving criteres
        self.elements[3].functionEntryCritere()
        for key in UtilsConstants.parametersStep04:
            UtilsConstants.parametersStep04[key] = float(self.elements[3].criteres[key][2])
        # getting new description       
        for line in self.interface.csvclean.sample(1).itertuples():
            # extracting info
            self.codeNAF = line[2]
            description = line[3].decode("utf8")
        self.elements[4].l.set(description)
        self.testerDescription()
    
    def reinitParameters(self):
        UtilsConstants.loadConstants
        for key in UtilsConstants.parametersStep04:
            self.elements[3].criteresButton[self.elements[3].criteres[key][0]][2].delete(0, END)
            self.elements[3].criteresButton[self.elements[3].criteres[key][0]][2].insert(0, UtilsConstants.parametersStep04[key])

        
        
'''
Elements réutilisables dans l'application
'''    
class Element():
    def __init__(self, fenetre, texte = "", image=None, width = 0, height=0):
        self.content = Label(fenetre, text=texte, image = image, width=width, height= height)
    def display(self, **options):
        self.content.pack(**options)  
    def hide(self):
        self.content.pack_forget()
    def update(self):
        pass
     
class PaneauBoutons(Element):
    def __init__(self, fenetre, listBoutons, listCallBack = [], relief=FLAT, ncolumns=2):
        self.content = Frame(fenetre, relief=relief) 
        # liste de boutons
        for i in range(len(listBoutons)/ncolumns+1):
            p = PanedWindow(self.content, orient=HORIZONTAL)
            for j in range(min(ncolumns,len(listBoutons)-i*ncolumns)):
                if len(listCallBack)<len(listBoutons):
                    p.add(Button(p, text=listBoutons[i*ncolumns+j], height = 2, width = 30))
                else:
                    p.add(Button(p, text=listBoutons[i*ncolumns+j], height = 2, width = 30, command= listCallBack[i*ncolumns+j]))
            p.pack()       
               
class Criteres(Element):
    def __init__(self, fenetre, criteres, textes, values=None):
        self.content = Frame(fenetre, relief=RAISED) 
        # critères de recherche
        self.criteres = {}
        for i in range(min(len(criteres),len(textes))):
            self.criteres[criteres[i]] = [i,textes[i],values[i] if not(values is None) else 0,False,IntVar()]  
        self.criteresButton = [0]*len(self.criteres)
        i=0
        j=0
        for critere in self.criteres.values():
            p = PanedWindow(self.content,orient=HORIZONTAL)
            l = StringVar()
            self.criteresButton[critere[0]] = [Checkbutton(p,
                                                            text="", 
                                                            var=critere[4], 
                                                            command=self.fonctionTickBoxCritere),
                                                Label(p,
                                                      text=critere[1]+" "*(25-len(critere[1])),
                                                      justify='left'),
                                                Entry(p,
                                                      width=20,
                                                      textvariable = l),
                                                Label(p,text="")]
            self.criteresButton[critere[0]][2].insert(0,str(critere[2]))
            for item in self.criteresButton[critere[0]]:
                p.add(item)
            p.grid(row=i, column=j, sticky=W)
            j+=1
            if j>3:
                j=0
                i+=1
        self.fonctionTickBoxCritere()
            
    def fonctionTickBoxCritere(self):
        '''
        fonction d'appel des tickbox des critères
        - met le boolean du critère à true ou false selon la tickbox
        '''      
        for critere in self.criteres.values():
            critere[3] = critere[4].get()
            self.criteresButton[critere[0]][1]["state"] = NORMAL if critere[3] else DISABLED
            self.criteresButton[critere[0]][2]["state"] = NORMAL if critere[3] else DISABLED

    def functionEntryCritere(self):
        '''
        fonction d'appel des entry des critères
        - modifie la valeur du critère dès que la valeur de l'entry est changée
        '''
        for critere in self.criteres.values():  
            critere[2] = self.criteresButton[critere[0]][2].get()     
              
class Description(Element):
    def __init__(self, fenetre, description, codeNAF):
        self.content = LabelFrame(fenetre, text="Description")
        Label(self.content, text=description, wrap = 700).pack()
        Label(self.content, text="").pack()
        Label(self.content, text="NAF "+str(codeNAF)+" : "+codeNAFs[codeNAF]).pack()
       
class MotsCles(Element):
    def __init__(self, fenetre, titre, keywords, valueskeywords = None, tickable = False, nbMax = 40):
        self.content = LabelFrame(fenetre,text=titre, height = 500)
        self.nbMax = nbMax
        self.keywords = keywords
        self.valueskeywords = valueskeywords
        self.tickable = tickable
        self.selectedKeyword = []
        ncolumns = 8
        nlignes = self.nbMax/ncolumns
        nlignes += (1 if nlignes*ncolumns<self.nbMax else 0)
        self.checkButtons = [None for _ in range(self.nbMax)]
        for i in range(nlignes):
            l = Frame(self.content)
            for j in range(ncolumns):
                try:
                    text = ""
                    if j+i*ncolumns<len(self.keywords):
                        text = "("+str(j+i*ncolumns)+") "+self.keywords[j+i*ncolumns]
                        if not(self.valueskeywords is None):
                            text += "   : "+str(1.0*int(self.valueskeywords[j+i*ncolumns]*1000)/1000.0)
                    text += " "*(80-len(text))
                    if tickable:
                        command = lambda i=i,j=j:self.tickBox(self.keywords[j+i*ncolumns])
                        self.checkButtons[j+i*ncolumns]=Checkbutton(l,text=text,command=command)
                    else:
                        self.checkButtons[j+i*ncolumns]=Label(l,text=text)
                    self.checkButtons[j+i*ncolumns].pack(side=LEFT)
                except:
                    pass
            l.pack(fill=X)
        
    def update(self):
        ncolumns = 5
        nlignes = self.nbMax/ncolumns
        nlignes += (1 if nlignes*ncolumns<self.nbMax else 0)
        for i in range(nlignes):
            for j in range(ncolumns):
                text = ""
                if j+i*ncolumns<len(self.keywords):
                    text = "("+str(j+i*ncolumns)+") "+self.keywords[j+i*ncolumns]
                    if not(self.valueskeywords is None):
                        text += "   : "+str(1.0*int(self.valueskeywords[j+i*ncolumns]*1000)/1000.0)
                text += " "*(40-len(text))
                self.checkButtons[j+i*ncolumns]['text'] = text

    def display(self, **options):
        self.content.pack(fill=X, **options)
    
    def tickBox(self, keyword):
        if keyword in self.selectedKeyword:
            self.selectedKeyword.remove(keyword)
        else:
            self.selectedKeyword.append(keyword)
    
    def deselectAll(self):
        for cb in self.checkButtons:
            cb.deselect()

class ValeurEntree(Element):
    def __init__(self, fenetre, titre, taille=200):
        self.content = LabelFrame(fenetre, text=titre)
        self.l = StringVar()
        Entry(self.content, width=taille, textvariable = self.l).pack()


