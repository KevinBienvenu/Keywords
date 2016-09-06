# -*- coding: utf-8 -*-
'''
Created on 14 juil. 2016

@author: Kévin Bienvenu
'''

from Tkinter import * 
import codecs
from operator import itemgetter
import os
import time

from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

import IOFunctions, KeywordSelector, GraphLearning, GeneticKeywords03, UtilsConstants, GeneticKeywords01
import pandas as pd


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
        self.images["stepKeywords"] = PhotoImage(file="stepKeywords.gif")
        self.images["step02"] = PhotoImage(file="step02.gif")
        self.images["step03"] = PhotoImage(file="step03.gif")
        self.images["step04"] = PhotoImage(file="step04.gif")
        self.images["pipeline"] = PhotoImage(file="pipeline.gif")
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
        self.ecrans["EcranStep1Training"] = EcranStep1Training
        self.ecrans["EcranStep1Learning"] = EcranStep1Learning
        self.ecrans["EcranStepGraph"] = EcranStepGraph
        self.ecrans["EcranStepKeywords"] = EcranStepKeywords
        self.ecrans["EcranStep3"] = EcranStep3
        self.ecrans["EcranStep3Training"] = EcranStep3Training
        self.ecrans["EcranStep3Visu"] = EcranStep3Visu
        self.ecrans["EcranStep3Learning"] = EcranStep3Learning
        self.ecrans["EcranStep4"] = EcranStep4
        self.ecrans["EcranPipeline"] = EcranPipeline
        self.ecrans["EcranPipelineTraining"] = EcranPipelineTraining
        self.ecrans["EcranPipelineEvaluation"] = EcranPipelineEvaluation
        self.ecranCourant = None
        self.changerEcran("EcranIntro")
        w, h = self.fenetreTk.winfo_screenwidth(), self.fenetreTk.winfo_screenheight()
        self.fenetreTk.geometry("%dx%d+0+0" % (w, h))
        self.fenetreTk.focus_set() # <-- move focus to this widget
        self.fenetreTk.mainloop()
        
    def changerEcran(self, ecran):    
        # on efface l'écran courant
        if not(self.ecranCourant is None):
            self.ecranCourant.hide()
        if ecran!="EcranStepGraph" and self.csvdesc is None:
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
        self.keywords = IOFunctions.importKeywords()
        self.dicWordWeight = UtilsConstants.importDicWordWeight(self.keywords)
        self.equivalences = IOFunctions.importSlugEquivalence()
    
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
        self.elements.append(Element(interface.fenetre,texte="KEYWORD PROJECT MANAGER"))
        self.elements.append(Element(interface.fenetre,texte="un projet qui envoie du pâté !"))
        self.elements.append(Element(interface.fenetre,image=interface.images["intro"]))
        # boutons
        self.elements.append(Element(interface.fenetre,texte="- Etapes de Pré-traitement -"))
        commands = [lambda a = "EcranStepKeywords" : self.interface.changerEcran(a),
                    lambda a = "EcranStepGraph" : self.interface.changerEcran(a)
                    ]
        self.elements.append(PaneauBoutons(interface.fenetre, ["Step: Keywords","Step: Graph"], commands, relief=RAISED))
        self.elements.append(Element(interface.fenetre,texte=""))
        self.elements.append(Element(interface.fenetre,texte="- Etapes principales -"))
        commands = [lambda a = "EcranStep1" : self.interface.changerEcran(a),
                    lambda : None,
                    lambda a = "EcranStep3" : self.interface.changerEcran(a),
                    lambda a = "EcranStep4" : self.interface.changerEcran(a),
                    lambda a = "EcranPipeline" : self.interface.changerEcran(a)
                    ]
        self.elements.append(PaneauBoutons(interface.fenetre, ["Step 1","Step 2","Step 3","Step 4","Pipeline"], commands, relief=RAISED))
        self.elements.append(Element(interface.fenetre,texte=""))
        self.elements.append(PaneauBoutons(interface.fenetre, ["Quitter"],[self.interface.fenetreTk.destroy], relief=RAISED))

