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
#On considerera que l'utilisateur ne commet pas d'erreur de typage
#
#Le programme mettra exagéremment l'accent (parfois au delà du raisonnable) sur:
#   ->la gestion des erreurs
#   ->l'orienté objet
#afin de se familiariser à ces notions.
#
#En espérant que le code soit aussi clair pour vous qu'il ne l'est pour moi.
#--------------------[Fin de la préface]--------------------


#--------------------[Remarques]--------------------
#Les exceptions terminent l'instruction en cours (le corps de boucle) à la
#manière de 'continue' --> SI J'AI LE TEMPS UTILISER MODULE WARNINGS POUR LES PSEUDO-ERREURS
#
#Spécifier le texte mais utiliser le value Eroor
#
#On reviendra sur l'implémentation de PATH comme un héritage de Graphe
#--------------------[Fin des remarques]--------------------



#On représentera le plus court chemin de n0 à n0 par Path({n0}, {})
#   -> par convention, length = 0
#   -> on le représente par '-'
#On représentera le plus court chemin entre n0 et n1 2 points non connexes par Path({n0, n1}, {})
#   -> par convention, length = inf
#   -> on le représente par '-'


import pyparsing as pp
import railroad
import graphviz as gv

#EXCEPTIONS
class UnexistingElement(Exception):
    "Raised when an instruction refers to an unexisting element"
    pass

#class AmbiguousElement(Exception):
#    "Raised when two distinct instances share the same attributes"
#    pass
    
class IncorrectPath(Exception):
    "Raised when an instruction refers to an incorrect Path"
    
    

#OBJETS
class Node:
#---Dunder methods
    def __init__(self, name):
        self.name = str(name)
        
    def __repr__(self):
        "Precise description"
        return f'Node("{self.name}")'
    
    def __str__(self):
        "Brief description"
        return self.name
    
    def __lt__(self, other):
        return self.name < other.name
    
#---Custom methods
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

class Arc:
#---Dunder methods
    def __init__(self, source, target, weight):
        self.source = source
        self.target = target
        self.weight = weight
        
    def __repr__(self):
        "Precise description"
        return f'Arc({self.source}, {self.target}, {self.weight})'
        
    def __str__(self):
        "Brief description"
        return f'{self.source}-[{self.weight}]>{self.target}'

    def __lt__(self, other):
        return self.weight < other.weight
        
#---Custom methods
    
    def asPath(self):
        "Returns the equivalent path to this arc"
        p_ = Path()
        p_.addNode(self.source)
        p_.addNode(self.target)
        p_.addArc(self)
        return p_
    
class Graph:
#---Dunder methods
    def __init__(self, nodes = set(), arcs = set(), name='graphe'):
        self.name = name
        self.nodes = nodes
        self.arcs = arcs
    
    def __add__(self, other):
        g_ = self.__class__()
        g_.name = self.name + '+' + other.name
        g_.nodes = self.nodes | other.nodes
        g_.arcs = self.arcs | other.arcs
        return g_
    
    def __sub__(self, other):
        g_ = self.__class__()
        g_.name = self.name + '-' + other.name
        g_.nodes = self.nodes | other.nodes
        g_.arcs = self.arcs - other.arcs
        return g_
    
    def __eq__(self, other):
        return self.arcs == other.arcs and self.nodes == other.nodes
    
