# -*- coding: utf-8 -*-
'''
Created on 27 avr. 2016

@author: Kévin Bienvenu
'''
from email import Utils
import UtilsConstants


''' functions of graph handling '''


class GraphKeyword():
    '''
     === Graph Description ===
     Graph structure containing all information about nodes and edges.
     
    - graphNodes V : dic{id (int): node (Node)]}
    
    - graphEdges E : dic{(id1 (int), id2 (int)), edge (Edge)}
    
    - dicIdNodes : dic{name (str) : id (int)}
    '''
    
    ''' construction and import/export'''
    def __init__(self, name="untitled_graph"):
        '''
        intialization of an empty graph
        '''
        try:
            self.name = str(name)
        except:
            self.name = "untitled_graph"
        self.graphNodes = {}
        self.graphEdges = {}
        self.dicIdNodes = {}
    
    def addEdgeValues(self, id0, id1, value):
        '''
        function that add the value 'value' to the edge between the nodes 1 and 2
        -- IN
        id0 : id of the first node (int)
        id1 : id of the second node (int)
        value : the value to add to the edge (float)
        -- OUT
        returns nothing
        '''
        try:
            i = int(id0)
            j = int(id1)
            if i>j:
                (i,j) = (j,i)
            v = float(value)
        except:
            print "failure in adding new edge :"
            print "id0", id0
            print "id1", id1
            print "value",value
            return
        if not((i,j) in self.graphEdges):
            self.graphEdges[(i,j)] = Edge(i,j)
            self.graphNodes[i].neighbours[self.getNode(j)] = 0
            self.graphNodes[j].neighbours[self.getNode(i)] = 0
        self.graphEdges[(i,j)].value += v
        self.graphNodes[i].neighbours[self.getNode(j)] += v
        self.graphNodes[j].neighbours[self.getNode(i)] += v
        self.graphEdges[(i,j)].nbOccurence += 1
    
    def addNodeValues(self, name, codeNAF="", valueNAF=0, genericity = 0):
        '''
        function that change the node 'name'
        if the node doesn't exist 
            it is created
        if the codeNAF is different than ""
            if the node doesn't have a value for codeNAF, 
                it is set to zero
            add the value 'valueNAF' to the codeNAF
        if the genericity is different than 0
            the node get this genericity
        -- IN
        name : name of the node to change (str)
        codeNAF : name of the codeNAF to change (str) default = ""
        value : value to add to the code NAF (float) default = 0
        genericity : value to set to the genericity (float) default = 0
        -- OUT
        the function returns nothing  
        '''
        try:
            v = float(valueNAF)
            g = float(genericity)
        except:
            return
        if not(name in self.dicIdNodes):
            self.dicIdNodes[name] = len(self.dicIdNodes)
            self.graphNodes[self.dicIdNodes[name]] = Node(self.dicIdNodes[name], name)
        if codeNAF != "":
            if not(codeNAF in self.graphNodes[self.dicIdNodes[name]].dicNAF):
                self.graphNodes[self.dicIdNodes[name]].dicNAF[codeNAF] = 0
            self.graphNodes[self.dicIdNodes[name]].dicNAF[codeNAF] += v
        if genericity>0:
            self.graphNodes[self.dicIdNodes[name]].genericity = g

    def getNodeByName(self, name):
        ''' return the node if it's present in the graph and None otherwise '''
        if name in self.dicIdNodes:
            return self.graphNodes[self.dicIdNodes[name]]
        else:
            return None

    def getNode(self, i):
        return self.graphNodes[i]

    def removeLonelyNodes(self):
        '''
        function that remove all nodes from graphNodes that
        aren't connected by any edge
        '''          
        toKeepNodes = {}
        for edge in self.graphEdges:
            toKeepNodes[edge[0]] = 1
            toKeepNodes[edge[1]] = 1
        toRemoveNodes = []
        for node in self.graphNodes:
            if not(node in toKeepNodes):
                toRemoveNodes.append(node)
        for node in toRemoveNodes:
            del self.graphNodes[node]

    def resetNodeColors(self):
        '''
        function used for visualization
        '''
        for node in self.graphNodes.values():
            node.setColor(0)

    def computeNodeFeatures(self, nodename, dicKeywords, dicWordWeight, codeNAF=""):
        ''' 
        function that computes the features of a node
        that is where the user define the features he wants to use for the graph learning
        this function is therefore meant to be modified
        -- IN
            nodename : keyword (string)
            dicKeywords : previously selected keywords and their values (dic{keyword (string):value(float)}
            codeNAF : current code NAF used for the propCodeNAF feature (string) default = 0
        -- OUT
            the fucntion returns nothing
        '''
        node = self.graphNodes[self.dicIdNodes[nodename]]
        nbVoisins1 = 0
        node.features["size"] = node.getSize()
        node.features["sumVoisins1"] = 0.0
        node.features["propSumVoisins1"] = 0.0
        node.features["propOccurenceVoisins1"] = 0.0
        maxEdge = max(0.1,max(node.neighbours.values()))
        sumVoisin = sum([neighbour.getSize()*node.neighbours[neighbour]/maxEdge for neighbour in node.neighbours])
        sumOccurrencesVoisin = sum([self.graphEdges[(min(node.id, neighbour.id),max(node.id, neighbour.id))].nbOccurence for neighbour in node.neighbours])
        for neighbour in node.neighbours:
            if neighbour.state==1 and neighbour.name in dicKeywords:
                nbVoisins1+=1
                node.features["sumVoisins1"]+=dicKeywords[neighbour.name]*node.neighbours[neighbour]/maxEdge
                node.features["propSumVoisins1"]+=neighbour.getSize()*node.neighbours[neighbour]/maxEdge
                node.features["propOccurenceVoisins1"] += self.graphEdges[(min(node.id, neighbour.id),max(node.id, neighbour.id))].nbOccurence
        node.features["propSumVoisins1"]/=1.0*sumVoisin
        node.features["propOccurenceVoisins1"]/=1.0*sumOccurrencesVoisin
        node.features["nbVoisins"] = len(node.neighbours)
        node.features["propVoisins1"] = 1.0*nbVoisins1 / node.features["nbVoisins"]
        t = [dicWordWeight[key] for key in UtilsConstants.tokenizeAndStemmerize(node.name, keepComa=False) if key in dicWordWeight]
        node.features["maxWordWeight"] = max(t)
        node.features["minWordWeight"] = min(t)
        node.features["meanWordWeight"] = sum(t)/(max(1,len(t)))
        if codeNAF!="nan" and codeNAF in node.dicNAF:
            node.features["propCodeNAF"] = node.dicNAF[codeNAF]/node.getSize()
        else:
            node.features["propCodeNAF"] = 0

    def deleteNode(self, name):
        '''
        function that deletes a node from the graph
        --IN
            name : keyword to delete (string)
        --OUT
            the function returns nothing
        '''
        if not(name in self.dicIdNodes):
            return
        i = self.dicIdNodes[name]
        del self.dicIdNodes[name]
        del self.graphNodes[i]
        toDelete = []
        for e in self.graphEdges:
            if i in e:
                toDelete.append(e)
        for e in toDelete:
            del self.graphEdges[e]
        
class Node():
    '''
    === Node description: 
    id (int)
    name (str)
    genericity (float)
    dicNAF (dic{codeNAF(str) : value (float)}
    '''
    def __init__(self, id1, name):
        self.id = id1
        self.name= name
        self.genericity = 0.0
        self.dicNAF = {}
        self.features = {}
        self.state = 0
        self.setColor(0)
        self.shape = "disc"
        self.size = 0
        self.neighbours = {}
        
    def setColor(self,state):
        '''
        function used for visualization
        '''
        self.state = state
        if state==1:
            self.color = [250,100,0]
            self.shape = "square"
            self.size = 100
        elif state==3:
            self.color = [0,100,250]
            self.shape = "square"
            self.size = 100
        else:
            self.color = [100,100,100]
            self.shape = "disc"
            self.size = 0
    
    def getSize(self):
        if self.size == 0 or self.size==100:
            self.size = sum(self.dicNAF.values())
        return self.size
            
class Edge():
    '''
    === Edge description:
    id0 (int)
    id1 (int)
    value (float)
    nbOccurence (int)
    '''
    def __init__(self, id0, id1):
        self.id0 = id0
        self.id1 = id1
        self.value = 0.0
        self.nbOccurence = 0


    