class EcranStepKeywords(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        self.elements.append(Element(interface.fenetre,texte="Step Keywords : Gérer la base de mots-clés"))
        self.elements.append(Element(interface.fenetre,image=interface.images["stepKeywords"]))
        self.liste = self.interface.keywords.keys()
        self.keywordsToDelete = []
        self.keywordsToAdd = []
        # critères
        criteres = ["longueur maximale",
                    "longueur minimale",
                    "nombre max de mots",
                    "nombre min de mots",
                    "frequence maximale",
                    "frequence minimale"
                    ]
        self.elements.append(Criteres(interface.fenetre, 
                                      criteres=criteres, 
                                      textes = criteres,
                                      command = lambda *args: self.majListe()))
        # volet de gauche: recherche, liste
        self.elements.append(Element(interface.fenetre))
        
        self.fgauche = Frame(self.elements[-1].content)
        self.motcle = StringVar()
        self.motcle.trace("w", lambda *args : self.majListe())
        f = Frame(self.fgauche)
        Button(f,text="Ajouter le mot clé",command=self.ajoutMotCle).pack(side=RIGHT)
        Entry(f, width=30, textvariable = self.motcle).pack(side=LEFT,padx=5)
        f.pack(pady = 5)
        self.listKeywords = Listbox(self.fgauche,height=20, width = 50,selectmode=SINGLE)
        self.listKeywords.pack_propagate(False)
        self.listKeywords.pack(side = BOTTOM)
        self.listKeywords.bind('<Double-1>', func = lambda *args: self.supprMotCle())
        self.fgauche.pack(fill=Y, side = LEFT)
        # volet de droite : mots clés ajoués et supprimés
        self.fdroite = Frame(self.elements[-1].content)
        self.labelKwAdd = LabelFrame(self.fdroite, text="mots-clés à ajouter",width = 400, height = 150)
        self.labelKwAdd.pack_propagate(False)
        self.labelKwAdd.pack()
        self.labelKwDelete = LabelFrame(self.fdroite, text="mots-clés à supprimer",width = 400, height = 150)
        self.labelKwDelete.pack_propagate(False)
        self.labelKwDelete.pack()
        self.fdroite.pack(fill = Y, side=RIGHT, padx=50)
        # boutons à la fin
        self.elements.append(PaneauBoutons(interface.fenetre, 
                                           ["Effectuer les changements","Retour"],
                                           [self.effectuerChangement,
                                            lambda : interface.changerEcran("EcranIntro")],
                                           relief = RAISED))
        self.majListe()
        
    def majListe(self):
        try:
            self.listKeywords.delete(0, END)
        except:
            return
        liste = self.liste
        liste.sort()
        self.elements[2].functionEntryCritere()
        for item in liste:
            flag = True
            # matching the current keyword
            flag = flag and (len(self.motcle.get())==0 or self.motcle.get() in item)
            # length criteria
            flag = flag and (not self.elements[2].criteres["longueur maximale"][3] 
                             or not self.elements[2].isInt("longueur maximale")
                             or len(item)<int(self.elements[2].criteres["longueur maximale"][2]))
            flag = flag and (not self.elements[2].criteres["longueur minimale"][3] 
                             or not self.elements[2].isInt("longueur minimale")
                             or len(item)>int(self.elements[2].criteres["longueur minimale"][2]))
            # number of words criteria
            flag = flag and (not self.elements[2].criteres["nombre max de mots"][3] 
                             or not self.elements[2].isInt("nombre max de mots")
                             or len(item.split(" "))<int(self.elements[2].criteres["nombre max de mots"][2]))
            flag = flag and (not self.elements[2].criteres["nombre min de mots"][3] 
                             or not self.elements[2].isInt("nombre min de mots")
                             or len(item.split(" "))>int(self.elements[2].criteres["nombre min de mots"][2]))
            # fre maximale
            flag = flag and (not self.elements[2].criteres["frequence maximale"][3] 
                             or not self.elements[2].isInt("frequence maximale")
                             or max([self.interface.dicWordWeight[s] for s in self.interface.keywords[item]])<int(self.elements[2].criteres["frequence maximale"][2]))
            flag = flag and (not self.elements[2].criteres["frequence minimale"][3] 
                             or not self.elements[2].isInt("frequence minimale")
                             or min([self.interface.dicWordWeight[s] for s in self.interface.keywords[item]])>int(self.elements[2].criteres["frequence minimale"][2]))
            if flag:
                self.listKeywords.insert(END, item)
                
        
    def majKeywords(self):
        self.labelKwAdd.pack_forget()
        self.labelKwAdd = LabelFrame(self.fdroite, text="mots-clés à ajouter",width = 400, height = 150)
        self.labelKwAdd.pack_propagate(False)
        self.labelKwAdd.pack()
        for kw in self.keywordsToAdd:
            l = Button(self.labelKwAdd,text = kw,command = lambda kw=kw : self.ajoutMotCle(kw))
            l.pack(side=LEFT,padx = 5)
        self.labelKwDelete.pack_forget()
        self.labelKwDelete = LabelFrame(self.fdroite, text="mots-clés à supprimer",width = 400, height = 150)
        self.labelKwDelete.pack_propagate(False)
        self.labelKwDelete.pack()
        for kw in self.keywordsToDelete:
            l = Button(self.labelKwDelete,text = kw,command = lambda kw=kw : self.supprMotCle(kw))
            l.pack(side=LEFT,padx = 5)
        
        
    
    def ajoutMotCle(self, kw=None):
        if kw is None:
            kw = self.motcle.get()
            self.motcle.set("")
        if not(kw in self.keywordsToAdd):
            self.keywordsToAdd.append(kw)
        else:
            self.keywordsToAdd.remove(kw)
        self.majKeywords()
            

    def supprMotCle(self, kw=None):
        try:
            if kw is None:
                kw = self.listKeywords.get(ACTIVE)
            if kw in self.keywordsToDelete:
                self.keywordsToDelete.remove(kw)
            else:
                self.keywordsToDelete.append(kw)
        except IndexError:
            pass
        self.majKeywords()
    
    def effectuerChangement(self):
        for kw in self.keywordsToAdd:
            self.interface.keywords.add(kw)
        self.elements[-1].buttons[0]['text'] = "Suppression"
        KeywordSelector.deleteKeyword(self.keywordsToDelete, self.elements[-1].buttons[0])
        self.elements[-1].buttons[0]['text'] = "Nettoyage"
        KeywordSelector.cleanKeyword(False,self.elements[-1].buttons[0])
        self.elements[-1].buttons[0]['text'] = "Effectuer le changement"
        self.keywordsToAdd = []
        self.keywordsToDelete = []
        self.interface.keywords = IOFunctions.importKeywords()
        self.interface.dicWordWeight = UtilsConstants.importDicWordWeight(self.interface.keywords)
        self.liste = self.interface.keywords.keys()
        self.motcle.set("")
        self.majKeywords()
        
        
        
        
class EcranStepGraph(Ecran):
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
        self.critereStep0.functionEntryCritere()
        self.critereStep2.functionEntryCritere()
        t0 = str(1)
        t1 = str((280*int(self.critereStep0.criteres["n"][2])+4500)/3600)
        t2 = str(8+(int(self.critereStep2.criteres["percent"][2])-50)/25)
        self.tempsEstimeStep0['text'] = "temps estimé : ~ "+t0+" heure"
        self.tempsEstimeStep1['text'] = "temps estimé : ~ "+t1+" heures"
        self.tempsEstimeStep2['text'] = "temps estimé : ~ "+t2+" heures"
        self.tempsEstimeStep0['text'] += " "*(100-len(self.tempsEstimeStep0['text']))
        self.tempsEstimeStep1['text'] += " "*(100-len(self.tempsEstimeStep1['text']))
        self.tempsEstimeStep2['text'] += " "*(100-len(self.tempsEstimeStep2['text']))
        pass

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
        # B Visualiser des exemples
        self.elements.append(Element(interface.fenetre,texte="B - Visualiser les exemples")) 
        func = lambda ecran="EcranStep1Param", x=0: (self.elements[3].functionEntryCritere(),
                                                     interface.appliquerCritereBaseDeDonnees(self.elements[3].criteres),
                                                     interface.changerEcran(ecran))
        self.elements.append(PaneauBoutons(interface.fenetre,["Visualiser"],[func], relief = RAISED))
        # C Learning
        self.elements.append(Element(interface.fenetre,texte="C - Learning"))
        self.elements.append(PaneauBoutons(interface.fenetre, 
                                           ["Améliorer le training","Lancer le learning"],
                                           [lambda : interface.changerEcran("EcranStep1Training"),
                                            lambda : interface.changerEcran("EcranStep1Learning")],
                                           relief = RAISED))
        # D Autres 
        self.elements.append(Element(interface.fenetre,texte="D - Autres"))        
        self.elements.append(PaneauBoutons(interface.fenetre,["Retour"],[lambda ecran="EcranIntro":interface.changerEcran(ecran)], relief = RAISED))
    
class EcranStep1Param(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        # Titre + Image
        self.parameters = UtilsConstants.parametersStep01
        self.elements.append(Element(interface.fenetre,texte="Step 01 : Analyse des paramètres"))
        self.elements.append(Element(interface.fenetre,image=interface.images["step01param"]))
        # Gestion des parametres
        self.elements.append(Criteres(interface.fenetre, criteres=self.parameters.keys()+["booleanMatchParfait"], textes=self.parameters.keys()+["booleanMatchParfait"], values=self.parameters.values()+[1]))
        # Entrer une description
        self.elements.append(ValeurEntree(interface.fenetre,"Description"))
        listcallback = [self.genererDescription, self.testerDescription, self.reinitParameters, UtilsConstants.saveConstants, self.addKeyword]
        self.elements.append(PaneauBoutons(interface.fenetre,["Générer une description","Tester la description","Reinitialiser les paramètres","Sauvegarder les paramètres","Ajouter le mot clé"],listcallback))
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
                                                     parametersStep01 = {critere[1]:float("0"+critere[2]) for critere in self.elements[2].criteres.values()},  
                                                     booleanMatchParfait = self.elements[2].criteres["booleanMatchParfait"][2] == "1",
                                                     toPrint=False)
        if len(self.elements[5].l.get())>0:
            self.scorePropMotCle['text'] = "score : "+str(KeywordSelector.getProbKeywordInDescription(keyword = self.elements[5].l.get(), 
                                                                                                      stemmedDesc = UtilsConstants.tokenizeAndStemmerize(self.elements[3].l.get(), True), 
                                                                                                      parametersStep01 = {critere[1]:float(critere[2]) for critere in self.elements[2].criteres.values()}, 
                                                                                                      equivalences = self.interface.equivalences, 
                                                                                                      dicWordWeight = self.interface.dicWordWeight))
            self.scorePropMotCle['text'] += " "*(100-len(self.scorePropMotCle['text']))
        else:
            self.scorePropMotCle['text'] = "score :"
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

    def addKeyword(self):
        self.interface.keywords[self.elements[5].l.get()] = UtilsConstants.tokenizeAndStemmerize(self.elements[5].l.get())
        IOFunctions.saveKeywords(self.interface.keywords)
        KeywordSelector.cleanKeyword()
 
class EcranStep1Training(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        self.keywordsDispo = []
        self.keywordsSelect = []
        self.confirmreset = False
        # Titre + Image
        self.elements.append(Element(interface.fenetre,texte="Step 01 : Analyse des paramètres"))
        # Entrer une description
        self.elements.append(Element(interface.fenetre,texte="Description"))
        self.elements.append(ValeurEntree(interface.fenetre,"Description"))
        # liste de mots clés disponibles
        self.elements.append(Element(interface.fenetre))
        self.labelKwDispo = LabelFrame(self.elements[3].content, text="mots-clés disponible",width = 800, height = 100)
        self.labelKwDispo.pack_propagate(False)
        self.labelKwDispo.pack()
        # liste de mots clés sélectionnés
        self.elements.append(Element(interface.fenetre))
        self.labelKwSelect = LabelFrame(self.elements[4].content, text="mots-clés choisis",width = 800, height = 100)
        self.labelKwSelect.pack_propagate(False)
        self.labelKwSelect.pack()
        listcallback = [self.nouvelleDescription, 
                        self.testerDescription,
                        self.validerDescription, 
                        self.resetTraining,
                        lambda ecran = "EcranStep1" : interface.changerEcran(ecran)]
        self.elements.append(PaneauBoutons(interface.fenetre,["Générer description","Tester Description","Valider la description","Effacer le training","Retour"],listcallback))
        self.majKeywords()
        
    def majKeywords(self):
        self.labelKwDispo.pack_forget()
        self.labelKwDispo = LabelFrame(self.elements[3].content, text="mots-clés disponible",width = 800, height = 100)
        self.labelKwDispo.pack_propagate(False)
        self.labelKwDispo.pack()
        for kw in self.keywordsDispo:
            l = Button(self.labelKwDispo,text = kw,command = lambda kw=kw : self.switchKeyword(kw))
            l.pack(side=LEFT,padx = 10)
        self.labelKwSelect.pack_forget()
        self.labelKwSelect = LabelFrame(self.elements[4].content, text="mots-clés choisis",width = 800, height = 100)
        self.labelKwSelect.pack_propagate(False)
        self.labelKwSelect.pack()
        for kw in self.keywordsSelect:
            l = Button(self.labelKwSelect,text = kw,command = lambda kw=kw : self.switchKeyword(kw))
            l.pack(side=LEFT,padx = 10)
        if len(self.keywordsDispo)>0:
            self.elements[-1].buttons[2]['state'] = DISABLED
        else:
            self.elements[-1].buttons[2]['state'] = NORMAL
            
      
    def switchKeyword(self,keyword):
        self.confirmreset = False
        self.elements[-1].buttons[3]['text'] = "Effacer le training"
        if keyword in self.keywordsDispo:
            self.keywordsDispo.remove(keyword)
            self.keywordsSelect.append(keyword)
        elif keyword in self.keywordsSelect:
            self.keywordsSelect.remove(keyword)
            self.keywordsDispo.append(keyword)
        self.majKeywords()
            
    def nouvelleDescription(self):
        flag = False
        while not flag:
            for line in self.interface.csvclean.sample(1).itertuples():
                # extracting info
                description = line[3].decode("utf8")
            self.elements[2].l.set(description)
            self.testerDescription()
            flag = len(self.keywordsDispo)>1
    
    def resetTraining(self):
        if self.confirmreset == True:
            os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
            with codecs.open("trainingStep1.txt","w","utf8") as _:
                pass
            self.elements[-1].buttons[3]['text'] = "Effacer le training"
            self.confirmreset = False
        else:
            self.confirmreset = True
            self.elements[-1].buttons[3]['text'] = "Vraiment ?"
                
    
    def testerDescription(self):
        self.confirmreset = False
        self.elements[-1].buttons[3]['text'] = "Effacer le training"
        self.keywordsDispo = KeywordSelector.extractFromDescription(self.elements[2].l.get(),
                                                                    keywords = self.interface.keywords,
                                                                    dicWordWeight = self.interface.dicWordWeight,
                                                                    equivalences = self.interface.equivalences).keys()
        self.keywordsSelect = []
        self.majKeywords()
    
    def validerDescription(self):
        if len(self.keywordsDispo)>0:
            return
        os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
        with codecs.open("trainingStep1.txt","a","utf8") as fichier:
            fichier.write(self.elements[2].l.get()+"_")
            for kw in self.keywordsSelect:
                fichier.write(kw+"=")
            fichier.write("\r\n")
        self.nouvelleDescription()

class EcranStep1Learning(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        # Titre + Image
        self.elements.append(Element(interface.fenetre,texte="Step 01 : Apprentissage du modèle"))
        self.elements.append(Element(interface.fenetre,image=interface.images["step03learning"]))
        # Step 0 : training models
        self.elements.append(Element(interface.fenetre))
        l = LabelFrame(self.elements[-1].content, text="SubStep 0 : Training des modèles")
        #   Modele Génétique
        self.elements.append(Criteres(l, 
                                      ['nbChromo','nbTotalStep','nbDesc'],
                                      ["Taille de population :","Nombre d'étapes :","Nombre de descriptions"],
                                      [100,100,0]))
        self.tempsEstime = Label(l, text="", width=200,height=2)
        self.tempsEstime['text'] = "temps estimé :"
        self.tempsEstime['text'] += " "*(100-len(self.tempsEstime['text']))
        self.tempsEstime.pack()
        l.pack()
        listCallBack = [self.estimationTemps,
                        self.algorithmStep01learning
                        ]
        self.elements.append(PaneauBoutons(interface.fenetre, ["Estimer le temps","Lancer le training*"], listCallBack))
        self.elements.append(Element(interface.fenetre, texte="*Lancer l'algorithme ferme la fenêtre et le reste du processus se déroule dans la console"))

        self.elements.append(PaneauBoutons(interface.fenetre, ["Retour"], [lambda ecran = "EcranStep1" :interface.changerEcran(ecran)]))
        
    def algorithmStep01learning(self):
        self.elements[3].functionEntryCritere()
        algo = GeneticKeywords01.GeneticKeywords01(nbDesc = int(self.elements[3].criteres["nbDesc"][2]), 
                                                   nbChromo = int(self.elements[3].criteres["nbChromo"][2]), 
                                                   nbTotalStep = int(self.elements[3].criteres["nbTotalStep"][2]))
        temps = time.time()
        self.interface.fenetreTk.destroy()
        algo.run()
        UtilsConstants.printTime(temps)

    
    def estimationTemps(self):
        self.elements[3].functionEntryCritere()
        os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
        with open("trainingStep1.txt","r") as fichier:
            i = 0
            for _ in fichier:
                i+=1
        t = str(int(self.critereGen.criteres["nbTotalStep"][2])*int(self.critereGen.criteres["nbChromo"][2])*i/2000/3600)
        self.tempsEstime['text'] = "temps estimé : ~ "+t+" heures"
        self.tempsEstime['text'] += " "*(100-len(self.tempsEstime['text']))
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
        self.elements.append(PaneauBoutons(interface.fenetre,
                                           ["Nouvelle description",
                                            "Valider la description",
                                            "Effacer le training"], 
                                           [self.genererDescription, 
                                            self.validerDescription, 
                                            self.resetTraining,]))
        self.elements.append(PaneauBoutons(interface.fenetre,["Retour"],[lambda ecran="EcranStep3":interface.changerEcran(ecran)], relief = RAISED))
        # notice
        self.elements.append(Element(interface.fenetre, texte="Step 03: A partir uniquement des mots clés sortis à la Step 01, sélectionner des mots-clés similaires. Mieux vaut trop que pas assez, à priori on a pas accès à la description."))
        self.genererDescription()
    
    def genererDescription(self):
        self.elements[-3].buttons[2]['text'] = "Effacer le training"
        self.confirmreset = False
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
    
    def resetTraining(self):
        if self.confirmreset == True:
            os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
            with codecs.open("trainingStep1.txt","w","utf8") as _:
                pass
            self.elements[-3].buttons[2]['text'] = "Effacer le training"
            self.confirmreset = False
        else:
            self.confirmreset = True
            self.elements[-3].buttons[2]['text'] = "Vraiment ?"
        
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
        self.critereGen.functionEntryCritere()
        os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
        with open("trainingStep3.csv","r") as fichier:
            i = 0
            for _ in fichier:
                i+=1
        t = str(int(self.critereGen.criteres["nbTotalStep"][2])*int(self.critereGen.criteres["nbChromo"][2])*i/2000/3600)
        self.tempsEstime['text'] = "temps estimé : ~ "+t+" heures"
        self.tempsEstime['text'] += " "*(100-len(self.tempsEstime['text']))
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
                         lambda ecran="EcranIntro":interface.changerEcran(ecran)]
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
        dicMerge = KeywordSelector.mergingKeywords(dicDesc, dicGraph, self.interface.graph, self.codeNAF)
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

class EcranPipeline(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        self.elements.append(Element(interface.fenetre,texte="Pipeline complet"))
        self.elements.append(Element(interface.fenetre,image=interface.images["pipeline"]))
        self.elements.append(PaneauBoutons(interface.fenetre, 
                                           ["Améliorer le training","Lancer l'évaluation","Retour"],
                                           [lambda : interface.changerEcran("EcranPipelineTraining"),
                                            lambda : interface.changerEcran("EcranPipelineEvaluation"),
                                            lambda : interface.changerEcran("EcranIntro")],
                                           relief = RAISED))
      
class EcranPipelineTraining(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        self.keywordsSelect = []
        self.confirmreset = False
        # Titre + Image
        self.elements.append(Element(interface.fenetre,texte="Pipeline Training"))
        # Entrer une description
        self.elements.append(Element(interface.fenetre,texte="Description"))
        self.elements.append(ValeurEntree(interface.fenetre,"Description"))
        # liste de mots clés sélectionnés
        self.elements.append(Element(interface.fenetre))
        self.labelKwSelect = LabelFrame(self.elements[3].content, text="mots-clés choisis",width = 800, height = 100)
        self.labelKwSelect.pack_propagate(False)
        self.labelKwSelect.pack()
        self.elements.append(ValeurEntree(interface.fenetre,"Mot clé ?", taille = 50, command = lambda *args: self.majKeywords()))
        self.listKeywords = Listbox(self.elements[4].content,height=10, width = 40,selectmode=SINGLE)
        self.listKeywords.pack_propagate(False)
        self.listKeywords.pack()
        self.listKeywords.bind('<Double-1>', func = self.selKeywordInList)
        listcallback = [self.nouvelleDescription, 
                        self.validerDescription, 
                        self.resetTraining,
                        lambda ecran = "EcranPipeline" : interface.changerEcran(ecran)]
        self.elements.append(PaneauBoutons(interface.fenetre,["Générer description","Valider la description","Effacer le training","Retour"],listcallback))
        self.majKeywords()
        self.nouvelleDescription()
        
    def majKeywords(self):
        self.labelKwSelect.pack_forget()
        self.labelKwSelect = LabelFrame(self.elements[3].content, text="mots-clés choisis",width = 800, height = 100)
        self.labelKwSelect.pack_propagate(False)
        self.labelKwSelect.pack()
        for kw in self.keywordsSelect:
            l = Button(self.labelKwSelect,text = kw,command = lambda kw=kw : self.switchKeyword(kw))
            l.pack(side=LEFT,padx = 10)
        liste = self.interface.keywords.keys()
        liste.sort()
        self.listKeywords.delete(0, END)
        for item in liste:
            if len(self.elements[4].l.get())==0 or self.elements[4].l.get() in item:
                self.listKeywords.insert(END, item)
            
    def selKeywordInList(self, event):
        try:
            self.switchKeyword(self.listKeywords.get(ACTIVE))
        except IndexError:
            pass
      
    def switchKeyword(self,keyword):
        self.confirmreset = False
        self.elements[-1].buttons[2]['text'] = "Effacer le training"
        if keyword in self.keywordsSelect:
            self.keywordsSelect.remove(keyword)
        else:
            self.keywordsSelect.append(keyword)
        self.majKeywords()
            
    def nouvelleDescription(self):
        for line in self.interface.csvclean.sample(1).itertuples():
                # extracting info
            description = line[3].decode("utf8")
            self.codeNAF = line[2]
        self.keywordsSelect = []
        self.elements[4].l.set("")
        self.elements[2].l.set(description)
        
    def resetTraining(self):
        if self.confirmreset == True:
            os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
            with codecs.open("trainingPipeline.txt","w","utf8") as _:
                pass
            self.elements[-1].buttons[2]['text'] = "Effacer le training"
            self.confirmreset = False
        else:
            self.confirmreset = True
            self.elements[-1].buttons[2]['text'] = "Vraiment ?"
                  
    def validerDescription(self):
        os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
        with codecs.open("trainingPipeline.txt","a","utf8") as fichier:
            fichier.write(self.codeNAF+"_"+self.elements[2].l.get()+"_")
            for kw in self.keywordsSelect:
                fichier.write(kw+"=")
            fichier.write("\r\n")
        self.nouvelleDescription()
  
class EcranPipelineEvaluation(Ecran):
    def __init__(self, interface):
        Ecran.__init__(self, interface)
        # Titre + Image
        self.elements.append(Element(interface.fenetre,texte="Pipeline Evaluation"))
        # Description courante
        self.elements.append(Element(interface.fenetre))
        self.descriptionFrame = LabelFrame(self.elements[-1].content,text="Description", height=300, width=1500)
        self.description = Label(self.descriptionFrame, text = "Description :", height = 2, width=160)
        self.note = Label(self.descriptionFrame, text = "Note :", height = 2, width=20)
        self.description.pack_propagate(False)
        self.description.pack(fill=X)
        self.note.pack_propagate(False)
        self.note.pack()
        # mots clés du training
        self.labelKwTraining = LabelFrame(self.descriptionFrame, text="mots-clés du training",width = 800, height = 100)
        self.labelKwTraining.pack_propagate(False)
        self.labelKwTraining.pack(fill=X)
        # mots clés obtenus
        self.labelKwPipeline = LabelFrame(self.descriptionFrame, text="mots-clés obtenus",width = 800, height = 100)
        self.labelKwPipeline.pack_propagate(False)
        self.labelKwPipeline.pack(fill=X)
        self.descriptionFrame.pack_propagate(False)
        self.descriptionFrame.pack(fill=X)
        # liste des descriptions
        self.elements.append(Element(interface.fenetre))
        self.listKeywords = Listbox(self.elements[-1].content,height=10, width = 80,selectmode=SINGLE)
        self.listKeywords.pack_propagate(False)
        self.listKeywords.pack()
        self.listKeywords.bind('<Double-1>', func = self.switchDescription)
        # note finale
        self.elements.append(Element(interface.fenetre))
        self.noteGlobale = Label(self.elements[-1].content, text="Note Globale :", width = 80)
        self.noteGlobale.pack()
        # boutons
        listcallback = [self.launch,
                        lambda ecran = "EcranPipeline" : interface.changerEcran(ecran)]
        self.elements.append(PaneauBoutons(interface.fenetre,["Lancer l'évaluation","Retour"],listcallback))
       
    def switchDescription(self, event):
        i = self.listKeywords.curselection()[0]
        if i<0 or i>len(self.entreprises):
            return
        self.description['text'] = "Description :" + self.entreprises[i][1]
        self.note['text'] = "Note :" + str(self.entreprises[i][-1])
        self.labelKwTraining.pack_forget()
        self.labelKwTraining = LabelFrame(self.descriptionFrame, text="mots-clés du training",width = 1400, height = 100)
        self.labelKwTraining.pack_propagate(False)
        self.labelKwTraining.pack(fill=X)
        for kw in self.entreprises[i][2]:
            l = Label(self.labelKwTraining,text = kw, relief = RAISED if kw in self.entreprises[i][3] else FLAT)
            l.pack(side=LEFT,padx = 5)
        self.labelKwPipeline.pack_forget()
        self.labelKwPipeline = LabelFrame(self.descriptionFrame, text="mots-clés obtenus",width = 1400, height = 100)
        self.labelKwPipeline.pack_propagate(False)
        self.labelKwPipeline.pack(fill=X)
        for kw in self.entreprises[i][3]:
            l = Label(self.labelKwPipeline,text = kw, relief = RAISED if kw in self.entreprises[i][2] else FLAT)
            l.pack(side=LEFT,padx = 5)
           
    def launch(self):    
        # importing entreprises
        self.entreprises = []
        os.chdir(os.path.join(UtilsConstants.path,"preprocessingData"))
        with open("trainingPipeline.txt","r") as fichier:
            for line in fichier:
                self.entreprises.append(line.split("_"))
                self.entreprises[-1][-1] = [UtilsConstants.preprocessString(a) for a in self.entreprises[-1][-1].split("=")[:-1]]
        # computing 
        for entreprise in self.entreprises:
            entreprise.append(KeywordSelector.pipeline([entreprise[0:2]], len(entreprise[1]), False)[0])
            entreprise.append(KeywordSelector.compareKeywords(entreprise[2],entreprise[3]))
            
        self.majDescriptions()
        self.noteGlobale['text']="Note Globale : "+str(1.0*sum([e[4] for e in self.entreprises])/len(self.entreprises))
                                 
    def majDescriptions(self):
        for e in self.entreprises:
            self.listKeywords.insert(END,e[0]+" - "+e[1][:20]+'... - '+ str(e[-1]))
        

'''
Elements réutilisables dans l'application
'''    
class Element():
    def __init__(self, fenetre, texte = "", image=None, width = 0, height=0):
        self.content = Label(fenetre, text=texte, image = image, width=width, height= height)
        self.options = None
    def display(self, **options):
        self.content.pack(**options)  
    def hide(self):
        self.content.pack_forget()
    def update(self):
        pass
     
class PaneauBoutons(Element):
    def __init__(self, fenetre, listBoutons, listCallBack = [], relief=FLAT, ncolumns=2):
        self.options = None
        self.content = Frame(fenetre, relief=relief) 
        self.buttons = []
        # liste de boutons
        for i in range(len(listBoutons)/ncolumns+1):
            p = PanedWindow(self.content, orient=HORIZONTAL)
            for j in range(min(ncolumns,len(listBoutons)-i*ncolumns)):
                if len(listCallBack)<len(listBoutons):
                    self.buttons.append(Button(p, text=listBoutons[i*ncolumns+j], height = 2, width = 30))
                    p.add(self.buttons[-1])
                else:
                    self.buttons.append(Button(p, text=listBoutons[i*ncolumns+j], height = 2, width = 30, command= listCallBack[i*ncolumns+j]))
                    p.add(self.buttons[-1])
            p.pack()       
               
class Criteres(Element):
    def __init__(self, fenetre, criteres, textes, values=None, command=lambda *args: 0):
        self.options = None
        self.command = command
        self.content = Frame(fenetre, relief=RAISED) 
        # critères de recherche
        self.criteres = {}
        for i in range(min(len(criteres),len(textes))):
            self.criteres[criteres[i]] = [i,textes[i],values[i] if not(values is None) else "",False,IntVar()]  
        self.criteresButton = [0]*len(self.criteres)
        self.l = [StringVar() for _ in self.criteres]
        for l in self.l:
            l.trace("w",command)
        i=0
        j=0
        for critere in self.criteres.values():
            p = PanedWindow(self.content,orient=HORIZONTAL)

            self.criteresButton[critere[0]] = [Checkbutton(p,
                                                            text="", 
                                                            var=critere[4], 
                                                            command=self.fonctionTickBoxCritere),
                                                Label(p,
                                                      text=critere[1]+" "*(25-len(critere[1])),
                                                      justify='left'),
                                                Entry(p,
                                                      width=20,
                                                      textvariable = self.l[i*4+j]),
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
        self.command()

    def functionEntryCritere(self):
        '''
        fonction d'appel des entry des critères
        - modifie la valeur du critère dès que la valeur de l'entry est changée
        '''
        for critere in self.criteres.values():  
            critere[2] = self.criteresButton[critere[0]][2].get()     
         
    def isInt(self, critere):
        try:
            int(self.criteres[critere][2])
            return True
        except:
            return False
     
class Description(Element):
    def __init__(self, fenetre, description, codeNAF):
        self.options = None
        self.content = LabelFrame(fenetre, text="Description")
        Label(self.content, text=description, wrap = 700).pack()
        Label(self.content, text="").pack()
        Label(self.content, text="NAF "+str(codeNAF)+" : "+codeNAFs[codeNAF]).pack()
       
class MotsCles(Element):
    def __init__(self, fenetre, titre, keywords, valueskeywords = None, tickable = False, nbMax = 40):
        self.options = None
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
    def __init__(self, fenetre, titre, taille=200, command = lambda *args: 0):
        self.options = None
        self.content = LabelFrame(fenetre, text=titre)
        self.l = StringVar()
        self.l.trace("w", command)
        Entry(self.content, width=taille, textvariable = self.l).pack()