#---Custom methods
    def addNode(self, node):
        "Adds node to the graph"
        if node.name in [n.name for n in self.nodes]:
            pass
            #Pseudo-erreur, juste à titre informatif
            #
            #IL FAUT RAISE UN WARNING AMBIGOUS ELT
        self.nodes.add(node)
        
    def removeNode(self, node):
        "Removes node from the graph"
        if not node in self.nodes:
            raise UnexistingElement
        else: self.nodes.remove(node)
        
    def addArc(self, arc):
        "Adds arc to the graph"
        if (arc.source, arc.target, arc.weight) in [(a.source, a.target, a.weight) for a in self.arcs]:
            pass
            #Pseudo-erreur, juste à titre informatif
            #
            #IL FAUT RAISE UN WARNING AMBIGOUS ELT
        self.arcs.add(arc)
    
    def removeArc(self, arc):
        "Removes arc from the graph"
        if not arc in self.arcs:
            raise UnexistingElement
        else: self.arcs.remove(arc)
        
    def getNode(self, name)->Node:
        "Returns one of the graph's nodes whose name is name"
        nodes = [n for n in self.nodes if n.name == str(name)]
        if nodes == []:
            raise UnexistingElement
            return None
        else:
            if len(nodes) > 1:
                pass
                #Pseudo-erreur, juste à titre informatif
                #
                #IL FAUT RAISE UN WARNING AMBIGOUS ELT
            return nodes[0]
        
    def fromFile(self, parser, fileName:str):
        "Load the graph's data from the '../fileName' file"
        #Parse les données selon le pattern du parser
        parsedData = parser.parse(fileName)
        
        #Charge les parametres du graphe dans un dictionnaire
        #(on ne doit avoir que Name=nomDuGraphe)
        parametres = {p[0]:p[1] for p in parsedData[0]}
        nodes = parsedData[1]
        arcs = parsedData[2]
    
        if 'Name' in parametres:
            self.name = parametres['Name']
    
        self.nodes = set([Node(n) for n in nodes])
        self.arcs = set([Arc(self.getNode(a[0]), self.getNode(a[1]), float(a[2])) for a in arcs])
    
    def cleanerDijkstra(self, root):
        """cleanerDijkstra(self, n0)
        Renvoie l'arbre de parentée des sommets du graphe tel que:
            -sa racine est n0
            -tout point non atteignable n'est pas dans ce graphe"""
        
        tree = Tree()
        dist = {n:float('inf') for n in self.nodes}
        dist[root]=0
        parent = dict()
        
        while len(self.nodes-tree.nodes) > 0:
            L = list(self.nodes - tree.nodes)
            nMin = L[0]
            dMin = dist[nMin]
            for n in L[1:]:
                if dist[n] <= dMin:
                    nMin = n
                    dMin = dist[n]
            tree.addNode(nMin)
            if nMin != root:
                tree.addArc(Arc(parent[nMin], nMin, dist[nMin]-dist[parent[nMin]]))
            
            for a in nMin.arcsFrom(self):
                if a.target not in tree.nodes:
                    if dist[a.target] > dist[nMin] + a.weight:
                        dist[a.target] = dist[nMin] + a.weight
                        parent[a.target] = nMin
        return tree

     
    def cleanerDijkstraBuguee(self, root):
        """cleanerDijkstra(self, n0)
        Renvoie l'arbre de parentée des sommets du graphe tel que:
            -sa racine est n0
            -tout point non atteignable n'est pas dans ce graphe"""
        
        tree = Tree()
        toExplore = {root}
        dist = {root:0}
        parent = dict()
        
        while len(toExplore-tree.nodes) > 0:
            L = list(toExplore - tree.nodes)
            nMin = L[0]
            dMin = dist[nMin]
            for n in L[1:]:
                if dist[n] <= dMin:
                    nMin = n
                    dMin = dist[n]
            tree.addNode(nMin)
            if nMin != root:
                tree.addArc(Arc(parent[nMin], nMin, dist[nMin]-dist[parent[nMin]]))
            
            for a in nMin.arcsFrom(self):
                if a.target not in tree.nodes:
                    if a not in toExplore:
                        toExplore.add(a.target)
                        dist[a.target] = dist[nMin] + a.weight
                        parent[a.target] = nMin
                    else:
                        if dist[a.target] > dist[nMin] + a.weight:
                            dist[a.target] = dist[nMin] + a.weight
                            parent[a.target] = nMin
        return tree

    def dijkstra(self, n0):
        "Returns the dictionary of shorter paths towards all the graph's nodes"
        p0 = Path()
        p0.addNode(n0)
        
        toVisit = {n0}
        visited = set()
        paths = {n0: p0}
        while(len(toVisit) > 0):
            p = min([paths[n_] for n_ in paths if n_ not in visited])
            n = p.endingNode()
            toVisit.remove(n)
            visited.add(n)
            
            #On notera v_ toute variable v qu'on utilise pour explorer les arcs
            for a_ in n.arcsFrom(self):
                #On ne parcourt que les arcs dont les sommets d'arrivées ne sont pas visités
                if not a_.target in visited:
                    p_ = p + a_.asPath()
                    if a_.target in toVisit:
                        if p_ < paths[a_.target]: paths[a_.target] = p_
                    else:
                        toVisit.add(a_.target)
                        paths[a_.target] = p_
                        
        for n in self.nodes - visited:
            pNone = Path()
            pNone.addNode(n0)
            pNone.addNode(n)
            paths[n] = pNone
        
        return paths

    def cleanerTable(self, BASE):
        """Returns a 2-tensor whose column vectors are the distances from the
        base node"""
        parentyTrees = {node : cleanerDijkstra(node) for node in BASE}
        #Qu'est ce qui est le plus élégant ?
        #   -garder la convertion en chemins (structure claire et précise mais code plus long)
        #   -travailler directement sur le graphe de parentée (syntaxe plus lourde mais pas de redondance)  
        shortestPaths = {node0 : {node1 : parentyTrees[node0].pathTowards(node1)for node1 in BASE} for node0 in BASE}
        text = " "*5
        for node1 in BASE:
            text += f'{node1.name:^5}'
        for node0 in BASE:
            row = f'{node2.name:^5}'
            for node1 in BASE:
                path = shortestPaths[node0][node1]
                if path.isNone() or path.isNull():
                    row += f'{"-":^5}'
                else:
                    row += f'{path.length():^5}'
            text += row + '\n'
        return text
    
    def matrice(self, base):
        """Returns a 2-tensor whose column vectors are the distances from the
        base node"""
        M = []
        for n0 in base:
            paths = self.dijkstra(n0)
            row = []
            for n in base:
                row.append(paths[n].length())
            M.append(row)
        return [[M[j][i] for j in range(len(M[i]))] for i in range(len(M))]
    
    def longestShortestPath(self):
        "Returns the longest shortest path of the graph"
        maxPaths = []
        for n0 in self.nodes:
            paths = self.dijkstra(n0)
            maxPaths.append(max([paths[n] for n in paths]))
        return max(maxPaths)
    
    def display(self):
        G =  gv.Digraph(self.name, filename=f'{self.name}.gv', format='svg')
        for arc in self.arcs:
            G.edge(arc.source.name, arc.target.name, label=f'{arc.weight}')
        return G
       
