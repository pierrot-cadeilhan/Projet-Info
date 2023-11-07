# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 13:59:06 2023

@author: Pierrot
"""

#--------------------[Préface]--------------------
#On acceptera l'existence de deux instances (ex: Node, Arc, ...) aux attributs
#identiques comme deux objets distincts.
#
#On considèrera que le chemin Path({n1, n2}, {}) est un chemin inexistant entre n1 et n2
#On pourra ainsi considérer des graphes d'arêtes de poids infinis
#On considèrera que le chemin Path({n0}, {}) est le chemin entre n0 et n0 sans arête
#On pourra ainsi considérer des graphes d'arêtes de coefficients nuls
#
#/!\ et des graphes d'arêtes à poids négatif ?
#
#En espérant que le code soit aussi clair pour vous qu'il ne l'est pour moi.
#--------------------[Fin de la préface]--------------------


#----------------------[Remarques]--------------------
#Il me faut construire la fonction DijkstraVersion2 qui renvoie l'arbre de parenté
#méthodes et fonctions: Fonction()
#variables: maSuperVariable

#Path n'hérite pas de Tree car n'est pas forcément connexe
#--------------------[Fin des remarques]--------------------


import pyparsing as pp
import graphviz as gv
noFigure = 0

#OBJETS
class Node:
#---Dunder methods
    def __init__(self, name='Sommet'):
        self.name = str(name)
        
    def __repr__(self):
        """Description non ambigue de l'objet."""
        return f'Node("{self.name}")'
    
    def __str__(self):
        """Description claire de l'objet."""
        return self.name
    
    def __lt__(self, other):
        return self.name < other.name
    
#---Custom methods
    def ArcsTowards(self, graph)->set:
        """node.ArcsTowards(graph)
        Renvoie le sous-ensemble des arêtes de graph pointant vers node.
        """
        if not self in graph.nodes:
            print(f"Le sommet {self.name} n'est pas dans le graphe {graph.name}.")
            return set()
        else:
            return set([a for a in graph.arcs if a.target == self])
    
    def ArcsFrom(self, graph)->set:
        """node.ArcsFrom(graph)
        Renvoie le sous-ensemble des arêtes de graph partant de node.
        """
        if not self in graph.nodes:
            print(f"Le sommet {self.name} n'est pas dans le graphe {graph.name}.")
            return set()
        else:
            return set([a for a in graph.arcs if a.source == self])

class Arc:
#---Dunder methods
    def __init__(self, source, target, weight):
        self.source = source
        self.target = target
        self.weight = weight
        
    def __repr__(self):
        """Description non ambigue de l'objet."""
        return f'Arc({self.source}, {self.target}, {self.weight})'
        
    def __str__(self):
        """Description claire de l'objet."""
        return f'({self.source}, {self.target}, {self.weight})'

    def __lt__(self, other):
        return self.weight < other.weight
        
#---Custom methods
    def AsPath(self):
        """arc.AsPath()
        Renvoie le chemin équivalent à l'arc"""
        return Path(nodes={self.source, self.target}, start=self.source, arcs={self}, name='Arc')
    
class Graph:
#---Dunder methods
    def __init__(self, arcs=set(), nodes=set(), name='Graphe'):
        self.name = name
        self.nodes = nodes
        self.arcs = arcs
    
    def __add__(self, other):
        """Somme de deux graphes comme la réunion
        des sommets et des arêtes."""
        g = self.__class__()
        g.name = self.name + '+' + other.name
        g.nodes = self.nodes | other.nodes
        g.arcs = self.arcs | other.arcs
        return g
    
    def __sub__(self, other):
        """Différence de deux graphes comme la réunion
        des sommets et la différence des arêtes."""
        g = Graph()
        g.name = self.name + '-' + other.name
        g.nodes = self.nodes | other.nodes
        g.arcs = self.arcs - other.arcs
        return g
    
