import sympy as sp

class Edge:
    def __init__(self, potentialFrom, potentialTo, resistance = 0, current = None):
        self.potentialFrom = sp.sympify(potentialFrom)
        self.potentialTo = sp.sympify(potentialTo)
        self.resistance = sp.sympify(resistance)

        self.voltage = self.isConductor = self.current = None
        self.update(current)

    def __str__(self) -> str:
        return "(" + str(self.potentialFrom) + ") -> (" + str(self.potentialTo) + "): " + str(self.resistance)

    def __repr__(self) -> str:
        return "(" + str(self.potentialFrom) + ") -> (" + str(self.potentialTo) + "): " + str(self.resistance)

    def update(self, current = None):
        self.voltage = self.potentialFrom - self.potentialTo

        self.isConductor = (self.resistance == 0)
        if not self.isConductor:
            self.current = self.voltage / self.resistance
        else:
            self.current = sp.sympify(current)