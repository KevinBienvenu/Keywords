# -*- coding: utf-8 -*-
'''
Created on 1 juin 2016

@author: Kévin Bienvenu
'''

from Tkinter import * 
import KeywordTraining
from main import IOFunctions, Constants
import os
import pandas as pd

# attributes

class Interface():
    def __init__(self):
        # On initialise la fenetre
        self.fenetre = Tk()
        self.fenetre.title("Learning Process")
        self.fenetre.minsize(800,600)
        self.fenetre.maxsize(800,600)
        # on charge les photos
        os.chdir(Constants.path+"/src/learning/")
        self.imageKw = PhotoImage(file="keywords.gif")
        
        # on charge la liste des codes NAF
        os.chdir(Constants.pathCodeNAF)
        self.listeCodeNAF = []
        with open("listeCodeNAF.txt","r") as fichier:
            for line in fichier:
                self.listeCodeNAF.append(line[:-1])
    
        # on loade les lignes déjà vues
        os.chdir(Constants.path+"/preprocessingData")
        indexToDrop = []
        with open("processedRows.txt","r") as fichier:
            for line in fichier:
                try:
                    indexToDrop.append(int(line[:-1]))
                except:
                    pass
        # on charge la db
        os.chdir(Constants.pathAgreg)
        csvdesc = pd.read_csv("descriptions.csv")
        csvdesc.drop(indexToDrop,inplace=True)
        self.csvdesc=csvdesc
        
        os.chdir(Constants.pathCodeNAF+"/graphcomplet_size_5000")
        # import nécessaires à l'extraction de description
    #    TODO: à remettre pour la fonction finale
    #     graph = IOFunctions.importGraph("graphcomplet")
        graph = IOFunctions.importGraph("graphcomplet_size_5000")
        [self.keywordSet,self.dicWordWeight] = IOFunctions.importKeywords()
        self.listKeywordComplete = self.keywordSet.values()
        self.indexToDrop=[]
        self.graph=graph
            
        self.currentStep = IntVar()
        self.currentStep.set(1)
            
        self.idSuggestKeybord = -1
        self.idPropList = -1
        self.idPropListYView = 0
        self.criteres = {"codeNAF":[0,"code NAF","",False,IntVar()],
                         "nbWordMin":[1,"nombre de mots minimal",0,False,IntVar()],
                         "nbWordMax":[2,"nombre de mots maximal",0,False,IntVar()]}
        self.criteresButton = []
        self.entryPropKwContent = StringVar()
        self.entryPropKwContent.trace("w", self.updateListKeyword)
        
        self.switchEcranIntro()
        self.bindAll()

        
    ''' Fonctions d'affichage des modules'''
    
    def displayIntro(self):
        '''
        fonction qui affiche le menu d'ouverture du logiciel
        '''
        # titre + image
        self.frIntroMenu = Frame(self.fenetre,padx=20,pady=20)
        Label(self.frIntroMenu, text=" ").pack()
        Label(self.frIntroMenu, text=" ").pack()
        Label(self.frIntroMenu, text="Learning Process Tool").pack()
        Label(self.frIntroMenu, text=" ").pack()
        Label(self.frIntroMenu, image=self.imageKw).pack()
        Label(self.frIntroMenu, text=" ").pack()
        
        # critères de recherche
        self.lfCritere = LabelFrame(self.frIntroMenu, text="Critères")
        i=0
        self.criteresButton = [0]*len(self.criteres)
        for critere in self.criteres.values():
            p = PanedWindow(self.lfCritere,orient=HORIZONTAL)
            command = lambda critere=critere:self.fonctionTickBoxCritere(critere)
            l = StringVar()
            self.criteresButton[critere[0]] = [Checkbutton(p,
                                                            text="", 
                                                            var=critere[4], 
                                                            command=command),
                                                Label(p,
                                                      text=critere[1]+" : ",
                                                      justify='left'),
                                                Entry(p,
                                                      width=20,
                                                      textvariable = l),
                                                Label(p,text="")]
            self.criteresButton[critere[0]][2].insert(0,str(critere[2]))
            self.fonctionTickBoxCritere(critere)
            for item in self.criteresButton[critere[0]]:
                p.add(item)
            p.grid(row=i, column=1, sticky=W)
            i+=1
            
        Button(self.lfCritere,text="Enregistrer",command=self.functionEntryCritere).grid(row=i, column=1)
        self.lfCritere.pack()
        # choix de l'étape
        self.lfChoiceStep = LabelFrame(self.frIntroMenu, text="Choix de l'étape")
        Radiobutton(self.lfChoiceStep, text="Etape 1", variable=self.currentStep, value=1).pack(anchor=W)
        Radiobutton(self.lfChoiceStep, text="Etape 3", variable=self.currentStep, value=3).pack(anchor=W)
        self.lfChoiceStep.pack()
        # liste de boutons
        p = PanedWindow(self.frIntroMenu, orient=HORIZONTAL)
        p.add(Button(p, text="Commencer (Entrée)", command= self.functionToucheEntree))
        p.add(Button(p, text="Quitter (Echap)", command= self.fonctionToucheEchap))
        p.pack(padx = 2, pady=2)
        
        self.frIntroMenu.pack(fill=BOTH)
    def displayCritereCourant(self):
        '''
        fonction qui affiche les critères courants s'il y en a
        '''
        flag = False
        for critere in self.criteres.values():
            flag = flag or critere[3]
        if not flag:
            return
        self.lfCritereCourant = LabelFrame(self.fenetre, text="Critères de Recherche")
        p = PanedWindow(self.lfCritereCourant, orient=HORIZONTAL)
        for critere in self.criteres.values():
            if not critere[3]:
                continue
            p.add(Label(p,text=critere[1]+" : "+str(critere[2])))
        p.pack()
        self.lfCritereCourant.pack(fill=X)        
    def displayDescription(self):
        self.lfDesc = LabelFrame(self.fenetre,text="Description",padx=20,pady=20)
        self.descLabel = Label(self.lfDesc,text=self.desc, wrap = 700)
        self.unraisedCheckButton()
        self.descLabel["text"] = self.desc
        try:
            #TODO: gérer correctement l'affichage des écrans
            self.lfSuggestedKw.pack_forget()
        except:
            pass    
        self.descLabel.pack()
        self.lfDesc.pack(fill = X)  
    def displaySuggestedKeyword(self):                
        self.lfSuggestedKw = LabelFrame(self.fenetre,text="Suggestions",padx=20,pady=20)
        ncolumns = 3
        frac = len(self.keywords)/ncolumns+1
        self.checkButtons = [0]*len(self.keywords)
        for i in range(frac):
            for j in range(ncolumns):
                try:
                    text = "("+str(i+j*frac)+") "+self.keywords[i+j*frac][:]+" "+str(self.origins[i+j*frac])
                    command = lambda i=i,j=j:self.fonctionTickBox(self.keywords[i+j*frac][:])
                    self.checkButtons[i+j*frac]=Checkbutton(self.lfSuggestedKw,text=text,command=command)
                    self.checkButtons[i+j*frac].grid(row=i,column=j,sticky=W)
                    if self.keywords[i+j*frac] in self.vkeywords:
                        self.checkButtons[i+j*frac].toggle()
                except:
                    pass
        self.lfSuggestedKw.pack(fill = X)      
    def displayValidatedKeywords(self):
        # on nettoie si le labelFrame existe déjà
        try:
            self.lfValidatedKw.pack_forget()
        except:
            pass
        # on affiche les keywords validés
        self.lfValidatedKw = LabelFrame(self.fenetre,text="Mots Clés validés",padx=20,pady=20)
        self.refreshValidatedKeywords()
        self.lfValidatedKw.pack(fill = X) 
    def refreshValidatedKeywords(self):
        ''' fonction auxiliaire de refraichissement des mots clés validés '''
        try:
            self.frValidatedKwContent.pack_forget()
        except:
            pass
        self.frValidatedKwContent = Frame(self.lfValidatedKw)
        if len(self.vkeywords)==0:
            Label(self.frValidatedKwContent,text="Aucun mot clé sélectionné").pack()
        else:
            ncolumns = 5
            frac = len(self.vkeywords)/ncolumns+1
            for i in range(frac):
                p = PanedWindow(self.frValidatedKwContent,orient=HORIZONTAL)
                for j in range(ncolumns):
                    try:
                        text = self.vkeywords[i+j*frac][:]
                        p.add(Label(p,text=text,relief=RAISED))
                    except:
                        pass 
                p.pack()
        self.frValidatedKwContent.pack(fill=X)
    def displayPropositionKeyword(self):
        '''
        fonction qui prépare l'écran de proposition
        les mots-clés suggérés sont effacés (temporairement)
        et le nouvel écran est mis en place
        '''         
        self.lfSuggestedKw.pack_forget()
        self.lfValidatedKw.pack_forget()
        self.lfProposedKw = LabelFrame(self.fenetre,text="Proposition de mot-clé",padx=20,pady=20)
        self.entryProp = Entry(self.lfProposedKw, textvariable=self.entryPropKwContent, width=200)
        self.entryProp.pack()
        self.listProp = Listbox(self.lfProposedKw)
        self.listPropNewKw = False
        self.listProp.pack(fill=X)
        self.listProp.bind("<<ListboxSelect>>",self.functionToucheEntree)
        for keyword in self.listKeywordComplete:
            self.listProp.insert(END,keyword)
        self.lfProposedKw.pack()
        self.entryProp.focus()  
    def displayButtonBar(self):
        '''
        function printing the button bar at the bottom of the page
        '''
        # on affiche la barre avec les boutons
        self.frButtonBar = Frame(self.fenetre)
        p = PanedWindow(self.frButtonBar, orient=HORIZONTAL)
        self.boutonSignaler = Button(p,text="(S)ignaler", command = self.fonctionToucheS)
        self.boutonProposer = Button(p,text="Proposer (Entrée)", command = self.fonctionToucheP)
        self.boutonValider = Button(p,text="Valider (Espace)", command = self.functionToucheEspace)
        self.boutonQuitter = Button(p,text="Quitter (Echap)", command = self.fonctionToucheEchap)
        p.add(self.boutonSignaler)
        p.add(self.boutonProposer)
        p.add(self.boutonValider)
        p.add(self.boutonQuitter)
        p.pack(side= BOTTOM, padx=2,pady=2)
        self.frButtonBar.pack()
      
    def hideIntro(self):
        try:
            self.frIntroMenu.pack_forget()
        except:
            pass
    def hideCritereCourant(self):
        try:
            self.lfCritereCourant.pack_forget()
        except:
            pass
    def hideDescription(self):
        try:
            self.lfDesc.pack_forget()
        except:
            pass
    def hideSuggestedKeyword(self):
        try:
            self.lfSuggestedKw.pack_forget()
        except:
            pass
    def hideValidatedKeywords(self):
        try:
            self.lfValidatedKw.pack_forget()
        except:
            pass
    def hidePropositionKeyword(self):
        try:
            self.lfProposedKw.pack_forget()
        except:
            pass
    def hideButtonBar(self):
        try:
            self.frButtonBar.pack_forget()
        except:
            pass

    def hideAll(self):
        self.hideButtonBar()
        self.hideCritereCourant()
        self.hideDescription()
        self.hideIntro()
        self.hidePropositionKeyword()
        self.hideSuggestedKeyword()
        self.hideValidatedKeywords()

    ''' Fonctions de switch entre écrans '''
        
    def switchEcranIntro(self):
        ''' va vers l'écran d'intro '''
        self.ecranCourant = "Intro"
        self.hideAll()
        self.displayIntro()
    
    def switchEcranDesc(self):
        ''' va vers l'écran de desc'''
        self.ecranCourant = "Desc"
        self.hideAll()
        self.displayCritereCourant()
        self.displayDescription()   
        self.displaySuggestedKeyword()
        self.displayValidatedKeywords() 
        self.displayButtonBar()
    
    def switchEcranProp(self):
        ''' va vers l'écran de prop'''
        self.ecranCourant = "Prop"
        self.hideAll()
        # on met à jour les variables
        self.listPropNewKw = False
        self.entryPropKwContent.set("")
        
        self.displayCritereCourant()
        self.displayDescription()   
        self.displayPropositionKeyword()
       
    ''' Fonctions de callback sur touches '''     
        
    def functionToucheEntree(self,event=None):
        '''
        fonction d'appel du bouton entrée
        '''
        # ECRAN INTRO
        if self.ecranCourant=="Intro":
            # on va vers l'écran desc
            try:
                self.csvclean
            except:
                KeywordTraining.getCsvWithCriteres(self)

            KeywordTraining.pickNewRow(self)
            self.switchEcranDesc()
        
        # ECRAN DESCRIPTION
        elif self.ecranCourant=="Desc":
            # si un mot clé est proposé par les touches numériques,
            # on le valide
            if self.idSuggestKeybord > -1 and self.idSuggestKeybord < len(self.keywords):
                self.checkButtons[self.idSuggestKeybord].invoke()
                self.unraisedCheckButton() 
                self.lastChange = self.keywords[self.idSuggestKeybord]
            # sinon on ouvre l'écran proposer 
            else:
                self.switchEcranProp()
                
        # ECRAN PROPOSITION
        elif self.ecranCourant=="Prop":
            # si la proposition est vide on revient à l'écran desc
            if len(self.entryPropKwContent.get())==0 and len(self.listProp.curselection())==0:
                self.switchEcranDesc()
                return
            # si le mot clé n'est pas nouveau (ie. il fait partie des propositions)
            # on le récupère via la liste
            if self.listPropNewKw == False:
                w = self.listProp
                index = int(w.curselection()[0])
                keyword = w.get(index)
            # sinon il est nouveau, on le récupère via le contenu de l'entry
            else:
                keyword = self.entryPropKwContent.get()
            self.listProp.select_set(0)
            # on ajoute le keyword
            if not(keyword in self.keywords):
                self.keywords.append(keyword)
                self.origins.append([4])
            # on va vers l'écran desc
            self.switchEcranDesc()
            # on le valide
            for i in range(len(self.keywords)):
                if keyword==self.keywords[i]:
                    self.checkButtons[i].invoke()
            self.lastChange = keyword
            
    def functionToucheEspace(self, event=None):
        '''
        fonction d'appel du bouton espace
        '''
        if self.ecranCourant=="Desc":
            if len(self.vkeywords)>0:
                self.boutonValider.config(relief=SUNKEN)
                self.boutonValider.after(200, lambda: self.boutonValider.config(relief=RAISED))
                KeywordTraining.saveRow(self)
                KeywordTraining.pickNewRow(self)
                self.switchEcranDesc()
   
    def fonctionToucheEchap(self,event=None):
        '''
        fonction d'appel du bouton quitter
        - ferme la fenetre
        '''
        if self.ecranCourant=="Intro":
            self.fenetre.destroy()
        elif self.ecranCourant=="Desc":
            self.switchEcranIntro()
        elif self.ecranCourant=="Prop":
            self.listProp.select_set(0)
            self.switchEcranDesc()
    
    def fonctionToucheS(self,event=None):
        '''
        fonction d'appel du bouton signaler
        - enregistre la ligne dans le fichier signaler
        - appelle une nouvelle ligne
        '''
        if self.ecranCourant=="Desc":
            self.boutonSignaler.config(relief=SUNKEN)
            self.boutonSignaler.after(200, lambda: self.boutonSignaler.config(relief=RAISED))
            KeywordTraining.signaleRow(self)
            KeywordTraining.pickNewRow(self)
            self.switchEcranDesc()
        
    def fonctionToucheP(self,event=None):
        '''
        fonction d'appel du bouton proposer
        - ouvre une nouvelle fenetre proposer
        '''    
        if self.ecranCourant=="Desc":
            self.boutonProposer.config(relief=SUNKEN)
            self.boutonProposer.after(200, lambda: self.boutonProposer.config(relief=RAISED))
            self.switchEcranProp()
  
    def fonctionToucheNumerique(self, event):
        if event.char in [str(a) for a in range(10)]:
            if self.ecranCourant=="Desc":
                num = int(event.char)
                if self.idSuggestKeybord==-1:
                    self.idSuggestKeybord = 0
                else:
                    self.checkButtons[self.idSuggestKeybord]["relief"] = FLAT
                self.idSuggestKeybord *= 10
                self.idSuggestKeybord += num
                try:
                    self.checkButtons[self.idSuggestKeybord]["relief"] = RAISED
                except:
                    self.idSuggestKeybord = num
                    try:
                        self.checkButtons[self.idSuggestKeybord]["relief"] = RAISED
                    except:
                        self.idSuggestKeybord = -1
                
    def fonctionToucheBas(self, event):
        '''
        fonction d'appel de la touche bas lors des propositions
        - sélectionne l'élément suivant dans la liste de proposition
        '''
        if self.ecranCourant=="Prop":
            self.idPropList+=1
            if self.idPropList>=self.listProp.size():
                self.idPropList=0
            self.listProp.selection_clear(0,END)
            self.listProp.select_set(self.idPropList)
            if abs(self.idPropList-self.idPropListYView)>7:
                self.idPropListYView=self.idPropList-7
            self.listProp.yview(self.idPropListYView)
     
    def fonctionToucheHaut(self, event):
        '''
        fonction d'appel de la touche bas lors des propositions
        - sélectionne l'élément suivant dans la liste de proposition
        '''
        if self.ecranCourant=="Prop":
            self.idPropList-=1
            if self.idPropList<0:
                self.idPropList=self.listProp.size()-1
            self.listProp.selection_clear(0,END)
            self.listProp.select_set(self.idPropList)
            if abs(self.idPropList-self.idPropListYView)<3 or abs(self.idPropList-self.idPropListYView)>7:
                self.idPropListYView=self.idPropList-3
            self.listProp.yview(self.idPropListYView)
    
    def fonctionToucheBack(self, event):
        '''
        fonction d'appel de la touche retour arrière
        '''
        if self.ecranCourant=="Desc":
            if self.lastChange != "":
                for i in range(len(self.keywords)):
                    if self.lastChange==self.keywords[i]:
                        self.checkButtons[i].invoke()
     
    ''' Fonctions de callback sur autres items ''' 
      
    def fonctionTickBox(self, keyword):
        '''
        fonction d'appel des tickbox de suggestions de keyword
        '''
        self.unraisedCheckButton()
        if keyword in self.vkeywords:
            self.vkeywords.remove(keyword)
        else:
            self.vkeywords.append(keyword)
        self.refreshValidatedKeywords()
    
    def fonctionTickBoxCritere(self, critere):
        '''
        fonction d'appel des tickbox des critères
        - met le boolean du critère à true ou false selon la tickbox
        '''      
        critere[3] = critere[4].get()
        self.criteresButton[critere[0]][1]["state"] = NORMAL if critere[3] else DISABLED
        self.criteresButton[critere[0]][2]["state"] = NORMAL if critere[3] else DISABLED
    
    def fonctionEntryCritereUpdate(self, *args):
        ''' '''
        for critere in self.criteres.values():
            text = ""
            print critere[4].get()
            if critere[4].get()==0:
                text = ""
            else:
                if critere[1]=="code NAF":
                    if critere[4] in self.listeCodeNAF:
                        text = "code NAF correct"
                    else:
                        text = "code NAF incorrect"
                elif critere[1]=="nombre de mots minimal" or critere[1]=="nombre de mots maximal":
                    try:
                        int(critere[4])
                        text = ""
                    except:
                        text = "format incorrect"
            print self.criteresButton[critere[0]]
            self.criteresButton[critere[0]][3]["text"] = text
              
    def functionEntryCritere(self):
        '''
        fonction d'appel des entry des critères
        - modifie la valeur du critère dès que la valeur de l'entry est changée
        '''
        for critere in self.criteres.values():  
            critere[2] = self.criteresButton[critere[0]][2].get()
        KeywordTraining.getCsvWithCriteres(self)
              
    ''' Fonctions auxiliaires '''
        
    def unraisedCheckButton(self):
        if self.idSuggestKeybord!=-1:
            self.checkButtons[self.idSuggestKeybord]["relief"] = FLAT
        self.idSuggestKeybord=-1
    
    def bindAll(self):
        self.fenetre.bind("<space>", self.functionToucheEspace)
        self.fenetre.bind("<Escape>", self.fonctionToucheEchap)
        self.fenetre.bind("<s>", self.fonctionToucheS)
        self.fenetre.bind("<p>", self.fonctionToucheP)
        self.fenetre.bind("<Key>", self.fonctionToucheNumerique)
        self.fenetre.bind("<Return>", self.functionToucheEntree)
        self.fenetre.bind("<Up>", self.fonctionToucheHaut)
        self.fenetre.bind("<Down>", self.fonctionToucheBas)
        self.fenetre.bind("<BackSpace>", self.fonctionToucheBack)
    
    def unbindAll(self):
        self.fenetre.unbind("<space>")
        self.fenetre.unbind("<Escape>")
        self.fenetre.unbind("<s>")
        self.fenetre.unbind("<p>")
        self.fenetre.unbind("<Key>")
        self.fenetre.unbind("<Return>")
        self.fenetre.unbind("<Up>")
        self.fenetre.unbind("<Down>")
       
    def updateListKeyword(self, *args):
        self.listPropNewKw = False
        self.listKeyword = []
        try:
            self.listProp.delete(0,END)
            for keyword in self.listKeywordComplete:
                if self.entryProp.get() in keyword:
                    self.listProp.insert(END,keyword)
            # cas ou la liste est vide, on propose d'ajouter le mot clé
            if self.listProp.size()==0:
                self.listProp.insert(0, "ajouter : "+self.entryProp.get())
                self.listPropNewKw = True
        except:
            pass

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        