#---Custom methods
    def AddNode(self, node):
        """graph.AddNode(node)
        Ajoute node aux sommets de graph."""
        if node.name in [n.name for n in self.nodes]:
            print("Il y a déjà un sommet de nom {node.name} dans le graphe {self.name}.")
        self.nodes.add(node)
        
    def RemoveNode(self, node):
        """graph.RemoveNode(node)
        Retire node des sommets de graph."""
        if not node in self.nodes:
            print(f"Le sommet {node.name} n'est pas dans le graphe {self.name}.")
        else:
            self.nodes.remove(node)
        
    def AddArc(self, arc):
        """graph.AddArc(arc)
        Ajoute arc aux arcs de graph."""
        self.arcs.add(arc)
    
    def RemoveArc(self, arc):
        """graph.RemoveArc(arc)
        Retire arc des arcs de graph."""
        if not arc in self.arcs:
            print(f"L'arc {arc} n'est pas dans le graphe {self.name}.")
        else:
             self.arcs.remove(arc)
        
    def GetNode(self, name)->Node:
        """graph.GetNode(name)
        Renvoie un sommet de graph dont le nom est name"""
        nodes = [n for n in self.nodes if n.name == str(name)]
        if nodes == []:
            print("Il n'y a pas de sommet du nom de {name} dans le graphe {self.name}.")
            return None
        else:
            if len(nodes) > 1:
                print("Il y a plusieurs sommets du nom de {name} dans le graphe {self.name}.")
            return nodes[0]
        
    def FromFile(self, parser, fileName:str):
        """graph.FromFile(parser, fileName)
        Charge dans graph le graphe représenté dans fileName selon le parseur parser"""
        
        #Parse les données selon la syntaxe de parser
        parsedData = parser.Parse(fileName)
        #Charge les parametres du graphe dans un dictionnaire
        parametres = {p[0]:p[1] for p in parsedData[0]}
        
        nodes = parsedData[1]
        arcs = parsedData[2]
    
        if 'Name' in parametres:
            self.name = parametres['Name']
    
        self.nodes = set([Node(n) for n in nodes])
        self.arcs = set([Arc(self.GetNode(a[0]), self.GetNode(a[1]), float(a[2])) for a in arcs])
    
    def Dijkstra(self, node0):
        """graph.Dijkstra(node0)
        Renvoie le dictionnaire des plus courts chemins vers tous les sommets de graph depuis node0"""
        p0 = Path(nodes={node0}, start=node0)
        
        toVisit = {node0}
        visited = set()
        paths = {node0: p0}
        while(len(toVisit) > 0):
            minPath = min([paths[node] for node in paths if node not in visited])
            minNode = minPath.EndingNode()
            toVisit.remove(minNode)
            visited.add(minNode)
            
            #On notera v_ toute variable v qu'on utilise pour explorer les arcs
            for arc in minNode.ArcsFrom(self):
                #On ne parcourt que les arcs dont les sommets d'arrivées ne sont pas visités
                if not arc.target in visited:
                    path = minPath + arc.AsPath()
                    if arc.target in toVisit:
                        if path < paths[arc.target]:
                            paths[arc.target] = path
                    else:
                        toVisit.add(arc.target)
                        paths[arc.target] = path
                        
        for node in self.nodes - visited:
            pNone = Path(nodes={node0, node}, start=node0)
            paths[node] = pNone
        
        return paths
    
    def Display(self):
        """graph.Display()
        Construit, sauvegarde et affiche une représentation en svg de graph."""
        global noFigure
        diag = gv.Digraph(f'{self.name}', filename=f'figures/{noFigure}.gv', format='svg')
        noFigure += 1
        
        for arc in self.arcs:
            diag.edge(arc.source.name, arc.target.name, label=str(arc.weight))
        for node in self.nodes:
            diag.node(node.name)
        diag.view()
        
class Tree(Graph):
#---Dunder methods
    def __init__(self, nodes=set(), arcs=set(), name='Arbre'):
        super().__init__(nodes=nodes, arcs=arcs, name=name)
        
#---Custom methods
    def Depth(self, node):
        """tree.Depth(node)
        Renvoie la profondeur de node dans tree."""
        if not node in self.nodes:
            #Par convention, la longueur d'un chemin inexistant est l'infini
            depth = float('inf')
        else:
            depth = 0
            while len(node.ArcsTowards(self)) == 1:
                arc = list(node.ArcsTowards(self))[0]
                node = arc.source
                depth += arc.weight
        return depth
        
    def Root(self):
        """tree.Root()
        Renvoie le sommet racine de tree."""   
        #La formule est définie car l'arbre est connexe sans cycle
        return [node for node in self.nodes if len(node.ArcsTowards(self)) == 0][0]


    
