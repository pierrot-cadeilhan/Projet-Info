# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 13:59:06 2023

@author: Pierrot
"""

#--------------------[Préface]--------------------
#On conviendra que:
#   ->__repr__  est une description précise et non-ambigue.
#   ->__str__   est une description interprétable par l'utilisateur.
#
#On acceptera l'existence de deux instances (ex: Node, Arc, ...) aux attributs
#identiques comme deux objets distincts.
#
#Le programme mettra exagéremment l'accent (parfois au delà du raisonnable) sur:
#   ->la gestion des erreurs
#   ->l'orienté objet
#afin de se familiariser à ces notions.
#
#En espérant que le code soit aussi clair pour vous qu'il ne l'est pour moi.
#--------------------[Fin de la préface]--------------------


#--------------------[REMARQUES]--------------------
#Les exceptions terminent l'instruction en cours (le corps de boucle) à la
#manière de 'continue' --> SI J'AI LE TEMPS UTILISER MODULE WARNINGS POUR LES PSEUDO-ERREURS


#--------------------[EXCEPTIONS]--------------------
class UnexistingElement(Exception):
    "Raised when an instruction refers to an unexisting element"
    pass

class AmbiguousElement(Exception):
    "Raised when two distinct instances share the same attributes"
    pass
    
class IncorrectPath(Exception):
    "Raised when an instruction refers to an incorrect Path"


#--------------------[OBJETS]--------------------
#DONE
class Node:
    
    #Dunder methods
    def __init__(self, name):
        self.name = str(name)
        
    def __repr__(self):
        return f'Node("{self.name}")'
    
    def __str__(self):
        return self.name
    
    def __lt__(self, other):
        return self.name < other.name
    
    #Custom methods
    def arcsTowards(self, graph)->set:
        "Returns the sub-set of the graph's arcs pointing towards self"
        if not self in graph.nodes:
            raise UnexistingElement
            return set()
        else:
            return set([a for a in graph.arcs if a.target == self])
    
    def arcsFrom(self, graph)->set:
        "Returns the sub-set of the graph's arcs departing from self"
        if not self in graph.nodes:
            raise UnexistingElement
            return set()
        else:
            return set([a for a in graph.arcs if a.source == self])

    def parents(self, graph)->set:
        """Returns the sub-set of the graph's nodes whose self is a child
        Note: this information can be obtained with Node.arcsTowards"""
        if not self in graph.nodes:
            raise UnexistingElement
            return set()
        else:
            return set([a.source for a in graph.arcs if a.target == self])

    def children(self, graph)->set:
        """Returns the sub-set of the graph's nodes whose self is a parent
        Note: this information can be obtained with Node.arcsFrom"""
        if not self in graph.nodes:
            raise UnexistingElement
            return set()
        else:
            return set([a.target for a in graph.arcs if a.source == self])

#DONE
class Arc:
    
    #Dunder methods
    def __init__(self, source, target, weight):
        self.source = source
        self.target = target
        self.weight = weight
        
    def __repr__(self):
        return f'Arc({self.source}, {self.target}, {self.weight})'
        
    def __str__(self):
        return f'{self.source}-[{self.weight}]>{self.target}'

    def __lt__(self, other):
        return self.weight < other.weight
        
    #Custom methods
    def length(self):
        return self.weight
    
class Path:
    def __init__(self, arcs):
        self.arcs = arcs
        if not self.isCorrect():
            raise IncorrectPath
    
    def __add__(self, other):
        p = Path(self.arcs + other.arcs)
        if p.isCorrect():
            return p
        else:
            raise IncorrectPath
    
    def __lt__(self, other):
        return self.length() < other.length()
        
    def __str__(self):
        if self.arcs == []:
            return 'Path([])'
        else:
            txt = self.arcs[0].source.__str__()
            for a in self.arcs:
                txt += f'-[{a.weight}]>{a.target}'
            return txt
    def __repr__(self):
        return f'Path([{self.arcs}])'
        
    def isCorrect(self):
        correct = True
        for i in range(len(self.arcs)-1):
            if self.arcs[i].target != self.arcs[i+1].source:
                correct = False
        return correct
    
    def length(self):
        l = 0
        for a in self.arcs:
            l += a.length()
        return l
    
class Graph:
    
    #Dunder methods
    def __init__(self, name='graphe'):
        self.name = name
        self.nodes = set()
        self.arcs = set()
    
    #Custom methods
    def addNode(self, node):
        if node.name in [n.name for n in self.nodes]:
            #Pseudo-erreur, juste à titre informatif
            self.nodes.add(node)
            raise AmbiguousElement
        self.nodes.add(node)
        
    def removeNode(self, node):
        if not node in self.nodes:
            raise UnexistingElement
        else: self.nodes.remove(node)
        
    def addArc(self, arc):
        if (arc.source, arc.target, arc.weight) in [(a.source, a.target, a.weight) for a in self.arcs]:
            #Pseudo-erreur, juste à titre informatif
            self.arcs.add(arc)
            raise AmbiguousElement
        self.arcs.add(arc)
    
    def removeArc(self, arc):
        if not arc in self.arcs:
            raise UnexistingElement
        else: self.arcs.remove(arc)
        
    def getNode(self, name)->Node:
        "Returns one of the graph's nodes whose name is name"
        nodes = [n for n in self.nodes if n.name == str(name)]
        print(nodes)
        if nodes == []:
            raise UnexistingElement
            return None
        else:
            if len(nodes) > 1:
                #Pseudo-erreur, juste à titre informatif
                raise AmbiguousElement
            return nodes[0]
        