class Tree(Graph):
#---Dunder methods
    def __init__(self, nodes = set(), arcs = set(), name = 'arbre'):
        super().__init__(nodes, arcs, name)
            
#---Custom methods
    def Deepness(self, node):
        if not node in self.nodes:
            deepness = float('inf')
        else:
            deepness = 0
            while len(node.arcsTowards(self)) == 1:
                arc = list(node.arcsTowards(self))[0]
                node = arc.source
                deepness += arc.weight
        return deepness
        
    def Root(self):
        return [node for node in self.nodes if len(node.arcsTowards(self)) == 0][0]
    
    def pathTowards(self, node):
        if not node in self.nodes:
            path = Path(nodes={self.Root(), node})
        else:
            path = Path()
            path.addNode(node)
            while len(node.arcsTowards(self)) == 1:
                arc = list(node.arcsTowards(self))[0]
                node = arc.source
                path.addNode(node)
                path.addArc(arc)
        return path
        
class Path(Tree):
#---Dunder methods
    def __init__(self, nodes = set(), arcs = set(), name = 'chemin'):
        super().__init__(nodes, arcs, name)
    
    def __lt__(self, other):
        return self.length() < other.length()   
    
#---Custom methods
    def length(self):
        "Returns the length of the path"
        if self.isNone():
            return float('inf')
        else:
            return sum([a.weight for a in self.arcs])
        
    def startingNode(self):
        "Returns the starting node of the path"
        return self.Root()
    
    def endingNode(self):
        "Returns the ending node of the path"
        return [node for node in self.nodes if len(node.arcsFrom(self)) == 0][0]
    
    def isNone(self)->bool:
        return len(self.arcs) == 0 and len(self.nodes) == 2
    
    def isNull(self)->bool:
        return len(self.arcs) == 0 and len(self.nodes) == 1
    
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
    def parse(self, fileName: str):
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
    
    def createDiagram(self, filename = 'diagramme'):
        if int(pp.__version__.split('.')[0]) >= 3:
            self.graphePattern.create_diagram('parser_element_sommets_diag.html')


if __name__ == "__main__":
    p = Parser()
    g = Graph()
    g.fromFile(p, 'graphe.txt')
    
    BASE = [n for n in g.nodes]
    BASE.sort()
    
    lsp = g.longestShortestPath()
    G =  gv.Digraph(g.name, filename=f'{g.name}.gv', format='svg')
    for arc in (g - lsp).arcs:
        G.edge(arc.source.name, arc.target.name, label=f'{arc.weight}')
    for arc in lsp.arcs:
        G.edge(arc.source.name, arc.target.name, label=f'{arc.weight}', color='red')
    for n in lsp.nodes:
        G.node(n.name, color='red', fontcolor='red')