class Path(Graph):
#---Dunder methods
    def __init__(self, nodes=set(), start=Node(), arcs=set(), name='Chemin'):
        super().__init__(nodes=nodes, arcs=arcs, name=name)
        self.start = start
        
    def __lt__(self, other):
        return self.Length() < other.Length()
    
    def __add__(self, other):
        """Somme de deux graphes comme la réunion
        des sommets et la différence des arêtes."""
        #/!\ Il faut que le sommet à l'extrémité de self soit le sommet de départ de other
        p = Path()
        p.name = self.name + '-' + other.name
        p.nodes = self.nodes | other.nodes
        p.arcs = self.arcs | other.arcs
        p.start = self.start
        return p
        
        
#---Custom methods
    def Length(self):
        """path.Length()
        Renvoie la longueur de path."""
        if self.IsNot():
            return float('inf')
        else:
            return sum([arc.weight for arc in self.arcs])        
    
    def EndingNode(self):
        """path.EndingNode()
        Renvoie le sommet à l'extrémité de path."""
        if self.IsNot():
            return list(self.nodes-{self.start})[0]
        else:
            return [node for node in self.nodes if len(node.ArcsFrom(self)) == 0][0]
    
    def IsTrivial(self):
        """path.IsTrivial()
        Renvoie True si path connecte un sommet à lui même
        sans l'intermédiaire d'arêtes."""
        return len(self.nodes)==1 and len(self.arcs) == 0
    
    def IsNot(self):
        """path.IsNot()
        Renvoie True si path n'est pas connexe (par convention s'il n'existe pas)."""
        return len(self.nodes)==2 and len(self.arcs) == 0
    
    
class Parser:
#---Dunder methods    
    def __init__(self):
        "Initialise le pattern du parser"
        
        #Généralise la notion de paramètre
        parametrePattern = pp.Group(pp.Word(pp.alphanums + '_') + pp.Suppress('="') + pp.Word(pp.alphanums + '_' + '.' + ':' + '-' + ' ') + pp.Suppress('"'))
    
        #Parse une structure de type <SOMMETS> </SOMMETS>
        sommetPattern = pp.Word(pp.alphas)
        sommetsPattern = pp.Group(pp.Suppress("<SOMMETS>") + pp.ZeroOrMore(sommetPattern + pp.Suppress(';')) + pp.Suppress("</SOMMETS>"))
        
        #Parse une structure de type <ARCS> </ARCS>
        arcPattern = pp.Group(sommetPattern + pp.Suppress(':') + sommetPattern + pp.Suppress(':') + pp.Word(pp.nums))
        arcsPattern = pp.Group(pp.Suppress("<ARCS>") + pp.ZeroOrMore(arcPattern + pp.Suppress(';')) + pp.Suppress("</ARCS>"))
        
        #Parse les parametres d'une structure de type <GRAPHE> </GRAPHE>
        headingPattern = pp.Suppress('<GRAPHE') + pp.Group(pp.ZeroOrMore(parametrePattern + (pp.Suppress(',') | pp.Suppress(pp.Empty())))) + pp.Suppress('>')
        #Détecte la fin de la structure <GRAPHE> </GRAPHE>
        tailPattern = pp.Suppress("</GRAPHE>")
        
        #Parse une structure de type <GRAPHE> </GRAPHE>
        self.graphePattern = headingPattern + sommetsPattern + arcsPattern + tailPattern

 #---Custom methods       
    def Parse(self, fileName: str):
        "Parse a <GRAPHE> </GRAPHE> structure encoded in the '../fileName' file"
        #ATTENTION: On suppose que le fichier en question est bien encodé et ne contient qu'un graphe
        retourParser = None
        try:
            retourParser = self.graphePattern.parseFile(fileName, parseAll=True)
        except pp.ParseException as err:
            print(err.line)
            print(" "*(err.column-1) + "^")
            print(err)
        return retourParser

if __name__ == "__main__":
    p = Parser()
    g = Graph()
    g.FromFile(p, 'graphe.txt')
    
    BASE = [n for n in g.nodes]
    BASE.sort()
    
    g = Graph(nodes={BASE[0], BASE[1], BASE[2]}, arcs={Arc(BASE[0], BASE[1], 1), Arc(BASE[1], BASE[2], 1), Arc(BASE[2], BASE[0], 1)}, name="Cycle")
    t = Tree(nodes={BASE[0], BASE[1], BASE[2], BASE[3]}, arcs={Arc(BASE[0], BASE[1], 1), Arc(BASE[0], BASE[2], 1), Arc(BASE[2], BASE[3], 1)}, name='Arbre_exemple')
