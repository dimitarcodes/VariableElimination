"""
@Author: Dimitar Dimitrov, Carla Schindler
"""

import numpy as np

class Factor():

    def __init__(self, variables, probabilities):
        self.variables = variables
        self.probabilities = probabilities

    def reduction(self, observedName, observedValue):
        self.probabilities.pop(observedName)
        for k in self.probabilities.keys():
            if observedName in self.probabilities.get(k).keys():
                origin = self.probabilities.get(k)
                mask = origin[observedName] == observedValue
                new = origin[mask]
                self.probabilities.update({k:new})

    def product(self, other):
        common = []
        for var in self.variables:
            if var in other.variables:
                common.append(var)

