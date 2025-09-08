import sympy as sp

from edge import *

class Node:
    def __init__(self, potential):
        self.potential = sp.sympify(potential)

    def __str__(self) -> str:
        return "(" + str(self.potential) + ")"

    def __repr__(self) -> str:
        return "(" + str(self.potential) + ")"

class Circuit:
    def __init__(self, nodes : int = 0):
        self.nodes = [Node(sp.symbols(f"P_{i}")) for i in range(nodes)]
        self.positive = self.negative = None

        self.edges = dict()

        self.solveResult = None
        self.fullVoltage = None
        self.fullCurrent = None
        self.fullResistance = None

    def addNode(self):
        self.nodes += 1
        return self.nodes - 1

    def addEdge(self, u : int, v : int, resistance = 0):
        assert(u < len(self.nodes) and v < len(self.nodes) and u != v)

        resistance = sp.sympify(resistance)
        self.edges[(u, v)] = Edge(self.nodes[u].potential, self.nodes[v].potential, resistance)
        self.edges[(v, u)] = Edge(self.nodes[v].potential, self.nodes[u].potential, resistance)

    def setElectrode(self, positiveNode : int, negativeNode : int, positivePotential = None, negativePotential = 0):
        assert(positiveNode < len(self.nodes) and negativeNode < len(self.nodes))

        if positivePotential == None:
            positivePotential = sp.symbols("U_0")
        positivePotential, negativePotential = sp.sympify(positivePotential), sp.sympify(negativePotential)
        self.positive = (positiveNode, positivePotential)
        self.negative = (negativeNode, negativePotential)

    def solveCircuit(self):
        assert(self.nodes != [] and self.positive != None and self.negative != None)

        equations = []
        ukn = [node.potential for node in self.nodes]

        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                if (i, j) in self.edges and self.edges[(i, j)].isConductor:
                    self.edges[(i, j)].current = sp.symbols(f"I_{i}_{j}")
                    self.edges[(j, i)].current = -sp.symbols(f"I_{i}_{j}")
                    ukn.append(sp.symbols(f"I_{i}_{j}"))
                    equations.append(sp.Eq(self.nodes[i].potential, self.nodes[j].potential))

        equations.append(sp.Eq(self.nodes[self.positive[0]].potential, self.positive[1]))
        equations.append(sp.Eq(self.nodes[self.negative[0]].potential, self.negative[1]))

        for i in range(len(self.nodes)):
            if i == self.positive[0] or i == self.negative[0]:
                continue
            ISum = 0

            for j in range(len(self.nodes)):
                if not (i, j) in self.edges:
                    continue
                ISum += self.edges[(i, j)].current

            equations.append(sp.Eq(ISum, 0))

        print(equations, ukn)

        solveResult = sp.solve(equations, ukn, dict = True)
        if solveResult == []:
            raise RuntimeError("solve failed")
        self.solveResult = solveResult[0]

        self.fullVoltage = sp.simplify(self.positive[1] - self.negative[1])

        self.fullCurrent = 0
        for i in range(len(self.nodes)):
            if i == self.positive[0] or not (self.positive[0], i) in self.edges:
                continue
            self.fullCurrent += self.edges[(self.positive[0], i)].current.subs(self.solveResult)
        self.fullCurrent = sp.simplify(self.fullCurrent)

        self.fullResistance = sp.simplify(self.fullVoltage / self.fullCurrent)